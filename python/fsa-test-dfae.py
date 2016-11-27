#!/usr/bin/env python3

import fsa

class A (fsa.DFAe):
	class Start: pass
	class Emit:  pass

	def on_start (self, a):
		if a == fsa.EOI:
			return (A.Start, True)

		if a == 'a' or a == 'b':
			self.emit (a)
			return (A.Start, True)

		if a == 'c':
			return (A.Start, True)

		if a == 'e':
			return (A.Emit, False)

		raise ValueError ('Wrong input on start')

	def on_emit (self, a):
		self.emit (a)
		self.emit (a)
		return (A.Start, True)

test = A (A.Start)

try:
	for i in test.run ('aab'):
		print (i)

	for i in test.run ('baceaad'):
		print (i)
except ValueError as e:
	print ('running A failed with:', e)
