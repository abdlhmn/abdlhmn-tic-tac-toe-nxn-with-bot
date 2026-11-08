
import pygame, copy, random
from constraints import *
from sys import exit


class Buttons:
    def __init__(self, coords, surf, text=None):
        self.text_font = pygame.font.Font('font.ttf', 20)
        if text:
            self.blahblah = text
        self.surf = surf
        self.coords = coords
        self.rect = self.surf.get_rect(center=self.coords)
        self.clicked = False

    def textalise(self, text):
        self.blahblah = text

    def draw(self, screen):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            colour = (120, 220, 70)
            if pygame.mouse.get_pressed()[0]:
                colour = (90, 25, 200)
                self.clicked = True
        else:
            colour = 'black'
        self.text = self.text_font.render(self.blahblah, True, colour)
        self.text_rect = self.text.get_rect(center=self.coords)
        screen.blit(self.surf, self.rect)
        screen.blit(self.text, self.text_rect)


class Players:
    def __init__(self, turn, position, n=5):
        self.turn = turn
        self.position = position
        self.n = n
        self.coords = (self.position[0]*WIDTH//self.n+10, self.position[1]*HEIGHT//self.n+10)
        self.rect = pygame.Rect(self.coords[0], self.coords[1], WIDTH//self.n-20, HEIGHT//self.n-20)

    def draw(self, screen):
        font = pygame.font.Font(None, 144//self.n * 3)
        output = ('O', 'X')[self.turn]
        if output == 'O':
            color = CIRC_COLOR
        else: 
            color = CROSS_COLOR
        text = font.render(output, True, color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def winner_check(self, lst):
        nice_var = self.position[1]
        vertical_line = [self == lst[i][self.position[0]] for i in range(self.n)]
        diagonal = []
        annoying_diagonal = []
        for i in range(self.n):
            diagonal.append(self == lst[i][i])
            annoying_diagonal.append(self == lst[self.n-1-i][i])
        
        if all(map(lambda other:self==other, lst[nice_var])):
            y = WIDTH/(2*self.n)+nice_var*(HEIGHT/self.n)
            start_coords, end_coords = (0, y), (WIDTH, y)
        elif all(vertical_line):
            x = WIDTH/(2*self.n) + WIDTH/self.n*self.position[0]
            start_coords, end_coords = (x, 0), (x, HEIGHT)
        elif all(diagonal):
            start_coords, end_coords = (0,0), (WIDTH, HEIGHT)
        elif all(annoying_diagonal):
            start_coords, end_coords = (0, HEIGHT), (WIDTH, 0)
        else:
            start_coords, end_coords = None, None
        
        return start_coords, end_coords

    def __eq__(self, other):
        if isinstance(other, str):
            return False
        if self.turn == other.turn:
            return True
        return False

    def __str__(self):
        return ('O', 'X')[self.turn]


class HumanPlayers(Players):
    def __init__(self, turn, coords, n=5):
        Players.__init__(self, turn, coords, n)

    def update_coords(self, coords):
        self.coords = coords


class BotPlayers(Players):
    def __init__(self, lst, turn, n=5, difficulty='hard'):
        self.difficulty = difficulty
        self.n = n
        self.bot_turn = turn
        coords = self.generate_move(lst=lst, turn=turn)
        Players.__init__(self, turn, coords, n)

    def update_coords(self, coords):
        self.coords = coords

    def generate_move(self, lst=None, turn=1):
        if self.difficulty == 'easy':
            moves = [(col, row) for row in range(self.n) for col in range(self.n) if not lst[row][col]]
            return random.choice(moves)
        depth = 1 if self.difficulty == 'medium' else 4
        best_score = float('-inf')
        best_move = None
        beta = float('inf')
        alpha = float('-inf')
        for row in range(self.n):
            for col in range(self.n):
                if not lst[row][col]:
                    lst[row][col] = Players(turn, (col, row), n=self.n)
                    minimax_score = self.minimax(turn, lst, False, depth=depth, alpha=alpha, beta=beta)
                    alpha = max(alpha, minimax_score)
                    
                    lst[row][col] = ''
                    if minimax_score > best_score:
                        best_score = minimax_score
                        best_move = (col, row)
        return best_move

    def minimax(self, turn, board, is_maximizing, depth=4, alpha=float('-inf'), beta=float('inf')):
        winner = self.winner_check_bot(board)
        if winner==self.bot_turn:
            return 10**5
        if winner==1-self.bot_turn:
            return -10**5
        b_flat = []
        for row in board:
            b_flat.extend(row)
        if all(b_flat):
            return 0
        if depth == 0:
            return self.evaluate(board) if self.bot_turn == 1 else -self.evaluate(board)

        if is_maximizing: 
            score = float('-inf')
            turn = self.bot_turn
        else:
            score = float('inf')
            turn = 1-self.bot_turn
        for row in range(self.n):
            for col in range(self.n):
                if not board[row][col]:
                    board[row][col] = Players(turn, (col, row), n=self.n)
                    minimax_score = self.minimax(turn, board, not is_maximizing, depth=depth-1, alpha=alpha, beta=beta)
                    board[row][col] = ''
                    if minimax_score > score and is_maximizing or minimax_score < score and not is_maximizing:
                        score = minimax_score
                    if is_maximizing:
                        alpha = max(alpha, score)
                    else:
                        beta = min(beta, score)
                    if alpha >= beta:
                        return score
        return score

    def evaluate(self, board):
        total_score = 0
        lines = [] 
        for i in range(self.n):
            vertical_lines = [] 
            lines.append(board[i])
            for j in range(self.n):
                vertical_lines.append(board[j][i]) # vertical lines
            lines.append(vertical_lines)
        lines.append([board[i][i] for i in range(self.n)]) # diagonal lines
        lines.append([board[self.n-1-i][i] for i in range(self.n)]) # diagonal lines
        for line in lines:
            x_count = 0
            o_count = 0
            for cell in line:
                if cell:
                    if cell.turn == 1:
                        x_count += 1
                    else:
                        o_count += 1
            if x_count > 0 and o_count > 0:
                continue
            if x_count > 0: 
                total_score += 10 ** x_count
            elif o_count > 0:
                total_score -= 10 ** o_count
        return total_score



    def winner_check_bot(self, board):
        winning_lines = [] 
        diagonal1 = [] 
        diagonal2 = []
        for i in range(self.n):
            vertical_lines = [] 
            winning_lines.append(board[i])
            diagonal1.append(board[i][i]) # diagonal lines
            diagonal2.append(board[self.n-1-i][i]) # diagonal lines
            for j in range(self.n):
                vertical_lines.append(board[j][i]) # vertical lines
            winning_lines.append(vertical_lines)
        winning_lines.append(diagonal1)
        winning_lines.append(diagonal2)

        for line in winning_lines:
            if line[0] and all(line[0] == cell for cell in line):
                return line[0].turn
        return None
                




        
class Main:
    def __init__(self, n=5):
        pygame.init()
        self.n = n
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Gamerisms')
        self.clock = pygame.time.Clock()
        self.game_over = 'menu'
        self.counter = 1
        self.human_turn = 0
        self.bot_turn = 1
        self.difficulty = 'hard'
        self.bg = pygame.image.load('bg.png').convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        self.bg_rect = self.bg.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.button_surf = pygame.image.load('optionsRect.png').convert_alpha()
        self.button_surf = pygame.transform.scale(self.button_surf, (700, 100))
        self.button_rect = self.button_surf.get_rect(center=(WIDTH//2, HEIGHT//2))

        self.text_font = pygame.font.Font('font.ttf', 20)
        self.winner_player = Buttons((WIDTH//2, HEIGHT//3), self.button_surf)
        self.text_player = Buttons((WIDTH//2, HEIGHT//3+150), self.button_surf, 'play with a friend')
        self.bot_player = Buttons((WIDTH//2, HEIGHT//3+150*2), self.button_surf, 'play with a bot')
        self.easy_button = Buttons((WIDTH//2, HEIGHT//3), self.button_surf, 'easy')
        self.medium_button = Buttons((WIDTH//2, HEIGHT//3+150), self.button_surf, 'medium')
        self.hard_button = Buttons((WIDTH//2, HEIGHT//3+150*2), self.button_surf, 'hard')
        self.x_button = Buttons((WIDTH//2, HEIGHT//2-75), self.button_surf, 'play as X')
        self.o_button = Buttons((WIDTH//2, HEIGHT//2+75), self.button_surf, 'play as O')
        self.board_lst = [['' for _ in range(self.n)] for _ in range(self.n)]
        self.start_coords, self.end_coords = None, None
        self.turn = self.counter % 2

    def initialise(self, n=5):
        self.n = n
        self.counter = 1
        self.start_coords, self.end_coords = None, None
        self.board_lst = [['' for _ in range(self.n)] for _ in range(self.n)]
        # self.board_lst = [['', '', ''],
        #                 ['', '', ''],
        #                 ['', '', '']]
        self.turn = self.counter % 2
    
    def process_events(self):
        mouse = pygame.mouse.get_pos()
        grid_coords = (mouse[0]//SQSIZE, mouse[1]//SQSIZE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over in ('human', 'bot'):
                    if self.game_over == 'bot' and self.turn != self.human_turn:
                        continue
                    if 0 <= grid_coords[0] < self.n and 0 <= grid_coords[1] < self.n:
                        if not self.board_lst[grid_coords[1]][grid_coords[0]]:
                            self.make_move(grid_coords)
                if self.game_over is True or self.game_over == 'menu':
                    if self.text_player.rect.collidepoint(mouse):
                        self.initialise(self.n)
                        self.game_over = 'human'
                    elif self.bot_player.rect.collidepoint(mouse):
                        self.game_over = 'choose_difficulty'
                elif self.game_over == 'choose_difficulty':
                    if self.easy_button.rect.collidepoint(mouse):
                        self.difficulty = 'easy'
                        self.game_over = 'choose_symbol'
                    elif self.medium_button.rect.collidepoint(mouse):
                        self.difficulty = 'medium'
                        self.game_over = 'choose_symbol'
                    elif self.hard_button.rect.collidepoint(mouse):
                        self.difficulty = 'hard'
                        self.game_over = 'choose_symbol'
                elif self.game_over == 'choose_symbol':
                    if self.x_button.rect.collidepoint(mouse):
                        self.human_turn = 1
                        self.bot_turn = 0
                        self.initialise(self.n)
                        self.game_over = 'bot'
                    elif self.o_button.rect.collidepoint(mouse):
                        self.human_turn = 0
                        self.bot_turn = 1
                        self.initialise(self.n)
                        self.game_over = 'bot'
                        self.make_move()
    
    def make_move(self, coords=None):
        # print(self.counter, 'counter initial')
        if self.game_over == 'bot':
            if self.turn == self.human_turn and coords:
                hp = HumanPlayers(self.turn, coords, n=self.n)
                self.board_lst[coords[1]][coords[0]] = hp
                self.start_coords, self.end_coords = hp.winner_check(self.board_lst)
                self.counter += 1
                self.turn = self.counter % 2
                # print(self.counter, 'human')
            if self.turn == self.bot_turn and self.start_coords is None:
                if all(cell for row in self.board_lst for cell in row):
                    return
                # print('board check')
                bot = BotPlayers(self.board_lst, self.turn, n=self.n, difficulty=self.difficulty)
                self.board_lst[bot.position[1]][bot.position[0]] = bot
                # print(self.counter, 'bot')
                # self.op()
                self.start_coords, self.end_coords = bot.winner_check(self.board_lst)
                self.counter += 1
                self.turn = self.counter % 2
        if coords and self.game_over == 'human':
            hp = HumanPlayers(self.turn, coords, n=self.n)
            self.board_lst[coords[1]][coords[0]] = hp
            self.start_coords, self.end_coords = hp.winner_check(self.board_lst)
            # print('make_move check')
            # self.op()
            self.counter += 1
            self.turn = self.counter % 2



    def draw(self):
        # self.n = 4
        if self.game_over == 'menu':
            self.screen.blit(self.bg, self.bg_rect)
            self.winner_player.textalise('TIC TAC TOE')
            self.winner_player.draw(self.screen)
            self.text_player.draw(self.screen)
            self.bot_player.draw(self.screen)
            return 'menu'
        if self.game_over == 'choose_difficulty':
            self.screen.blit(self.bg, self.bg_rect)
            self.easy_button.draw(self.screen)
            self.medium_button.draw(self.screen)
            self.hard_button.draw(self.screen)
            return 'choose_difficulty'
        if self.game_over == 'choose_symbol':
            self.screen.blit(self.bg, self.bg_rect)
            self.x_button.draw(self.screen)
            self.o_button.draw(self.screen)
            return 'choose_symbol'
        if self.game_over is True:
            self.winner_player.textalise(self.text)
            self.screen.blit(self.bg, self.bg_rect)
            self.winner_player.draw(self.screen)
            self.text_player.draw(self.screen)
            self.bot_player.draw(self.screen)
            if self.text_player.clicked == True:
                self.text_player.clicked = False
                return 'human'
            if self.bot_player.clicked == True:
                self.bot_player.clicked = False
                return 'choose_difficulty'
            else:
                return True
        self.screen.fill(BG_COLOR)

        for i in range(1, self.n):
            pygame.draw.line(self.screen, LINE_COLOR, (0, HEIGHT//self.n*i), (WIDTH, HEIGHT//self.n*i), width=8)
            pygame.draw.line(self.screen, LINE_COLOR, (WIDTH//self.n*i, 0), (WIDTH//self.n*i, HEIGHT), width=8)

            
        counter = 0
        for row in self.board_lst:
            for obj in row:
                if obj:
                    obj.draw(self.screen)
                    counter += 1
        if self.start_coords and self.end_coords:
            pygame.draw.line(self.screen, LINE_COLOR, self.start_coords, self.end_coords, width=10)
            self.text =  ('O', 'X')[1-self.turn] + ' won !! :)'
            return True
        elif all(cell for row in self.board_lst for cell in row):
            self.text = 'DRAW :('
            return True
        return self.game_over
    
    def run(self):
        # n=5
        self.initialise(self.n)
        # WIDTH, HEIGHT = WIDTH * n/3, HEIGHT * n/3
        while True:
            if self.counter != 1 and self.game_over is True:
                pygame.time.wait(1000)
                self.initialise(self.n)

            self.process_events()
            self.game_over = self.draw()
            self.clock.tick(60)
            pygame.display.update()
    
    def op(self):
        for lst in self.board_lst:
            print(*lst)
        print()
        
n = 5
SQSIZE = WIDTH // n
main = Main(n)
main.run()
