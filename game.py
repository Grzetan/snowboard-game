import pygame
import random
import sys
import os
import neat

pygame.init()

W = 600
H = 800
pygame.display.set_caption('Snowboard game')
WIN = pygame.display.set_mode((W,H))
CLOCK = pygame.time.Clock()

#fonts

WELCOME_FONT = pygame.font.SysFont('comcisans', 60)
BTN_FONT = pygame.font.SysFont('comicsans', 40)
FONT = pygame.font.SysFont('comicsans', 30)
COUNT_DOWN_FONT = pygame.font.SysFont('comicsans', 100)

after_pause = False

def game_loop():
    FPS = 30
    FPS_COUNTER = 0
    run = True
    bg = pygame.image.load('imgs/bg.png').convert()
    y = 0
    GAP = 150
    FLAG_SPREAD = W
    STARTING_SPEED = 10
    OBSTACLES_FREQUENCY = STARTING_SPEED * 50
    global after_pause

    #imgs

    FLAG_IMG = pygame.image.load('imgs/flag.png').convert_alpha()
    SNOWBOARD_IMG = pygame.image.load('imgs/snowboard2.png').convert_alpha()
    TRACE_IMG = pygame.image.load('imgs/trace.png').convert_alpha()
    HEART_IMG = pygame.image.load('imgs/heart.png').convert_alpha()
    BLACK_HEART_IMG = pygame.image.load('imgs/black_heart.png').convert_alpha()
    FLAG_WARNING_IMG = pygame.image.load('imgs/flag_warning.png').convert_alpha()

    #Sounds

    game_over_sound = pygame.mixer.Sound('sounds/game_over_sound.wav')
    count_down_sound = pygame.mixer.Sound('sounds/Count_down_sound.wav')

    class Snowboard:
        def __init__(self, x, y, r, speed):
            self.x = x
            self.y = y
            self.speed = speed
            self.max_speed_down = 50
            self.trace = []
            self.momentum = 0
            self.max_speed = 15
            self.score = 0
            self.width = SNOWBOARD_IMG.get_width()
            self.height = SNOWBOARD_IMG.get_height()
            self.lives = 2

        def draw(self):
            tilt_angle = self.momentum * -3
            self.trace.append([self.x, self.y, tilt_angle])
            tilted_img = pygame.transform.rotate(SNOWBOARD_IMG, tilt_angle)
            WIN.blit(tilted_img, (self.x, self.y))
            #pygame.draw.circle(WIN, (0,0,0), (self.x, self.y), self.r)

        def draw_trace(self):
            for pos in self.trace:
                if pos[1] > H + TRACE_IMG.get_height():
                    self.trace.pop(self.trace.index(pos))
            for pos in self.trace:
                pos[1] += snowboard.speed
                tilted_img = pygame.transform.rotate(TRACE_IMG, pos[2])
                WIN.blit(tilted_img, (pos[0], pos[1]))
                #pygame.draw.rect(WIN, (120,120,120), (pos[0], pos[1], SNOWBOARD_IMG.get_width(), SNOWBOARD_IMG.get_height()))

        def draw_lives(self):
            drawed_lives = 0
            for i in range(3):
                if drawed_lives <= self.lives:
                    heart = HEART_IMG
                else:
                    heart = BLACK_HEART_IMG
                WIN.blit(heart, (300 + i * 50, 20))
                drawed_lives += 1

        def update(self):
            if self.x + self.momentum >= 0 and self.x + self.width + self.momentum <= W:
                snowboard.x += snowboard.momentum
            elif self.x + self.momentum < 0:
                self.momentum = 0
                self.x = 0
            elif self.x + self.width + self.momentum > W:
                self.momentum = 0
                self.x = W - self.width

        def turn(self, dir):
            if dir < 0:
                if snowboard.momentum > snowboard.max_speed * -1:
                    snowboard.momentum -= 1
            elif dir > 0:
                if snowboard.momentum < snowboard.max_speed:
                    snowboard.momentum += 1
            else:
                if snowboard.momentum > 0:
                    snowboard.momentum -= 1
                elif snowboard.momentum < 0:
                    snowboard.momentum += 1
        
        def between_obstacles(self, obstacles):
            for flag in obstacles:
                if self.y < flag.y + flag.height and self.y + self.height > flag.y and not flag.done:
                    if self.x > flag.hitbox and self.x < flag.hitbox + GAP:
                        self.score += 1
                        flag.done = True
                    else:
                        self.lives -= 1
                        if self.lives < 0:
                            if int(options[0][1]) > 0:
                                game_over_sound.play()
                            save_stats(self.score, FPS_COUNTER)
                            game_over()
                        flag.done = True

    class Obstacle:
        def __init__(self, y):
            self.y = y
            self.width = random.randint(20, 100)
            self.width = FLAG_IMG.get_width()
            self.height = FLAG_IMG.get_height()
            if len(obstacles) > 0:
                last_flag = obstacles[len(obstacles) - 1]
                min_x_range = last_flag.x - FLAG_SPREAD
                if min_x_range < 0:
                    min_x_range = 0
                max_x_range = last_flag.x + FLAG_SPREAD + GAP
                if max_x_range > W - GAP - FLAG_IMG.get_width():
                    max_x_range = W - GAP - FLAG_IMG.get_width()
                self.x = random.randint(min_x_range, max_x_range)
            else:
                x = W//2
                self.x = x
            self.done = False
            self.hitbox = self.x + 17

        def draw(self):
            WIN.blit(FLAG_IMG, (self.x, self.y - FLAG_IMG.get_height()))
            WIN.blit(FLAG_IMG, (self.x + GAP, self.y - FLAG_IMG.get_height()))
            pygame.draw.circle(WIN, (255,0,0), (self.hitbox, self.y), 1)
            pygame.draw.circle(WIN, (255,0,0), (self.hitbox + GAP, self.y), 1)
            # pygame.draw.circle(WIN, (0,0,0), (self.x, self.y), self.r)
            # pygame.draw.circle(WIN, (0,0,0), (self.x + GAP, self.y), self.r)
            
        def update(self):
            self.y += snowboard.speed

        def show_warning(self):
            WIN.blit(FLAG_WARNING_IMG, (self.x + GAP//2 - FLAG_WARNING_IMG.get_width() // 2, 50))

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

    def keys():
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            snowboard.turn(-1)
        elif keys[pygame.K_RIGHT]:
            snowboard.turn(1)
        else:
            snowboard.turn(0)


    def refresh_win():
        nonlocal y
        bg_rel_y = y % H
        WIN.blit(bg, (0, bg_rel_y - bg.get_height()))
        if bg_rel_y < H:
            WIN.blit(bg, (0, bg_rel_y))
        y += snowboard.speed
        snowboard.update()
        snowboard.between_obstacles(obstacles)
        snowboard.draw_trace()
        snowboard.draw_lives()
        snowboard.draw()
        for obs in obstacles:
            obs.update()
            if obs.y > H + obs.height:
                obstacles.remove(obs)
            obs.draw()
        if obstacles[len(obstacles) - 1].y < 0 and int(options[2][1]) > 0:
            obstacles[len(obstacles) - 1].show_warning()
        text = FONT.render(f'Score: {snowboard.score}', 1, (255,0,0))
        WIN.blit(text, (40, 40))
        create_button('||', (90,90,90), (120,120,120), W-70, 20, 50, 50, game_pause)
        pygame.display.update()

    snowboard = Snowboard(W // 2 - 15, 600, 15, STARTING_SPEED)
    obstacles = []

    options = get_options()

    while run:
        CLOCK.tick(FPS)
        #add flag

        if len(obstacles) > 0:
            if obstacles[len(obstacles) - 1].y - OBSTACLES_FREQUENCY >= -50 or obstacles[len(obstacles) - 1].y >= snowboard.y:
                if obstacles[len(obstacles) - 1].y >= snowboard.y:
                    flag_y = obstacles[len(obstacles) - 1].y - OBSTACLES_FREQUENCY
                else:
                    flag_y = -50
                obstacles.append(Obstacle(flag_y))
        else:
            obstacles.append(Obstacle(-50))

        #speed up

        if FPS_COUNTER % 400 == 0 and snowboard.speed < snowboard.max_speed_down:
            FLAG_SPREAD -= 11
            OBSTACLES_FREQUENCY += 20
            snowboard.speed += 1

        events()
        keys()
        refresh_win()
        
        FPS_COUNTER += 1

        #Count down

        if int(options[1][1]) > 0:
            if FPS_COUNTER == 1 or after_pause:
                after_pause = False
                if int(options[0][1]) > 0:
                    count_down_sound.play()
                for i in range(3,0, -1):
                    count_down_text = COUNT_DOWN_FONT.render(f'{i}', 1, (255,0,0))
                    WIN.blit(bg, (0,0))
                    snowboard.draw_trace()
                    snowboard.draw()
                    text = FONT.render(f'Score: {snowboard.score}', 1, (255,0,0))
                    WIN.blit(text, (40, 40))
                    for obs in obstacles:
                        obs.draw()
                    WIN.blit(count_down_text, (W//2 - count_down_text.get_width()//2, H//2-count_down_text.get_height()//2))
                    pygame.display.update()
                    pygame.time.wait(1000)

def game_intro():
    run = True

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
    
    def refresh_win():
        WIN.fill(0)
        welcome_text = WELCOME_FONT.render('Snowboard game', 1, (255,255,255))
        WIN.blit(welcome_text, (W//2 - welcome_text.get_width() // 2, 100))

        create_button("PLAY", (0,255,0), (0,160,0), W//2-150, 200, 300, 80, game_loop)  
        create_button("OPTIONS", (255, 255, 0), (126,126,0), W//2 - 150, 300, 300,80, options)
        create_button("STATS", (255, 255, 0), (126,126,0), W//2 - 150, 400, 300,80, stats)
        create_button("WATCH AI PLAY", (255,255,0), (126,126,0), W//2 - 150, 500, 300, 80, ai_loop)
        create_button('QUIT', (255,0,0), (160,0,0), W//2-150, 600, 300, 80, end_game)

        pygame.display.update()

    while run:
        CLOCK.tick(15)
        events()
        refresh_win()

def options():
    run = True

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

    def refresh_win():
        nonlocal options_buttons
        WIN.fill(0)
        welcome_text = WELCOME_FONT.render('Options', 1, (255,255,255))
        WIN.blit(welcome_text, (W//2 - welcome_text.get_width() // 2, 100))
        create_button('X', (30,30,30), (100,100,100), 50, 50, 50, 50, game_intro)
        options_buttons = []
        for i, option in enumerate(options):
            pygame.draw.rect(WIN, (120,120,120), (W//2 - 250, 200 + 70 * i, 500, 50))
            text = FONT.render(' '.join(option[0].split('_')).upper(), 1, (255,255,255))
            WIN.blit(text, (80, 50 // 2 - text.get_height() // 2 + 200 + 70 * i))
            if int(option[1]) > 0:
                x = 480
                color = (0,255,0)
            else:
                x = 450
                color = (255,0,0)
            pygame.draw.rect(WIN, color, (450, 50 // 2 - 15 + 200 + 70 * i, 60, 30))
            options_buttons.append(pygame.draw.rect(WIN, (0,0,0), (x, 50//2 - 15 + 200 + 70 * i, 30, 30)))
        
        create_button('Save (restart game)', (30,30,30), (120,120,120), W//2 - 150, H - 300, 300, 80, end_game)

        mouse = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        for x, btn in enumerate(options_buttons):
            if mouse_pressed[0] == 1 and mouse[0] >= btn.x and mouse[0] <= btn.x + btn.width and mouse[1] >= btn.y and mouse[1] <= btn.y + btn.height:
                options[x][1] = int(options[x][1]) * -1

                #save option

                options_file.seek(0)
                options_file.truncate(0)
                for option in options:
                    options_file.write(f'{option[0]} {option[1]}\n')

                pygame.time.wait(200)
        pygame.display.update()

    options_buttons = []
    options = get_options()

    with open('options.txt', 'r+') as options_file:
        while run:
            CLOCK.tick(15)
            events()
            refresh_win()

def stats():
    run = True

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

    def refresh_win():
        WIN.fill(0)
        welcome_text = WELCOME_FONT.render('Stats', 1, (255,255,255))
        WIN.blit(welcome_text, (W//2 - welcome_text.get_width() // 2, 100))
        create_button('X', (30,30,30), (100,100,100), 50, 50, 50, 50, game_intro)
        for i, stat in enumerate(stats):
            pygame.draw.rect(WIN, (120,120,120), (W//2 - 250, 200 + 70 * i, 500, 50))
            text = FONT.render(' '.join(stat[0].split('_')).upper(), 1, (255,255,255))
            WIN.blit(text, (80, 50 // 2 - text.get_height() // 2 + 200 + 70 * i))
            val = FONT.render(stat[1], 1, (255,255,255))
            WIN.blit(val, (W - 200, val.get_height() // 2 + 200 + 70 * i))
        pygame.display.update()
    
    stats = get_stats()

    while run:
        CLOCK.tick(10)
        events()
        refresh_win()

def ai_loop():

    GENERATIONS = 0
    FONT = pygame.font.SysFont('comicsans', 50)
    FPS = 30
    bg = pygame.image.load('imgs/bg.png').convert()
    FLAG_IMG = pygame.image.load('imgs/flag.png').convert_alpha()
    SNOWBOARD_IMG = pygame.image.load('imgs/snowboard2.png').convert_alpha()
    TRACE_IMG = pygame.image.load('imgs/trace.png').convert_alpha()

    def main(genomes, config):

        nonlocal GENERATIONS

        SPEED = 10
        GAP = 150
        y = 0
        run = True
        FLAG_SPREAD = W
        FLAG_FREQUENCY = 400
        SCORE = 0

        flags = []

        class Snowboard:
            def __init__(self):
                self.x = W//2
                self.y = 600
                self.max_speed_down = 50
                self.trace = []
                self.momentum = 0
                self.max_speed = 15
                self.score = 0
                self.width = SNOWBOARD_IMG.get_width()
                self.height = SNOWBOARD_IMG.get_height()

            def draw(self):
                tilt_angle = self.momentum * -3
                self.trace.append([self.x, self.y, tilt_angle])
                tilted_img = pygame.transform.rotate(SNOWBOARD_IMG, tilt_angle)
                WIN.blit(tilted_img, (self.x, self.y))

            def draw_trace(self):
                for pos in self.trace:
                    if pos[1] > H + TRACE_IMG.get_height():
                        self.trace.pop(self.trace.index(pos))
                for pos in self.trace:
                    pos[1] += SPEED
                    tilted_img = pygame.transform.rotate(TRACE_IMG, pos[2])
                    WIN.blit(tilted_img, (pos[0], pos[1]))

            def update(self):
                if self.x + self.momentum >= 0 and self.x + self.width + self.momentum <= W:
                    self.x += self.momentum
                elif self.x + self.momentum < 0:
                    self.momentum = 0
                    self.x = 0
                elif self.x + self.width + self.momentum > W:
                    self.momentum = 0
                    self.x = W - self.width

            def turn(self, dir):
                if dir < 0:
                    if self.momentum > self.max_speed * -1:
                        self.momentum -= 1
                elif dir > 0:
                    if self.momentum < self.max_speed:
                        self.momentum += 1
                else:
                    if self.momentum > 0:
                        self.momentum -= 1
                    elif self.momentum < 0:
                        self.momentum += 1
        
            def between_flag(self, flag):
                return self.x > flag.hitbox and self.x < flag.hitbox + GAP
        
            def on_flag_level(self, flag):
                return self.y < flag.y + flag.height and self.y + self.height > flag.y

        #Flag

        class Flag:
            def __init__(self, y):
                self.y = y
                self.width = random.randint(20, 100)
                self.width = FLAG_IMG.get_width()
                self.done = False
                self.height = FLAG_IMG.get_height()
                if len(flags) > 0:
                    last_flag = flags[len(flags) - 1]
                    min_x_range = last_flag.x - FLAG_SPREAD
                    if min_x_range < 0:
                        min_x_range = 0
                    max_x_range = last_flag.x + FLAG_SPREAD + GAP
                    if max_x_range > W - GAP - FLAG_IMG.get_width():
                        max_x_range = W - GAP - FLAG_IMG.get_width()
                    self.x = random.randint(min_x_range, max_x_range)
                else:
                    self.x = W//2 - GAP // 2
                self.hitbox = self.x + 17

            def draw(self):
                WIN.blit(FLAG_IMG, (self.x, self.y - FLAG_IMG.get_height()))
                WIN.blit(FLAG_IMG, (self.x + GAP, self.y - FLAG_IMG.get_height()))
                pygame.draw.circle(WIN, (255,0,0), (self.hitbox, self.y), 1)
                pygame.draw.circle(WIN, (255,0,0), (self.hitbox + GAP, self.y), 1)

            def update(self):
                self.y += SPEED

            def show_warning(self):
                pygame.draw.rect(WIN, (255,0,0), (self.x + GAP // 2 - 10, 20, 20, 30))

        def events():
            nonlocal run
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    sys.exit()

        def keys():
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                snowboards[0].turn(-1)
            elif keys[pygame.K_RIGHT]:
                snowboards[0].turn(1)
            else:
                snowboards[0].turn(0)

        def refresh_win():

            #snowboards

            for snowboard in snowboards:
                snowboard.update()
                snowboard.draw_trace()
                snowboard.draw()

            #flags

            for flag in flags:
                flag.update()
                flag.draw()

            #score

            score_text = FONT.render(f'Score: {str(SCORE)}', 1, (255,0,0))
            WIN.blit(score_text, (50, 20))

            #generations counter

            gen_text = FONT.render(f'Generation: {str(GENERATIONS)}', 1, (255,0,0))
            WIN.blit(gen_text, (W - 250, 20))    

            #population size

            pop_size_text = FONT.render(f'Alive: {len(snowboards)}', 1, (255,0,0))
            WIN.blit(pop_size_text, (400, 80))

            #close button

            create_button('X', (200,200,200), (120,120,120), 20, 80, 50, 50, game_intro)

            pygame.display.update()


        nets = []
        ge = []
        snowboards = []

        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            snowboards.append(Snowboard())
            g.fitness = 0
            ge.append(g)

        while run:
            if len(snowboards) <= 0:
                run = False
                GENERATIONS += 1
                break
            CLOCK.tick(FPS)

            #BACKGROUND

            bg_rel_y = y % H
            WIN.blit(bg, (0, bg_rel_y - bg.get_height()))
            if bg_rel_y < H:
                WIN.blit(bg, (0, bg_rel_y))
            y += SPEED

            #flags

            if len(flags) > 0:
                if flags[len(flags) - 1].y - FLAG_FREQUENCY >= -50 or flags[len(flags) - 1].y >= snowboards[0].y:
                    if flags[len(flags) - 1].y >= snowboards[0].y:
                        flag_y = flags[len(flags) - 1].y - FLAG_FREQUENCY
                    else:
                        flag_y = -50
                    flags.append(Flag(flag_y))
            else:
                flags.append(Flag(-50))

            for flag in flags:

                for x, snowboard in enumerate(snowboards):
                    if snowboard.on_flag_level(flag):
                        if not snowboard.between_flag(flag):
                            nets.pop(x)
                            ge.pop(x)
                            snowboards.pop(x)
                        else:
                            if not flag.done:
                                SCORE += 1
                                flag.done = True
                            ge[x].fitness += 2
                        

                if flag.y - flag.height > H:
                    flags.remove(flag)

            #Turning

            for x, snowboard in enumerate(snowboards):

                #wall collision

                if snowboard.x <= 0 or snowboard.x + snowboard.width >= W:
                    ge.pop(x)
                    nets.pop(x)
                    snowboards.pop(x)
                else:

                    flag_index = 0
                    if snowboard.y < flags[flag_index].y + flags[flag_index].height:
                        flag_index += 1
                    pygame.draw.circle(WIN, (255,255,0), (flags[flag_index].x + GAP//2, flags[flag_index].y), 10)
                    output = nets[x].activate((snowboard.x, snowboard.momentum, abs(flags[flag_index].x - snowboard.x), abs(flags[flag_index].x + GAP - snowboard.x)))
                    if output[0] > output[1]:
                        snowboard.turn(-1)
                    else:
                        snowboard.turn(1)

                    #add fitness

                    ge[x].fitness += 0.1

            events()
            #keys()
            refresh_win()

    def run(config_path):
    
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

        p = neat.Population(config)

        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)

        winner = p.run(main, 50)

    current_path = os.path.dirname(__file__)
    config_path = os.path.join(current_path, 'config-feedforward.txt')
    run(config_path)
    
def game_over():
    run = True

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

    def refresh_win():
        WIN.fill(0)
        welcome_text = WELCOME_FONT.render('Game over', 1, (255,255,255))
        WIN.blit(welcome_text, (W//2 - welcome_text.get_width() // 2, 100))

        create_button("REPLAY", (0,255,0), (0,160,0), W//2-150, 300, 300, 80, game_loop)  
        create_button('MENU', (255,255,0), (126,126,0), W//2 - 150, 400, 300, 80, game_intro)
        create_button('QUIT', (255,0,0), (160,0,0), W//2-150, 500, 300, 80, end_game)

        pygame.display.update()

    while run:
        CLOCK.tick(15)
        events()
        refresh_win()

def game_pause():
    global after_pause
    run = True
    after_pause = True

    def events():
        nonlocal run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
    
    def refresh_win():
        WIN.fill(0)
        welcome_text = WELCOME_FONT.render('Paused', 1, (255,255,255))
        WIN.blit(welcome_text, (W//2 - welcome_text.get_width() // 2, 100))

        create_button("RESUME", (0,255,0), (0,160,0), W//2-150, 250, 300, 80, unpause)  
        create_button('MENU (reset game)', (255,0,0), (160,0,0), W//2-150, 350, 300, 80, game_intro)

        pygame.display.update()

    def unpause():
        nonlocal run
        run = False

    while run:
        CLOCK.tick(15)
        events()
        refresh_win()

def end_game():
    pygame.quit()
    sys.exit()

def get_options():
    with open('options.txt', 'r+') as options_file:
        options_file.seek(0)
        options_list = list(options_file.readlines())
        options = []
        for option in options_list:
            options.append(option.split())
        return options

def get_stats():
    with open('stats.txt', 'r+') as stats_file:
        arr = list(stats_file.readlines())
        stats = []
        for stat in arr:
            stats_item = stat.split(' ')
            stats.append([stats_item[0].strip(), stats_item[1].strip()])
        return stats

def save_stats(score, fps):
    stats = get_stats()
    stats[0][1] = str(int(stats[0][1]) + int(score))
    stats[1][1] = str(int(stats[1][1]) + int(fps // 30))
    if int(stats[2][1]) < int(score):
        stats[2][1] = str(score) 

    with open('stats.txt', 'w') as stats_file:
        stats_file.seek(0)
        stats_file.truncate(0)
        for stat in stats:
            stats_file.writelines(' '.join(stat) + '\n')

def create_button(text, color, highlight_color, x, y, width, height, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if mouse[0] > x and mouse[0] < x + width and mouse[1] > y and mouse[1] < y + height:  
        if click[0] == 1 and action != None:
            action()
        btn_color = highlight_color
    else:
        btn_color = color
    btn_text = BTN_FONT.render(text, 1, (0,0,0))

    if x is False:
        x = W//2-width//2

    pygame.draw.rect(WIN, btn_color, (x,y,width,height))
    WIN.blit(btn_text, (x+width//2 - btn_text.get_width() // 2, y+height//2 - btn_text.get_height() // 2))
        
game_intro()

pygame.quit()


