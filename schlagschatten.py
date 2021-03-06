#!/usr/bin/env python2

import sys
import os
import pygame
from random import randint
from random import uniform
from random import choice
from math import pi
import subprocess


FPS = 30
ZOOM = 4
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 200
DISPLAY_WIDTH = SCREEN_WIDTH * ZOOM
DISPLAY_HEIGHT = SCREEN_HEIGHT * ZOOM

GFX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'gfx'))
SFX_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sfx'))
MUSIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'music'))



class Ship(object):
    speed = 3
    x = 0
    y = 0

    def __init__(self,gfx_file):
        self.surface = pygame.image.load(gfx_file)
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()

    def blit(self,target):
        target.blit(self.surface,(self.x,self.y))
        
    def move(self,dx,dy):
        self.move_to(self.x+dx,self.y+dy)

    def move_to(self,x,y,legal=True):
        if legal:
            if (x < -self.w):
                x = -self.w
            elif (x > SCREEN_WIDTH):
                x = SCREEN_WIDTH
            if (y < -self.h):
                y = -self.h
            elif (y > SCREEN_HEIGHT):
                y = SCREEN_HEIGHT
        self.x = x
        self.y = y

    def collides(self,other):
        dx = self.x - other.x
        dy = self.y - other.y
        if (dx > 0 and dx < other.w) or (dx < 0 and abs(dx) < self.w):
            if (dy > 0 and dy < other.h) or (dy < 0 and abs(dy) < self.h):
                return True
        return False

    def collide(self,other):
        if self.collides(other):
            self.die()
            if isinstance(other,Ship):
                other.die()
            elif isinstance(other,Box):
                main.player.die()


class Shot(Ship):
    def __init__(self,dx,dy,enemy):
        if (enemy):
            gfx = GFX_DIR+'/enemy1-shot.png'
            self.sound = pygame.mixer.Sound(SFX_DIR+'/slime.wav')
        else:
            gfx = GFX_DIR+'/player-shot.png'
            self.sound = pygame.mixer.Sound(SFX_DIR+'/cannon.wav')
        super(Shot,self).__init__(gfx)
        self.dx = dx
        self.dy = dy
        self.enemy = enemy

    def play_sound(self):
        self.sound.play()

    def logic(self):
        if self.y <= -self.h or self.y >= SCREEN_HEIGHT + self.h or self.x <= -self.w or self.x >= SCREEN_WIDTH :
            self.die()
            return
        self.move(self.dx,self.dy)

    def die(self):
        if self in main.shots:
            main.shots.remove(self)


class Enemy(Ship):
    dx = 0
    dy = 0
    xvar = 0.5
    yvar = 0.2
    next_shot = 0

    def __init__(self,gfx_file):
        super(Enemy,self).__init__(gfx_file)
        self.sound = pygame.mixer.Sound(SFX_DIR+'/enemy-explode.wav')

    def die(self):
        main.enemies.remove(self)
        main.lighting.flash(255)
        main.score += 1
        self.sound.play()

    def logic(self):
        if (self.x <= 0 and self.dx < 0) or (self.x >= SCREEN_WIDTH and self.dx > 0):
            self.dx = -self.dx
        if (self.y <= 0 and self.dy < 0) or (self.y >= SCREEN_HEIGHT and self.dy > 0):
            self.dy = -self.dy

        self.dx += uniform(0.0,self.xvar) - self.xvar/2
        self.dy += uniform(0.0,self.yvar) - self.yvar/2
        if self.dx < -self.speed:
            self.dx = -self.speed
        elif self.dx > self.speed:
            self.dx = self.speed
        if self.dy < -self.speed:
            self.dy = -self.speed
        elif self.dy > self.speed:
            self.dy = self.speed
        if self.y < 0:
            self.dy = 1
        self.move(self.dx,self.dy)
        
        if not main.player.dead:
            min_shot_interval = 20
            max_shot_interval = 200
            if main.tick > self.next_shot:
                self.next_shot = main.tick + randint(min_shot_interval,max_shot_interval)
                main.lighting.add_flare(Flare(24,8))
                shot_speed = 2.0
                dx = main.player.x - self.x
                dy = main.player.y - self.y
                s = (dx**2 + dy**2)**0.5
                sx = dx / s * shot_speed / pi
                sy = dy / s * shot_speed / pi
                shot = Shot(sx,sy,True)
                shot.move_to(self.x + self.w/2 - shot.x/2, self.y + self.h)
                shot.play_sound()
                main.shots.append(shot)
        

class EnemyOne(Enemy):
    def __init__(self):
        super(EnemyOne,self).__init__(GFX_DIR+'/enemy1.png')


class Box(object):
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Player(Ship):
    last_shot = 0
    dead = False

    def __init__(self):
        super(Player,self).__init__(GFX_DIR+'/player.png')     
        self.sound = pygame.mixer.Sound(SFX_DIR+'/player-explode.wav')
        self.box = Box(self.x,self.y,self.w,self.h)

    def poll_keys(self):
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed
        self.move(dx,dy)
        
    def key_down(self,key):
        if key == pygame.K_SPACE:
            if (main.tick - self.last_shot > 10):
                self.last_shot = main.tick
                main.lighting.add_flare(Flare(64,16))
                shot = Shot(0,-5,False)
                shot.move_to(self.x + self.w/2 - shot.w/2, self.y - shot.h)
                shot.play_sound()
                main.shots.append(shot)

    def move_to(self,x,y,legal=True):
        super(Player,self).move_to(x,y,legal)
        self.box.x = self.x + self.w/4
        self.box.y = self.y + self.h/4
        self.box.w = self.w/2
        self.box.h = self.h/2

    def die(self):
        self.sound.play()
        self.dead = True
        main.lighting.flash(512)
        main.shutdown_in(FPS * 4)
#        main.shutdown_in(self.sound.get_length() * FPS)
            
class Background(object):
    scroll_speed = 0.3
    yoff = 0

    def __init__(self):
        self.front = self.create_screen()
        self.back = self.create_screen()

    def create_screen(self):
        min_stars = int(SCREEN_WIDTH * SCREEN_HEIGHT / 1000)
        num_stars = randint(min_stars, int(min_stars * 1.2))
        min_bright = 64
        max_bright = 196
        screen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
        screen.fill((16,8,32))
        pixels = pygame.PixelArray(screen)
        for t in range (0,num_stars):
            color = pygame.Color(randint(min_bright,max_bright),randint(min_bright,max_bright),randint(min_bright,max_bright),0)
            pixels[randint(0,SCREEN_WIDTH-1),randint(0,SCREEN_HEIGHT-1)] = color
        return screen

    def blit(self,target):
        target.blit(self.back,(0,int(self.yoff)-self.back.get_height()))
        target.blit(self.front,(0,int(self.yoff)))

        self.yoff += self.scroll_speed
        if self.yoff >= self.front.get_height():
            self.yoff = 0
            self.front = self.back
            self.back = self.create_screen()


class Flare(object):
    def __init__(self,brightness,cooldown):
        self.brightness = brightness
        self.cooldown = cooldown

    def cool(self):
        self.brightness -= self.cooldown


class Lighting(object):
    flares = []

    def __init__(self):
        self.sur_light = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
        self.sur_light.fill((255,255,255))
        self.sur_shadow = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()

    def flash(self,amount):
        self.add_flare(Flare(amount,5))

    def add_flare(self,flare):
        self.flares.append(flare)

    def blit(self,target):
        brightness = 0
        for flare in self.flares:
            if flare.brightness > 0:
                brightness += flare.brightness
                flare.cool()
            else:
                self.flares.remove(flare)
        light = min(255,int(brightness))
        shadow = 255-light

        self.sur_shadow.set_alpha(shadow)
        target.blit(self.sur_shadow,(0,0))
        self.sur_light.set_alpha(light)
        target.blit(self.sur_light,(0,0))  


class Main(object):
    score = 0

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption('Schlagschatten')
        self.font = pygame.font.Font(None,20)
        self.display = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT),pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.tick = 0
        self.shutdown_tick = 0
        self.background = Background()
        self.lighting = Lighting()
        self.player = Player()
        self.player.move(SCREEN_WIDTH/2,SCREEN_HEIGHT*0.7)
        self.enemies = []
        self.shots = []
        self.play_music()

    def play_music(self):
        files = ['Commando.sid','After_the_War.sid']
        file = MUSIC_DIR+'/'+files[1]
        command = "sidplay2 >/dev/null 2>/dev/null %s" % file
        self.sidplay = subprocess.Popen("exec " + command, shell=True)

    def shutdown_in(self,frames):
        self.shutdown_tick = self.tick + frames

    def shutdown(self):
        self.running = False
        self.sidplay.terminate()
        pygame.mixer.quit()

    def run(self):
        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.shutdown()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.shutdown()
                    elif not self.player.dead:
                        self.player.key_down(event.key)
            self.logic()
            self.tick += 1
            self.clock.tick(self.fps)
            
            self.screen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
            self.draw()
            self.screen = pygame.transform.scale(self.screen,(DISPLAY_WIDTH,DISPLAY_HEIGHT))
            self.display.blit(self.screen,(0,0))
            pygame.display.flip()

            if self.shutdown_tick > 0 and self.tick > self.shutdown_tick:
                self.shutdown()

    def logic(self):
        max_enemies = 7
        if len(self.enemies) < max_enemies:
            enemy_appear_chance = 0.15 * 0.5**len(self.enemies)
            if uniform(0,1) <= enemy_appear_chance:
               enemy = EnemyOne()
               enemy.move_to(randint(0,SCREEN_WIDTH-1),-enemy.h)
               self.enemies.append(enemy)

        if not self.player.dead:
            for shot in self.shots:
                if shot.enemy:
                    shot.collide(self.player.box)
                else:
                    for enemy in self.enemies:
                        shot.collide(enemy)
            for enemy in self.enemies:
                enemy.collide(self.player.box)

        for shot in self.shots:
            shot.logic()
        for enemy in self.enemies:
            enemy.logic()

        if not self.player.dead:
            self.player.poll_keys()

    def draw(self):
        self.background.blit(self.screen)
        for enemy in self.enemies:
            enemy.blit(self.screen)
        if not self.player.dead:
            self.player.blit(self.screen)
        for shot in self.shots:
            shot.blit(self.screen)
        self.lighting.blit(self.screen)
        text = self.font.render("%s" % self.score, True, (255,255,255))
        self.screen.blit(text,(4,4))
#        self.screen.blit(text,(SREEN_WIDTH-128,16))


main = Main()
main.run()
