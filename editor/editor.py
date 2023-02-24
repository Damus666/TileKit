from .state import State
import pygame,json,os,ntpath
from .layer import Layer
from .tile import Tile,TileData
from .camera import Camera
from .scene import Scene
from pygameUI import pygameUI
from .settings import *

class Editor(State):
    def __init__(self,app,manager):
        super().__init__(app,manager)
        
        # ICONS
        
        icons_names = ["downarrow","uparrow","paint","erase","move","eye","plus","save","bin"]
        self.icons = {name:pygame.image.load("assets/"+name+".png").convert_alpha() for name in icons_names}
        
        # UI
        
        self.topbar_cont = pygameUI.UIContainer(TOPBAR_RECT,self.manager,colored=True)
        self.topbar_cont._shape_renderer.only_outline = True
        self.quit_btn = pygameUI.UIButton(QUITBTN_RECT,self.manager,text="Quit",id="quit")
        self.savequit_btn = pygameUI.UIButton(SAVEQUITBTN_RECT,self.manager,text="Save & Quit",id="save_quit")
        self.menu_btn = pygameUI.UIButton(MENUBTN_RECT,self.manager,text="Menu",id="menu")
        self.save_btn = pygameUI.UIButton(SAVEBTN_RECT,self.manager,text="Save",id="save")
        
        self.options_cont = pygameUI.UIContainer(LEFTCONT_RECT,self.manager,colored=True)
        self.options_cont._shape_renderer.only_outline = True
        
        self.layervisibility_image = pygameUI.UIImage(LAYERBTNS_RECTS["visibility"],self.manager,self.icons["eye"],self.options_cont,id="layer_visibility")
        self.layerup_image = pygameUI.UIImage(LAYERBTNS_RECTS["up"],self.manager,self.icons["uparrow"],self.options_cont,id="layer_up")
        self.layerdown_image = pygameUI.UIImage(LAYERBTNS_RECTS["down"],self.manager,self.icons["downarrow"],self.options_cont,id="layer_down")
        self.layersave_image = pygameUI.UIImage(LAYERBTNS_RECTS["save"],self.manager,self.icons["save"],self.options_cont,id="layer_save")
        self.layerplus_image = pygameUI.UIImage(LAYERBTNS_RECTS["plus"],self.manager,self.icons["plus"],self.options_cont,id="layer_plus")
        self.layerdelete_image = pygameUI.UIImage(LAYERBTNS_RECTS["delete"],self.manager,self.icons["bin"],self.options_cont,id="layer_delete")
        
        self.layerslist = pygameUI.UISelectionList(LAYERLIST_RECT,self.manager,[],container=self.options_cont,id="layers_list")
        self.createlayer_entry = pygameUI.UIEntryLine(CREATELAYERENTRY_RECT,self.manager,visible=False)
        self.createlayer_btn = pygameUI.UIButton(CREATELAYERBTN_RECT,self.manager,text="Create Layer",id="create_layer",visible=False)
        
        self.lil_cont = pygameUI.UIContainer(LILCONT_RECT,self.manager,colored=True)
        self.selectedlayer_label = pygameUI.UILabel(SELECTEDLAYERLABEL_RECT,self.manager,"No Layer Selected",id="selected")
        self.selectedmode_label = pygameUI.UILabel(MODESELECTEDLABEL_RECT,self.manager,"Mode Selected: Tiles",id="selected")
        self.selected_label = pygameUI.UILabel(SELECTEDLABEL_RECT,self.manager,"Selected: Nothing",id="selected")
        self.selectedtool_label = pygameUI.UILabel(SELECTEDTOOLLABEL_RECT,self.manager,"Selected: Paint",id="selected")
        
        self.tools_cont = pygameUI.UIContainer(TOOLSCONT_RECT,self.manager,colored=True)
        self.painttool_img = pygameUI.UIImage(TOOLIMAGES_RECTS["paint"],self.manager,self.icons["paint"],self.tools_cont,id="tool_paint")
        self.erasetool_img = pygameUI.UIImage(TOOLIMAGES_RECTS["erase"],self.manager,self.icons["erase"],self.tools_cont,id="tool_erase")
        self.movetool_img = pygameUI.UIImage(TOOLIMAGES_RECTS["move"],self.manager,self.icons["move"],self.tools_cont,id="tool_move")
        
        self.addimage_entry = pygameUI.UIEntryLine(ADDIMAGEENTRY_RECT,self.manager,visible=False)
        self.addimage_btn = pygameUI.UIButton(ADDIMAGEBTN_RECT,self.manager,text="Add Image",id="add_image",visible=False)
        self.tiles_btn = pygameUI.UIButton(TILESBTN_RECT,self.manager,self.options_cont,"Tiles",id="select_tiles")
        self.objects_btn = pygameUI.UIButton(OBJSBTN_RECT,self.manager,self.options_cont,"Objects",id="select_objects")
        self.addimage_img = pygameUI.UIImage(ADDIMAGEIMG_RECT,self.manager,self.icons["plus"],self.options_cont,id="toggle_add_image")
        self.tiles_cont = pygameUI.UIScrollableContainer(TILESCONT_RECT,self.manager,self.options_cont,True)
        self.tiles_cont._shape_renderer.only_outline = True
        self.objects_cont = pygameUI.UIScrollableContainer(OBJSCONT_RECT,self.manager,self.options_cont,True,False)
        self.objects_cont._shape_renderer.only_outline = True
        scrolltiles = pygameUI.UIVerticalScrollbar(TILESCONTSCROLLBAR_RECT,self.manager,self.tiles_cont)
        self.tiles_cont.set_vertical_scrollbar(scrolltiles)
        scrollobjs = pygameUI.UIVerticalScrollbar(OBJSCONTSCROLLBAR_RECT,self.manager,self.objects_cont)
        self.objects_cont.set_vertical_scrollbar(scrollobjs)
        
        self.exportas_btn = pygameUI.UIButton(EXPORTDROPDOWN_RECT,self.manager,text="Export",id="export_as")
        
        # CORE

        self.toolidnames = {0:"Paint",1:"Erase",2:"Move",3:"Info"}
        self.mode = 0
        self.tool = 0
        self.was_pressing = False
        self.scene = Scene(self)
        self.layers:list[Layer] = list()
        self.tile_size = 0
        self.map_size = pygame.Vector2()
        self.tilesdata:list[TileData] = list()
        self.selected_layer:Layer = None
        self.selected_tiledata:TileData = None
        self.selected_obj:Tile = None
        self.tileimages = list()
        self.objsimages = list()
        self.lastobj = 0
        self.cooldown = 100
        
    def export(self):
        savedict = {
            "settings":{
                "tile_size":self.tile_size,
                "map_size":[int(self.map_size.x),int(self.map_size.y)]
            },
            "tiles":[
                {
                    "id":t.id,
                    "path":t.pathname,
                    "type":t.type    
                } for t in self.tilesdata
            ],
            "layers":[
                {
                    "name":l.name,
                    "visible":l.visible,
                    "tiles":[
                        {
                            "id":t.id,
                            "position":[t.position.x,t.position.y]
                        } for t in l.tiles
                    ]
                } for l in self.layers
            ]
        }
        
        with open(DATA_FILE+self.name+"/exports/"+self.name+DOTJSON,"w") as file:
            json.dump(savedict,file)
        
    def load(self,name):
        self.name = name
        with open(DATA_FILE+self.name+"/settings"+DOTJSON,"r") as file:
            data =  json.load(file)
            self.tile_size = data["tilesize"]
            self.map_size.x = data["mapsize"]["x"]
            self.map_size.y = data["mapsize"]["y"]
        with open(DATA_FILE+self.name+"/tiles"+DOTJSON,"r") as file:
            data = json.load(file)
            for t in data["tiles"]:
                self.tilesdata.append(TileData(t["id"],t["type"],DATA_FILE+self.name+"/images/"+t["path"],t["path"]))
        with open(DATA_FILE+self.name+"/layers"+DOTJSON,"r") as file:
            data = json.load(file)
            for l in data["layers"]:
                layer = Layer(l["name"],l["visible"])
                for t in l["tiles"]:
                    sprite,type = self.get_tiledata(t["id"])
                    pos = pygame.Vector2(t["position"][0],t["position"][1])
                    tile = Tile(t["id"],sprite,type,pos,self.scene.camera)
                    layer.add_tile(tile)
                self.layers.append(layer)
        
        if len(self.layers) > 0:
            self.selected_layer = self.layers[0]
            self.refresh_selected_layer()
            
        if len(self.tilesdata)>0:
            self.selected_tiledata = self.tilesdata[0]
            self.refresh_selection()
                
        self.refresh_layers()
        self.scene.finish()
        self.refresh_images()
        self.refresh_selected_tool()
        
    def unload(self):
        for l in self.layers:
            for t in l.tiles:
                del t
            l.tiles.clear()
        self.layers.clear()
        for t in self.tilesdata:
            del t
        self.tilesdata.clear()
                
    def get_tiledata(self,id):
        for t in self.tilesdata:
            if t.id == id:
                return t.sprite,t.type
            
    def get_tiledata_really(self,id):
        for t in self.tilesdata:
            if t.id == id:
                return t
    
    def save(self):
        tiledatadict = {
            "tiles":[
                {
                    "id":t.id,
                    "path":t.pathname,
                    "type":t.type    
                } for t in self.tilesdata
            ]
        }
        layersdatadict = {
            "layers":[
                {
                    "name":l.name,
                    "visible":l.visible,
                    "tiles":[
                        {
                            "id":t.id,
                            "position":[t.position.x,t.position.y]
                        } for t in l.tiles
                    ]
                } for l in self.layers
            ]
        }
        with open(DATA_FILE+self.name+"/tiles"+DOTJSON,"w") as file:
            json.dump(tiledatadict,file)
        with open(DATA_FILE+self.name+"/layers"+DOTJSON,"w") as file:
            json.dump(layersdatadict,file)
    
    def render(self,screen):
        self.scene.render(screen,self.layers)
        
    def update(self):
        mouse = pygame.mouse.get_pressed()
        pos = pygame.mouse.get_pos()
        pos = (pos[0]-SCENE_VIEW_POS.x,pos[1]-SCENE_VIEW_POS.y)
        if self.tool == 0:
            self.update_0(mouse,pos)
        elif self.tool == 1:
            self.update_1(mouse,pos)
        elif self.tool == 2:
            self.update_2(mouse,pos)
        elif self.tool == 3:
            self.update_3(mouse,pos)
                                
    def update_0(self,mouse,pos):
        if mouse[0]:
            realpos = self.scene.camera.screen_to_world(pos)
            found = False
            if realpos.x < 0 or realpos.x > self.map_size.x*self.tile_size or realpos.y < 0 or realpos.y > self.map_size.y*self.tile_size:
                return
            if self.selected_layer and self.selected_tiledata:
                toremove = []
                toadd = []
                for tile in self.selected_layer.tiles:
                    if tile.rect.collidepoint(pos):
                        if self.mode == 0 and tile.type == "tile":
                            found = True
                            if tile.id != self.selected_tiledata.id:
                                oldpos = tile.position
                                toremove.append(tile)
                                newtile = Tile(self.selected_tiledata.id,self.selected_tiledata.sprite,self.selected_tiledata.sprite,oldpos,self.scene.camera)
                                newtile.refresh()
                                toadd.append(newtile)
                            
                for t in toremove:
                    self.selected_layer.remove_tile(t)
                for t in toadd:
                    self.selected_layer.add_tile(t)
                if not found:
                    if self.mode == 1:
                        if pygame.time.get_ticks()-self.lastobj > self.cooldown:
                            new = Tile(self.selected_tiledata.id,self.selected_tiledata.sprite,self.selected_tiledata.type,realpos,self.scene.camera)
                            new.refresh()
                            self.selected_layer.add_tile(new)
                            self.lastobj = pygame.time.get_ticks()
                    else:
                        newpos = (realpos.x-(realpos.x%self.tile_size),realpos.y-(realpos.y%self.tile_size))
                        new = Tile(self.selected_tiledata.id,self.selected_tiledata.sprite,self.selected_tiledata.type,newpos,self.scene.camera)
                        new.refresh()
                        self.selected_layer.add_tile(new)
    
    def update_1(self,mouse,pos):
        if mouse[0]:
            if self.mode == 1:
                if pygame.time.get_ticks()-self.lastobj <= self.cooldown:
                    return
            if self.selected_layer:
                toremove = []
                for tile in self.selected_layer.tiles:
                    if tile.rect.collidepoint(pos):
                        if self.mode == 1:
                            self.lastobj = pygame.time.get_ticks()
                        toremove.append(tile)
                        break
                for t in toremove:
                    self.selected_layer.remove_tile(t)
    
    def update_2(self,mouse,pos):
        if mouse[0]:
            if not self.was_pressing:
                self.was_pressing = True
                if self.selected_layer:
                    for tile in self.selected_layer.tiles:
                        if tile.rect.collidepoint(pos) and tile.type == "object":
                            self.selected_obj = tile
        else:
            self.was_pressing = False
            self.selected_obj = None
    
    def update_3(self,mouse,pos):
        pass
        
    def event(self,e):
        self.scene.event(e)
        if e.type == pygameUI.BUTTON_PRESSED:
            # TOPBAR BUTTONS
            
            if e.element_ID == "quit":
                self.app.quit()
            elif e.element_ID == "save_quit":
                self.save()
                self.app.quit()
            elif e.element_ID == "menu":
                self.save()
                self.app.change_state(0,"none")
            elif e.element_ID == "save":
                self.save()
            elif e.element_ID == "export_as":
                self.export()
                
            # LAYER BUTTONS
            
            elif e.element_ID == "create_layer":
                self.layer_create()
            
            # TILE OBJ
                
            elif e.element_ID == "select_tiles":
                self.change_selection(0)
            elif e.element_ID == "select_objects":
                self.change_selection(1)
            elif e.element_ID == "add_image":
                self.add_image()
                
        elif e.type == pygameUI.SELECTION_CHANGED:
            
            # SELECT LAYER
            
            if e.element_ID == "layers_list":
                index,self.selected_layer = self.get_layer(e.new_selection)
                self.refresh_selected_layer()
        elif e.type == pygameUI.ELEMENT_PRESSED:
            
            # IMAGE SELECTION
            if e.element_ID.startswith("tile_image_"):
                id = int(e.element_ID.replace("tile_image_",""))
                self.selected_tiledata = self.get_tiledata_really(id)
                self.refresh_selection()
            elif e.element_ID.startswith("object_image_"):
                id = int(e.element_ID.replace("object_image_",""))
                self.selected_tiledata = self.get_tiledata_really(id)
                self.refresh_selection()
                
            # TOOL SELECTION
            elif e.element_ID == "tool_paint":
                self.select_tool(0)
            elif e.element_ID == "tool_erase":
                self.select_tool(1)
            elif e.element_ID == "tool_move":
                self.select_tool(2)
            
            # IMAGE TOGGLE
            elif e.element_ID == "toggle_add_image":
                self.image_toggle_create()
            
            # LAYER IMG BUTTONS
            elif e.element_ID == "layer_visibility":
                self.layer_toggle()
            elif e.element_ID == "layer_delete":
                self.layer_delete()
            elif e.element_ID == "layer_up":
                self.layer_up()
            elif e.element_ID == "layer_down":
                self.layer_down()
            elif e.element_ID == "layer_save":
                self.layer_save()
            elif e.element_ID == "layer_plus":
                self.layer_toggle_create()
                
            
        elif e.type == pygame.MOUSEMOTION:
            # MOVE OBJECT
            
            if self.tool == 2:
                if self.selected_obj:
                    self.selected_obj.position += Vector2(e.rel)/self.scene.camera.zoom
                    if self.selected_obj.position.x < 0-self.selected_obj.width*0.5:
                        self.selected_obj.position.x = 0-self.selected_obj.width*0.5
                    elif self.selected_obj.position.x > self.map_size.x*self.tile_size-self.selected_obj.width*0.5:
                        self.selected_obj.position.x = self.map_size.x*self.tile_size-self.selected_obj.width*0.5
                    if self.selected_obj.position.y < 0-self.selected_obj.height*0.5:
                        self.selected_obj.position.y = 0-self.selected_obj.height*0.5
                    elif self.selected_obj.position.y > self.map_size.y*self.tile_size-self.selected_obj.height*0.5:
                        self.selected_obj.position.y = self.map_size.y*self.tile_size-self.selected_obj.height*0.5
        
        # SHORTCUTS
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_p:
                self.select_tool(0)
            elif e.key == pygame.K_e:
                self.select_tool(1)
            elif e.key == pygame.K_m:
                self.select_tool(2)
                        
    def select_tool(self,tool):
        self.tool = tool
        self.refresh_selected_tool()
                
    def add_image(self):
        path = self.addimage_entry.get_text().strip()
        if path:
            if os.path.exists(path):
                if os.path.isfile(path):
                    filename = ntpath.basename(path)
                    type = "tile" if self.mode == 0 else "object"
                    for td in self.tilesdata:
                        if td.pathname == filename and td.type == type:
                            return
                    sprite = pygame.image.load(path).convert_alpha()
                    pygame.image.save(sprite,DATA_FILE+self.name+"/images/"+filename)
                    tildata = TileData(self.get_available_id(),type,DATA_FILE+self.name+"/images/"+filename,filename)
                    self.tilesdata.append(tildata)
                    self.addimage_entry.set_text("")
                    self.refresh_images()
        self.image_toggle_create(True)
                    
    def refresh_selection(self):
        if self.selected_tiledata:
            self.selected_label.set_text("Selected: "+self.selected_tiledata.pathname.replace(".png","").replace(".jpg","")+", "+str(self.selected_tiledata.id))
        else:
            self.selected_label.set_text("Selected: Nothing")
                    
    def get_available_id(self):
        ids = list()
        for td in self.tilesdata:
            ids.append(td.id)
        num = 0
        while num in ids:
            num += 1
        return num
    
    def refresh_images(self):
        listtouse = self.tileimages if self.mode == 0 else self.objsimages
        for img in listtouse:
            img.destroy()
        if self.mode == 0:
            row = 0
            col = 0
            for td in self.tilesdata:
                if td.type == "tile":
                    if col == MAXIMGS:
                        col = 0
                        row += 1
                    rect = pygame.Rect(S+S*col+IMAGE_SIZES.x*col,S+S*row+IMAGE_SIZES.y*row,IMAGE_SIZES.x,IMAGE_SIZES.y)
                    img = pygameUI.UIImage(rect,self.manager,td.sprite,self.tiles_cont,id="tile_image_"+str(td.id))
                    self.tileimages.append(img)
                    col += 1
        elif self.mode == 1:
            row = 0
            col = 0
            for td in self.tilesdata:
                if td.type == "object":
                    if col == MAXIMGS:
                        col = 0
                        row += 1
                    rect = pygame.Rect(S+S*col+IMAGE_SIZES.x*col,S+S*row+IMAGE_SIZES.y*row,IMAGE_SIZES.x,IMAGE_SIZES.y)
                    img = pygameUI.UIImage(rect,self.manager,td.sprite,self.objects_cont,id="object_image_"+str(td.id))
                    self.objsimages.append(img)
                    col += 1
    
    def change_selection(self,mode):
        self.mode = mode
        if self.mode == 0:
            self.objects_cont.visible = False
            self.tiles_cont.visible = True
            self.selectedmode_label.set_text("Mode: Tiles")
            if self.selected_tiledata and self.selected_tiledata.type != "tile":
                self.selected_tiledata = None
                self.refresh_selection()
        elif self.mode == 1:
            self.objects_cont.visible = True
            self.tiles_cont.visible = False
            self.selectedmode_label.set_text("Mode: Objects")
            if self.selected_tiledata and self.selected_tiledata.type != "object":
                self.selected_tiledata = None
                self.refresh_selection()
        self.refresh_images()
            
    def refresh_layers(self):
        layerliststring = [l.name if l.visible else l.name+HIDDEN_FLAG for l in self.layers]
        self.layerslist.set_item_list(layerliststring)
        
    def get_layer(self,name)->Layer:
        name = name.replace(HIDDEN_FLAG,"")
        for i,l in enumerate(self.layers):
            if l.name == name:
                return(i,l)
        return (None,None)
    
    def layer_toggle_create(self,forceoff=False):
        self.createlayer_entry.visible = not self.createlayer_entry.visible if not forceoff else False
        self.createlayer_btn.visible = not self.createlayer_btn.visible if not forceoff else False
            
    def layer_toggle(self):
        if self.selected_layer:
            self.selected_layer.visible = not self.selected_layer.visible
            self.refresh_layers()
    
    def layer_delete(self):
        if self.selected_layer:
            self.layers.remove(self.selected_layer)
            self.refresh_layers()
    
    def layer_up(self):
        if self.selected_layer:
            index = self.get_layer_index(self.selected_layer)
            if index > 0:
                self.layers.pop(index)
                self.layers.insert(index-1,self.selected_layer)
                self.refresh_layers()
                
    def get_layer_index(self,layer):
        for i,l in enumerate(self.layers):
            if l == layer:
                return i
    
    def layer_down(self):
        if self.selected_layer:
            index = self.get_layer_index(self.selected_layer)
            if index < len(self.layers)-1:
                self.layers.pop(index)
                self.layers.insert(index+1,self.selected_layer)
                self.refresh_layers()
    
    def layer_create(self):
        name = self.createlayer_entry.get_text()
        if name.strip():
            index,layer = self.get_layer(name)
            if index == None and layer == None:
                new = Layer(name,True)
                self.layers.append(new)
                self.refresh_layers()
                self.selected_layer = new
                self.refresh_selected_layer()
                self.createlayer_entry.set_text("")
        self.layer_toggle_create(True)
        
    def image_toggle_create(self,forceoff=False):
        self.addimage_entry.visible = not self.addimage_entry.visible if not forceoff else False
        self.addimage_btn.visible = not self.addimage_btn.visible if not forceoff else False
                
    def layer_save(self):
        if self.selected_layer:
            self.selected_layer.save(self.map_size,self.tile_size,self.name)
                
    def refresh_selected_layer(self):
        if self.selected_layer:
            self.selectedlayer_label.set_text("Layer: "+self.selected_layer.name)
        else:
            self.selectedlayer_label.set_text("No Layer Selected")
            
    def refresh_selected_tool(self):
        self.selectedtool_label.set_text("Tool: "+self.toolidnames[self.tool])