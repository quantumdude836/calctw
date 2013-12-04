#!/usr/bin/env python

class Expr:
	_cached_val = False

	def _inner_value(self, env):
		pass

	def value(self, env):
		if self._is_const:
			if not self._cached_val:
				self._cached_val = self._inner_value(env)
			return self._cached_val
		return self._inner_value(env)

class ConstExpr(Expr):
	def __init__(self, val):
		self._val = val
		self._is_const = True

	def _inner_value(self, env):
		return self._val

class VarExpr(Expr):
	def __init__(self, var):
		self._var = var
		self._is_const = False
	
	def _inner_value(self, env):
		return env[self._var]

bin_ops = { }
bin_ops['+'] = lambda x, y: x + y
bin_ops['-'] = lambda x, y: x - y
bin_ops['*'] = lambda x, y: x * y
bin_ops['/'] = lambda x, y: x / y
bin_ops['%'] = lambda x, y: x % y
bin_ops['^'] = lambda x, y: x ** y

class BinaryExpr(Expr):
	def __init__(self, op, left, right):
		self._op = bin_ops[op]
		self._left = left
		self._right = right
		self._is_const = left._is_const and right._is_const

	def _inner_value(self, env):
		return self._op(self._left.value(env), self._right.value(env))

class NegExpr(Expr):
	def __init__(self, inner):
		self._inner = inner
		self._is_const = inner._is_const
	
	def _inner_value(self, env):
		return -self._inner.value(env)

# expression grammar:
#	$ -> E
#	E -> E '+' T
#	E -> E '-' T
#	E -> T
#	T -> T '*' F
#	T -> T '/' F
#	T -> T '%' F
#	T -> F
#	F -> N '^' F
#	F -> N
#	N -> '-' P
#	N -> P
#	P -> '(' E ')'
#	P -> num

def parse(text):
	return None
