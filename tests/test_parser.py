"""
Run with:

  python -m py.test
"""

from typing import Any
import pytest

from parsemath import MathParser

@pytest.mark.parametrize('expr, expect', [
  ('1+2',                3),
  ('round(1.123+2/5)',   2),
  ('3*2',                6),
  ('2^2/4',              1.0),
  ('any(0, 0, 1)',       True),
  ('1.2 > 1',            True),
  ('2 == 3',             False),
  ('2 != 3',             True),
  ('1+3 == 2*2',         True),
  ('2/3',                0.6666666666666666),
])
def test_parser(expr:str, expect:Any):

  p = MathParser()

  result = p.eval(expr)
  print(expr, ' = ', result)
  assert result == expect

@pytest.mark.parametrize('expr', [
  ('1d20'),
  ('d20'),
  ('3d20'),
  ('1d5 + 2'),
  ('1d5 / 2.0'),
  ('1d5 > 0'),
  ('any(1d5, 1d5)'),
  ('sum(1d5, 1d5) / 2'),
])
def test_dice_rolls(expr:str):
  p = MathParser()
  result = p.eval(expr)
  print(expr, ' = ', result)

def test_make_railroad_diagram():
  # requires pyparsing==3.0.0b2 or newer, railroad-diagrams, and jinja2

  from pyparsing.diagram import to_railroad, railroad_to_html
  from pathlib import Path

  p = MathParser()
  p.expr.setName('MathParser')

  rr = to_railroad(p.expr)
  Path('parser_math_diagram.html').write_text(railroad_to_html(rr))
