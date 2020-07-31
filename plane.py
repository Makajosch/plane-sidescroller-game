import pygame
import sys
from random import randint

# Variablen für Bildschirm
x = 1600
y = int(x * 9 / 16)

gold = (212,175,55)

points = 0

# Variablen für Spieler-Flugzeug
breite = 222
hoehe = 151
xpos = 0
ypos = int(y / 2)


frame_count_b = 0 # Variable für Schussgeschwindigkeit Spieler
frame_count_e = 0 # Variable für Abstand Feindfugzeuge

# Gruppen für sprites
plane_sprites = pygame.sprite.GroupSingle()
bullet_sprites = pygame.sprite.Group()
bomb_sprites = pygame.sprite.GroupSingle()
flame_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
rocket_sprites = pygame.sprite.Group()
explosion_sprites = pygame.sprite.Group()

# Liste für einblendbare Texte
texte = []

# pygame initialisieren
pygame.mixer.init(44100, -16, 1, 512) # Soundmixer zuerst
pygame.init()
screen = pygame.display.set_mode([x, y])
pygame.display.set_caption('plane')
clock = pygame.time.Clock()

# Sounds laden
plane_sound = pygame.mixer.Sound('sounds/plane_2.wav')
plane_sound.set_volume(0.5)
gun_sound = pygame.mixer.Sound('sounds/gun.wav')
explosion_sound = pygame.mixer.Sound('sounds/explosion.wav')
explosion_sound.set_volume(0.5)
breakdown_sound = pygame.mixer.Sound('sounds/breakdown.wav')
bomb_sound = pygame.mixer.Sound('sounds/bomb.wav')

# Hintergrundbilder laden
sky = pygame.image.load('graphics/background/sky.png').convert()
farground = pygame.image.load('graphics/background//farground_mountains.png').convert_alpha()
midground = pygame.image.load('graphics/background//midground_mountains.png').convert_alpha()
foreground = pygame.image.load('graphics/background/foreground_mountains.png').convert_alpha()

far_x = 0
mid_x = 0
fore_x = 0


class Plane(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('graphics/plane/fly_1.png').convert_alpha(),
                       pygame.image.load('graphics/plane/fly_2.png').convert_alpha(),
                       pygame.image.load('graphics/plane/shoot_1.png').convert_alpha(),
                       pygame.image.load('graphics/plane/shoot_2.png').convert_alpha(),
                       pygame.image.load('graphics/plane/shoot_3.png').convert_alpha(),
                       pygame.image.load('graphics/plane/shoot_4.png').convert_alpha(),
                       pygame.image.load('graphics/plane/shoot_5.png').convert_alpha(),
                       pygame.image.load('graphics/plane/dead_1.png').convert_alpha(),
                       pygame.image.load('graphics/plane/dead_1.png').convert_alpha(),
                       pygame.image.load('graphics/plane/dead_1.png').convert_alpha()]
                      
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.shoot = False
        self.dead = False
        
    def update(self):
        if self.dead:
            if self.index > 8:
                self.index = 5
            self.rect.x += 5
            self.rect.y += 5
        elif self.shoot:
            if self.index > 6:
                self.index = 2
            self.rect.x = xpos
            self.rect.y = ypos
        else:
            if self.index > 1:
                self.index = 0
            self.rect.x = xpos
            self.rect.y = ypos
        self.image = self.images[self.index]
        self.index += 1
        
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('graphics/ammo/bullet.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.centerx = xpos + 180
        self.rect.centery = ypos + 111
        self.visible = True
              
    def update(self):
        self.rect.x += 50
        if self.rect.x > x:
            self.visible = False
            
            
class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('graphics/ammo/bomb.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.drop = False
        self.visible = True
              
    def update(self):
        if self.drop:
            self.rect.y += 10
            if self.rect.y > y - 50:
                self.visible = False
        else:    
            self.rect.x = plane.rect.x +50
            self.rect.y = plane.rect.y + 112
            
            
class Rocket(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('graphics/ammo/rocket_0.png').convert_alpha(),
                       pygame.image.load('graphics/ammo/rocket_1.png').convert_alpha(),
                       pygame.image.load('graphics/ammo/rocket_2.png').convert_alpha(),
                       pygame.image.load('graphics/ammo/rocket_3.png').convert_alpha()]
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = enemy.rect.x +50
        self.rect.y = enemy.rect.y + 105
        self.xspeed = enemy.xspeed
        self.visible = True        
              
    def update(self):
        if self.rect.right < x - 100:
            self.rect.x -= 20
            diff = abs(self.rect.centery - (ypos + 111)) # Austritt bullets, damit rockets nicht direkt im Schusskanal anfliegen
            if diff > 40:
                if self.rect.centery < ypos + 111:
                    self.rect.centery += 4
                elif self.rect.centery > ypos + 111:
                    self.rect.centery -= 4
            if self.rect.x < 0 :
                self.visible = False
        else:
            self.rect.x -= self.xspeed
        if self.index > 3:
            self.index = 0
        self.image = self.images[self.index]
        self.index += 1
        

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('graphics/enemy/enemy_yellow.png').convert_alpha(),
                       pygame.image.load('graphics/enemy/enemy_red.png').convert_alpha(),
                       pygame.image.load('graphics/enemy/enemy_2_yellow.png').convert_alpha(),
                       pygame.image.load('graphics/enemy/enemy_2_red.png').convert_alpha()]
        
        self.index = randint(0, 3)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x + 111, randint(55, y - 55))
        self.xspeed = 5 + self.index * 5
        self.alive = True        
               
    def update(self):
        self.rect.centerx -= self.xspeed
        if self.rect.centerx < -111: #rechter rand von rect
            self.alive = False


class Explosion(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('graphics/explosion/explosion_01.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_02.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_03.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_04.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_05.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_06.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_07.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_08.png').convert_alpha(),
                       pygame.image.load('graphics/explosion/explosion_09.png').convert_alpha()]
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.visible = True
        
    def update(self):
        self.rect.centerx -= self.xspeed
        if self.index <= 8:
            self.image = self.images[self.index]
        else:
            self.visible = False
        self.index += 1
        
   
class Flame(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('graphics/flames/flame_1.png').convert_alpha(),
                       pygame.image.load('graphics/flames/flame_2.png').convert_alpha(),
                       pygame.image.load('graphics/flames/flame_3.png').convert_alpha()]
        
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        
    def update(self):
        self.rect.x = plane.rect.x - 100
        self.rect.y = plane.rect.y + 45
        if self.index > 2:
            self.index = 0
        self.image = self.images[self.index]
        self.index += 1


class Text():
    def __init__(self, inhalt):
        self.text_object = pygame.font.SysFont('comicsansms', 48, True).render(inhalt, True, (gold))
        self.rect = self.text_object.get_rect()
        self.visible = True
        self.counter = 0
        
    def update(self):
        if self.counter < 120:
            screen.blit(self.text_object, self.rect)
        else:
            self.visible = False
        self.counter += 1



def update_window():
    global bomb
    
    # Hintergrund
    screen.blit(sky, (0, 0))
        
    screen.blit(farground, (far_x, y - 330))
    screen.blit(farground, (far_x + 2048, y - 330))
       
    screen.blit(midground, (mid_x, y - 119))
    screen.blit(midground, (mid_x + 2048, y - 119))
       
    screen.blit(foreground, (fore_x, y - 109))
    screen.blit(foreground, (fore_x + 2048, y - 109))
       
    # Anzeige der erreichten Punktzahl
    points_display = pygame.font.SysFont('comicsansms', 72, True).render(str(points), True, (gold))
    points_rect = points_display.get_rect()
    points_rect.x = 10
    points_rect.y = 0
    screen.blit(points_display, points_rect)
    
    # Sprites updaten
    plane_sprites.update()
           
    if bomb.visible == False:
        bomb_sound.stop()
        bomb_sprites.remove(bomb)
        explosion_sound.play()
        explosion = Explosion()
        explosion_sprites.add(explosion)
        explosion.xspeed = 0
        explosion.rect.center = bomb.rect.center
        bomb = Bomb()
        bomb_sprites.add(bomb)
    bomb_sprites.update()
    
    flame_sprites.update()
    
    for text in texte:
        if text.visible == False:
            texte.remove(text)
        Text.update(text)
        
    for enemy in enemy_sprites:
        if enemy.alive == False:
            enemy_sprites.remove(enemy)
    enemy_sprites.update()
    
    for rocket in rocket_sprites:
        if rocket.visible == False:
            rocket_sprites.remove(rocket)
    rocket_sprites.update()
    
    for explosion in explosion_sprites:
        if explosion.visible == False:
            explosion_sprites.remove(explosion)
    explosion_sprites.update()
    
    for bullet in bullet_sprites:
        if bullet.visible == False:
            bullet_sprites.remove(bullet)
    bullet_sprites.update()
    
    
    bomb_sprites.draw(screen)
    plane_sprites.draw(screen)
    bullet_sprites.draw(screen)
    flame_sprites.draw(screen)
    enemy_sprites.draw(screen)
    rocket_sprites.draw(screen)
    explosion_sprites.draw(screen)
       
    pygame.display.update()
  
plane = Plane()
plane_sprites.add(plane)
bomb = Bomb()
bomb_sprites.add(bomb)
plane_sound.play(-1)


while True:
    
    # Framerate
    clock.tick(60)
    update_window()
    
    if far_x <= -2048:
        far_x = 0
    far_x -= 1
    if mid_x <= -2048:
        mid_x = 0
    mid_x -= 2
    if fore_x <= -2048:
        fore_x = 0
    fore_x -= 4
    
   
    # Kollisionen
    
    # enemy - bullet
    for enemy in pygame.sprite.groupcollide(enemy_sprites, bullet_sprites, True, True):
        explosion_sound.play()
        explosion = Explosion()
        explosion_sprites.add(explosion)
        explosion.xspeed = enemy.xspeed
        explosion.rect.center = enemy.rect.center
        if enemy.index <=1 and rocket.rect.right > x - 100:
            rocket.visible = False
        text = Text(str((enemy.index ** 2)* 10 + 10))
        points += (enemy.index ** 2)* 10 + 10
        text.rect.center = enemy.rect.center
        texte.append(text)
        
    # rocket - bullet  
    for rocket in pygame.sprite.groupcollide(rocket_sprites, bullet_sprites, True, True):
        explosion_sound.play()
        explosion = Explosion()
        explosion_sprites.add(explosion)
        explosion.xspeed = rocket.xspeed
        explosion.rect.center = rocket.rect.center
        points += 100
        text = Text('100')
        text.rect.center = rocket.rect.center
        texte.append(text)
    
    # enemy - plane
    if plane.dead == False:
        for enemy in pygame.sprite.groupcollide(enemy_sprites, plane_sprites, True, False):
            plane_sound.stop()
            breakdown_sound.play()
            explosion = Explosion()
            explosion_sprites.add(explosion)
            explosion.xspeed = enemy.xspeed
            flame = Flame()
            flame_sprites.add(flame)
            plane.dead = True
        
    # rocket - plane
        
    # Events (Tastatur Maus)        
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE : sys.exit()
    keys = pygame.key.get_pressed()    
       
    if keys[pygame.K_d] and xpos < x - breite:
        xpos += 10
    elif keys[pygame.K_a] and xpos >= 10:
        xpos -= 10
        
    if keys[pygame.K_w] and ypos > 10:
        ypos -= 10
    elif keys[pygame.K_s] and ypos < y - hoehe:
        ypos += 10
       
    if frame_count_b > 5:
        plane.shoot = False # Ende Schussanimation Spieler-Flugzeug 
    if keys[pygame.K_SPACE] and plane.dead == False and frame_count_b > 10:
        plane.shoot = True # Start Schussanimation Spieler-Flugzeug
        gun_sound.play()
        bullet = Bullet()
        bullet_sprites.add(bullet)
        frame_count_b = 0
      
    if keys[pygame.K_b] and plane.dead == False and bomb.drop == False:
        bomb.drop = True
        bomb_sound.play(0, 1500)
     
    
    # Neue Feindflugzeuge generieren
    if frame_count_e > randint(50, 150):
        enemy = Enemy()
        enemy_sprites.add(enemy)
        if enemy.index <=1: # Nur die ersten beiden enemy-typen werden mit Raketen ausgestattet
            rocket = Rocket()
            rocket_sprites.add(rocket)
        frame_count_e = 0
     
    #print(len(bullet_sprites))
    #print(len(enemy_sprites))
    #print(len(explosion_sprites))
   
    frame_count_b += 1
    frame_count_e += 1
    
    #print (int(clock.get_fps()))
    #print(frame_count)
    
      
            
                

  
                
    
            


         
