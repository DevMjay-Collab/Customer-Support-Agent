import pytest
from calculator import add, divide, format_result, multiply, subtract
from calculator_gui import evaluate_expression


def test_basic_operations() -> None:
    assert add(2, 3) == 5
    assert subtract(9, 4) == 5
    assert multiply(2.5, 4) == 10
    assert divide(15, 3) == 5


def test_division_by_zero_is_rejected() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)


def test_result_formatting() -> None:
    assert format_result(4.0) == "4"
    assert format_result(2.5) == "2.5"


def test_gui_expression_evaluation() -> None:
    assert evaluate_expression("2 + 3 * 4") == 14
    assert evaluate_expression("-5 / 2") == -2.5


def test_gui_rejects_invalid_expression() -> None:
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        evaluate_expression("1 / 0")
