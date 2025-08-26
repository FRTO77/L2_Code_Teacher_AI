from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TestCase:
    description: str
    input_args: List[Any]
    input_kwargs: Dict[str, Any]
    expected_output: Any


@dataclass
class Task:
    id: str
    title: str
    description: str
    function_name: str
    starter_code: str
    tests: List[TestCase]


def _task_sum_two_numbers() -> Task:
    starter = '''
def sum_two_numbers(a: int, b: int) -> int:
    """Return the sum of a and b."""
    # Write your solution below
    return a + b
'''.strip()
    tests = [
        TestCase("small positives", [1, 2], {}, 3),
        TestCase("with zero", [0, 5], {}, 5),
        TestCase("negatives", [-3, -7], {}, -10),
    ]
    return Task(
        id="sum_two_numbers",
        title="Sum Two Numbers",
        description="Implement sum_two_numbers(a, b) -> int that returns a + b.",
        function_name="sum_two_numbers",
        starter_code=starter,
        tests=tests,
    )


def _task_is_palindrome() -> Task:
    starter = '''
def is_palindrome(s: str) -> bool:
    """Return True if s reads the same forwards and backwards (case-insensitive, ignore spaces)."""
    s_clean = ''.join(ch.lower() for ch in s if not ch.isspace())
    return s_clean == s_clean[::-1]
'''.strip()
    tests = [
        TestCase("racecar", ["racecar"], {}, True),
        TestCase("mixed case", ["RaceCar"], {}, True),
        TestCase("with space", ["nurses run"], {}, True),
        TestCase("not palindrome", ["python"], {}, False),
    ]
    return Task(
        id="is_palindrome",
        title="Palindrome Checker",
        description="Return True if a string is a palindrome (case-insensitive, ignoring spaces).",
        function_name="is_palindrome",
        starter_code=starter,
        tests=tests,
    )


def _task_fizz_buzz() -> Task:
    starter = '''
def fizz_buzz(n: int) -> str:
    """Return 'Fizz' for multiples of 3, 'Buzz' for multiples of 5, 'FizzBuzz' for both, else str(n)."""
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
'''.strip()
    tests = [
        TestCase("3 -> Fizz", [3], {}, "Fizz"),
        TestCase("5 -> Buzz", [5], {}, "Buzz"),
        TestCase("15 -> FizzBuzz", [15], {}, "FizzBuzz"),
        TestCase("2 -> '2'", [2], {}, "2"),
    ]
    return Task(
        id="fizz_buzz",
        title="FizzBuzz",
        description="Classic FizzBuzz problem.",
        function_name="fizz_buzz",
        starter_code=starter,
        tests=tests,
    )


def _task_factorial() -> Task:
    starter = '''
def factorial(n: int) -> int:
    """Return n! for n >= 0; raise ValueError for negative n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
'''.strip()
    tests = [
        TestCase("0!", [0], {}, 1),
        TestCase("1!", [1], {}, 1),
        TestCase("5!", [5], {}, 120),
    ]
    return Task(
        id="factorial",
        title="Factorial",
        description="Compute factorial of n (iterative).",
        function_name="factorial",
        starter_code=starter,
        tests=tests,
    )


def _task_reverse_string() -> Task:
    starter = '''
def reverse_string(s: str) -> str:
    """Return the reversed string."""
    return s[::-1]
'''.strip()
    tests = [
        TestCase("simple", ["abc"], {}, "cba"),
        TestCase("empty", [""], {}, ""),
        TestCase("unicode", ["Привет"], {}, "тевирП"),
    ]
    return Task(
        id="reverse_string",
        title="Reverse String",
        description="Return the reversed string.",
        function_name="reverse_string",
        starter_code=starter,
        tests=tests,
    )


def get_tasks() -> List[Task]:
    return [
        _task_sum_two_numbers(),
        _task_is_palindrome(),
        _task_fizz_buzz(),
        _task_factorial(),
        _task_reverse_string(),
    ]
