from pyparsing import (
    infix_notation,
    one_of,
    OpAssoc,
    Forward,
    Group,
    Suppress,
    Optional,
    delimited_list,
    ParserElement,
    QuotedString,
)
import numexpr
from pyparsing.common import pyparsing_common

LPAREN, RPAREN = map(Suppress, "()")
NUMEXPR_FUNCS = [
    "where",
    "sin",
    "cos",
    "tan",
    "arcsin",
    "arccos",
    "arctan",
    "arctan2",
    "sinh",
    "cosh",
    "tanh",
    "arcsinh",
    "arccosh",
    "arctanh",
    "log",
    "log10",
    "log1p",
    "exp",
    "expm1",
    "sqrt",
    "abs",
    "conj",
    "real",
    "imag",
    "complex",
    "contains",
    "sum",
    "prod",
]


def get_parser() -> Forward:
    """Get a parser for validation of a infix expressions
    for the numexpr package, based on the functions,
    operators and constants support found in the numexpr
    user guide.

    Returns:
        Forward: pyparsing.Forward object
    """
    ParserElement.enablePackrat()
    integer = pyparsing_common.integer
    real = pyparsing_common.real | pyparsing_common.sci_real
    double_quoted = QuotedString('"')
    single_quoted = QuotedString('"')
    imaginary = (real | integer) + one_of("j J")
    arith_expr = Forward()
    fn_call = Group(
        one_of(NUMEXPR_FUNCS)
        + LPAREN
        - Group(Optional(delimited_list(arith_expr)))
        + RPAREN
    )
    operand = (
        fn_call
        | imaginary
        | real
        | integer
        | double_quoted
        | single_quoted
        | pyparsing_common.identifier
    )

    bitwise_operators = one_of("& | ~ ^")
    comparison_operators = one_of("< <= == != >= >")
    unary_arithmetic = one_of("-")
    binary_arithmetic = one_of("+ - * / ** % << >>")

    arith_expr << infix_notation(
        operand,
        [
            (bitwise_operators, 2, OpAssoc.LEFT, None),
            (comparison_operators, 2, OpAssoc.LEFT, None),
            (unary_arithmetic, 1, OpAssoc.RIGHT, None),
            (binary_arithmetic, 2, OpAssoc.LEFT, None),
        ],
    )

    return arith_expr


def numexpr_evaluate(ex: str, *args, **kwargs):
    """
    Pre-expression-parsing wrapper for numexpr.evaulate

    Validates the ex arg with a parser returned by `get_parser`
    and raises an error if parsing of that expression fails.
    *args **kwargs are passed directly to `numexpr.evaluate` if
    pre-parsing succeeds.

    Args:
        ex (str): the expression to validate and potentially pass
            on to `numexpr.evaluate`.

    Raises:
        ValueError: The expression parsing failed, information
            derived from `pyparsing` about the error is returned.

    Returns:
        Any: the returned value from numexpr
    """
    parse_success, parse_results = get_parser().run_tests(
        ex, print_results=False
    )
    if not parse_success:
        raise ValueError(parse_results[0][1])
    return numexpr.evaluate(ex, *args, **kwargs)
