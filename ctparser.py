#!/usr/bin/env python

from ctexpr import *


# each tuple is (type, token)
def tokenize(line):
	pos = 0
	while pos < len(line):
		# skip whitespace
		while pos < len(line) and line[pos].isspace():
			pos += 1
		if pos == len(line):
			return
		# tokenize based on next char
		start = pos
		ch = line[pos]
		pos += 1
		if ch in "+-*/%^(),": # single-character operators
			yield (ch, ch)
		elif ch.isalpha(): # identifiers
			while pos < len(line) and line[pos].isalnum():
				pos += 1
			yield ("i", line[start:pos])
		elif ch.isdigit() or ch == '.': # numbers
			# tokenize similar to C preprocessing number - worry about validating it later
			while pos < len(line) and (line[pos].isalnum() or line[pos] == '.'):
				if line[pos] == 'E' or line[pos] == 'e':
					# check for a '+' or '-' (exponent sign)
					if pos + 1 < len(line) and (line[pos + 1] == '+' or line[pos + 1] == '-'):
						pos += 1
				pos += 1
			yield ("n", line[start:pos])
		else:
			raise SyntaxError


# expression grammar:
#	$ -> E eol
#	E -> E '+'/'-' T
#	E -> T
#	T -> T '*'/'/'/'%' F
#	T -> F
#	F -> N '^' F
#	F -> N
#	N -> '+'/'-' P
#	N -> P
#	P -> ident '(' ')'
#	P -> ident '(' L ')'
#	P -> '(' E ')'
#	P -> num
#	L -> E
#	L -> L ',' E

action = [
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ 'i':~2, 'n':~6 },
	{ '(':~3 },
	{ ')':~4, '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':9, '-':9, '*':9, '/':9, '%':9, '^':9, 'i':9, 'e':9, 'n':9, '(':9, ')':9, ',':9 },
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':12, '-':12, '*':12, '/':12, '%':12, '^':12, 'i':12, 'e':12, 'n':12, '(':12, ')':12, ',':12 },
	{ ')':~8, '+':~9, '-':~9 },
	{ '+':11, '-':11, '*':11, '/':11, '%':11, '^':11, 'i':11, 'e':11, 'n':11, '(':11, ')':11, ',':11 },
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':1, '-':1, '*':~11, '/':~11, '%':~11, '^':1, 'i':1, 'e':1, 'n':1, '(':1, ')':1, ',':1 },
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':3, '-':3, '*':3, '/':3, '%':3, '^':3, 'i':3, 'e':3, 'n':3, '(':3, ')':3, ',':3 },
	{ '+':6, '-':6, '*':6, '/':6, '%':6, '^':~14, 'i':6, 'e':6, 'n':6, '(':6, ')':6, ',':6 },
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':5, '-':5, '*':5, '/':5, '%':5, '^':5, 'i':5, 'e':5, 'n':5, '(':5, ')':5, ',':5 },
	{ '+':8, '-':8, '*':8, '/':8, '%':8, '^':8, 'i':8, 'e':8, 'n':8, '(':8, ')':8, ',':8 },
	{ '+':4, '-':4, '*':4, '/':4, '%':4, '^':4, 'i':4, 'e':4, 'n':4, '(':4, ')':4, ',':4 },
	{ '+':2, '-':2, '*':~11, '/':~11, '%':~11, '^':2, 'i':2, 'e':2, 'n':2, '(':2, ')':2, ',':2 },
	{ ')':~20, ',':~21 },
	{ '+':10, '-':10, '*':10, '/':10, '%':10, '^':10, 'i':10, 'e':10, 'n':10, '(':10, ')':10, ',':10 },
	{ '+':~1, '-':~1, 'i':~2, '(':~5, 'n':~6 },
	{ '+':~9, '-':~9, '*':14, '/':14, '%':14, '^':14, 'i':14, 'e':14, 'n':14, '(':14, ')':14, ',':14 },
	{ '+':~9, '-':~9, '*':13, '/':13, '%':13, '^':13, 'i':13, 'e':13, 'n':13, '(':13, ')':13, ',':13 },
	{ '+':~9, '-':~9, 'e':0 },
	{ '+':7, '-':7, '*':7, '/':7, '%':7, '^':7, 'i':7, 'e':7, 'n':7, '(':7, ')':7, ',':7 },
]

# each tuple is (nonterm, symbol_count)
reduction = [
	('$', 2),
	('E', 3),
	('E', 1),
	('T', 3),
	('T', 1),
	('F', 3),
	('F', 1),
	('N', 2),
	('N', 1),
	('P', 3),
	('P', 4),
	('P', 3),
	('P', 1),
	('L', 1),
	('L', 3)
]

goto = [
	{ 'E':24, 'T':18, 'F':17, 'N':13, 'P':16 },
	{ },
	{ },
	{ 'L':19, 'E':23, 'T':18, 'F':17, 'N':13, 'P':16 },
	{ },
	{ 'E':7, 'T':18, 'F':17, 'N':13, 'P':16 },
	{ },
	{ },
	{ },
	{ 'T':10, 'F':17, 'N':13, 'P':16 },
	{ },
	{ 'F':12, 'N':13, 'P':16 },
	{ },
	{ },
	{ 'F':15, 'N':13, 'P':16 },
	{ },
	{ },
	{ },
	{ },
	{ },
	{ },
	{ 'E':22, 'T':18, 'F':17, 'N':13, 'P':16 },
	{ },
	{ },
	{ },
	{ }
]


def build_ast(tokens):
	stack = [(0, None)]
	n = 0
	while True:
		state = stack[-1][0]
		todo = action[state][tokens[n][0]]
		# negative values indicate shift actions, positive indicate reduce actions
		if todo == 0:
			# accept state
			break
		elif todo < 0:
			# shift
			stack.append((~todo, tokens[n]))
			n += 1
		else:
			# reduce
			popped = []
			reduct = reduction[todo]
			for i in range(reduct[1]):
				s = stack.pop()
				popped.append(s[1])
			popped.reverse()
			# goto
			g = goto[stack[-1][0]][reduct[0]]
			stack.append((g, (reduct[0], todo, popped)))

	return stack[-1][1]


def print_ast(ast, indent):
	if len(ast) == 2:
		print " " * indent + ast[0] + ": " + ast[1]
	else:
		print " " * indent + ast[0]
		for s in ast[2]:
			print_ast(s, indent + 2)


def condense(ast):
	# TODO: maybe not hardcode?

	# grab reduction rule number
	reduct = ast[1]
	# rule 0 will never appear (as it is treated as accept in the parser)
	if reduct == 1:
		# E -> E '+'/'-' T
		l = condense(ast[2][0])
		r = condense(ast[2][2])
		return BinExpr(l, ast[2][1][1], r)
	elif reduct == 2:
		# E -> T
		return condense(ast[2][0])
	elif reduct == 3:
		# T -> T '*'/'/'/'%' F
		l = condense(ast[2][0])
		r = condense(ast[2][2])
		return BinExpr(l, ast[2][1][1], r)
	elif reduct == 4:
		# T -> F
		return condense(ast[2][0])
	elif reduct == 5:
		# F -> N '^' F
		l = condense(ast[2][0])
		r = condense(ast[2][2])
		return BinExpr(l, ast[2][1][1], r)
	elif reduct == 6:
		# F -> N
		return condense(ast[2][0])
	elif reduct == 7:
		# N -> '+'/'-' P
		inner = condense(ast[2][1])
		return UnExpr(ast[2][0][1], inner)
	elif reduct == 8:
		# N -> P
		return condense(ast[2][0])
	elif reduct == 9:
		# P -> ident '(' ')'
		return FuncExpr(ast[2][0][1], [])
	elif reduct == 10:
		# P -> ident '(' L ')'
		args = condense(ast[2][2])
		return FuncExpr(ast[2][0][1], args)
	elif reduct == 11:
		# P -> '(' E ')'
		return condense(ast[2][1])
	elif reduct == 12:
		# P -> num
		# this is where numbers are actually verified
		return ConstExpr(float(ast[2][0][1]))
	elif reduct == 13:
		# L -> E
		return [condense(ast[2][0])]
	elif reduct == 14:
		# L -> L ',' E
		rest = condense(ast[2][0])
		last = condense(ast[2][2])
		rest.append(last)
		return rest

	print reduct
	raise Exception("shouldn't be here")


def parse(text):
	# tokenize line
	tokens = [t for t in tokenize(text)]
	tokens.append(("e", ""))

	# construct AST
	ast = build_ast(tokens)
	#print_ast(ast, 0)

	# condense AST into expression tree
	tree = condense(ast)

	return tree
