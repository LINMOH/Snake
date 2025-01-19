import pygame
import sys
import random

# 初始化pygame和混音模块
pygame.init()
pygame.mixer.init()

# 背景音乐初始化（只加载一次）
def start_music():
    pygame.mixer.music.load("music\\music.mp3")
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

# 背景音乐加载
start_music()

# 隐藏鼠标光标
pygame.mouse.set_visible(False)

# 窗口和方块大小
window_width = 800
window_height = 600
snake_block_size = 20

# 颜色定义
snake_color = (255, 100, 100)  # 设定蛇的颜色为柔和的红色
food_color = (255, 69, 0)
small_mine_color = (255, 255, 255)  # 小地雷（白色）
large_mine_color = (255, 105, 180)  # 大地雷（粉色）
black = (0, 0, 0)
background_base_color = (50, 50, 255)  # 背景的基础颜色，用于渐变

# 初始化窗口
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("贪吃蛇 v1.3.2(20241229)")
clock = pygame.time.Clock()

# 字体
font_style = pygame.font.SysFont("SimHei", 30)
game_over_font = pygame.font.SysFont("SimHei", 50)

# 音效加载
eat_food_sound = pygame.mixer.Sound("sounds\\eat_food.wav")
hit_small_mine_sound = pygame.mixer.Sound("sounds\\hit_small_mine.wav")
game_over_sound = pygame.mixer.Sound("sounds\\game_over.wav")

# 背景图片（整个格子内渐变背景）
def draw_background(surface):
    for x in range(0, window_width, snake_block_size):
        for y in range(0, window_height, snake_block_size):
            # 根据位置计算渐变色
            color_factor_x = x / window_width  # 横向渐变
            color_factor_y = y / window_height  # 纵向渐变
            r = int(background_base_color[0] * (1 - color_factor_x))
            g = int(background_base_color[1] * color_factor_y)
            b = 255 - int(255 * color_factor_y)
            color = (r, g, b)
            pygame.draw.rect(surface, color, [x, y, snake_block_size, snake_block_size])

# 粒子特效类
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.lifetime = 60  # 增加粒子存在的时间，提升视觉效果
        self.velocity = [random.randint(-2, 2), random.randint(-2, 2)]  # 随机漂浮速度

    def update(self):
        self.x += self.velocity[0]  # 横向漂浮
        self.y += self.velocity[1]  # 纵向漂浮
        self.size -= 0.1  # 随着时间减小
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:  # 只绘制有效的粒子
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size)

particles = []

# 食物类
class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = food_color
        self.randomize_position()

    def randomize_position(self):
        # 设置最小边界距离，避免食物生成在靠近边缘的区域
        min_distance = 50  # 食物与边缘的最小距离
        x = round(random.randrange(min_distance, window_width - snake_block_size - min_distance) / snake_block_size) * snake_block_size
        y = round(random.randrange(min_distance, window_height - snake_block_size - min_distance) / snake_block_size) * snake_block_size
        self.position = (x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, [self.position[0], self.position[1], snake_block_size, snake_block_size])

# 地雷类（基类）
class Mine:
    def __init__(self, color, damage):
        self.position = (0, 0)
        self.color = color
        self.damage = damage
        self.randomize_position()

    def randomize_position(self):
        # 设置最小边界距离，避免地雷生成在靠近边缘的区域
        min_distance = 50  # 地雷与边缘的最小距离
        x = round(random.randrange(min_distance, window_width - snake_block_size - min_distance) / snake_block_size) * snake_block_size
        y = round(random.randrange(min_distance, window_height - snake_block_size - min_distance) / snake_block_size) * snake_block_size
        self.position = (x, y)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, [self.position[0], self.position[1], snake_block_size, snake_block_size])

# 蛇类
class Snake:
    def __init__(self):
        self.length = 3
        self.positions = [(window_width // 2, window_height // 2)]
        self.direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.color = snake_color
        self.score = 0

    def move(self):
        x, y = self.positions[0]
        dx, dy = self.direction
        self.positions.insert(0, (x + dx * snake_block_size, y + dy * snake_block_size))
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self, surface):
        for i, position in enumerate(self.positions):
            # 使用渐变色
            color_factor = (i / self.length)  # 根据蛇身的位置变化颜色
            color = (255 - int(color_factor * 100), 100 + int(color_factor * 50), int(color_factor * 100))
            pygame.draw.rect(surface, color, [position[0], position[1], snake_block_size, snake_block_size])
        score_text = font_style.render(f"得分: {self.score}", True, black)
        surface.blit(score_text, (10, 10))

        # 在屏幕顶部显示名字和学校
        school_name_text = font_style.render("学校: 平阴实高", True, black)
        player_name_text = font_style.render("作者: 林墨瀚", True, black)
        window.blit(school_name_text, (10, 40))  # 在屏幕顶部显示学校名称
        window.blit(player_name_text, (10, 70))  # 在屏幕顶部显示玩家名字

    def update_direction(self, direction):
        self.direction = direction

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.direction != (0, 1):
            self.update_direction((0, -1))
        elif keys[pygame.K_DOWN] and self.direction != (0, -1):
            self.update_direction((0, 1))
        elif keys[pygame.K_LEFT] and self.direction != (1, 0):
            self.update_direction((-1, 0))
        elif keys[pygame.K_RIGHT] and self.direction != (-1, 0):
            self.update_direction((1, 0))



# 游戏主循环
def game_loop():
    snake = Snake()
    food = Food()
    small_mines = [Mine(small_mine_color, -20) for _ in range(3)]  # 初始生成3个小地雷
    large_mines = [Mine(large_mine_color, 0)]  # 初始生成1个大地雷
    game_close = False
    food_eaten = False  # 用来标记是否吃掉了食物
    previous_food_position = food.position  # 记录上一个食物的位置

    while True:
        while game_close:
            window.fill((255, 255, 255))  # 白色背景
            game_over_text = game_over_font.render("游戏结束", True, (255, 69, 0))
            restart_text = font_style.render("按Enter再来一次或按ESC退出", True, black)
            window.blit(game_over_text, (window_width // 2 - game_over_text.get_width() // 2, window_height // 4))
            window.blit(restart_text, (window_width // 2 - restart_text.get_width() // 2, window_height // 2))
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_RETURN:
                        game_loop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # 更新蛇的方向
        snake.handle_keys()
        snake.move()

        # 撞到边框死亡检测
        x, y = snake.positions[0]
        if x < 0 or x >= window_width or y < 0 or y >= window_height:
            game_close = True  # 撞到边框，游戏结束
            game_over_sound.play()  # 播放游戏结束音效

        # 撞到小地雷的处理
        for small_mine in small_mines[:]:
            if snake.positions[0] == small_mine.position:
                small_mines.remove(small_mine)  # 碰到小地雷，地雷消失
                snake.score -= 20  # 撞到小地雷，减去20分
                hit_small_mine_sound.play()  # 播放碰到小地雷音效

        # 撞到大地雷的处理
        for large_mine in large_mines:
            if snake.positions[0] == large_mine.position:
                game_close = True  # 撞到大地雷，游戏结束
                game_over_sound.play()  # 播放游戏结束音效

        # 吃到食物时处理
        if snake.positions[0] == food.position:
            previous_food_position = food.position  # 记录吃掉食物时的位置
            food.randomize_position()
            snake.length += 1
            snake.score += 10
            food_eaten = True
            eat_food_sound.play()  # 播放吃到食物音效

        # 根据分数生成地雷
        if len(small_mines) < (snake.score // 10) + 3:  # 随着分数增加，小地雷每10分加一个，初始有3个
            small_mines.append(Mine(small_mine_color, -20))

        if len(large_mines) < (snake.score // 20) + 1:  # 随着分数增加，大地雷每20分加一个，初始有1个
            large_mines.append(Mine(large_mine_color, 0))

        # 生成粒子效果
        if food_eaten:
            for _ in range(30):  # 生成30个粒子
                particles.append(Particle(previous_food_position[0] + snake_block_size // 2, 
                                          previous_food_position[1] + snake_block_size // 2, 
                                          random.choice([(255, 100, 100), (255, 200, 100)])))
            food_eaten = False  # 重置标志，粒子效果只会在食物吃掉后生成

        # 更新和绘制粒子效果
        for particle in particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                particles.remove(particle)
            particle.draw(window)

        # 绘制背景
        draw_background(window)

        # 绘制蛇、食物、地雷
        snake.draw(window)
        food.draw(window)
        for mine in small_mines + large_mines:
            mine.draw(window)

        pygame.display.update()
        clock.tick(15)

game_loop()
