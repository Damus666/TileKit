import pygame
from .camera import Camera
from .settings import *

class Scene:
    def __init__(self,editor):
        self.editor = editor
        self.surface = pygame.Surface((SCENE_VIEW_RECT.w,SCENE_VIEW_RECT.h))
        self.camera = Camera(self)
        
    def finish(self):
        self.mapxrange = range(int(self.editor.map_size.x)+1)
        self.mapyrange = range(int(self.editor.map_size.y)+1)
        self.camera.finish()
        
    def event(self,e):
        self.camera.event(e)
        
    def refresh(self):
        for layer in self.editor.layers:
            for tile in layer.tiles:
                tile.refresh()
    
    def render(self,screen,layers):
        self.surface.fill("black")
        self.render_grid()
        for layer in layers:
            if layer.visible:
                layer.render(self.surface)
        screen.blit(self.surface,SCENE_VIEW_RECT)
        
    def render_grid(self):
        zoom = self.camera.zoom
        sy1,sy2 = 0,self.editor.map_size.y*self.editor.tile_size
        sx1,sx2 = 0,self.editor.map_size.x*self.editor.tile_size
        
        for ox in self.mapxrange:
            
            sx = ox*self.editor.tile_size
            dx = sx-self.camera.position.x
            dy1,dy2 = sy1-self.camera.position.y,sy2-self.camera.position.y
            fx = int((sx-self.camera.left())+((dx*zoom)-dx))
            fy1,fy2 = int((sy1-self.camera.top())+((dy1*zoom)-dy1)),int((sy2-self.camera.top())+((dy2*zoom)-dy2))
            if fx >= 0 and fx <= TILE_CHECK_RECT.w:
                pygame.draw.line(self.surface,GRID_COL,(fx,fy1),(fx,fy2),int(max(GRID_SIZE*self.camera.zoom,1)))
                
        for oy in self.mapyrange:
            
            sy = oy*self.editor.tile_size
            dy = sy-self.camera.position.y
            dx1,dx2 = sx1-self.camera.position.x,sx2-self.camera.position.x
            fy = int((sy-self.camera.top())+((dy*zoom)-dy))
            fx1,fx2 = int((sx1-self.camera.left())+((dx1*zoom)-dx1)),int((sx2-self.camera.left())+((dx2*zoom)-dx2))
            if fy >= 0 and fy <= TILE_CHECK_RECT.h:
                pygame.draw.line(self.surface,GRID_COL,(fx1,fy),(fx2,fy),int(max(GRID_SIZE*self.camera.zoom,1)))