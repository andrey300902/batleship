import pygame
import os
import sys

pygame.init()
CELL_SIZE = 40
size = width, height = 24*CELL_SIZE, 30+14*CELL_SIZE
screen = pygame.display.set_mode(size)

def load_image(name, colorkey = None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    return image

class GUI:
    def __init__(self):
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self, surface):
        for element in self.elements:
            render = getattr(element, "render", None)
            if callable(render):
                element.render(surface)

    def update(self):
        for element in self.elements:
            update = getattr(element, "update", None)
            if callable(update):
                element.update()

    def get_event(self, event):
        for element in self.elements:
            get_event = getattr(element, "get_event", None)
            if callable(get_event):
                element.get_event(event)

class Label:
    def __init__(self, rect, text, text_color=(255, 255, 255), text_background=(0, 0, 0)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bgcolor = pygame.Color(*text_background)
        self.font_color = pygame.Color(*text_color)
        # Рассчитываем размер шрифта в зависимости от высоты
        self.font = pygame.font.Font(None, self.rect.height - 4)
        self.rendered_text = None
        self.rendered_rect = None


    def render(self, surface):
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 2, centery=self.rect.centery)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

class Button(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.bgcolor = pygame.Color("blue")
        # при создании кнопка не нажата
        self.pressed = False

    def render(self, surface):
        global radius
        surface.fill(self.bgcolor, self.rect)
        self.rendered_text = self.font.render(self.text, 1, self.font_color)
        if not self.pressed:
            color1 = pygame.Color("white")
            color2 = pygame.Color("black")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 5, centery=self.rect.centery)
        else:
            color1 = pygame.Color("black")
            color2 = pygame.Color("white")
            self.rendered_rect = self.rendered_text.get_rect(x=self.rect.x + 7, centery=self.rect.centery + 2)

        # рисуем границу
        pygame.draw.rect(surface, color1, self.rect, 2)
        pygame.draw.line(surface, color2, (self.rect.right - 1, self.rect.top), (self.rect.right - 1, self.rect.bottom), 2)
        pygame.draw.line(surface, color2, (self.rect.left, self.rect.bottom - 1),
                         (self.rect.right, self.rect.bottom - 1), 2)
        # выводим текст
        surface.blit(self.rendered_text, self.rendered_rect)

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):
            return True

pygame.mixer.music.load('battleship.mp3')

class Board:
    def __init__(self, file=None):
        self.board = [['0' for _ in range(10)] for _ in range(10)]
        if file != None:
            file = open(file, 'r').readlines()
            for i in range(10):
                s = file[i].strip().split(', ')
                for j in range(10):
                    self.board[i][j] = s[j]
        self.cell = CELL_SIZE
        self.top = 30

    def render(self, mode):
        for i in range(width//CELL_SIZE):
            for j in range(height//CELL_SIZE):
                pygame.draw.rect(screen, (0, 0, 255), (self.cell * i, self.top + self.cell * j, self.cell, self.cell), 1)
        if mode == 1:
            self.left = CELL_SIZE
        elif mode == 2:
            self.left = 13*CELL_SIZE
        if mode != 0:
            pygame.draw.rect(screen, (0, 0, 255), (self.left, 110, CELL_SIZE*10, CELL_SIZE*10), 4)
            for i in range(len(self.board)):
                for j in range(len(self.board[i])):
                    if self.board[i][j] == 'su':
                        pygame.draw.line(screen, (255, 0, 0), (self.left + i * self.cell, self.top + 80 + (j + 1) * self.cell), (self.left + (i + 1) * self.cell, self.top + 80 + j* self.cell), 5)
                        pygame.draw.line(screen, (255, 0, 0), (self.left + i*self.cell, self.top + 80 + j*self.cell), (self.left + (i+1)*self.cell, self.top + 80 + (j+1)*self.cell), 5)
                    if self.board[i][j] == 'm':
                        pygame.draw.rect(screen, (0, 0, 255), (self.left + i*self.cell, self.top + 80 + j*self.cell, self.cell, self.cell))

class TextBox(Label):
    def __init__(self, rect, text):
        super().__init__(rect, text)
        self.active = False
        self.blink = True
        self.blink_timer = 0

    def get_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                self.text += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

    def update(self):
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def render(self, surface):
        super(TextBox, self).render(surface)
        if self.blink and self.active:
            pygame.draw.line(surface, pygame.Color("black"),
                             (self.rendered_rect.right + 2, self.rendered_rect.top + 2),
                             (self.rendered_rect.right + 2, self.rendered_rect.bottom - 2))

def imported():
    running = True
    label = Label([200, 100, 400, 50], 'Укажите адрес')
    text = TextBox([200, 200, 400, 50], '')
    string = None
    while running:
        screen.fill((0, 0, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            string = text.get_event(event)
        if string:
            return string
        label.render(screen)
        text.render(screen)
        pygame.display.flip()

def startBoard():
    pygame.mixer.music.play()
    button = Button([600, 500, 350, 50], 'Импортировать поле')
    image = load_image('start.jpg')
    image = pygame.transform.scale(image, [width, height])
    running = True
    board1, board2 = Board(), Board()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.get_event(event):
                    adress1 = imported()
                    adress2 = imported()
                    board1, board2 = Board(adress1), Board(adress2)
                running = False
                return board1, board2

        screen.blit(image, [0, 0])
        button.render(screen)
        pygame.display.flip()

board1, board2 = startBoard()
pygame.mixer.music.stop()

class Ships(pygame.sprite.Sprite):
    image = load_image('ships-4.jpg')
    image = pygame.transform.scale(image, (4*CELL_SIZE, CELL_SIZE))

    def __init__(self, group, mode, x, y):
        super().__init__(group)

        Ships.image = load_image('ships-'+str(mode)+'.jpg')
        self.image = pygame.transform.scale(Ships.image, (mode*CELL_SIZE+1, 41))
        self.x, self.y = x*CELL_SIZE, 30 + y*CELL_SIZE
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.mask = pygame.mask.from_surface(self.image)

    def get_event(self, pos):
        if self.rect.collidepoint(pos):
            return True
        else:
            return False

    def orient(self):
        self.image = pygame.transform.rotate(self.image, 90)
        self.rect.w, self.rect.h = self.rect.h, self.rect.w

def make_place():
    running = True
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, width, height))
    board = board1

    button = Button([width-120, height-CELL_SIZE, 120, CELL_SIZE], 'Далее')
    all_ships = pygame.sprite.Group()
    sprite = Ships(all_ships, 4, 14, 2)
    for i in range(2):
        sprite = Ships(all_ships, 3, i*4 + 12, 4)
    for i in range(3):
        sprite = Ships(all_ships, 2, i*3 + 12, 6)
    for i in range(4):
        sprite = Ships(all_ships, 1, i*2 + 12, 8)
    is_move = False
    is_draw = False
    while running:
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, width, height))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


            if event.type == pygame.KEYDOWN and is_move:
                if event.key == 13:
                    for ships in all_ships:
                        if ships != is_move and pygame.sprite.collide_mask(is_move, ships):
                            is_draw = label = Label([100, 0, 300, 30], 'Корабли не могут стоять рядом', (255, 0, 0), (0, 0, 255))
                    if is_draw == False:
                        for i in range((is_move.rect.x - CELL_SIZE) // CELL_SIZE, (is_move.rect.x - CELL_SIZE + is_move.rect.w) // CELL_SIZE):
                            board.board[i][(is_move.rect.y - 110) // CELL_SIZE] = 's'
                        for i in range((is_move.rect.y - 110) // CELL_SIZE, (is_move.rect.y - 110 + is_move.rect.h) // CELL_SIZE):
                            board.board[(is_move.rect.x - CELL_SIZE) // CELL_SIZE][i] = 's'
                        is_move = False
                if event.key == pygame.K_RIGHT:
                    if is_move.rect.x + is_move.rect.w < 11*CELL_SIZE:
                        is_move.rect.x += CELL_SIZE
                    is_draw = False
                if event.key == pygame.K_DOWN:
                    if is_move.rect.y + is_move.rect.h < 30 + 12*CELL_SIZE:
                        is_move.rect.y += CELL_SIZE
                    is_draw = False
                if event.key == pygame.K_LEFT:
                    if is_move.rect.x > CELL_SIZE:
                        is_move.rect.x -= CELL_SIZE
                    is_draw = False
                if event.key == pygame.K_UP:
                    if is_move.rect.y > 30 + 2*CELL_SIZE:
                        is_move.rect.y -= CELL_SIZE
                    is_draw = False
                if event.key == pygame.K_SPACE:
                    i.orient()
                    is_draw = False


            if event.type == pygame.MOUSEBUTTONDOWN:
                if button.get_event(event) == True:
                    ships = 0
                    for i in board.board:
                        ships += i.count('s')
                    if ships < 20:
                        is_draw = Label([100, 570, 300, 30], 'Не все корабли расставлены', (255, 0, 0), (0, 0, 255))
                    else:
                        is_draw = False
                        if board == board2:
                            return board1, board
                        board = board2
                        for i in all_ships:
                            i.rect.x, i.rect.y = i.x, i.y
                            if i.rect.h > 41:
                                i.orient()
                else:
                    for i in all_ships:
                        if i.get_event(event.pos):
                            i.rect.x, i.rect.y = CELL_SIZE, 30+2*CELL_SIZE
                            is_move = i
                            break

        board.render(1)
        all_ships.draw(screen)
        button.render(screen)
        if is_draw:
            is_draw.render(screen)
        pygame.display.flip()

ships = 0
for i in board1.board:
    ships += i.count('s')
if ships == 0:
    board1, board2 = make_place()

def check(board):
    flag = True
    for i in board.board:
        if 's' in i:
            flag = False
    return flag

def check_dead(board, pos, dont=[]):
    x, y = pos
    flag = True
    if x > 0:
        if (-1, 0) not in dont:
            if board[x-1][y] == 's':
                return False
            elif board[x-1][y] == 'su':
                flag = check_dead(board, [x-1, y], dont + [(1, 0)])
        if (-1, 1) not in dont:
            if y < 9:
                if board[x-1][y+1] == 's':
                    return False
                elif board[x-1][y+1] == 'su':
                    flag = check_dead(board, [x-1, y+1], dont + [(1, -1)])
        if (-1, -1) not in dont:
            if y > 0:
                if board[x-1][y-1] == 's':
                    return False
                elif board[x-1][y-1] == 'su':
                    flag = check_dead(board, [x-1, y-1], dont + [(1, 1)])
    if x < 9:
        if (1, 0) not in dont:
            if board[x+1][y] == 's':
                return False
            elif board[x+1][y] == 'su':
                flag = check_dead(board, [x+1, y], dont + [(-1, 0)])
        if (1, 1) not in dont:
            if y < 9:
                if board[x+1][y+1] == 's':
                    return False
                elif board[x+1][y+1] == 'su':
                    flag = check_dead(board, [x+1, y+1], dont + [(-1, -1)])
        if (1, -1) not in dont:
            if y > 0:
                if board[x+1][y-1] == 's':
                    return False
                elif board[x+1][y-1] == 'su':
                    flag = check_dead(board, [x+1, y-1], dont + [(-1, 1)])
    if y > 0:
        if (0, -1) not in dont:
            if board[x][y - 1] == 's':
                return False
            elif board[x][y - 1] == 'su':
                flag = check_dead(board, [x, y - 1], dont + [(0, 1)])
    if y < 9:
        if (0, 1) not in dont:
            if board[x][y + 1] == 's':
                return False
            elif board[x][y + 1] == 'su':
                flag = check_dead(board, [x, y + 1], dont + [(0, -1)])
    return flag

def draw(board, pos, dont=[]):
    x, y = pos
    if x > 0:
        if (-1, 0) not in dont:
            if board[x - 1][y] == '0':
                board[x - 1][y] = 'm'
            elif board[x - 1][y] == 'su':
                draw(board, [x - 1, y], dont + [(1, 0)])
        if (-1, 1) not in dont:
            if y < 9:
                if board[x - 1][y + 1] == '0':
                    board[x - 1][y + 1] = 'm'
                elif board[x - 1][y + 1] == 'su':
                    draw(board, [x - 1, y + 1], dont + [(1, -1)])
        if (-1, -1) not in dont:
            if y > 0:
                if board[x - 1][y - 1] == '0':
                    board[x - 1][y - 1] = 'm'
                elif board[x - 1][y - 1] == 'su':
                    draw(board, [x - 1, y - 1], dont + [(1, 1)])
    if x < 9:
        if (1, 0) not in dont:
            if board[x+1][y] == '0':
                board[x + 1][y] = 'm'
            elif board[x+1][y] == 'su':
                draw(board, [x+1, y], dont + [(-1, 0)])
        if (1, 1) not in dont:
            if y < 9:
                if board[x+1][y+1] == '0':
                    board[x + 1][y + 1] = 'm'
                elif board[x+1][y+1] == 'su':
                    draw(board, [x+1, y+1], dont + [(-1, -1)])
        if (1, -1) not in dont:
            if y > 0:
                if board[x+1][y-1] == '0':
                    board[x + 1][y - 1] = 'm'
                elif board[x+1][y-1] == 'su':
                    draw(board, [x+1, y-1], dont + [(-1, 1)])
    if y > 0:
        if (0, -1) not in dont:
            if board[x][y - 1] == '0':
                board[x][y - 1] = 'm'
            elif board[x][y - 1] == 'su':
                draw(board, [x, y - 1], dont + [(0, 1)])
    if y < 9:
        if (0, 1) not in dont:
            if board[x][y + 1] == '0':
                board[x][y + 1] = 'm'
            elif board[x][y + 1] == 'su':
                draw(board, [x, y + 1], dont + [(0, -1)])

def play(board1, board2):
    screen.fill((255, 255, 255))
    running = True
    number_player = 1
    PROPUSK = 31
    label = False
    pygame.time.set_timer(PROPUSK, 30000)
    DELETE = False
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == PROPUSK:
                print(10)
                label = Label([100, 500, 150, 30], 'Вы не успели')
                DELETE = 29
                pygame.time.set_timer(DELETE, 5000)
                if number_player == 1:
                    number_player = 2
                else:
                    number_player = 1
            if DELETE:
                if event.type == DELETE:
                    label = False
                    DELETE = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if number_player == 1:
                    pos = [event.pos[0] - 13*CELL_SIZE, event.pos[1] - (30+2*CELL_SIZE)]
                    if pos[0] > 0 and pos[1] > 0:
                        pos[0], pos[1] = pos[0]//CELL_SIZE, pos[1]//CELL_SIZE
                        if pos[0] < 10 and pos[1] < 10:
                            if board2.board[pos[0]][pos[1]] == '0':
                                board2.board[pos[0]][pos[1]] = 'm'
                                pygame.mixer.music.load('water.wav')
                                pygame.mixer.music.play()
                                number_player = 2
                            elif board2.board[pos[0]][pos[1]] == 's':
                                pygame.mixer.music.load('popadanie.wav')
                                pygame.mixer.music.play()
                                board2.board[pos[0]][pos[1]] = 'su'
                                if check_dead(board2.board, [pos[0], pos[1]]):
                                    pygame.mixer.music.load('dead.wav')
                                    pygame.mixer.music.play()
                                    draw(board2.board, [pos[0], pos[1]])

                elif number_player == 2:
                    pos = [event.pos[0] - CELL_SIZE, event.pos[1] - (30+2*CELL_SIZE)]
                    if pos[0] > 0 and pos[1] > 0:
                        pos[0], pos[1] = pos[0]//CELL_SIZE, pos[1]//CELL_SIZE
                        if pos[0] < 10 and pos[1] < 10:
                            if board1.board[pos[0]][pos[1]] == '0':
                                board1.board[pos[0]][pos[1]] = 'm'
                                pygame.mixer.music.load('water.wav')
                                pygame.mixer.music.play()
                                number_player = 1
                            elif board1.board[pos[0]][pos[1]] == 's':
                                pygame.mixer.music.load('popadanie.wav')
                                pygame.mixer.music.play()
                                board1.board[pos[0]][pos[1]] = 'su'
                                if check_dead(board1.board, [pos[0], pos[1]]):
                                    pygame.mixer.music.load('dead.wav')
                                    pygame.mixer.music.play()
                                    draw(board1.board, [pos[0], pos[1]])

        if number_player == 1:
            pygame.draw.polygon(screen, (255, 0, 0), [(13*CELL_SIZE, 30+7*CELL_SIZE), (12*CELL_SIZE, 30+8*CELL_SIZE), (12*CELL_SIZE, 30+6*CELL_SIZE)])
        else:
            pygame.draw.polygon(screen, (255, 0, 0), [(11*CELL_SIZE, 30+7*CELL_SIZE), (12*CELL_SIZE, 30+8*CELL_SIZE), (12*CELL_SIZE, 30+6*CELL_SIZE)])

        board1.render(1)
        board2.render(2)
        pygame.draw.line(screen, (255, 0, 0), (11*CELL_SIZE, 30+7*CELL_SIZE), (13*CELL_SIZE, 30+7*CELL_SIZE), 5)
        if label:
            label.render(screen)
        pygame.display.flip()
        if check(board1):
            return 2
        elif check(board2):
            return 1

winner = play(board1, board2)
screen.fill((255, 255, 255))
board1.render(0)
if winner == 1:
    label = Label([100, 300, 700, 100], 'Первый выиграл', (255, 0, 0), (0, 0, 255))
elif winner == 2:
    label = Label([100, 300, 700, 100], 'Второй выиграл', (255, 0, 0), (0, 0, 255))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    label.render(screen)
    pygame.display.flip()
pygame.quit()