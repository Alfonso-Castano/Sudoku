#This is the main file that will make the game cohesive, and serves as the GUI space
import pygame, sys, copy
from sudoku_generator import SudokuGenerator

# Configuration 
WIDTH, HEIGHT = 540, 600
BOARD_SIZE = 9
BOX = 3
FPS = 60

ORANGE = (242, 140, 40)
BUTTON_TEXT = (255, 255, 255)
BOARD_BG = (207, 232, 255)

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)

DIFFICULTY_REMOVED = {"easy":30, "medium":40, "hard":50}

# Cell Class
class Cell:
    def __init__(self, value, row, col, width, height, screen):
        self.value = value
        self.original_value = value
        self.sketched_value = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.screen = screen
        self.selected = False

    def draw(self, font_value, font_sketch):
        x = self.col * self.width
        y = self.row * self.height

        pygame.draw.rect(self.screen, BOARD_BG, (x, y, self.width, self.height))

        if self.value != 0:
            text = font_value.render(str(self.value), True, BLACK)
            rect = text.get_rect(center=(x+self.width//2, y+self.height//2))
            self.screen.blit(text, rect)
        elif self.sketched_value != 0:
            text = font_sketch.render(str(self.sketched_value), True, (80,80,80))
            self.screen.blit(text, (x+4, y+2))

        if self.selected:
            pygame.draw.rect(self.screen, RED, (x,y,self.width,self.height), 3)
        else:
            pygame.draw.rect(self.screen, BLACK, (x,y,self.width,self.height), 1)


# Board Class
class Board:
    def __init__(self, width, height, screen, difficulty):
        self.width = width
        self.height = height
        self.screen = screen
        self.cell_width = width//9
        self.cell_height = height//9

        removed = DIFFICULTY_REMOVED[difficulty]
        g = SudokuGenerator(9, removed)
        g.fill_values()
        self.solution = copy.deepcopy(g.get_board())
        g.remove_cells()
        puzzle = copy.deepcopy(g.get_board())

        self.board = puzzle
        self.original_board = copy.deepcopy(puzzle)

        self.cells = [
            [Cell(self.board[r][c], r, c, self.cell_width, self.cell_height, screen)
             for c in range(9)] for r in range(9)
        ]

        self.selected_cell = None

    def draw(self, fval, fsketch):
        pygame.draw.rect(self.screen, BOARD_BG, (0,0,self.width,self.height))

        for row in self.cells:
            for cell in row:
                cell.draw(fval, fsketch)

        for i in range(10):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (0, i*self.cell_height), (self.width, i*self.cell_height), thick)
            pygame.draw.line(self.screen, BLACK, (i*self.cell_width, 0), (i*self.cell_width, self.height), thick)

    def select(self, r, c):
        if self.selected_cell:
            self.selected_cell.selected = False
        self.selected_cell = self.cells[r][c]
        self.selected_cell.selected = True

    def click(self, x, y):
        if x < 0 or x > self.width or y < 0 or y > self.height:
            return None
        return (y//self.cell_height, x//self.cell_width)

    def clear(self):
        if self.selected_cell and self.selected_cell.original_value == 0:
            self.selected_cell.value = 0
            self.selected_cell.sketched_value = 0
            self.update_board()

    def place_number(self, v):
        if self.selected_cell and self.selected_cell.original_value == 0:
            self.selected_cell.value = v
            self.selected_cell.sketched_value = 0
            self.update_board()
            return True
        return False

    def sketch(self, v):
        if self.selected_cell and self.selected_cell.original_value == 0:
            self.selected_cell.sketched_value = v

    def reset_to_original(self):
        for r in range(9):
            for c in range(9):
                val = self.original_board[r][c]
                self.cells[r][c].value = val
                self.cells[r][c].sketched_value = 0
        self.update_board()

    def update_board(self):
        for r in range(9):
            for c in range(9):
                self.board[r][c] = self.cells[r][c].value

    def is_full(self):
        return all(self.board[r][c] != 0 for r in range(9) for c in range(9))

    def check_board(self):
        self.update_board()
        for r in range(9):
            if len(set(self.board[r])) != 9:
                return False
        for c in range(9):
            col = [self.board[r][c] for r in range(9)]
            if len(set(col)) != 9:
                return False
        for br in range(0,9,3):
            for bc in range(0,9,3):
                vals = []
                for r in range(br,br+3):
                    for c in range(bc,bc+3):
                        vals.append(self.board[r][c])
                if len(set(vals)) != 9:
                    return False
        return True


# Buttons and Bakcground
def draw_button(screen, rect, text, font):
    pygame.draw.rect(screen, ORANGE, rect, border_radius=6)
    pygame.draw.rect(screen, BLACK, rect, 2, border_radius=6)
    label = font.render(text, True, BUTTON_TEXT)
    screen.blit(label, label.get_rect(center=(rect[0]+rect[2]//2, rect[1]+rect[3]//2)))


def draw_bg(screen, bg):
    screen.blit(bg, (0,0))


# Main Function
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")

    background = pygame.image.load("background.jpg")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    clock = pygame.time.Clock()

    f_big = pygame.font.Font(None, 60)
    f_medium = pygame.font.Font(None, 36)
    f_val = pygame.font.Font(None, 40)
    f_sketch = pygame.font.Font(None, 22)

    state = "start"
    board = None

    btnW, btnH = 120, 45
    spacing = 30
    easy_btn    = (WIDTH//2 - btnW - spacing - 50, HEIGHT//2, btnW, btnH)
    medium_btn  = (WIDTH//2 - btnW//2, HEIGHT//2, btnW, btnH)
    hard_btn    = (WIDTH//2 + spacing + 50, HEIGHT//2, btnW, btnH)

    reset_btn   = (40, 555, 100, 35)
    restart_btn = (220, 555, 120, 35)
    exit_btn    = (400, 555, 100, 35)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # START SCREEN
            if state == "start":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos
                    if easy_btn[0] <= mx <= easy_btn[0]+easy_btn[2] and easy_btn[1] <= my <= easy_btn[1]+easy_btn[3]:
                        board = Board(540,540,screen,"easy");  state="play"
                    if medium_btn[0] <= mx <= medium_btn[0]+medium_btn[2] and medium_btn[1] <= my <= medium_btn[1]+medium_btn[3]:
                        board = Board(540,540,screen,"medium");state="play"
                    if hard_btn[0] <= mx <= hard_btn[0]+hard_btn[2] and hard_btn[1] <= my <= hard_btn[1]+hard_btn[3]:
                        board = Board(540,540,screen,"hard");  state="play"

            # PLAY STATE
            elif state == "play":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos

                    pos = board.click(mx,my)
                    if pos:
                        board.select(*pos)
                    elif reset_btn[0]<=mx<=reset_btn[0]+reset_btn[2] and reset_btn[1]<=my<=reset_btn[1]+reset_btn[3]:
                        board.reset_to_original()
                    elif restart_btn[0]<=mx<=restart_btn[0]+restart_btn[2] and restart_btn[1]<=my<=restart_btn[1]+restart_btn[3]:
                        state="start"
                    elif exit_btn[0]<=mx<=exit_btn[0]+exit_btn[2] and exit_btn[1]<=my<=exit_btn[1]+exit_btn[3]:
                        running=False

                if event.type == pygame.KEYDOWN:
                    if board.selected_cell:
                        r=board.selected_cell.row
                        c=board.selected_cell.col
                    else:
                        r,c = 0,0

                    if event.key == pygame.K_UP:    board.select((r-1)%9,c)
                    if event.key == pygame.K_DOWN:  board.select((r+1)%9,c)
                    if event.key == pygame.K_LEFT:  board.select(r,(c-1)%9)
                    if event.key == pygame.K_RIGHT: board.select(r,(c+1)%9)

                    if pygame.K_1 <= event.key <= pygame.K_9:
                        board.sketch(event.key - pygame.K_0)

                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if board.selected_cell and board.selected_cell.sketched_value:
                            board.place_number(board.selected_cell.sketched_value)
                            if board.is_full():
                                state = "win" if board.check_board() else "lose"

                    if event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                        board.clear()

            # END SCREENS
            elif state in ("win","lose"):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx,my = event.pos

                    centered_exit = (
                        WIDTH//2 - exit_btn[2]//2,
                        HEIGHT//2,
                        exit_btn[2],
                        exit_btn[3]
                    )

                    if state == "win":
                        if centered_exit[0] <= mx <= centered_exit[0]+centered_exit[2] and \
                           centered_exit[1] <= my <= centered_exit[1]+centered_exit[3]:
                            running = False

                    if state == "lose":
                        centered_restart = (
                            WIDTH//2 - restart_btn[2]//2,
                            HEIGHT//2,
                            restart_btn[2],
                            restart_btn[3]
                        )

                        if centered_restart[0] <= mx <= centered_restart[0] + centered_restart[2] and \
                           centered_restart[1] <= my <= centered_restart[1] + centered_restart[3]:
                            state = "start"

        # DRAW GUI
        if state=="start":
            draw_bg(screen, background)
            txt = f_big.render("Welcome to Sudoku", True, BLACK)
            screen.blit(txt, txt.get_rect(center=(WIDTH//2, HEIGHT//3)))

            sub = f_medium.render("Select Game Mode:", True, BLACK)
            screen.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//3 + 50)))

            draw_button(screen, easy_btn, "EASY", f_medium)
            draw_button(screen, medium_btn, "MEDIUM", f_medium)
            draw_button(screen, hard_btn, "HARD", f_medium)

        elif state=="play":
            board.draw(f_val, f_sketch)
            draw_button(screen, reset_btn, "RESET", f_medium)
            draw_button(screen, restart_btn, "RESTART", f_medium)
            draw_button(screen, exit_btn, "EXIT", f_medium)

        elif state=="win":
            draw_bg(screen, background)
            msg = f_big.render("Game Won!", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//3)))

            centered_exit = (
                WIDTH//2 - exit_btn[2]//2,
                HEIGHT//2,
                exit_btn[2],
                exit_btn[3]
            )
            draw_button(screen, centered_exit, "EXIT", f_medium)

        elif state=="lose":
            draw_bg(screen, background)
            msg = f_big.render("Game Over :(", True, BLACK)
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//3)))

            centered_restart = (
                WIDTH//2 - restart_btn[2]//2,
                HEIGHT//2,
                restart_btn[2],
                restart_btn[3]
            )
            draw_button(screen, centered_restart, "RESTART", f_medium)

        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()