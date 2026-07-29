def digit(n: int, k: int) -> int:
    """Return the digit that is k from the right of n for positive integers n and k.

    >>> digit(3579, 2)
    5
    >>> digit(3579, 0)
    9
    >>> digit(3579, 10)
    0
    """
    return (n // pow(10, k)) % 10


def middle(a: int, b: int, c: int) -> int:
    """Return the number among a, b, and c that is not the smallest or largest.
    Assume a, b, and c are all different numbers.

    >>> middle(3, 5, 4)
    4
    >>> middle(30, 5, 4)
    5
    >>> middle(3, 5, 40)
    5
    >>> middle(3, 5, 40)
    5
    >>> middle(30, 5, 40)
    30
    """
    return a + b + c - max(a, b, c) - min(a, b, c)


def falling(n: int, k: int) -> int:
    """Compute the falling factorial of n to depth k.

    >>> falling(6, 3)  # 6 * 5 * 4
    120
    >>> falling(4, 3)  # 4 * 3 * 2
    24
    >>> falling(4, 1)  # 4
    4
    >>> falling(4, 0)
    1
    """
    ret: int = 1
    while k > 0:
        ret *= n
        n -= 1
        k -= 1
    return ret


def divisible_by_k(n: int, k: int) -> int:
    """
    >>> a = divisible_by_k(10, 2)  # 2, 4, 6, 8, and 10 are divisible by 2
    2
    4
    6
    8
    10
    >>> a
    5
    >>> b = divisible_by_k(3, 1)  # 1, 2, and 3 are divisible by 1
    1
    2
    3
    >>> b
    3
    >>> c = divisible_by_k(6, 7)  # There are no integers up to 6 divisible by 7
    >>> c
    0
    """
    count: int = 0
    while n > 0:
        if n % k == 0:
            print(n)
            count += 1
        n -= 1
    return count


def sum_digits(y: int) -> int:
    """Sum all the digits of y.

    >>> sum_digits(10) # 1 + 0 = 1
    1
    >>> sum_digits(4224) # 4 + 2 + 2 + 4 = 12
    12
    >>> sum_digits(1234567890)
    45
    >>> a = sum_digits(123) # make sure that you are using return rather than print
    >>> a
    6
    """
    s: int = 0
    while y > 0:
        s += y % 10
        y //= 10
    return s


def double_eights(n: int) -> bool:
    """Return true if n has two eights in a row.
    >>> double_eights(8)
    False
    >>> double_eights(88)
    True
    >>> double_eights(2882)
    True
    >>> double_eights(880088)
    True
    >>> double_eights(12345)
    False
    >>> double_eights(80808080)
    False
    """
    i: int = n % 10
    while n > 0:
        j: int = (n // 10) % 10
        if i == j:
            return True
        n //= 10
        i = j
    return False
