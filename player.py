import pygame
from support import *
from timer import *
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group):
        super().__init__(group)
        # General Setup
        self.import_assets()
        self.status='down_idle'
        self.frame_index=0
        
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        
        
        self.timers={'tool_timer':Timer(350,self.use_tool),
                     'switch_tool':Timer(200,None)
        }
        self.tools=["axe","water","hoe"]
        self.selectedTool='axe'
        
    def use_tool(self):
        print(self.selectedTool)
    def import_assets(self):
        self.animations={'up':[],'down':[],'left':[],'right':[],
                         'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
                         'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
                         'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
                         'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
        for animation in self.animations.keys():
            full_path='graphics/character/'+animation
            self.animations[animation]=import_folder(full_path)
        
    def animate(self,dt):
        self.frame_index+=4*dt
        if self.frame_index>=len(self.animations[self.status]):
            self.frame_index=0
        self.image=self.animations[self.status][int(self.frame_index)]
    def input(self):
        keys = pygame.key.get_pressed()
        if not self.timers['tool_timer'].active:
            # Movement
            if keys[pygame.K_w]:
                self.direction.y = -1
                self.status='up'
            elif keys[pygame.K_s]:
                self.direction.y = 1
                self.status='down'
            else:
                self.direction.y = 0
                
                
            if keys[pygame.K_a]:
                self.direction.x = -1
                self.status='left'
            elif keys[pygame.K_d]:
                self.direction.x = 1
                self.status='right'
            else:
                self.direction.x = 0
            
            if keys[pygame.K_SPACE]:
                self.timers['tool_timer'].activate()
                self.direction=pygame.math.Vector2()
                self.frame_index=0
                #use tool
            if keys[pygame.K_q] and not self.timers['switch_tool'].active:
                self.timers['switch_tool'].activate()
                self.change_tool()


    def move(self, dt):
    
        if self.direction.magnitude()>0:
            self.direction=self.direction.normalize()
            
        #horizontal movement
        self.pos.x+= self.direction.x * self.speed * dt
        self.rect.centerx = self.pos.x

        #vertical movement
        self.pos.y+= self.direction.y * self.speed * dt
        self.rect.centery = self.pos.y
        
    def get_status(self):
        #animation idle
        if self.direction.magnitude()==0:
            self.status= self.status.split('_')[0]+'_idle'
            
        if self.timers['tool_timer'].active:
            self.status=self.status.split('_')[0]+'_'+self.selectedTool
        
    def change_tool(self):
        for tool in self.tools:
            if tool==self.selectedTool:
                self.selectedTool=self.tools[(self.tools.index(tool)+1)% len(self.tools)]
                break
        #animation tools
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.move(dt)
        self.animate(dt)
