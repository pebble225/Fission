from abc import ABC, abstractmethod
import time
import numpy as np

# it's just one of those tools that gets passed around now...

class RNG:
	def __init__(self, seed: int = 0):
		self.seed = seed

	@abstractmethod
	def nextInt32(self) -> int:
		raise NotImplementedError("This rng does not support 32 bit integer values.")
	
	@abstractmethod
	def nextInt64(self) -> int:
		raise NotImplementedError("This rng does not support 64 bit integer values.")
	
	@abstractmethod
	def nextFloat(self, scale: float = 1.0) -> float:
		raise NotImplementedError("This rng does not support floating point values.")

	@abstractmethod
	def floatRange(self, min: float, max: float):
		raise NotImplementedError("This rng does not support float range.")

	@abstractmethod
	def intRange(self, min: int, max: int):
		raise NotImplementedError("This rng does not support int range.")


class LCG(RNG):
	def __init__(self, m: int, a: int, c: int, seed: int = 0):
		RNG.__init__(self, seed)
		self.m = m
		self.a = a
		self.c = c
		if seed == 0:
			self.state = int(time.time())
		else:
			self.state = seed

	@staticmethod
	def NADS64bit(seed: int = 0) -> "LCG":
		lcg = LCG(18446744073709551616, 2862933555777941757, 3037000493, seed)
		return lcg
	
	def nextInt64(self) -> int:
		self.state = (self.a * self.state + self.c) % self.m
		return self.state

	def nextInt32(self):
		return self.nextInt64() & 0xFFFFFFFF

	def nextFloat(self, scale: float = 1.0) -> float:
		n = self.nextInt64()
		return (float(n)/float(self.m))*scale

	def floatRange(self, min: float, max: float):
		value = self.nextFloat(max-min+1)
		if not (value < max + 1):
			value -= 1.0
		return value + min

	def intRange(self, min: int, max: int):
		value = self.nextFloat(max-min+1)
		if not (value < max + 1):
			value -= 1.0 #astronomically unlikely
		return int(value) + min


if __name__ == "__main__":
	ran = LCG.NADS64bit()
	for i in range(100):
		print(ran.intRange(1, 4) < 4)