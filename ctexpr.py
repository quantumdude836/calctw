#!/usr/bin/env python

import math


class Expr:
	_cached_val = None


	def _inner_value(self, env):
		# actual evaluator to be implemented by subclasses
		# env is a dictionary to be used by functions
		pass


	def value(self, env):
		# for constant expressions, just cache the value
		if self._is_const:
			if not self._cached_val:
				self._cached_val = self._inner_value(env)
			return self._cached_val
		else:
			return self._inner_value(env)


# numeric constants
class ConstExpr(Expr):
	def __init__(self, val):
		self._val = val
		self._is_const = True
	

	def _inner_value(self, env):
		return self._val


# table of binary expression lambdas
bin_ops = {
	'+':lambda x, y: x + y,
	'-':lambda x, y: x - y,
	'*':lambda x, y: x * y,
	'/':lambda x, y: x / y,
	'%':lambda x, y: x % y,
	'^':lambda x, y: x ** y
}


# binary expressions
class BinExpr(Expr):
	def __init__(self, left, op, right):
		self._left = left
		self._op = bin_ops[op]
		self._right = right
		self._is_const = left._is_const and right._is_const
	

	def _inner_value(self, env):
		return self._op(self._left.value(env), self._right.value(env))


# table of unary expression lambdas
un_ops = {
	'+':lambda x: x,
	'-':lambda x: -x
}


# unary expressions
class UnExpr(Expr):
	def __init__(self, op, inner):
		self._op = un_ops[op]
		self._inner = inner
		self._is_const = inner._is_const
	

	def _inner_value(self, env):
		return self._op(self._inner.value(env))


# table of function objects (is_const, func_lambda)
funcs = {
	"sin":(True, lambda env, x: math.sin(x)),
	"cos":(True, lambda env, x: math.cos(x)),
	"tan":(True, lambda env, x: math.tan(x)),
	"abs":(True, lambda env, x: abs(x)),
	"pi":(True, lambda env: math.pi
}

# function expressions
class FuncExpr(Expr):
	def __init__(self, func, args):
		fn = funcs[func]
		self._func = fn[1]
		self._args = args
		self._is_const = fn[0] and all(a._is_const for a in args)
	

	def _inner_value(self, env):
		args = [a.value(env) for a in self._args]
		return self._func(env, *args)
