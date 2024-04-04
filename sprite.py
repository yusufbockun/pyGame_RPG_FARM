import pygame
from settings import *
from random import randint,choice
from timer import Timer
class Generic(pygame.sprite.Sprite):
	def __init__(self,pos,surf,groups,z=LAYERS['main']):
		super().__init__(groups)
		self.image = surf
		self.rect=self.image.get_rect(topleft=pos)
		self.z=z
		self.hitbox = self.rect.copy().inflate(-self.rect.width*0.2,-self.rect.height*0.75)

class Interaction(Generic):
	def __init__(self,pos,size,groups, name):
		surf=pygame.Surface(size)
		super().__init__(pos,surf,groups)
		self.name = name
class Water(Generic):
	def __init__(self,pos,frames,groups):
		self.frames=frames
		self.frame_index = 0
		
		#sprite setup
		super().__init__(pos=pos,
		                 surf=self.frames[self.frame_index],
		               groups=groups,
		               z = LAYERS['water']  
		                 
		                 )
		
	def animate(self,dt):
		self.frame_index +=5*dt
		if self.frame_index >= len(self.frames):
			self.frame_index =0
		self.image = self.frames[int(self.frame_index)]
	
	def update(self,dt):
		self.animate(dt)
		
class WildFlower(Generic):
	def __init__(self,pos,surf,groups):
		super().__init__(pos,surf,groups)
		self.hitbox =self.rect.copy().inflate(-20,-self.rect.height*0.9)

class Tree(Generic):
	def __init__(self,pos,surf,groups,name,player_add):
		super().__init__(pos,surf,groups)
		
		#tree attributes
		self.health = 5
		self.alive = True
		stump_path = f'graphics/stumps/{"small"  if name =="Small" else "large"}.png'
		self.stum_surf = pygame.image.load(stump_path).convert_alpha()
		self.invul_timer = Timer(200)
		#apples
		self.apples_surf = pygame.image.load(f'graphics/fruit/apple.png').convert_alpha()
		self.apple_sprites = pygame.sprite.Group()
		self.apple_pos = APPLE_POS[name]
		self.create_fruit()

		self.player_add = player_add
	def damage(self):
		#damage tree
		self.health -=1
		
		#remove an apple
		if len(self.apple_sprites.sprites())>0:
			random_apple = choice(self.apple_sprites.sprites())
			random_apple.kill()
			self.player_add('apple')

	def check_dead(self):
		if self.health <= 0:
			self.image =self.stum_surf
			self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
			self.hitbox = self.rect.copy().inflate(-10,-self.rect.height*0.6)
			self.alive = False
			self.player_add('wood',5)
			
	def update(self,dt):
		if self.alive:
			self.check_dead()
	def create_fruit(self):
		for pos in self.apple_pos:
			if randint(0, 10) < 2:
				x = pos[0] + self.rect.left
				y = pos[1] + self.rect.top
				# Adding apple sprites to the same groups as the Tree sprite
				apple_sprite = Generic(pos=(x, y),
				                       surf=self.apples_surf,
				                       groups=[self.groups(), self.apple_sprites],
				                       z=LAYERS['fruit']
				                       )
				
		