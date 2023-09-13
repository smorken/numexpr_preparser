
# Infix pre-parser for [numexpr](https://github.com/pydata/numexpr)

This is an infix parser for the basic syntax outlined in the `numexpr` user guide.
It may not correctly parse every supported numexpr expression.

It is defined using the [pyparsing package](https://pypi.org/project/pyparsing/)

Not supported at this time/known issues
 * String constants are not yet supported, and will not be sucessfully parsed
 * the axis keyword in numexpr `sum` and `prod` will not be sucessfully parsed

It can be used as numexpr pre-parser/validator:

 * ensure string expressions are strictly infix expressions
 * get detailed error feedback for parsing errors via pyparsing
 * assert only function names that are supported in numexpr
 * assert identifiers are valid python identifiers
 * assert that only the numexpr unary and binary operators are used

constant values supported are:
 * floating point with scientific and complex notation
 * integers

Example usage:

Using as a pre-parser, to reject expressions that are not strictly infix
notation with the documented `numexpr` syntax

```python
import numexpr
from numexpr_preparser import parser as preparser

def numexpr_safe_evaluate(ex: str, *args, **kwargs):
    parse_success, results = parser.run_tests(ex)
    if not parse_success:
        raise ValueError(results[0][1])
    numexpr.evaluate(ex, *args, **kwargs)
```
