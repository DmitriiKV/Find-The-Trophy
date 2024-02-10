import os
import random
import sys
import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

size = width, height = 550, 550
screen = pygame.display.set_mode(size)
screen.fill((255, 255, 255))
screen_rect = (0, 0, width, height)
pygame.display.set_caption('Find The Trophy')
icon = pygame.image.load('data/icon.jpg')
pygame.display.set_icon(icon)

GRAVITY = 0
FPS = 10
player = None
player_group = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
animated_sprites = pygame.sprite.Group()
special_sprites = pygame.sprite.Group()


# Функция загрузки изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден!")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# Функция загрузки уровня
def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))


# Словать с тайлами для игры
tiles_image = {
    'wall': pygame.transform.scale(load_image('wall.png'), (50, 50)),
    'empty': pygame.transform.scale(load_image('floor.png'), (50, 50)),
    'trophy': pygame.transform.scale(load_image('trophy.jpg'), (50, 50)),
    'coin': pygame.transform.scale(load_image('coin.png'), (50, 50)),
}
player_image = pygame.transform.scale(load_image('knight_.png'), (50, 50))
tile_width = tile_height = 50


# Класс тайла
class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tiles_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс монетки
class Coin(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tiles_image[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# Класс для частиц, появляющихся при победе
class StarParticle(pygame.sprite.Sprite):
    fire = [pygame.transform.scale(load_image('star.jpg', -1), (20, 20))]
    for scale in range(5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(animated_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 0

    def update(self, *args, **kwargs):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Класс для частиц, появляющихся при сборе монетки
class CoinParticle(pygame.sprite.Sprite):
    fire = [pygame.transform.scale(load_image('coin_.png'), (20, 20))]
    for scale in range(5):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(animated_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self, *args, **kwargs):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


# Функция, отвечающая за создание частиц
def create_particles(position, flag):
    if flag == "star":
        particles_count = 50
        speed = range(-10, 10)
        for _ in range(particles_count):
            StarParticle(position, random.choice(speed), random.choice(speed))
    elif flag == "coin":
        particles_count = 10
        speed = range(-10, 10)
        for _ in range(particles_count):
            CoinParticle(position, random.choice(speed), random.choice(speed))


# Класс камеры
class Camera:
    def __init__(self, field_size):
        self.x = 0
        self.y = 0
        self.fied_size = field_size

    def apply(self, obj):
        obj.rect.x += self.x
        if obj.rect.x < -obj.rect.width:
            obj.rect.x += (self.fied_size[0] + 1) * obj.rect.width
        if obj.rect.x >= (self.fied_size[0]) * obj.rect.width:
            obj.rect.x += -obj.rect.width * (1 + self.fied_size[0])
        obj.rect.y += self.y
        if obj.rect.y < -obj.rect.height:
            obj.rect.y += (self.fied_size[1] + 1) * obj.rect.height
        if obj.rect.y >= (self.fied_size[1]) * obj.rect.height:
            obj.rect.y += -obj.rect.height * (1 + self.fied_size[1])

    def update(self, target):
        self.x = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.y = -(target.rect.y + target.rect.h // 2 - height // 2)


# Класс анимированных спрайтов
class AnimateSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(animated_sprites)
        self.frame = []
        self.cut_sheet(sheet, columns, rows)
        self.current_frame = 0
        self.image = self.frame[self.current_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for i in range(rows):
            for j in range(columns):
                frame_location = (self.rect.w * j, self.rect.h * i)
                self.frame.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self, *args, **kwargs):
        self.current_frame = (self.current_frame + 1) % len(self.frame)
        self.image = self.frame[self.current_frame]


# Функция, вызываемая при закрытии окна или выхода из игры
def terminate():
    pygame.quit()
    sys.exit()


# Функция для создания всех элементов игрового поля
def generate_level(level):
    new_player, x, y, walls, floor, player_pos, trophy_pos, coins = None, None, None, [], [], [], [], {}
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
                floor.append((x, y))
            elif level[y][x] == '#':
                Tile('wall', x, y)
                walls.append((x, y))
            elif level[y][x] == '@':
                Tile('empty', x, y)
                floor.append((x, y))
                new_player = Player(x, y)
                player_pos = [x, y]
            elif level[y][x] == '!':
                Tile('trophy', x, y)
                trophy_pos = [x, y]
            elif level[y][x] == '0':
                Tile('empty', x, y)
                coin = Coin('coin', x, y)
                coins[(x, y)] = coin
    return new_player, x, y, walls, floor, player_pos, trophy_pos, coins


# Функция для отображения текста, возвращающая его координаты
def text_func(screen, text_list, text_coord):
    font = pygame.font.Font(None, 30)
    for line in text_list:
        string_renderer = font.render(line, 1, pygame.Color('yellow'), 1)
        intro_rect = string_renderer.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_renderer, intro_rect)
        return intro_rect


# Функция с интерактивным текстом для отображения начального экрана игры
def start_screen():
    description = ["Описание"]
    play = ["Играть"]
    quit = ["Выход"]
    fon = pygame.transform.scale(load_image('BG.png'), (width, height))
    screen.blit(fon, (0, 0))
    description_rect = text_func(screen, description, 70)
    play_rect = text_func(screen, play, 90)
    quit_rect = text_func(screen, quit, 110)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(description_rect[0], description_rect[0] + description_rect[2]) \
                        and event.pos[1] in range(description_rect[1], description_rect[1] + 10):
                    print_rules()
                if event.pos[0] in range(play_rect[0], play_rect[0] + play_rect[2]) \
                        and event.pos[1] in range(play_rect[1], play_rect[1] + 10):
                    choose_level()
                if event.pos[0] in range(quit_rect[0], quit_rect[0] + quit_rect[2]) \
                        and event.pos[1] in range(quit_rect[1], quit_rect[1] + 10):
                    terminate()
        pygame.display.flip()
        clock.tick(FPS)


# Функция вывода на экран описания игры и управления
def print_rules():
    intro_text = ["Многие думают, что рыцари остались где-то в прошлом.",
                  "Но возможно, где-то в подземельях древнейших замков они ещё остались",
                  "Древний лабиринт скрывает множество опасностей и тайн, и только самый",
                  "отважный и бесстрашный рыцарь может смело пройти через его запутанные ходы",
                  "В поисках древнего кубка, который обладает волшебной силой,",
                  "игрок отправится в глубины лабиринта, у него очень мало времени,",
                  "и каждый его шаг может быть последним", "",
                  "Цель игры: найти кубок в лабиринте и собрать все монеты за заданное время",
                  "Управление: перемещайтесь с помощью кнопок WASD или стрелок",
                  "и следуйте подсказкам"]
    back = ["Назад"]
    fon = pygame.transform.scale(load_image('BG.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 20)
    text_coord = 50

    for line in intro_text:
        string_renderer = font.render(line, 1, pygame.Color('yellow'), 1)
        intro_rect = string_renderer.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_renderer, intro_rect)

    back_rect = text_func(screen, back, 500)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(back_rect[0], back_rect[0] + back_rect[2]) \
                        and event.pos[1] in range(back_rect[1], back_rect[1] + 10):
                    start_screen()
            elif event.type == pygame.KEYDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)


# Функция выбора уровня
def choose_level():
    heading = ["Выберите уровень:"]
    sandbox = ["Тренировочный уровень"]
    level1 = ["Уровень 1"]
    level2 = ["Уровень 2"]
    back = ["Назад"]
    fon = pygame.transform.scale(load_image('BG.png'), (width, height))
    screen.blit(fon, (0, 0))

    text_coord = 50
    font = pygame.font.Font(None, 30)
    for line in heading:
        string_renderer = font.render(line, 1, pygame.Color('yellow'), 1)
        intro_rect = string_renderer.get_rect()
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_renderer, intro_rect)

    sandbox_rect = text_func(screen, sandbox, 70)
    level1_rect = text_func(screen, level1, 90)
    level2_rect = text_func(screen, level2, 110)
    back_rect = text_func(screen, back, 500)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(sandbox_rect[0], sandbox_rect[0] + sandbox_rect[2]) \
                        and event.pos[1] in range(sandbox_rect[1], sandbox_rect[1] + 10):
                    start_game('sandbox', 100, 15)
                if event.pos[0] in range(level1_rect[0], level1_rect[0] + level1_rect[2]) \
                        and event.pos[1] in range(level1_rect[1], level1_rect[1] + 10):
                    start_game('level1', 75, 15)
                if event.pos[0] in range(level2_rect[0], level2_rect[0] + level2_rect[2]) \
                        and event.pos[1] in range(level2_rect[1], level2_rect[1] + 10):
                    start_game('level2', 50, 10)
                if event.pos[0] in range(back_rect[0], back_rect[0] + back_rect[2]) \
                        and event.pos[1] in range(back_rect[1], back_rect[1] + 10):
                    start_screen()
        pygame.display.flip()
        clock.tick(FPS)


# Функция, отвечающая за игровой процесс
def start_game(levelname, seconds, total_coins):
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    timeline = seconds
    coins_count = 0
    time_counter = font.render(str(timeline), True, pygame.Color('yellow'), 1)
    cointer = font.render(f"{coins_count}/{total_coins}", True, pygame.Color('yellow'), 1)
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 1000)
    player, level_x, level_y, walls, floor, player_pos, trophy_pos, coins = generate_level(
        load_level(levelname + '.txt'))
    camera = Camera((level_x, level_y))
    running = True
    run = pygame.mixer.Sound("data/running.ogg")
    tip = pygame.mixer.Sound("data/coin.wav")
    victory = pygame.mixer.Sound("data/victory.mp3")
    back = ["Назад"]
    back_rect = text_func(screen, back, 500)
    win = False
    lose = False
    total_moves = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == timer_event:
                timeline -= 1
                time_counter = font.render(str(timeline), True, pygame.Color('yellow'), 1)
                if timeline == 0:
                    back = ['Нажмите любую кнопку']
                    lose = True
                    pygame.time.set_timer(timer_event, 0)
            elif event.type == pygame.KEYDOWN:
                # Обработка перемещений игрока и проверка стен
                if not win and not lose:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        run.play()
                        total_moves += 1
                        AnimateSprite(pygame.transform.scale(load_image('walk_mirrored_.png'), (400, 50)), 8, 1, 250,
                                      250)
                        pposXL = player_pos[0]
                        if player_pos[0] - 1 < 0:
                            player_pos[0] = 23
                        else:
                            player_pos[0] -= 1
                        if (player_pos[0], player_pos[1]) not in walls:
                            player.rect.x -= 50
                        else:
                            player_pos[0] = pposXL
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        run.play()
                        total_moves += 1
                        AnimateSprite(pygame.transform.scale(load_image('walk_.png'), (400, 50)), 8, 1, 250, 250)
                        pposXR = player_pos[0]
                        if player_pos[0] + 1 > 23:
                            player_pos[0] = 0
                        else:
                            player_pos[0] += 1
                        if (player_pos[0], player_pos[1]) not in walls:
                            player.rect.x += 50
                        else:
                            player_pos[0] = pposXR
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        run.play()
                        total_moves += 1
                        AnimateSprite(pygame.transform.scale(load_image('idle_mirrored_.png'), (200, 50)), 4, 1, 250,
                                      250)
                        pposYL = player_pos[1]
                        if player_pos[1] - 1 < 0:
                            player_pos[1] = 23
                        else:
                            player_pos[1] -= 1
                        if (player_pos[0], player_pos[1]) not in walls:
                            player.rect.y -= 50
                        else:
                            player_pos[1] = pposYL
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        run.play()
                        total_moves += 1
                        AnimateSprite(pygame.transform.scale(load_image('idle_.png'), (200, 50)), 4, 1, 250, 250)
                        pposYR = player_pos[1]
                        if player_pos[1] + 1 > 23:
                            player_pos[1] = 0
                        else:
                            player_pos[1] += 1
                        if (player_pos[0], player_pos[1]) not in walls:
                            player.rect.y += 50
                        else:
                            player_pos[1] = pposYR
                    # Обработка сбора монет на пути
                    if (player_pos[0], player_pos[1]) in coins.keys():
                        tip.play()
                        coins_count += 1
                        coins[(player_pos[0], player_pos[1])].kill()
                        del coins[(player_pos[0], player_pos[1])]
                        create_particles((250, 250), "coin")
                        cointer = font.render(f"{coins_count}/{total_coins}", True, pygame.Color('yellow'), 1)
                    # Обработка достижения конца лабиринта
                    if player_pos == trophy_pos:
                        victory.play()
                        win = True
                        create_particles((275, 275), "star")
                        back = ['Нажмите любую кнопку']
                # Вызов победной функции
                elif win:
                    player.kill()
                    win = False
                    winning(f"{coins_count}/{total_coins}", seconds - timeline, total_moves)
                # Вызов проигрышной функции
                elif lose:
                    player.kill()
                    lose = False
                    game_over(f"{coins_count}/{total_coins}", seconds, total_moves)
            # Обработка нажатий на кнопку "Назад"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[0] in range(back_rect[0], back_rect[0] + back_rect[2]) \
                        and event.pos[1] in range(back_rect[1], back_rect[1] + 10):
                    choose_level()
        camera.update(player)
        # Отрисовка спрайтов, тайлов, текста и других элементов
        for sprite in all_sprites:
            camera.apply(sprite)
        screen.fill(pygame.Color(255, 255, 255))
        tiles_group.draw(screen)
        player_group.draw(screen)
        animated_sprites.update()
        animated_sprites.draw(screen)
        back_rect = text_func(screen, back, 500)
        screen.blit(cointer, (10, 10))
        screen.blit(time_counter, (500, 10))
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


# Функция, отображающая экран завершения игры и игровую статистику в случае победы
def winning(coins, time, total_moves):
    outro_text = ["ПОЗДРАВЛЯЮ С ПОБЕДОЙ,", "ЮНЫЙ РЫЦАРЬ!", f"Всего перемещений: {total_moves}",
                  f"Монет собрано: {coins}",
                  f"Время прохождения (сек): {time}", "Нажмите любую кнопку"]
    fon = pygame.transform.scale(load_image('BG.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in outro_text:
        string_renderer = font.render(line, 1, pygame.Color('yellow'), 1)
        intro_rect = string_renderer.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_renderer, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                start_screen()
        pygame.display.flip()
        clock.tick(FPS)


# Функция, отображающая экран завершения игры и игровую статистику в случае проигрыша
def game_over(coins, time, total_moves):
    lost = [["ВРЕМЯ ВЫШЛО", "свет в подземелье неожиданно погас", "и вы проиграли"],
            ["ВРЕМЯ ВЫШЛО", "в подземелье случился обвал", "и вы проиграли"],
            ["ВРЕМЯ ВЫШЛО", "свет в подземелье погас, в темноте", "на вас набросились огромные мыши и съели вас,",
             "и вы проиграли"]]
    losing_text = random.choice(lost)
    losing_text += [f"Всего перемещений: {total_moves}", f"Монет собрано: {coins}", f"Время прохождения (сек): {time}",
                    "Нажмите любую кнопку"]
    fon = pygame.transform.scale(load_image('BG.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in losing_text:
        string_renderer = font.render(line, 1, pygame.Color('yellow'), 1)
        intro_rect = string_renderer.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_renderer, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                start_screen()
        pygame.display.flip()
        clock.tick(FPS)


clock = pygame.time.Clock()
# Вызов начального экрана икры
start_screen()
