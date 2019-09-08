# Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 <http://creativecommons.org/licenses/by/3.0/>?

import pygame
import random
import time
from os import path

#loading directories
img_dir = path.join(path.dirname(__file__),"img")
snd_dir = path.join(path.dirname(__file__),"snd")

#defining game constants
WIDTH = 480
HEIGHT = 600
FPS = 60
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

#load game graphics

background = pygame.image.load(path.join(img_dir,"background.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_dir,"playerShip.png")).convert()
laser_img = pygame.image.load(path.join(img_dir,"laserRed01.png")).convert()
meteor_images = []
meteor_list = ["meteor.png","meteorBrown_big1.png","meteorBrown_big2.png","meteorBrown_big3.png","meteorBrown_big4.png",
               "meteorBrown_med1.png","meteorBrown_med3.png","meteorBrown_small1.png","meteorBrown_small2.png",
               "meteorBrown_tiny1.png","meteorBrown_tiny2.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir,img)).convert())

explosion_anim = {}
explosion_anim["sm"] = []
explosion_anim["lg"] = []

for i in range(9):
	filename = "regularExplosion0{}.png".format(i)
	img = pygame.image.load(path.join(img_dir,filename)).convert()
	img.set_colorkey(BLACK)
	img_lg = pygame.transform.scale(img,(75,75))
	img_sm = pygame.transform.scale(img,(32,32))
	explosion_anim["sm"].append(img_sm)
	explosion_anim["lg"].append(img_lg)

#load game audio

shoot_sound = pygame.mixer.Sound(path.join(snd_dir,"pew.wav"))
ship_blast = pygame.mixer.Sound(path.join(snd_dir,"shipBlast.wav"))
exp_sounds = [pygame.mixer.Sound(path.join(snd_dir,"meteorBlast1.wav")),pygame.mixer.Sound(path.join(snd_dir,"meteorBlast2.wav"))]
pygame.mixer.music.load(path.join(snd_dir,"backgroundMusic.ogg"))
pygame.mixer.music.set_volume(0.4)


font_name = pygame.font.match_font("arial")

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface, text_rect)

def drawSheid(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_WIDTH = 20
    fill = (pct/100)*BAR_LENGTH

    outline_rect = pygame.Rect(x,y,BAR_LENGTH,BAR_WIDTH)
    fill_rect = pygame.Rect(x,y,fill,BAR_WIDTH)

    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect,2)
    
def newMob():
    m = Mob()
    mobs.add(m)
    all_sprites.add(m)

class Explosion(pygame.sprite.Sprite):
	def __init__(self, center, size):
		pygame.sprite.Sprite.__init__(self)
		self.size = size
		self.image = explosion_anim[self.size][0]
		self.rect = self.image.get_rect()
		self.rect.center = center
		self.frame = 0
		self.last_update = pygame.time.get_ticks()
		self.frame_rate = 50

	def update(self):
		now = pygame.time.get_ticks()
		if now - self.last_update > self.frame_rate:
			self.last_update = now
			self.frame += 1
			if self.frame == len(explosion_anim[self.size]):
				self.kill()
			else:
				center = self.rect.center
				self.image = explosion_anim[self.size][self.frame]
				self.rect = self.image.get_rect()
				self.rect.center = center 

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()

        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy

        if self.rect.y < -30:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(50,40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH//2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.sheild = 100
        self.shoot_delay = 200  
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = +8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            shoot_sound.play()    
            bullet = Bullet(self.rect.centerx, self.rect.top)
            bullets.add(bullet)
            all_sprites.add(bullet)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)

        self.image = self.image_orig.copy()

        self.rect = self.image.get_rect()
        self.radius = self.rect.width * 0.85 / 2
        self.rect.x = random.randrange(-25, WIDTH+25)
        self.rect.y = random.randrange(-300,-150)
        self.speedx = random.randrange(-3,3)
        self.speedy = random.randrange(1,3)
        self.rot = 0
        self.rot_speed = random.randrange(-8,8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed)%360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy

        if self.rect.y > HEIGHT + 25 or self.rect.x > WIDTH + 25 or self.rect.x < -25:
            self.rect.x = random.randrange(-25, WIDTH+25)
            self.rect.y = random.randrange(-50,-25)
            self.speedx = random.randrange(-5,5)
            self.speedy = random.randrange(1,10)



all_sprites = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

score = 0

mobs = pygame.sprite.Group()
for i in range(5):
    newMob()

bullets = pygame.sprite.Group()

pygame.mixer.music.play(loops = -1)

#Game loop
running = True
while running:
    #keep loop running at the right speed
    clock.tick(FPS)

    # Process inputs(events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    #update
    all_sprites.update()

    #check for collision with bullets
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        random.choice(exp_sounds).play()
        score += int(50 - hit.radius)
        expl = Explosion(hit.rect.center,"lg")
        all_sprites.add(expl)
        newMob()

    #check for collision with block
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        newMob()
        player.sheild -= hit.radius * 2
        ship_blast.play()
        expl = Explosion(hit.rect.center,"sm")
        all_sprites.add(expl)
        if player.sheild <= 0:
            running = False


    # Draw / Render
    screen.fill(BLACK)
    screen.blit(background,background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score),18,WIDTH//2,10)
    drawSheid(screen,5,5,player.sheild)
    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
