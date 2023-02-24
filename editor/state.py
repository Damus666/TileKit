from pygameUI import pygameUI

class State:
    def __init__(self,app,manager):
        self.app = app
        self.manager:pygameUI.UIManager = manager
        self.manager.window_container._shape_renderer.only_outline = True
        
    def event(self,e):
        pass
    
    def render(self,screen):
        pass
    
    def update(self):
        pass