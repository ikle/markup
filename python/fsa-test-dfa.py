#!/usr/bin/env python3

import fsa

class A (fsa.DFA):
	class Start: pass

	def on_start (self, a):
		if a == fsa.EOI:
			return A.Start

		if a == 'a' or a == 'b':
			self.emit (a)
			return A.Start

		if a == 'c':
			return A.Start

		raise ValueError ('Wrong input on start')

test = A (A.Start)

try:
	for i in test.run ('aab'):
		print (i)

	for i in test.run ('bacaad'):
		print (i)
except ValueError as e:
	print ('running A failed with:', e)
