import pytest
from typeguard import typechecked, TypeCheckError


def test_typechecked():
    @typechecked
    def add_numbers(a: int, b: int) -> int:
        return a + b

    assert add_numbers(2, 3) == 5

    with pytest.raises(TypeCheckError):
        add_numbers(2, "3")

    @typechecked
    def return_string(a: int) -> int:
        return str(a)

    with pytest.raises(TypeCheckError):
        return_string(5)
