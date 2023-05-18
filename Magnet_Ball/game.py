import pygame
from pygame.locals import *
from pygame import mixer
import random

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1152
screen_height = 720

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Magnet Ball')

# game variables
meteor_frequency = 800 #miliseconds
last_meteor = pygame.time.get_ticks() - meteor_frequency
wormhole_frequency = 9000
last_wormhole = pygame.time.get_ticks()
gate_frequency = 5000
last_gate = pygame.time.get_ticks()
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255,255,255)

# load images
bg = pygame.image.load('img/bg.png')

# load music/sounds
jump_sound = pygame.mixer.Sound("audio/jump.mp3")
wormhole_sound = pygame.mixer.Sound("audio/wormhole.mp3")
wormhole_sound.set_volume(0.5)
meteor_sound = pygame.mixer.Sound("audio/meteor.mp3")
gate_sound = pygame.mixer.Sound("audio/gate.mp3")

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

    


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.index = 0
        self.counter = 0
        self.color = "red"

        self.redimages = []
        for num in range(1, 5):
            img = pygame.image.load(f'img/redball{num}.png')
            img = pygame.transform.scale(img, (100, 100))
            self.redimages.append(img)
        
        self.blueimages = []
        for num in range(1, 5):
            img = pygame.image.load(f'img/blueball{num}.png')
            img = pygame.transform.scale(img, (100, 100))
            self.blueimages.append(img)
            
        self.imagelist = self.redimages
        self.image = self.imagelist[self.index]

        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.vel = 0
        self.jumped = False
        self.in_air = True
        self.changed = False
        self.dx = 0
        
    def update(self):
        # constraint boundary
        if self.color == "red":
            if self.rect.bottom > 700:
                self.rect.bottom = 700
            if self.rect.top < 30:
                self.rect.top = 30
        else:
            if self.rect.bottom > 690:
                self.rect.bottom = 690
            if self.rect.top < 21:
                self.rect.top = 1

        # x axis movement
        if self.dx > 0:
            self.rect.x += 10
            self.dx -= 10
        elif self.dx < 0:
            self.rect.x -= 10
            self.dx += 10

        # y axis movement
        if self.color == "red":
            self.vel += 2
            if self.vel > 40:
                self.vel = 40
            if self.rect.bottom + int(self.vel) > 700:
                self.rect.bottom = 700
                self.in_air = False
                self.vel = 10
            else: self.rect.y += int(self.vel)

        elif self.color == "blue":
            self.vel -= 2
            if self.vel < -40:
                self.vel = -40
            if self.rect.top + int(self.vel) < 21:
                self.rect.top = 21
                self.in_air = False
                self.vel = -10
            else: self.rect.y += int(self.vel)

        # keypress
        key = pygame.key.get_pressed()

        if key[pygame.K_SPACE] and self.in_air == False:
            if self.color == "red":
                self.vel -= 45
            else:
                self.vel += 45
            self.rect.y += self.vel
            self.jumped = True
            self.in_air = True
            jump_sound.play()
            
        if key[pygame.K_SPACE] == False:
            self.jumped = False
        
        if key[pygame.K_q]:
            self.rect.x -= 10
        if key[pygame.K_w]:
            self.rect.x += 1

        if key[pygame.K_a] and self.changed == False and self.in_air == False:
            self.vel = 0
            if self.color == "red":
                self.color = "blue"
            elif self.color == "blue":
                self.color = "red"
            self.changed = True
            self.in_air = True
        
        if key[pygame.K_a] == False:
            self.changed = False
    
        # animation
        self.counter += 1
        roll_countdown = 5

        if self.color == "red":
            self.imagelist = self.redimages
        elif self.color == "blue":
            self.imagelist = self.blueimages

        if self.counter > roll_countdown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.imagelist):
                self.index = 0
        self.image = self.imagelist[self.index]


class Meteor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/meteor.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x -= 8
        if self.rect.x <= 52:
            self.kill()
        


class Wormhole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/wormhole.png')
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

    def update(self):
        self.rect.x -= 8
        if self.rect.x <= 52:
            self.kill()

class Gate(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/lightgate.png')
        self.image = pygame.transform.scale(self.image, (100, 900))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.activated = False
    def update(self):
        self.rect.x -= 8
        if self.rect.x <= 52:
            self.kill()



class Button():
    def __init__(self, x, y, text):
        self.image = font.render(text, True, white)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.clicked = False
    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        pos = pygame.mouse.get_pos()
        if restartButton.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                return True


        
restartButton = Button(screen_width//2, screen_height//2, "Restart")
startButton = Button(screen_width//2, screen_height//2, "Start")


meteor_group = pygame.sprite.Group()
wormhole_group = pygame.sprite.Group()
gate_group = pygame.sprite.Group()
gate = Gate(screen_height//2, screen_width//2)
ball_group = pygame.sprite.Group()
ball = Ball(screen_width//2, 360) # y range70to650
ball_group.add(ball)

music = pygame.mixer.music.load("audio/bgm.mp3")
music = pygame.mixer.music.load("audio/void.mp3")
pygame.mixer.music.play(-1)

music_playing = False
score = 0
game_state = "start"
run = True
while run:

    clock.tick(fps)
    screen.blit(bg, (0,0))

    if music_playing == False:
        music_playing = True
        if game_state == "over":
            music = pygame.mixer.music.load("audio/void.mp3")
            pygame.mixer.music.play(-1)
        else:
            music = pygame.mixer.music.load("audio/bgm.mp3")
            
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)

    if game_state == "start":
        if startButton.draw() == True:
            game_state = "play"
            meteor_group.empty()
            gate_group.empty()
            wormhole_group.empty()

    elif game_state == "play":
        score += 1
        #pygame.draw.line(screen, (0,0,0), (60, 360), ball.rect.center, 5)
        ball_group.draw(screen)
        ball_group.update()

        if pygame.sprite.groupcollide(ball_group, meteor_group, False, True, collided=pygame.sprite.collide_circle_ratio(0.6)):
            meteor_sound.play()
            ball.dx -= 100

        if pygame.sprite.groupcollide(ball_group, wormhole_group, False, True):
            wormhole_sound.play()
            ball.dx += 100
        
        if pygame.sprite.groupcollide(ball_group, gate_group, False, False):
            if gate.activated == False:
                gate_sound.play()
                ball.dx += 50
                if ball.color == "red":
                    ball.color = "blue"
                else:
                    ball.color = "red"
            gate.activated = True
            ball.in_air = True

        if ball.rect.left <= 52:
            ball_group.empty()
            game_state = "over"
            music_playing = False

    elif game_state == "over":
        if restartButton.draw() == True:
            music = pygame.mixer.music.load("audio/bgm.mp3")
            game_state = "play"
            meteor_group.empty()
            gate_group.empty()
            wormhole_group.empty()
            ball = Ball(screen_width//2, 360)
            ball_group.add(ball)
            score = 0
            music_playing = False


    # timer
    time_now = pygame.time.get_ticks()
    
    # meteor
    if time_now - last_meteor > meteor_frequency:
        position = random.randint(1,99) % 3
        position2 = random.randint(90, 630)
        meteor = Meteor(1230, position2)
        meteor_group.add(meteor)
        last_meteor = time_now
    meteor_group.draw(screen)
    meteor_group.update()
    pygame.sprite.groupcollide(meteor_group, wormhole_group, True, False)
    
    # wormhole
    if time_now - last_wormhole > wormhole_frequency:
        position = random.randint(90, 630)
        wormhole = Wormhole(1230, position)
        wormhole_group.add(wormhole)
        last_wormhole = time_now
    wormhole_group.draw(screen)
    wormhole_group.update()

    #lightgate
    if time_now - last_gate > gate_frequency:
        gate = Gate(1230, screen_height//2)
        gate_group.add(gate)
        last_gate = time_now
    gate_group.draw(screen)
    gate_group.update()

    draw_text(str(score//60), font, white, 5, 30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()