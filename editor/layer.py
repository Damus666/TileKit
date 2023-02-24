from .tile  import Tile
from .settings import *

class Layer:
    def __init__(self,name,visible):
        self.name = name
        self.visible = visible
        self.tiles:list[Tile] = list()
        
    def render(self,screen):
        for t in self.tiles:
            t.check_visibility()
            if t.visible:
                t.render(screen)
                
    def sort(self):
        tiles = list()
        objs = list()
        for t in self.tiles:
            if t.type == "tile":
                tiles.append(t)
            elif t.type == "object":
                objs.append(t)
        self.tiles = tiles.copy()
        self.tiles.extend(objs)
                
    def add_tile(self,tile):
        self.tiles.append(tile)
        self.sort()
        
    def remove_tile(self,tile):
        self.tiles.remove(tile)
        self.sort()
    
    def save(self,map_size,tile_size,pname):
        surface = pygame.Surface((int(map_size.x*tile_size),int(map_size.y*tile_size)),pygame.SRCALPHA).convert_alpha()
        #surface.fill(0)
        for tile in self.tiles:
            surface.blit(tile.sprite,tile.position)
        pygame.image.save(surface,DATA_FILE+pname+"/exports/"+self.name+".png")
