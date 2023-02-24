import pygame,os,shutil
from pygameUI import pygameUI
from .state import State
from .settings import *
import json

class Menu(State):
    def __init__(self,app,manager):
        super().__init__(app,manager)
        
        self.project_list = pygameUI.UISelectionList(PROJECT_LIST_RECT,self.manager,[])
        self.title = pygameUI.UILabel(MENU_TITLE_RECT,self.manager,"Projects",id="menu_title")
        self.create_btn = pygameUI.UIButton(M_CREATEBTN_RECT,self.manager,text="Create New",id="menu_create")
        self.open_btn = pygameUI.UIButton(M_OPENBTN_RECT,self.manager,text="Open Selected",id="menu_open")
        self.delete_btn = pygameUI.UIButton(M_DELETEBTN_RECT,self.manager,text="Delete Selected",id="menu_delete")
        self.quit_btn = pygameUI.UIButton(M_QUITBTN_RECT,self.manager,text="Quit",id="menu_quit")
        
        self.has_window = False
        
    def load(self):
        with open(PROJECTS_NAMES_FILE,"r") as file:
            j = json.load(file)
            names = j["projects"]
            self.project_list.set_item_list(names)
        
    def event(self,e:pygame.event.Event):
        if e.type == pygameUI.BUTTON_PRESSED:
            if e.element_ID == "menu_quit":
                self.app.quit()
            elif e.element_ID == "menu_create":
                self.create_window()
            elif e.element_ID == "menu_open":
                self.open()
            elif e.element_ID == "menu_win_cancel":
                self.has_window = False
                self.window.destroy()
            elif e.element_ID == "menu_win_create":
                self.create()
            elif e.element_ID == "menu_delete":
                self.delete()
        elif e.type == pygameUI.WINDOW_CLOSED:
            self.has_window = False
                
    def create_window(self):
        if not self.has_window:
            window = pygameUI.UIWindow(M_NEWPROJECT_WIN_RECT,self.manager,"Create New Project")
            self.has_window = True
            self.window = window
            
            cont = window.get_container()
            w_name_label = pygameUI.UILabel(MWIN_NAMELABEL_RECT,self.manager,"Name:",cont)
            w_name_entry = pygameUI.UIEntryLine(MWIN_NAMENTRY_RECT,self.manager,cont)
            w_tilesize_label = pygameUI.UILabel(MWIN_TILESIZELABEL_RECT,self.manager,"Tile Size:",cont)
            w_tilesize_entry = pygameUI.UIEntryLine(MWIN_TILESIZEENTRY_RECT,self.manager,cont)
            w_mapsize_label = pygameUI.UILabel(MWIN_MAPSIZELABEL_RECT,self.manager,"Map Size:",cont)
            w_mapsizex_entry = pygameUI.UIEntryLine(MWIN_MAPSIZEENTRYX_RECT,self.manager,cont)
            w_mapsizey_entry = pygameUI.UIEntryLine(MWIN_MAPSIZEWNTRYY_RECT,self.manager,cont)
            w_cancel_btn = pygameUI.UIButton(MWIN_CANCELBTN_RECT,self.manager,cont,"Cancel",id="menu_win_cancel")
            w_create_btn = pygameUI.UIButton(MWIN_CREATEBTN_RECT,self.manager,cont,"Create",id="menu_win_create")
            self.inputs:dict[str,pygameUI.UIEntryLine] = {
                "name":w_name_entry,
                "tilesize":w_tilesize_entry,
                "mapsize":{"x":w_mapsizex_entry,"y":w_mapsizey_entry}
            }
    
    def open(self):
        if not self.has_window:
            txt = self.project_list.get_selection()
            if txt:
                self.app.change_state(1,txt)
                
    def create(self):
        t = self.inputs["name"].get_text()
        name = t if t else "UnnamedProject"
        if name in self.project_list._items_list:
            return
        else:
            t = self.inputs["tilesize"].get_text()
            try:
                tilesize = int(t) if t else 16
            except:
                return
            t = self.inputs["mapsize"]["x"].get_text()
            try:
                mapsizex = int(t) if t else 64
            except:
                return
            t = self.inputs["mapsize"]["y"].get_text()
            try:
                mapsizey = int(t) if t else 32
            except:
                return
            newlist = self.project_list._items_list.copy()
            newlist.append(name)
            self.project_list.set_item_list(newlist)
            
            os.mkdir(DATA_FILE+name)
            
            settingsdict = {
                "tilesize":tilesize,
                "mapsize":{
                    "x":mapsizex,
                    "y":mapsizey
                }
            }
            
            with open(DATA_FILE+name+"/"+"settings"+DOTJSON,"w") as file:
                json.dump(settingsdict,file)
                
            layersdict = {"layers":[]}
            
            with open(DATA_FILE+name+"/"+"layers"+DOTJSON,"w") as file:
                json.dump(layersdict,file)
                
            tilesdict = {"tiles":[]}
            
            with open(DATA_FILE+name+"/"+"tiles"+DOTJSON,"w") as file:
                json.dump(tilesdict,file)
                
            os.mkdir(DATA_FILE+name+"/images")
            os.mkdir(DATA_FILE+name+"/exports")
                
            self.window.destroy()
            self.has_window = False
    
    def save(self):
        projectnamesdict = {"projects":self.project_list._items_list}
        with open(PROJECTS_NAMES_FILE,"w") as file:
            json.dump(projectnamesdict,file)
            
    def delete(self):
        if not self.has_window:
            selected = self.project_list.get_selection()
            if selected:
                oldlist = self.project_list._items_list.copy()
                oldlist.remove(selected)
                self.project_list.set_item_list(oldlist)
                
                try:
                    shutil.rmtree(DATA_FILE+selected)
                except Exception as e:
                    print(f"[ERROR]: CANNOT DELETE {selected}: '{e}'")