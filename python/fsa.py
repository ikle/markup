# Finite-State Automata module

# end-of-input marker
class EOI: pass

class DFA (object):
	def __init__ (self, start):
		self.state   = start
		self.actions = {}

	def step (self, item):
		def get_action_name (state):
			name = 'on'

			for a in state.__name__:
				if a.isupper ():
					name += '_' + a.lower ()
				else:
					name += a

			return name

		if not self.state in self.actions:
			name = get_action_name (self.state)
			self.actions[self.state] = getattr (self, name)

		self.queue = []
		return self.actions[self.state] (item)

	def emit (self, obj):
		self.queue.append (obj)

	def run (self, seq):
		for i in seq:
			self.state = self.step (i)
			for o in self.queue: yield o

		self.state = self.step (EOI)
		for o in self.queue: yield o

class DFAe (DFA):
	def run (self, seq):
		for i in seq:
			while True:
				self.state, consume = self.step (i)
				for o in self.queue: yield o
				if consume: break

		while True:
			self.state, consume = self.step (EOI)
			for o in self.queue: yield o
			if consume: break
