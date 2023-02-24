import pygame
from .settings import *

class TileData:
    def __init__(self,id,type,path,basename):
        self.id = id
        self.type = type
        self.pathname = basename
        self.sprite = pygame.image.load(path).convert_alpha()

class Tile:
    def __init__(self,id,sprite,type,position,camera):
        self.camera = camera
        self.id = id
        self.type = type
        self.sprite = sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.spriteScaled = self.sprite
        self.position = pygame.Vector2(position)
        self.visible = True
        self.rect = self.sprite.get_rect()
        self.x = 0
        self.y = 0
        if type == "object":
            self.position.x -= self.width/2
            self.position.y -= self.height/2
        
    def refresh(self):
        self.spriteScaled = pygame.transform.scale(self.sprite,(self.width*self.camera.zoom,
                                                                self.height*self.camera.zoom))
        self.rect = self.spriteScaled.get_rect()
        
    def check_visibility(self):
        dx = self.position.x-self.camera.position.x
        dy = self.position.y-self.camera.position.y
        self.x = ((self.position.x-self.camera.left())+((dx*self.camera.zoom)-dx))
        self.y = ((self.position.y-self.camera.top())+((dy*self.camera.zoom)-dy))
        self.rect.topleft = (self.x,self.y)
        self.visible = TILE_CHECK_RECT.colliderect(self.rect)
    
    def render(self,screen):
        screen.blit(self.spriteScaled,self.rect)