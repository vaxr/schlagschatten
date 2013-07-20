#!/usr/bin/env python2

#import sys
import pygame
from random import randint


FPS = 30
ZOOM = 4
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 180
DISPLAY_WIDTH = SCREEN_WIDTH * ZOOM
DISPLAY_HEIGHT = SCREEN_HEIGHT * ZOOM



class Ship(object):
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

    def move_to(self,x,y):
        if (x < 0):
            x = 0
        elif (x > SCREEN_WIDTH - self.w):
            x = SCREEN_WIDTH - self.w
        if (y < 0):
            y = 0
        elif (y > SCREEN_HEIGHT - self.h):
            y = SCREEN_HEIGHT - self.h
        self.x = x
        self.y = y


class Player(Ship):
    def __init__(self):
        super(Player,self).__init__('gfx/player.png')     

    def poll_keys(self):
        speed = 3
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_DOWN]:
            dy += speed
        self.move(dx,dy)
        
    def key_pushed(self,key):
        if key == pygame.K_LEFT:
            self.move(-1,0)
        elif key == pygame.K_RIGHT:
            self.move(1,0)
        elif key == pygame.K_UP:
            self.move(0,-1)
        elif key == pygame.K_DOWN:
            self.move(0,1)


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


class Main(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Schlagschatten')
        self.display = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT),pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = FPS

        self.background = Background()
        self.player = Player()


    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            self.player.poll_keys()
            self.clock.tick(self.fps)
            pygame.display.flip()
            
            self.screen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
            self.draw()
            self.screen = pygame.transform.scale(self.screen,(DISPLAY_WIDTH,DISPLAY_HEIGHT))
            self.display.blit(self.screen,(0,0))

    def draw(self):
        self.background.blit(self.screen)
        self.player.blit(self.screen)


Main().run()
