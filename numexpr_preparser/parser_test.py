import pytest
from mock import MagicMock
from mock import patch
from numexpr_preparser import parser


def test_passing_expressions():
    result, _ = parser.get_parser().runTests(
        [
            "where(a, 1, 2) ==  b",  # function argument list
            "b ** 1.59123",  # regular floating point numbers
            "c * 1+2e6",  # scientific notation floating point numbers
            "c - 1.0+2.0j",  # complex floating point numbers
            "d / 1+2j",  # complex integer numbers
            "e != 1+2e6j",  # scientific notation combined with complex number
            "1 + 2.0 + _abc + sin(cos(o))",  # nested function
            "1 + 2.0 + __abc",  # dunder "__abc" is technically valid
            "((c<32.0) | (d==-22.0))",  # boolean expression, nested brackets
            "z==True"  #
        ]
    )
    assert result


def test_failing_expressions():
    tests = [
        "eval(12)"  # unsupported function
        """(lambda fc=(
            lambda n: [
                c for c in
                    ().__class__.__bases__[0].__subclasses__()
                    if c.__name__ == n
                ][0]
            ):
            fc("function")(
                fc("Popen")("echo verybad",shell=True),{}
            )()
        )()""",  # see https://github.com/pydata/numexpr/issues/442
        "a = b",  # unsupported operator =
        "'string'",  # strings not yet supported
        "b'binary string'",  # strings not yet supported
    ]

    _parser = parser.get_parser()
    for test in tests:
        result, _ = _parser.run_tests(test)
        assert not result


def test_full_binary_operator_support():
    binary_operators = [
        # Bitwise operators (and, or, not, xor):
        "&",
        "|",
        "~",
        "^",
        # Comparison operators:
        "<",
        "<=",
        "==",
        "!=",
        ">=",
        ">",
        # Binary arithmetic operators:
        "+",
        "-",
        "*",
        "/",
        "**",
        "%",
        "<<",
        ">>",
    ]
    _parser = parser.get_parser()
    for op in binary_operators:
        result, _ = _parser.run_tests([f"a {op} b"])
        assert result


def test_numexpr_function_support():
    functions = parser.NUMEXPR_FUNCS

    _parser = parser.get_parser()
    tests = (
        [f"{f}(a)" for f in functions] +
        [f"{f}(1,a)" for f in functions]
    )
    result, out = _parser.run_tests(tests)
    if not result:
        raise
    assert result


def test_full_unary_operator_support():
    _parser = parser.get_parser()
    result, _ = _parser.run_tests(["a - b"])
    assert result


@patch("numexpr_preparser.parser.numexpr.evaluate")
def test_evaluate_safe_with_error(evaluate: MagicMock):
    with pytest.raises(ValueError):
        parser.numexpr_evaluate("non_supported_func(1) > 5")
        assert evaluate.call_count == 0


@patch("numexpr_preparser.parser.numexpr.evaluate")
def test_evaluate_wrapper(evaluate: MagicMock):
    parser.numexpr_evaluate("sin(a) > 5", 1, a=2)
    assert evaluate.call_count == 1
    evaluate.assert_called_once_with("sin(a) > 5", 1, a=2)
