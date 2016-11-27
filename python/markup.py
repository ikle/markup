import fsa
import re

def order (s):
	i = 0

	def roundup (x, to):
		return (x + to) // to * to

	for a in s:
		if a == '\t':
			i = roundup (i, 8)
		else:
			i += 1

	return i

class Plain (object):
	def __init__ (o, data):
		o.data = data

	def head (o):
		return '(' + type (o).__name__

	def __repr__ (o):
		return o.head () + ' ' + repr (o.data) + ')'

class Group (Plain):
	def __repr__ (o):
		def view ():
			for i in o.data:
				yield repr (i)

		return o.head () + ' [' + ', '.join (view ()) + '])'

class Head (Group):
	def __init__ (o, level, data):
		o.level = level
		o.data  = data

	def head (o):
		return super ().head () + ' ' + repr (o.level)

class Dict (Group):
	def __init__ (o, tag, data):
		o.tag  = tag
		o.data = data

	def head (o):
		return super ().head () + ' ' + repr (o.tag)

class Line (Plain):
	def __init__ (o, indent, data):
		o.indent = indent
		o.data   = data

	def head (o):
		return super ().head () + ' ' + repr (o.indent)

class EmptyLine: pass

class Code (Plain): pass
class Para (Plain): pass
class List (Group): pass
class Enum (Group): pass

def parse_regular (lines):
	def tokenize (lines):
		for l in lines:
			if type (l) != str:
				raise ValueError ('string expected')

			if l == '':
				yield EmptyLine
			elif l[0] == ' ':
				yield Code ([l])
			else:
				yield Para (l)

	class Parser (fsa.DFAe):
		class Start:  pass
		class Work:   pass
		class Empty:  pass

		def on_start (o, l):
			if l == fsa.EOI or l == EmptyLine:
				return (o.Start, True)

			o.line = l
			return (o.Work, True)

		def on_work (o, l):
			if l == fsa.EOI:
				o.emit (o.line)
				return (o.Start, True)

			if l == EmptyLine:
				o.count = 1
				return (o.Empty, True)

			if type (l) != type (o.line):
				o.emit (o.line)
				return (o.Start, False)

			if type (l) == Para:
				o.line.data += ' ' + l.data
				return (o.Work, True)

			o.line.data.append (l.data[0])
			return (o.Work, True)

		def on_empty (o, l):
			if l == fsa.EOI:
				o.emit (o.line)
				return (o.Start, True)

			if l == EmptyLine:
				o.count += 1
				return (o.Empty, True)

			if type (l) == Code and type (o.line) == Code:
				for i in range (o.count):
					o.line.data.append ('')
				return (o.Work, False)

			o.emit (o.line)
			return (o.Start, False)

	return Parser (Parser.Start).run (tokenize (lines))

def parse (lines):
	def tokenize (lines):
		for l in lines:
			if type (l) != str:
				raise ValueError ('string expected')

			m = re.match (r'(#+) +(.+)', l)
			if m:
				yield Head (len (m.group (1)), m.group (2))
				continue

			m = re.match (r'\* +(.+)', l)
			if m:
				yield List (m.group (1))
				continue

			m = re.match (r'\d+\. +(.+)', l)
			if m:
				yield Enum (m.group (1))
				continue

			m = re.match (r'\[([^]]+)\] +(.*)', l)
			if m:
				yield Dict (m.group (1), m.group (2))
				continue

			m = re.match (r'[ \t]*$', l)
			if m:
				yield EmptyLine
				continue

			m = re.match (r'([ \t]*)(.+)', l)
			if m:
				yield Line (order (m.group (1)), m.group (2))
				continue

	class Parser (fsa.DFAe):
		class Start:  pass
		class Indent: pass
		class Work:   pass
		class Empty:  pass

		def is_good (o, l):
			return type (l) == Line and o.indent <= l.indent

		def accumulate (o, l):
			o.line.data.append (' ' * (l.indent - o.indent) + l.data)

		def on_start (o, l):
			if l == fsa.EOI:
				o.emit ()
				return (o.Start, True)

			if l == EmptyLine:
				return (o.Start, True)

			o.line = l
			o.line.data = [o.line.data]

			if type (l) == Line:
				o.indent = l.indent
				return (o.Work, True)

			return (o.Indent, True)

		def on_indent (o, l):
			if l == fsa.EOI:
				o.emit ()
				return (o.Start, True)

			if l == EmptyLine:
				o.count = 1
				return (o.Empty, True)

			if type (l) != Line:
				o.emit ()
				return (o.Start, False)

			o.indent = l.indent
			o.line.data.append (l.data)
			return (o.Work, True)

		def on_work (o, l):
			if l == fsa.EOI:
				o.emit ()
				return (o.Start, True)

			if l == EmptyLine:
				o.count = 1
				return (o.Empty, True)

			if o.is_good (l):
				o.accumulate (l)
				return (o.Work, True)

			o.emit ()
			return (o.Start, False)

		def on_empty (o, l):
			if l == fsa.EOI:
				o.emit ()
				return (o.Start, True)

			if l == EmptyLine:
				o.count += 1
				return (o.Empty, True)

			if o.is_good (l):
				for i in range (o.count):
					o.line.data.append ('')
				o.accumulate (l)
				return (o.Work, True)

			o.emit ()
			return (o.Start, False)

		def emit (o):
			if type (o.line) == Line:
				for i in parse_regular (o.line.data):
					super ().emit (i)
			else:
				o.line.data = parse (o.line.data)
				super ().emit (o.line)

	return Parser (Parser.Start).run (tokenize (lines))
