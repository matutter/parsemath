"""
Adapted from: https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py
"""

import operator
from typing import *
from pyparsing import (CaselessKeyword, Group, Literal, ParseException, Regex, Suppress, Word,
                       alphanums, alphas, nums, Forward, delimitedList)
import math

import random

import logging

from pyparsing.results import ParseResults

log = logging.getLogger(__name__)

class MathParser:
    """
    MathParser usage.

    parser = MathParser()
    parser.eval('1+2') # = 3
    parser.eval('round(2/3)') # = 1
    parser.eval('1 > 2 or 2 > 1') # = True
    """

    stack: List[str]
    expr: Forward
    functions: MutableMapping[str, Callable]
    binary_ops: MutableMapping[str, Callable]
    constants: MutableMapping[str, Union[int, float]]

    def __init__(self):
        self.stack = []

        self.binary_ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '^': operator.pow,
            '>': operator.gt,
            '>=': operator.ge,
            '<': operator.lt,
            '<=': operator.le,
            '!=': operator.ne,
            '==': operator.eq,
            'or': operator.or_,
            'and': operator.and_
        }

        self.constants = {
            'PI': math.pi,
            'E': math.e
        }

        self.functions = {
            'sum': lambda *a: sum(a),
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'exp': math.exp,
            'hypot': math.hypot,
            'abs': abs,
            'trunc': int,
            'round': round,
            'sgn': lambda a: -1 if a < -math.e else 1 if a > math.e else 0,
            'multiply': lambda a, b: a * b,
            'all': lambda *a: all(a),
            'any': lambda *a: any(a)
        }

        # lang vars
        e = CaselessKeyword("E")
        pi = CaselessKeyword("PI")
        number = Regex(r"[+-]?\d+(?:\.\d*)?(?:[eE][+-]?\d+)?")
        number.setName('Number')
        ident = Word(alphas, alphanums + "_$")
        ident.setName('Ident')
        dice = Regex(r'\d?[dD]\d+')
        dice.setName('Dice')
        plus, minus, lt, le, gt, ge, eq, ne, or_, and_ = map(Literal, [
            '+', '-', '<', '<=', '>', '>=', '==', '!=', 'or', 'and'])
        bi_op = plus | minus | lt | le | gt | ge | eq | ne | or_ | and_
        bi_op.setName('LowBinaryOp')
        mult = Literal('*')
        div = Literal('/')
        multop = mult | div
        multop.setName('MediumBinaryOp')
        expop = Literal('^')
        expop.setName('HighBinaryOp')
        lpar = Suppress('(')
        rpar = Suppress(')')
        factor = Forward()
        expr = Forward()
        expr_list = delimitedList(Group(expr))
        expr_list.setName('ExpressionList')

        def dice_role(s:str) -> int:
            s = s.lower()
            if s.startswith('d'):
                count = 1
                limit = s[1:]
            else:
                count, limit = s.lower().split('d')
            count = int(count)
            limit = int(limit)
            sum = 0
            for _ in range(0, count):
                roll = random.randint(1, limit)
                sum += roll
            return sum

        def insert_fn_arg_count_tuple(t: Tuple) -> None:
            fn = t.pop(0)
            argc = len(t[0])
            t.insert(0, (fn, argc))

        def push(tokens) -> None:
            self.stack.append(tokens[0])

        def push_unary_minus(tokens) -> None:
            if '-' in tokens:
                push('unary -')

        import functools
        def push_dice(t:ParseResults) -> None:
            self.stack.append( functools.partial(dice_role, t[0]) )
        dice.setParseAction(push_dice)


        fn_call = ((ident + lpar - Group(expr_list) + rpar)
                   .setParseAction(insert_fn_arg_count_tuple))

        atom = dice | (bi_op[...] + (
            ((fn_call | pi | e | number | ident )
             .setParseAction(push))
            | Group(lpar + expr + rpar)
        ).setParseAction(push_unary_minus))


        factor <<= atom + (expop + factor).setParseAction(push)[...]
        term = factor + (multop + factor).setParseAction(push)[...]
        expr <<= term + (bi_op + term).setParseAction(push)[...]

        self.expr = expr
        expr.setName('Expression')
        factor.setName('Factor')
        atom.setName('Atom')
        term.setName('Term')

    def _eval_stack(self) -> Any:
        op, num_args = self.stack.pop(), 0
        if isinstance(op, tuple):
            op, num_args = op
        if op == 'unary -':
            return -self._eval_stack()

        if callable(op):
            return op()
        elif op in self.binary_ops:
            binary_op = self.binary_ops[op]
            op2 = self._eval_stack()
            op1 = self._eval_stack()
            return binary_op(op1, op2)
        elif op in self.constants:
            return self.constants[op]
        elif op in self.functions:
            fn = self.functions[op]
            args = reversed([self._eval_stack() for _ in range(num_args)])
            return fn(*args)
        elif op[0].isalpha():
            raise SyntaxError(f'Invalid identifier "{op}"')
        else:
            try:
                return int(op)
            except ValueError:
                return float(op)

    def eval(self, expression: str) -> Any:
        self.stack.clear()
        try:
            self.expr.parseString(expression, parseAll=True)
            val = self._eval_stack()
            return val
        except ParseException as e:
            err_type: str = type(e).__name__
            log.warn(
                f'Encountered {err_type} while evaluating "{expression}": {e}')
            raise


__all__ = ['MathParser']
