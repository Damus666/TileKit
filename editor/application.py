import pygame,sys
from pygameUI import pygameUI
from .settings import *
from .menu import Menu
from .state import State
from .editor import Editor

class Application:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SIZES)
        self.clock = pygame.time.Clock()
        self.menu_manager = pygameUI.UIManager(SIZES,True,settings=PYGAMEUI_SETTINGS)
        self.editor_manager = pygameUI.UIManager(SIZES,False,settings=PYGAMEUI_SETTINGS)
        self.menu = Menu(self,self.menu_manager)
        self.editor = Editor(self,self.editor_manager)
        self.state_index = 0
        self.state:State = self.menu
        
    def change_state(self,index,name):
        if index == 1:
            self.editor.load(name)
            self.state_index = index
            self.state = self.editor
        elif index == 0:
            self.editor.unload()
            self.state_index = index
            self.state = self.menu
    
    def awake(self):
        self.menu.load()
    
    def update(self):
        self.state.manager.update_ui(1)
        self.state.update()
    
    def events(self):
        self.clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.quit()
            self.state.event(e)
            self.state.manager.handle_events(e)
    
    def render(self):
        self.screen.fill(BG_COL)
        self.state.render(self.screen)
        self.state.manager.draw_ui(self.screen)
        pygame.display.update()
    
    def quit(self):
        self.menu.save()
        pygame.quit()
        sys.exit()
    
    def run(self):
        while True:
            self.events()
            self.update()
            self.render()