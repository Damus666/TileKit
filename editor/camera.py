from pygame.math import Vector2
import pygame
from .settings import *

class Camera:
    def __init__(self,scene):
        self.scene = scene
        self.position = Vector2()
        self.zoom = 1
        self.maxpos = Vector2()
        
    def finish(self):
        self.position = Vector2(self.scene.editor.map_size.x/2*self.scene.editor.tile_size,self.scene.editor.map_size.y/2*self.scene.editor.tile_size)
        self.zoom = 1
        self.maxpos.x = self.scene.editor.map_size.x*self.scene.editor.tile_size
        self.maxpos.y = self.scene.editor.map_size.y*self.scene.editor.tile_size
        
    def realleft(self):
        return self.position.x - (SCENE_VIEW_RECT.w/self.zoom)*0.5
    
    def realtop(self):
        return self.position.y - (SCENE_VIEW_RECT.h/self.zoom)*0.5
    
    def left(self):
        return self.position.x-SCENE_VIEW_CENTER.x
    
    def top(self):
        return self.position.y-SCENE_VIEW_CENTER.y
    
    def event(self,e):
        if e.type == pygame.MOUSEWHEEL:
            self.zoom += (e.y*0.05)*self.zoom
            if self.zoom < 0.2:
                self.zoom = 0.2
            elif self.zoom > 10:
                self.zoom = 10
            self.scene.refresh()
        elif e.type == pygame.MOUSEMOTION:
            m = pygame.mouse.get_pressed()
            if m[1]:
                self.position -= Vector2(e.rel)/self.zoom
                if self.position.x > self.maxpos.x:
                    self.position.x = self.maxpos.x
                if self.position.x < 0:
                    self.position.x = 0
                if self.position.y > self.maxpos.y:
                    self.position.y = self.maxpos.y
                if self.position.y < 0:
                    self.position.y = 0
                
    def screen_to_world(self,point:pygame.Vector2)->pygame.Vector2:
        """Project a point on the screen to a point in the world."""
        return pygame.Vector2(((point[0]/self.zoom)+self.realleft()),((point[1]/self.zoom)+self.realtop()))
    
    def world_to_screen(self,point:pygame.Vector2)->pygame.Vector2:
        """Inverse of 'ScreenToWorld'."""
        return pygame.Vector2(((point[0]/self.zoom)-self.realleft()),((point[1]/self.zoom)-self.realtop()))