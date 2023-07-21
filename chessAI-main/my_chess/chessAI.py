import pygame
import chess
import chess.engine

# Initialize pygame
pygame.init()

# Define some colors
LIGHT_GREEN = (144, 238, 144)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

# Define the screen dimensions and square size
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
SQUARE_SIZE = SCREEN_WIDTH // 8

# Load the chessboard image
chessboard_img = pygame.image.load("chessboard.png")
chessboard_img = pygame.transform.scale(chessboard_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize the chess engine
engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\Meet\\Desktop\\Stockfish\\stockfish-windows-x86-64-avx2.exe")

# Initialize the chessboard
board = chess.Board()

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load the piece images
pieces_dir = "/Users/Meet/Desktop/chessAI-main/my_chess/"
piece_images = {
    "P": pygame.image.load(pieces_dir + "white_pawn.png"),
    "N": pygame.image.load(pieces_dir + "white_knight.png"),
    "B": pygame.image.load(pieces_dir + "white_bishop.png"),
    "R": pygame.image.load(pieces_dir + "white_rook.png"),
    "Q": pygame.image.load(pieces_dir + "white_queen.png"),
    "K": pygame.image.load(pieces_dir + "white_king.png"),
    "p": pygame.image.load(pieces_dir + "black_pawn.png"),
    "n": pygame.image.load(pieces_dir + "black_knight.png"),
    "b": pygame.image.load(pieces_dir + "black_bishop.png"),
    "r": pygame.image.load(pieces_dir + "black_rook.png"),
    "q": pygame.image.load(pieces_dir + "black_queen.png"),
    "k": pygame.image.load(pieces_dir + "black_king.png"),
}

# Function to draw the chessboard
def draw_board():
    screen.blit(chessboard_img, (0, 0))
    for square in chess.SQUARES:
        file, rank = chess.square_file(square), chess.square_rank(square)
        x = file * SQUARE_SIZE
        y = (7 - rank) * SQUARE_SIZE
        piece = board.piece_at(square)
        if piece is not None:
            piece_symbol = piece.symbol()
            img = piece_images[piece_symbol]
            screen.blit(img, (x, y))
        if selected_square is not None and square in valid_moves:
            pygame.draw.circle(screen, RED, (x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2), 5)

# Function to handle the player's move
def handle_player_move(from_square, to_square):
    move = chess.Move(from_square, to_square)
    if move in board.legal_moves:
        board.push(move)
        draw_board()
        pygame.display.flip()
        valid_moves.clear()  # Clear the valid moves for the next selection
        handle_ai_move()

# Function to handle the AI opponent's move
def handle_ai_move():
    result = engine.play(board, chess.engine.Limit(time=2.0))
    board.push(result.move)
    draw_board()
    pygame.display.flip()

# Function to undo the last move
def undo_move():
    if len(board.move_stack) >= 2:
        board.pop()
        board.pop()
        draw_board()
        pygame.display.flip()

# Function to reset the board
def reset_board():
    board.reset()
    draw_board()
    pygame.display.flip()

# Function to display evaluation score
def display_evaluation():
    info = engine.analyse(board, chess.engine.Limit(time=0.1))
    score = info["score"].relative.score()
    text = "Evaluation: {}".format(score)
    font = pygame.font.SysFont(None, 24)
    text_surface = font.render(text, True, WHITE)
    screen.blit(text_surface, (10, 10))

# Function to get a hint move from the engine
def get_hint_move():
    result = engine.play(board, chess.engine.Limit(time=2.0))
    hint_move = result.move
    return hint_move

# Main game loop
clock = pygame.time.Clock()
running = True
selected_square = None
valid_moves = []
dragging_piece = None

while running:
    clock.tick(60)  # Limit the frame rate to 60 FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if not board.turn or board.is_game_over():
                continue
            x, y = event.pos
            file = x // SQUARE_SIZE
            rank = 7 - y // SQUARE_SIZE
            selected_square = chess.square(file, rank)
            dragging_piece = piece_images.get(board.piece_at(selected_square).symbol())
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_square is not None:
                x, y = event.pos
                file = x // SQUARE_SIZE
                rank = 7 - y // SQUARE_SIZE
                target_square = chess.square(file, rank)
                handle_player_move(selected_square, target_square)
                selected_square = None
                dragging_piece = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_board()
            elif event.key == pygame.K_u:
                undo_move()
            elif event.key == pygame.K_h:
                hint_move = get_hint_move()
                if hint_move is not None:
                    board.push(hint_move)
                    draw_board()
                    pygame.display.flip()
                    handle_ai_move()

    if selected_square is not None:
        valid_moves = [move.to_square for move in board.legal_moves if move.from_square == selected_square]

    draw_board()
    display_evaluation()
    if dragging_piece is not None:
        x, y = pygame.mouse.get_pos()
        x -= SQUARE_SIZE // 2
        y -= SQUARE_SIZE // 2
        screen.blit(dragging_piece, (x, y))
    if selected_square is not None:
        x = chess.square_file(selected_square) * SQUARE_SIZE
        y = (7 - chess.square_rank(selected_square)) * SQUARE_SIZE
        pygame.draw.rect(screen, LIGHT_GREEN, (x, y, SQUARE_SIZE, SQUARE_SIZE), 3)

    pygame.display.flip()

# Clean up
engine.quit()
pygame.quit()
