
from fastmcp import FastMCP
import math
import statistics

mcp = FastMCP("Mathematics MCP Server 🚀")


# ============================================================
# BASIC ARITHMETIC
# ============================================================

@mcp.tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool
def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@mcp.tool
def modulus(a: float, b: float) -> float:
    """Return the remainder of a divided by b."""
    if b == 0:
        raise ValueError("Cannot use modulus with zero.")
    return a % b


# ============================================================
# POWERS AND ROOTS
# ============================================================

@mcp.tool
def power(base: float, exponent: float) -> float:
    """Calculate base raised to exponent."""
    return base ** exponent


@mcp.tool
def square(number: float) -> float:
    """Calculate the square of a number."""
    return number ** 2


@mcp.tool
def cube(number: float) -> float:
    """Calculate the cube of a number."""
    return number ** 3


@mcp.tool
def square_root(number: float) -> float:
    """Calculate the square root of a non-negative number."""
    if number < 0:
        raise ValueError("Square root of a negative number is not real.")
    return math.sqrt(number)


@mcp.tool
def nth_root(number: float, n: float) -> float:
    """Calculate the nth root of a number."""
    if n == 0:
        raise ValueError("Root degree cannot be zero.")

    if number < 0 and int(n) % 2 == 0:
        raise ValueError("Even root of a negative number is not real.")

    if number < 0:
        return -((-number) ** (1 / n))

    return number ** (1 / n)


# ============================================================
# LOGARITHMS AND EXPONENTIALS
# ============================================================

@mcp.tool
def natural_log(number: float) -> float:
    """Calculate natural logarithm (ln)."""
    if number <= 0:
        raise ValueError("Logarithm requires a positive number.")
    return math.log(number)


@mcp.tool
def logarithm(number: float, base: float = 10) -> float:
    """Calculate logarithm of a number with a specified base."""
    if number <= 0:
        raise ValueError("Number must be positive.")

    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and not equal to 1.")

    return math.log(number, base)


@mcp.tool
def exponential(number: float) -> float:
    """Calculate e raised to the given number."""
    return math.exp(number)


# ============================================================
# TRIGONOMETRY
# ============================================================

@mcp.tool
def sin_degrees(angle: float) -> float:
    """Calculate sine of an angle in degrees."""
    return math.sin(math.radians(angle))


@mcp.tool
def cos_degrees(angle: float) -> float:
    """Calculate cosine of an angle in degrees."""
    return math.cos(math.radians(angle))


@mcp.tool
def tan_degrees(angle: float) -> float:
    """Calculate tangent of an angle in degrees."""
    return math.tan(math.radians(angle))


@mcp.tool
def asin_degrees(value: float) -> float:
    """Calculate inverse sine and return the angle in degrees."""
    if value < -1 or value > 1:
        raise ValueError("Input must be between -1 and 1.")

    return math.degrees(math.asin(value))


@mcp.tool
def acos_degrees(value: float) -> float:
    """Calculate inverse cosine and return the angle in degrees."""
    if value < -1 or value > 1:
        raise ValueError("Input must be between -1 and 1.")

    return math.degrees(math.acos(value))


@mcp.tool
def atan_degrees(value: float) -> float:
    """Calculate inverse tangent and return the angle in degrees."""
    return math.degrees(math.atan(value))


# ============================================================
# FACTORIAL / COMBINATORICS
# ============================================================

@mcp.tool
def factorial(n: int) -> int:
    """Calculate factorial of a non-negative integer."""
    if n < 0:
        raise ValueError("Factorial requires a non-negative integer.")

    return math.factorial(n)


@mcp.tool
def permutation(n: int, r: int) -> int:
    """Calculate nPr."""
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= r >= 0.")

    return math.perm(n, r)


@mcp.tool
def combination(n: int, r: int) -> int:
    """Calculate nCr."""
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require n >= r >= 0.")

    return math.comb(n, r)


# ============================================================
# NUMBER THEORY
# ============================================================

@mcp.tool
def gcd(a: int, b: int) -> int:
    """Calculate greatest common divisor."""
    return math.gcd(a, b)


@mcp.tool
def lcm(a: int, b: int) -> int:
    """Calculate least common multiple."""
    return math.lcm(a, b)


@mcp.tool
def is_prime(n: int) -> bool:
    """Check whether a number is prime."""
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    for i in range(3, math.isqrt(n) + 1, 2):
        if n % i == 0:
            return False

    return True


# ============================================================
# ROUNDING
# ============================================================

@mcp.tool
def round_number(number: float, digits: int = 2) -> float:
    """Round a number to a specified number of decimal places."""
    return round(number, digits)


@mcp.tool
def absolute_value(number: float) -> float:
    """Return the absolute value."""
    return abs(number)


# ============================================================
# PERCENTAGES
# ============================================================

@mcp.tool
def percentage_of(percent: float, number: float) -> float:
    """Calculate a percentage of a number."""
    return (percent / 100) * number


@mcp.tool
def percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change from old value to new value."""
    if old_value == 0:
        raise ValueError("Old value cannot be zero.")

    return ((new_value - old_value) / old_value) * 100


@mcp.tool
def percentage_increase(value: float, percent: float) -> float:
    """Increase a value by a percentage."""
    return value * (1 + percent / 100)


@mcp.tool
def percentage_decrease(value: float, percent: float) -> float:
    """Decrease a value by a percentage."""
    return value * (1 - percent / 100)


# ============================================================
# STATISTICS
# ============================================================

@mcp.tool
def mean(numbers: list[float]) -> float:
    """Calculate arithmetic mean."""
    if not numbers:
        raise ValueError("List cannot be empty.")

    return statistics.mean(numbers)


@mcp.tool
def median(numbers: list[float]) -> float:
    """Calculate median."""
    if not numbers:
        raise ValueError("List cannot be empty.")

    return statistics.median(numbers)


@mcp.tool
def mode(numbers: list[float]) -> float:
    """Calculate mode."""
    if not numbers:
        raise ValueError("List cannot be empty.")

    return statistics.mode(numbers)


@mcp.tool
def variance(numbers: list[float]) -> float:
    """Calculate population variance."""
    if not numbers:
        raise ValueError("List cannot be empty.")

    return statistics.pvariance(numbers)


@mcp.tool
def standard_deviation(numbers: list[float]) -> float:
    """Calculate population standard deviation."""
    if not numbers:
        raise ValueError("List cannot be empty.")

    return statistics.pstdev(numbers)


# ============================================================
# GEOMETRY
# ============================================================

@mcp.tool
def circle_area(radius: float) -> float:
    """Calculate area of a circle."""
    if radius < 0:
        raise ValueError("Radius cannot be negative.")

    return math.pi * radius ** 2


@mcp.tool
def circle_circumference(radius: float) -> float:
    """Calculate circumference of a circle."""
    if radius < 0:
        raise ValueError("Radius cannot be negative.")

    return 2 * math.pi * radius


@mcp.tool
def rectangle_area(length: float, width: float) -> float:
    """Calculate area of a rectangle."""
    return length * width


@mcp.tool
def rectangle_perimeter(length: float, width: float) -> float:
    """Calculate perimeter of a rectangle."""
    return 2 * (length + width)


@mcp.tool
def triangle_area(base: float, height: float) -> float:
    """Calculate area of a triangle."""
    return 0.5 * base * height


@mcp.tool
def pythagorean(a: float, b: float) -> float:
    """Calculate hypotenuse using Pythagorean theorem."""
    return math.sqrt(a ** 2 + b ** 2)


# ============================================================
# CONSTANTS
# ============================================================

@mcp.tool
def pi() -> float:
    """Return the mathematical constant pi."""
    return math.pi


@mcp.tool
def e() -> float:
    """Return Euler's number."""
    return math.e

if __name__ == "__main__":
    mcp.run()

