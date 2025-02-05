import pygame
import random
import numpy as np
import copy

pygame.init()

WIDTH, HEIGHT = 400, 450  # Aumentamos la altura para mostrar el puntaje
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Damas 4x4 con Q-Learning')

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

ROWS, COLS = 4, 4
SQUARE_SIZE = WIDTH // COLS

empty_square = 0
human = 1
bot = -1
selected_piece = None
valid_moves = []

human_score = 0
bot_score = 0
winner = None

Q = {}
alpha = 0.1
gamma = 0.9
epsilon = 0.1


def get_state():
    return tuple(map(tuple, board))


def draw_board():
    SCREEN.fill(WHITE)
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(SCREEN, BLACK if (row + col) % 2 else WHITE, rect)
            if board[row][col] == human:
                pygame.draw.circle(SCREEN, RED, rect.center, SQUARE_SIZE // 3)
            elif board[row][col] == bot:
                pygame.draw.circle(SCREEN, BLUE, rect.center, SQUARE_SIZE // 3)

    font = pygame.font.SysFont(None, 30)
    score_text = font.render(f"Rojo: {human_score}  Azul: {bot_score}", True, BLACK)
    SCREEN.blit(score_text, (10, HEIGHT - 40))

    if winner:
        winner_text = font.render(f"{winner} gana!", True, BLACK)
        SCREEN.blit(winner_text, (WIDTH // 3, HEIGHT - 20))


def get_valid_moves(player, row, col):
    moves, captures = [], []
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            if board[new_row][new_col] == empty_square:
                moves.append((new_row, new_col))
            elif board[new_row][new_col] == -player:
                jump_row, jump_col = new_row + dr, new_col + dc
                if 0 <= jump_row < ROWS and 0 <= jump_col < COLS and board[jump_row][jump_col] == empty_square:
                    captures.append(((new_row, new_col), (jump_row, jump_col)))
    return moves, captures


def move_piece(start, end):
    start_row, start_col = start
    end_row, end_col = end
    board[end_row][end_col] = board[start_row][start_col]
    board[start_row][start_col] = empty_square


def capture_piece(start, mid, end, player):
    global human_score, bot_score
    board[mid[0]][mid[1]] = empty_square
    move_piece(start, end)
    if player == human:
        human_score += 1
    else:
        bot_score += 1


def check_winner():
    global winner
    human_pieces = sum(row.count(human) for row in board)
    bot_pieces = sum(row.count(bot) for row in board)
    if human_pieces == 0:
        winner = "Azul"
    elif bot_pieces == 0:
        winner = "Rojo"


def bot_move():
    state = get_state()
    actions = [(r, c, move) for r in range(ROWS) for c in range(COLS) if board[r][c] == bot
               for move in get_valid_moves(bot, r, c)[0]]

    if actions:
        start_r, start_c, end = random.choice(actions)
        moves, captures = get_valid_moves(bot, start_r, start_c)
        if captures:
            mid, end = random.choice(captures)
            capture_piece((start_r, start_c), mid, end, bot)
        else:
            move_piece((start_r, start_c), end)

    check_winner()


def main():
    global selected_piece, valid_moves, winner
    run, turn = True, human
    while run:
        draw_board()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and turn == human and not winner:
                x, y = pygame.mouse.get_pos()
                col, row = x // SQUARE_SIZE, y // SQUARE_SIZE
                if selected_piece:
                    moves, captures = get_valid_moves(human, selected_piece[0], selected_piece[1])
                    if captures and any(end == (row, col) for _, end in captures):
                        for mid, end in captures:
                            if end == (row, col):
                                capture_piece(selected_piece, mid, end, human)
                                break
                        turn = bot
                    elif (row, col) in moves:
                        move_piece(selected_piece, (row, col))
                        turn = bot
                    selected_piece, valid_moves = None, []
                elif board[row][col] == human:
                    selected_piece = (row, col)
                    valid_moves, _ = get_valid_moves(human, row, col)

        if turn == bot and not winner:
            pygame.time.wait(500)
            bot_move()
            turn = human

        check_winner()

    pygame.quit()


if __name__ == '__main__':
    board = [[0, -1, 0, -1],
             [0, 0, 0, 0],
             [0, 0, 0, 0],
             [1, 0, 1, 0]]
    main()

