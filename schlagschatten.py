#!/usr/bin/env python2

#import sys
import pygame


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

    def key_pushed(self,key):
        dx = 0
        dy = 0
        if key == pygame.K_LEFT:
            self.move(-1,0)
        elif key == pygame.K_RIGHT:
            self.move(1,0)
        elif key == pygame.K_UP:
            self.move(0,-1)
        elif key == pygame.K_DOWN:
            self.move(0,1)


class Main(object):
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Schlagschatten')
        self.display = pygame.display.set_mode((DISPLAY_WIDTH,DISPLAY_HEIGHT),pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()
        self.fps = FPS
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
                    else:
                        self.player.key_pushed(event.key)
            self.clock.tick(self.fps)
            pygame.display.flip()
            
            self.screen = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
            self.draw()
            self.screen = pygame.transform.scale(self.screen,(DISPLAY_WIDTH,DISPLAY_HEIGHT))
            self.display.blit(self.screen,(0,0))

    def draw(self):
        self.screen.fill((255,0,0))
        self.player.blit(self.screen)


Main().run()
