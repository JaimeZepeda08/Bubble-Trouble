import pygame 
import os 
import math

pygame.init()

WIDTH,HEIGHT = 1000,550
WINDOW = pygame.display.set_mode((WIDTH,HEIGHT))

PLAYER_IMG1 = pygame.transform.scale(pygame.image.load(os.path.join("Assets","wall.png")),(25,55)) 
PLAYER_IMG2 = pygame.transform.scale(pygame.image.load(os.path.join("Assets","wall.png")),(25,55))
PLAYER_IMGS = [PLAYER_IMG1,PLAYER_IMG2]

SPIKES_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets","wall.png")),(10,500))

BUBBLE_IMG = pygame.image.load(os.path.join("Assets","bubble.png"))
WALL_IMG = pygame.image.load(os.path.join("Assets","wall.png"))
CEILING_IMG = pygame.transform.scale(pygame.image.load(os.path.join("Assets","wall.png")),(WIDTH,800))

STATS_FONT = pygame.font.Font(os.path.join("Assets","PressStart2P-Regular.ttf"),20)

GREY = (150,150,150)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLUE = (0,0,255)
RED = (255,0,0)

FLOOR_Y = HEIGHT - 50

FPS = 60

class Player:
	IMGS = PLAYER_IMGS
	VELOCITY = 3.5
	ANIMATION_TIME = 10

	def __init__(self,x):
		self.x = x 
		self.y = FLOOR_Y - self.IMGS[0].get_height()
		self.ammo = 1
		self.can_move = True
		self.timer = 5 #frames 
		self.img_counter = 0
		self.img = self.IMGS[0]

	def move_right(self):
		if self.can_move:
			#flip image to face right
			self.x += self.VELOCITY

			self.img_counter += 1
			if self.img_counter < self.ANIMATION_TIME:
				self.img = self.IMGS[0]
			elif self.img_counter < self.ANIMATION_TIME * 2:
				self.img = self.IMGS[1]
			elif self.img_counter < self.ANIMATION_TIME * 2 + 1:
				self.img = self.IMGS[0]
				self.img_counter = 0  

	def move_left(self):
		if self.can_move:
			#flip image to face left
			self.x -= self.VELOCITY

			self.img_counter += 1
			if self.img_counter < self.ANIMATION_TIME:
				self.img = self.IMGS[0]
			elif self.img_counter < self.ANIMATION_TIME * 2:
				self.img = self.IMGS[1]
			elif self.img_counter < self.ANIMATION_TIME * 2 + 1:
				self.img = self.IMGS[0]
				self.img_counter = 0  

	def shoot(self,spikes_lst):
		if self.ammo > 0:
			self.ammo -= 1 
			spikes_lst.append(Spikes(self.x + self.img.get_width() / 2 - SPIKES_IMG.get_width() / 2))
			self.timer = 5
			self.can_move = False 

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

	def draw(self,win):
		win.blit(self.img,(self.x,self.y))

class Spikes:
	IMG = SPIKES_IMG
	VELOCITY = 9

	def __init__(self,x):
		self.x = x 
		self.y = FLOOR_Y - PLAYER_IMG1.get_height()

	def move(self):
		self.y -= self.VELOCITY

	def collide(self,bubble):
		bubble_mask = bubble.get_mask()
		mask = pygame.mask.from_surface(self.IMG)
		offset = (int(self.x - bubble.x), int(self.y - round(bubble.y)))
		point = bubble_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 

	def draw(self,win):
		win.blit(self.IMG,(self.x,self.y))

class Bubble:
	def __init__(self,x,y,size,color,is_right,can_move): 
		self.x = x
		self.y = y 
		self.size = size #size: 1 - 5
		self.color = color 
		self.bounciness = math.log(size + 3,10) * 8
		self.is_right = is_right
		self.can_move = can_move
		self.velocity_y = 0
		self.velocity_x = 2
		self.time = 0
		self.img = pygame.transform.scale(BUBBLE_IMG,(self.size * 20,self.size * 20))

		self.img.fill(self.color,special_flags=3)

	def bounce(self):
		self.time += 0.1
		d = self.velocity_y * self.time + 1.5 * self.time ** 2
		if d >= self.bounciness:
			d = self.bounciness
		self.y += d

	def move(self):
		if self.can_move:
			if self.is_right:
				self.x += self.velocity_x
			else:
				self.x -= self.velocity_x

	def split(self,bubbles): #when two spikes are in the same place an collide --> error
		bubbles.remove(self)
		if self.size > 1: 
			new_bubble1 = Bubble(self.x + self.bounciness,self.y,self.size - 1,self.color,True,True)
			new_bubble2 = Bubble(self.x - self.bounciness,self.y,self.size - 1,self.color,False,True) 
			new_bubble1.velocity_y = -new_bubble1.bounciness * math.pow(0.8,self.size - 2.6) 
			new_bubble1.time = 0
			new_bubble2.velocity_y = -new_bubble2.bounciness * math.pow(0.8,self.size - 2.6) 
			new_bubble2.time = 0
			bubbles.append(new_bubble1)
			bubbles.append(new_bubble2)

	def collide(self,player):
		player_mask = player.get_mask()
		mask = pygame.mask.from_surface(self.img)
		offset = (int(self.x - player.x), int(self.y - round(player.y)))
		point = player_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 

	def get_mask(self):
		return pygame.mask.from_surface(self.img)

	def draw(self,win):
		win.blit(self.img,(self.x,self.y))

class Wall:
	def __init__(self,x,width,color,can_collide):
		self.x = x 
		self.y = 0
		self.width = width 
		self.color = color 
		self.can_collide = can_collide
		self.has_collided = False
		self.img = pygame.transform.scale(WALL_IMG,(width,HEIGHT))

		self.img.fill(color,special_flags=3)

	def collide_bubble(self,bubble):
		bubble_mask = bubble.get_mask()
		mask = pygame.mask.from_surface(self.img)
		offset = (int(self.x - bubble.x), int(self.y - round(bubble.y)))
		point = bubble_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 

	def collide_player(self,player):
		player_mask = player.get_mask()
		mask = pygame.mask.from_surface(self.img)
		offset = (int(self.x - player.x), int(self.y - round(player.y)))
		point = player_mask.overlap(mask,offset)

		if point:
			return True 
		else:
			return False 

	def draw(self,win):
		win.blit(self.img,(self.x,self.y))

class Ceiling: 
	IMG = CEILING_IMG

	def __init__(self,y,final_y,can_move,velocity):
		self.x = 0
		self.y = y - CEILING_IMG.get_height()
		self.final_y = final_y - CEILING_IMG.get_height()
		self.can_move = can_move
		self.velocity = velocity

	def move(self):
		if self.can_move:
			if self.y < self.final_y:
				self.y += self.velocity

	def collide_bubble(self,bubble):
		if bubble.y <= self.y + self.IMG.get_height():
			return True 
		else:
			return False 

	def collide_spikes(self,spikes):
		if spikes.y <= self.y + self.IMG.get_height():
			return True 
		else:
			return False 

	def draw(self,win):
		win.blit(self.IMG,(self.x,self.y))

class Timer:
	def __init__(self,x,y,width,height,time):
		self.x = x
		self.y = y
		self.initial_width = width
		self.width = self.initial_width
		self.height = height
		self.initial_time = time * FPS 
		self.time = self.initial_time

	def tick(self):
		self.time -= 1
		self.width = (self.time / self.initial_time) * self.initial_width

	def draw(self,win):
		pygame.draw.rect(win,WHITE,pygame.Rect(self.x,self.y,self.initial_width,self.height))
		pygame.draw.rect(win,RED,pygame.Rect(self.x,self.y,self.width,self.height))

class Levels:
	def __init__(self,level):
		self.level = level
		self.max_level = 9
		self.started = False 

	def Level_1(self,bubbles,walls):
		bubble = Bubble(150,400,2,BLUE,True,True)
		bubbles.append(bubble)

	def Level_2(self,bubbles,walls):
		bubble = Bubble(150,300,3,GREEN,True,True)
		bubbles.append(bubble)

	def Level_3(self,bubbles,walls):
		bubble = Bubble(150,300,4,RED,True,True)
		bubbles.append(bubble)

	def Level_4(self,bubbles,walls):
		bubble1 = Bubble(150,300,3,GREEN,False,True)
		bubble2 = Bubble(790,300,3,GREEN,True,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)

	def Level_5(self,bubbles,walls):
		bubble1 = Bubble(150,300,3,GREEN,True,True)
		bubble2 = Bubble(790,300,4,RED,False,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)

		wall = Wall(WIDTH / 2 - 30,60,GREY,False)
		wall2 = Wall(WIDTH / 2 - 25,50,BLACK,True)
		walls.append(wall)
		walls.append(wall2)

	def Level_6(self,bubbles,walls):
		bubble1 = Bubble(150,450,1,BLUE,False,True)
		bubble2 = Bubble(225,500,1,RED,False,True)
		bubble3 = Bubble(300,450,1,BLUE,False,True)
		bubble4 = Bubble(375,500,1,RED,False,True)
		bubble5 = Bubble(625,500,1,BLUE,True,True)
		bubble6 = Bubble(700,450,1,RED,True,True)
		bubble7 = Bubble(775,500,1,BLUE,True,True)
		bubble8 = Bubble(850,450,1,RED,True,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)
		bubbles.append(bubble3)
		bubbles.append(bubble4)
		bubbles.append(bubble5)
		bubbles.append(bubble6)
		bubbles.append(bubble7)
		bubbles.append(bubble8)

	def Level_7(self,bubbles,walls):
		bubble1 = Bubble(70,400,1,GREEN,True,True)
		bubble2 = Bubble(100,400,1,RED,True,True)
		bubble3 = Bubble(130,400,1,BLUE,True,True)
		bubble4 = Bubble(280,400,1,GREEN,True,True)
		bubble5 = Bubble(310,400,1,RED,True,True)
		bubble6 = Bubble(340,400,1,BLUE,True,True)
		bubble7 = Bubble(660,400,1,GREEN,False,True)
		bubble8 = Bubble(690,400,1,RED,False,True)
		bubble9 = Bubble(720,400,1,BLUE,False,True)
		bubble10 = Bubble(870,400,1,GREEN,False,True)
		bubble11 = Bubble(900,400,1,RED,False,True)
		bubble12 = Bubble(930,400,1,BLUE,False,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)
		bubbles.append(bubble3)
		bubbles.append(bubble4)
		bubbles.append(bubble5)
		bubbles.append(bubble6)
		bubbles.append(bubble7)
		bubbles.append(bubble8)
		bubbles.append(bubble9)
		bubbles.append(bubble10)
		bubbles.append(bubble11)
		bubbles.append(bubble12)

	def Level_8(self,bubbles,walls):
		bubble1 = Bubble(150,300,3,GREEN,True,True)
		bubble2 = Bubble(450,200,4,RED,True,True)
		bubble3 = Bubble(820,100,5,BLUE,True,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)
		bubbles.append(bubble3)

		wall1 = Wall(330,50,BLACK,True)
		wall2 = Wall(660,50,BLACK,True)
		walls.append(wall1)
		walls.append(wall2)

	def Level_9(self,bubbles,walls):
		bubble1 = Bubble(150,150,4,RED,False,True)
		bubble2 = Bubble(450,100,5,GREEN,True,False)
		bubble3 = Bubble(780,150,4,RED,True,True)
		bubbles.append(bubble1)
		bubbles.append(bubble2)
		bubbles.append(bubble3)

def draw_window(win,player,bubbles,spikes_lst,walls,ceiling,level,lives,timer):
	WINDOW.fill(GREY) #change to background image

	for spikes in spikes_lst:
		spikes.draw(win)

	for bubble in bubbles:
		bubble.draw(win)

	for wall in walls:
		wall.draw(win)

	player.draw(win)

	ceiling.draw(win)

	pygame.draw.rect(win,BLACK,pygame.Rect(0,FLOOR_Y,WIDTH,HEIGHT - FLOOR_Y)) #floor

	level_text = STATS_FONT.render("Level: " + str(level),1,WHITE)
	win.blit(level_text,(WIDTH - level_text.get_width() - 20,HEIGHT - 25 - level_text.get_height() / 2))
	lives_text = STATS_FONT.render("Lives: " + str(lives),1,WHITE)
	win.blit(lives_text,(20,HEIGHT - 25 - level_text.get_height() / 2))

	timer.draw(win)

	pygame.display.update()

def main():
	levels = Levels(1)
	lives = 8
	timer = Timer(200,FLOOR_Y + 50 / 4,600,25,60)

	player = Player(500) #default player 
	player_x = player.x

	spikes_lst = []

	bubbles = []	

	wall_right = Wall(WIDTH - 50,50,BLACK,True)
	wall_left = Wall(0,50,BLACK,True)
	walls = [wall_right,wall_left]

	ceiling = Ceiling(15,375,False,0.5) #default ceiling 

	right_pressed = False 
	left_pressed = False

	clock = pygame.time.Clock()
	run = True
	while run:
		clock.tick(FPS)

		if levels.started == False:
			if levels.level == 1:
				levels.Level_1(bubbles,walls)
				player.x = 500 
				levels.started = True 
			elif levels.level == 2:
				levels.Level_2(bubbles,walls)
				player.x = 500 
				levels.started = True 
			elif levels.level == 3:
				levels.Level_3(bubbles,walls)
				player.x = 500 
				levels.started = True 
			elif levels.level == 4:
				levels.Level_4(bubbles,walls)
				player.x = 500 
				levels.started = True 
			elif levels.level == 5:
				levels.Level_5(bubbles,walls)
				player.x = 80
				levels.started = True 
			elif levels.level == 6:
				levels.Level_6(bubbles,walls)
				player.x = 500
				ceiling.can_move = True
				levels.started = True 
			elif levels.level == 7:
				levels.Level_7(bubbles,walls)
				player.x = 500 
				ceiling.y = 300 - CEILING_IMG.get_height() 
				levels.started = True 
			elif levels.level == 8:
				levels.Level_8(bubbles,walls)
				player.x = 80
				levels.started = True 
			elif levels.level == 9:
				levels.Level_9(bubbles,walls)
				player.x = 500
				levels.started = True 

		#levels with special rules 
		if levels.level == 5:
			if len(bubbles) == 1:
				walls[len(walls) - 1].y = -110
		if levels.level == 8: 
			if len(bubbles) == 2:
				if len(walls) > 3:
					walls.pop(len(walls) - 2)
			elif len(bubbles) == 1:
				if len(walls) > 2:
					walls.pop(len(walls) - 1)

		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				run = False 
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					player.shoot(spikes_lst)
				if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					right_pressed = True
					left_pressed = False
				if event.key == pygame.K_LEFT or event.key == pygame.K_a:
					left_pressed = True 
					right_pressed = False
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
					right_pressed = False
				if event.key == pygame.K_LEFT or event.key == pygame.K_a:
					left_pressed = False

		if len(bubbles) == 0: #level passed 
			if levels.level < levels.max_level:
				levels.level += 1 
				levels.started = False
				walls = [wall_right,wall_left]
				bubbles = []
				ceiling = Ceiling(15,375,False,0.5)
				timer.time = timer.initial_time

		if lives <= 0: #game lost 
			main()

		if left_pressed:
			player.move_left()
		elif right_pressed:
			player.move_right()
		player.timer -= 1
		if player.timer <= 0:
			player.can_move = True 

		for spikes in spikes_lst:
			if ceiling.collide_spikes(spikes):
				spikes_lst.remove(spikes)
				player.ammo += 1
			spikes.move()

		for bubble in bubbles:
			for spikes in spikes_lst:
				if spikes.collide(bubble):
					spikes_lst.remove(spikes)
					player.ammo += 1
					bubble.split(bubbles)
			if bubble.collide(player): #lose 1 live
				lives -= 1
				levels.started = False
				walls = [wall_right,wall_left]
				bubbles = []
				ceiling = Ceiling(15,375,False,0.5)
				timer.time = timer.initial_time
			if ceiling.collide_bubble(bubble):
				bubbles.remove(bubble)
			if bubble.y >= FLOOR_Y - bubble.img.get_height():
				bubble.y = FLOOR_Y - bubble.img.get_height()
				bubble.velocity_y = -bubble.bounciness
				bubble.time = 0
			bubble.bounce()
			bubble.move()

		ceiling.move()

		for wall in walls:
			for bubble in bubbles:
				if wall.collide_bubble(bubble):
					bubble.is_right = not bubble.is_right
			if wall.can_collide:
				if wall.collide_player(player):
					if wall.has_collided == False:
						player_x = player.x 
					wall.has_collided = True
					player.x = player_x
				else:
					wall.has_collided = False

		timer.tick()
		if timer.time <= 0:
			lives -= 1
			levels.started = False
			walls = [wall_right,wall_left]
			bubbles = []
			ceiling = Ceiling(15,375,False,0.5)
			timer.time = timer.initial_time

		draw_window(WINDOW,player,bubbles,spikes_lst,walls,ceiling,levels.level,lives,timer)

if __name__ == '__main__':
	main()