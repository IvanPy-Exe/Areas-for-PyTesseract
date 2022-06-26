# from ctypes import windll
# import pygame

# pygame.init()
# screen = pygame.display.set_mode((100,100))
# # screen = pygame.display.set_mode((100,100), pygame.NOFRAME)

# SetWindowPos = windll.user32.SetWindowPos
# x, y = 0, 0
# SetWindowPos(pygame.display.get_wm_info()['window'], -1, x, y, 0, 0, 0x0001)

import pygame

import win32api
from win32api import RGB
from win32gui import GetWindowLong, SetWindowLong, SetLayeredWindowAttributes
from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_COLORKEY

from threading import Thread
# Thread(target=self.commands,daemon=True).start()

from pyml import yaml

class mouse:
	button = {1:0,2:0}

	@staticmethod
	def get_pos():
		return win32api.GetCursorPos()

	@staticmethod
	def is_pressed(key):
		if key not in mouse.button:
			return False

		res = win32api.GetKeyState(key)

		if res < 0:
			return True

		if res != mouse.button[key]:
			mouse.button[key] = res
			return True
				
		return False

class Event:
	MOUSEBUTTONDOWN = 1
	MOUSEBUTTONUP = 2

	def __init__(self,**kwargs):
		for name,value in kwargs.items():
			self.__dict__[name] = value

class Events:
	def __init__(self):
		self.left = False
		self.right = False

		self.left_up = True
		self.right_up = True

	def get(self):
		l = []

		res = mouse.is_pressed(1)
		if res != self.left:
			self.left = res
			self.left_up = not self.left_up

			if self.left_up:
				l.append(Event(type=2,button=1,pos=mouse.get_pos()))
			else:
				l.append(Event(type=1,button=1,pos=mouse.get_pos()))
				
		res = mouse.is_pressed(2)
		if res != self.right:
			self.right = res
			self.right_up = not self.right_up

			if self.right_up:
				l.append(Event(type=2,button=2,pos=mouse.get_pos()))
			else:
				l.append(Event(type=1,button=2,pos=mouse.get_pos()))

		return l
events = Events()

class App:
	def __init__(self,fps,fon):
		self.fps = fps
		self.fon = fon

		self.objects = []

		self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN, pygame.NOFRAME)
		self.run = True
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont('Consolas',20)

		self.image = self.font.render('REC',True,[200,0,0])

		self.start_pos = None

	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.run = True

			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.run = False

		for event in events.get():
			if event.type == Event.MOUSEBUTTONDOWN:
				if event.button == 1:
					if event.pos == (0,0):
						self.run = False
						l = {}
						for i, rect in enumerate(self.objects):
							l[i] = {
								'x': rect.x,
								'y': rect.y,
								'w': rect.width,
								'h': rect.height
							}
						yaml.save(l,'region.yaml')
					else:
						self.start_pos = event.pos

			elif event.type == Event.MOUSEBUTTONUP:
				if event.button == 1:
					x,y = self.start_pos
					x2, y2 = mouse.get_pos()
					self.objects.append(pygame.Rect(x,y,x2-x,y2-y))
					self.start_pos = None

		self.draw()

	def draw(self):
		self.screen.fill(self.fon)
		self.screen.set_at([0,0],[0,0,0])

		self.screen.blit(self.image,[10,10])
		
		if self.start_pos != None:
			x,y = self.start_pos
			x2, y2 = mouse.get_pos()
			pygame.draw.rect(self.screen,[200,0,0],[x,y,x2-x,y2-y],1)

		# if mouse.is_pressed(1):
		# 	pygame.draw.circle(self.screen,[200,0,0],mouse.get_pos(),10)

		for rect in self.objects:
			pygame.draw.rect(self.screen,[200,0,0],rect,1)

		pygame.display.update()

	def start(self):
		while self.run:
			self.update()
			self.clock.tick(self.fps)

if __name__ == '__main__':
	input()
	pygame.init()

	fon = (255, 0, 128)
	app = App(60,fon)

	winInfo = pygame.display.get_wm_info()['window']

	# Создать многослойное окно
	SetWindowLong(winInfo, GWL_EXSTYLE, GetWindowLong(winInfo, GWL_EXSTYLE) | WS_EX_LAYERED)

	# Установить цвет прозрачности окна
	SetLayeredWindowAttributes(winInfo, RGB(*fon), 0, LWA_COLORKEY)

	app.start()