import pygame
from screeninfo import get_monitors
from rng import LCG
import numpy as np
import weakref

class Particle:
	def __init__(self, pos: list[float, float] = [0.0, 0.0], radius: float = 2):
		self.pos = pos
		self.vel = [0.0, 0.0]
		self.radius = radius
		self.collisions: Particle = []

		self.remove = False

	def GetLeft(self):
		return self.pos[0]-self.radius

	def GetRight(self):
		return self.pos[0]+self.radius

	def GetTop(self):
		return self.pos[1]-self.radius

	def GetBottom(self):
		return self.pos[1]+self.radius

	def FlagForRemoval(self):
		self.remove = True


class Uranium(Particle):
	def __init__(self, pos: list[float, float] = [0, 0]):
		super().__init__(pos, radius = 3)

class AlphaParticle(Particle):
	def __init__(self, angle: float, parent: Uranium):
		super().__init__(list(parent.pos), radius = 2)

		SPEED = 10

		self.parent = parent
		self.vel = [np.cos(np.radians(angle)) * SPEED, np.sin(np.radians(angle)) * SPEED]

class Controller:
	def __init__(self):
		self.FLOOD = False
		self.COMPRESS = False
		self.FREEZE = False

	def RegisterEvent(self, e: pygame.Event):
		if e.type == pygame.KEYDOWN:
			if e.key == pygame.K_1:
				self.FLOOD = True
			elif e.key == pygame.K_2:
				self.COMPRESS = True
		elif e.type == pygame.KEYUP:
			if e.key == pygame.K_1:
				self.FLOOD = False
			elif e.key == pygame.K_2:
				self.COMPRESS = False
			elif e.key == pygame.K_3:
				self.FREEZE = not self.FREEZE


class Renderer:
	def __init__(self, window: pygame.Surface, dim: tuple[int, int], controller: Controller):
		self.window = window
		self.dim = dim
		self.controller = controller

		self.font = None

	def RenderUranium(self, uranium: Uranium):
		pygame.draw.circle(self.window, (30, 190, 75), uranium.pos, uranium.radius)

	def RenderAlphaParticle(self, alpha: Uranium, delta: float):
		pos = [alpha.pos[0] + alpha.vel[0]*delta, alpha.pos[1] + alpha.vel[1]*delta]
		pygame.draw.circle(self.window, (255, 255, 255), pos, alpha.radius)


class GameInstance:
	def __init__(self):
		self.running = True
		self.window: pygame.Surface | None = None

		self.controller = Controller()
		self.dim = (1600, 900)

		self.renderer: Renderer | None = None

		self.ran = LCG.NADS64bit()

		self.particles: list[Particle] = []
		self.floodTimer = 0
		self.floodTimerMax = 1

	def Input(self):
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				self.running = False
			self.controller.RegisterEvent(e)

	def RectCollision(self, a: Particle, b: Particle):
		return a.GetRight() > b.GetLeft() and a.GetLeft() < b.GetRight() and a.GetBottom() > b.GetTop() and a.GetTop() < b.GetBottom()

	def Collisions(self, distance: float | None = None, offset: list[float, float] | None = None, particles: list[Particle] | None = None):
		TOLERANCE = 4

		if offset is None:
			offset = [0, 0]
		if particles is None:
			particles = self.particles
		if distance is None:
			distance = self.dim[0]
			self.collision_list = []

		if len(particles) < 2:
			return

		if distance < TOLERANCE:
			for i in range(0, len(particles)-1, 1):
				for j in range(i+1, len(particles), 1):
					particleA: Particle = particles[i]
					particleB: Particle = particles[j]

					if self.RectCollision(particleA, particleB):
						if particleB not in particleA.collisions:
							particleA.collisions.append(particleB)
						if particleA not in particleB.collisions:
							particleB.collisions.append(particleA)
			return

		half_distance = distance / 2.0
		half_x = offset[0] + half_distance
		half_y = offset[1] + half_distance

		topLeft = []
		topRight = []
		bottomLeft = []
		bottomRight = []
		for particle in particles:
			if particle.GetLeft() < half_x and particle.GetTop() < half_y:
				topLeft.append(particle)
			if particle.GetRight() > half_x and particle.GetTop() < half_y:
				topRight.append(particle)
			if particle.GetLeft() < half_x and particle.GetBottom() > half_y:
				bottomLeft.append(particle)
			if particle.GetRight() > half_x and particle.GetBottom() > half_y:
				bottomRight.append(particle)

		if len(topLeft) > 1:
			self.Collisions(half_distance, [offset[0], offset[1]], topLeft)
		if len(topRight) > 1:
			self.Collisions(half_distance, [offset[0] + half_distance, offset[1]], topRight)
		if len(bottomLeft) > 1:
			self.Collisions(half_distance, [offset[0], offset[1] + half_distance], bottomLeft)
		if len(bottomRight) > 1:
			self.Collisions(half_distance, [offset[0] + half_distance, offset[1] + half_distance], bottomRight)


	def Start(self):
		self.renderer = Renderer(self.window, self.dim, self.controller)

		for i in range(20):
			self.particles.append(Uranium([self.ran.floatRange(0.0, self.dim[0]), self.ran.floatRange(0.0, self.dim[1])]))

	def FixedUpdate(self):
		if self.controller.FLOOD:
			if self.floodTimer == 0:
				self.particles.append(Uranium([self.ran.floatRange(0.0, self.dim[0]), self.ran.floatRange(0.0, self.dim[1])]))
				self.floodTimer = self.floodTimerMax
			else:
				self.floodTimer -= 1
		else:
			self.floodTimer = 0

		if self.controller.COMPRESS:
			for particle in self.particles:
				if isinstance(particle, Uranium):
					diff = [(self.dim[0] / 2 - particle.pos[0]) / 100, (self.dim[1] / 2 - particle.pos[1]) / 100]
					particle.pos[0] = particle.pos[0] + diff[0]
					particle.pos[1] = particle.pos[1] + diff[1]


		for particle in reversed(self.particles):
			if isinstance(particle, Uranium):
				if (not self.controller.FREEZE) and self.ran.intRange(1, 1000) == 1:
					self.particles.append(AlphaParticle(self.ran.floatRange(0.0, 360.0), particle))
					particle.collisions = []
			elif isinstance(particle, AlphaParticle):
				particle.pos[0] += particle.vel[0]
				particle.pos[1] += particle.vel[1]

				for collider in particle.collisions:
					if collider is particle.parent:
						pass
					elif isinstance(collider, Uranium):
						particle.FlagForRemoval()
						collider.FlagForRemoval()

						n = self.ran.intRange(3, 6)
						a = self.ran.floatRange(0.0, 360.0)
						for i in range(n):
							ap = AlphaParticle(a, collider)
							ap.parent = None # whoops
							self.particles.append(ap)

				if particle.pos[0] < 0 or particle.pos[1] > self.dim[0] or particle.pos[1] < 0 or particle.pos[1] > self.dim[1]:
					particle.FlagForRemoval()

		for index, particle in reversed(list(enumerate(self.particles))):
			if particle.remove:
				self.particles.pop(index)

		self.Collisions()


	def DrawText(self, string: str, pos: list[float, float], color: tuple[int, int, int] = (255, 255, 255)):
		surface = self.font.render(string, True, color)
		self.window.blit(surface, pos)

	def Render(self, delta: float):
		self.window.fill((0, 0, 0))

		for particle in self.particles:
			if isinstance(particle, Uranium):
				self.renderer.RenderUranium(particle)
			elif isinstance(particle, AlphaParticle):
				self.renderer.RenderAlphaParticle(particle, delta)

		pygame.display.flip()

	def main(self):
		pygame.init()
		pygame.font.init()

		self.font = pygame.font.SysFont("freesans", 30)

		for m in get_monitors():
			if m.is_primary:
				self.dim = (m.width, m.height)
		
		self.window = pygame.display.set_mode(self.dim, pygame.NOFRAME | pygame.SCALED, display = 0, vsync = 1)

		tps = 60.0
		tickMS = 1000.0 / tps

		tickDelta = 0

		lastTick = pygame.time.get_ticks()

		self.Start()

		while self.running:
			self.Input()

			nowTick_pygame = pygame.time.get_ticks()
			tickDelta += float(nowTick_pygame-lastTick)/tickMS
			lastTick = nowTick_pygame

			while not tickDelta < 1.0:
				if tickDelta > 10.0:
					tickDelta -= 10.0
				self.FixedUpdate()
				tickDelta -= 1.0

			self.Render(tickDelta)

if __name__ == "__main__":
	g = GameInstance()
	g.main()