# ParseMath

A [PyParsing][PyParsing] math parser adapted from the [example][example] that
evaluates simple math expressions.

[PyParsing]: https://github.com/pyparsing/pyparsing
[example]: https://github.com/pyparsing/pyparsing/blob/master/examples/fourFn.py

## Usage

```python
from parsemath import MathParser

p = MathParser()
result = p.eval('1 + 2')
assert result == 3
```

## Setup

The steps below will create the development environment and run the tests.

```bash
# Create a virtual environment
python3.8 -m venv .math

# Activate virtual environment
source .math/bin/activate

# Install python requirements
pip install -r requirements.txt

# Run tests
python -m py.test
```
