import pygame
import random
import math

window = None
running = True

screenDim = (1600, 900)

class Atom():
	def __init__(self, pos):
		self.pos = pos


class Neutron():
	def __init__(self, pos, r, owner = None):
		self.pos = pos[:]
		self.r = r % 360.0
		self.owner = owner
	

	def Update(self):
		global neutronInstance, neutronSpeed, screenDim, neutronRadius, uraniumRadius
		x = neutronSpeed * math.cos(self.r * math.pi / 180)
		y = neutronSpeed * math.sin(self.r * math.pi / 180)
		
		n = math.sqrt(x*x + y*y)
		step = ((x / n) * neutronRadius, (y / n) * neutronRadius)
		
		pos2 = self.pos[:]
		
		noCollision = True

		i = 0

		while i < neutronSpeed:
			pos2 = [pos2[0] + step[0], pos2[1] + step[1]]
			for u in uraniumInstance:
				if circlesIntersect(pos2[0], pos2[1], neutronRadius, u.pos[0], u.pos[1], uraniumRadius) and u != self.owner:
					u.splitFlag = True
					noCollision = False
			i += neutronRadius
		
		if (noCollision):
			self.pos = [self.pos[0] + x, self.pos[1] + y]
		else:
			neutronInstance.remove(self)
		if self.pos[0] < 0 or self.pos[0] > screenDim[0] or self.pos[1] < 0 or self.pos[1] > screenDim[1]:
			neutronInstance.remove(self)



	def Render(self):
		global window, uraniumRadius, neutronObservedRadius

		pygame.draw.circle(window, (255, 255, 100), self.pos, neutronObservedRadius)


class Uranium():
	def __init__(self, pos):
		Atom.__init__(self, pos)
		self.splitFlag = False
	def Update(self):
		global uraniumInstance, decayChance, neutronInstance, uraniumSplitRange, compressionMode, screenDim, uraniumDecay
		if self.splitFlag:
			uraniumInstance.remove(self)
			nCount = random.randint(uraniumSplitRange[0], uraniumSplitRange[1])
			for i in range(0, nCount, 1):
				neutronInstance.append(Neutron(self.pos, random.random()*360.0))
			return

		if uraniumDecay and random.random() <= decayChance:
			neutronInstance.append(Neutron(self.pos, random.random()*360.0, self))
		
		if compressionMode:
			diff = [(screenDim[0] / 2 - self.pos[0]) / 100, (screenDim[1] / 2 - self.pos[1]) / 100]
			self.pos = [self.pos[0] + diff[0], self.pos[1] + diff[1]]

	def Render(self):
		global window, uraniumRadius
		pygame.draw.circle(window, (255, 100, 100) if uraniumDecay else (200, 200, 200), self.pos, uraniumRadius)
	

def createUranium(tries = 0):
	global uraniumInstance

	u = Uranium([random.random()*1500 + 50, random.random()*800 + 50])

	f = False

	for n in uraniumInstance:
		if type(n) == Uranium:
			if circlesIntersect(u.pos[0], u.pos[1], uraniumRadius, n.pos[0], n.pos[1], uraniumRadius):
				f = True
	
	if f:
		u = None
		if tries < 2048:
			createUranium(tries + 1)
	else:
		uraniumInstance.append(u)


def Update():
	global uraniumInstance

	for n in uraniumInstance:
		n.Update()
	

	for n in neutronInstance:
		n.Update()


def Render():
	global window, uraniumInstance
	
	window.fill((0, 0, 0))

	for n in uraniumInstance:
		n.Render()
	for k in neutronInstance:
		k.Render()

	pygame.display.flip()


def circlesIntersect(x1, y1, r1, x2, y2, r2):
	return r1+r2 >= math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1))


uraniumInstance = []
neutronInstance = []


uraniumRadius = 2
neutronRadius = 0.5
neutronObservedRadius = 2
neutronSpeed = 10
decayChance = 1/600
uraniumSplitRange = (2, 6)


compressionMode = False
uraniumDecay = True

def main():
	global window, running, uraniumInstance, screenDim, uraniumDecay, compressionMode

	pygame.init()

	window = pygame.display.set_mode(screenDim)

	pygame.display.set_caption("Nuclear Fission")

	timer = pygame.time.get_ticks()

	for i in range(0, 10, 1):
		createUranium()

	while running:
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				running = False
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_1:
					for i in range(0, 10, 1):
						createUranium()
				elif e.key == pygame.K_2 and (not compressionMode):
					compressionMode = True
			elif e.type == pygame.KEYUP:
				if e.key == pygame.K_2 and compressionMode:
					compressionMode = False
				elif e.key == pygame.K_3:
					if uraniumDecay:
						uraniumDecay = False
					else:
						uraniumDecay = True


		theTime = pygame.time.get_ticks()

		if (theTime-timer > 17):
			timer = theTime
			Update()
			Render()

		
		

	pygame.quit()
	return


if __name__ == "__main__":
	main()


