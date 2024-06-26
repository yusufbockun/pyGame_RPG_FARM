import pygame
from settings import *
from support import *
from timer import *
from transition import Transition
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group,collision_sprites, tree_sprites,interaction,soil_layer):
        super().__init__(group)
        
        # General Setup
        self.import_assets()
        self.status='down_idle'
        self.frame_index=0
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.z = LAYERS['main']

        # Movement attributes
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 200
        self.collision_sprites = collision_sprites
        
        #Timers
        self.timers={'tool_timer':Timer(350,self.use_tool),
                     'switch_tool':Timer(200,None),
                     'seed_timer': Timer(350,self.use_seed),
                     'switch_seed':Timer(200)
        }
        
        #tools
        self.tools=["axe","water","hoe"]
        self.selectedTool='axe'
        
        #seeds
        self.seeds=['corn','tomato']
        self.selectedSeed='corn'
        
        
        #player_inventory
        
        self.item_inventory= {
            'wood': 0,
            'apple':0,
            'corn':0,
            'tomato':0
        }
        
        # interaction
        self.tree_sprites = tree_sprites
        self.interaction =interaction
        self.sleep =False
        self.soil_layer =soil_layer
    def get_target_pos(self):
        self.target_pos = self.rect.center + PLAYER_TOOL_OFFSET[self.status.split('_')[0]]
        
    def use_tool(self):
        if self.selectedTool =='hoe':
            self.soil_layer.get_hit(self.target_pos)
        if self.selectedTool =='axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_pos):
                    tree.damage()
                
        if self.selectedTool =='water':
            self.soil_layer.water(self.target_pos)
    
    def use_seed(self):
        self.soil_layer.plant_seed(self.target_pos,self.selectedSeed)
        
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
        if not self.timers['tool_timer'].active and not self.sleep:
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
            
            #use tools
            if keys[pygame.K_SPACE]:
                self.timers['tool_timer'].activate()
                self.direction=pygame.math.Vector2()
                self.frame_index=0
            #switch tool
            if keys[pygame.K_q] and not self.timers['switch_tool'].active:
                self.timers['switch_tool'].activate()
                self.change_tool()
            
            #use seed
            if keys[pygame.K_LCTRL]:
                self.timers['seed_timer'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            # switch seed
            if keys[pygame.K_e] and not self.timers['switch_seed'].active:
                self.timers['switch_seed'].activate()
                self.change_seed()
            if keys[pygame.K_z]:
                collided_interaction_sprite=pygame.sprite.spritecollide(self,self.interaction,False)
                if collided_interaction_sprite:
                    if collided_interaction_sprite[0].name =='Trader':
                        pass
                    else:
                        self.status ='left_idle'
                        self.sleep = True


    def collision(self,direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite,'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction =='horizontal':
                        if self.direction.x >0: #moving right
                            self.hitbox.right =sprite.hitbox.left
                        if self.direction.x<0: #moving left
                            self.hitbox.left =sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    if direction =='vertical':
                        if self.direction.y>0: #moving down
                            self.hitbox.bottom =sprite.hitbox.top
                        if self.direction.y<0: #moving up
                            self.hitbox.top =sprite.hitbox.bottom
                        self.rect.centery =self.hitbox.centery
                        self.pos.y=self.hitbox.centery
    def move(self, dt):
    
        if self.direction.magnitude()>0:
            self.direction=self.direction.normalize()
            
        #horizontal movement
        self.pos.x+= self.direction.x * self.speed * dt
        self.hitbox.centerx=round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        #vertical movement
        self.pos.y+= self.direction.y * self.speed * dt
        self.hitbox.centery=round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')
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
    def change_seed(self):
        for seed in self.seeds:
            if seed==self.selectedSeed:
                self.selectedSeed=self.seeds[(self.seeds.index(seed)+1)% len(self.seeds)]  
                break
                
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
        
    def update(self, dt):
        self.input()
        self.get_status()
        self.update_timers()
        self.get_target_pos()
        self.move(dt)
        self.animate(dt)
