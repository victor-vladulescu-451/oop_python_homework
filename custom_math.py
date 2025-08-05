import math


def nth_prime(count: int):

    primes: list[int] = [3]

    if count < 1:
        raise ValueError("Count must be higher than 0")
    elif count == 1:
        return 2
    elif count > 2:
        count -= 2
        candidate = primes[-1]
        while count > 0:
            candidate += 2
            is_prime = True
            limit = int(math.ceil(math.sqrt(candidate))) + 1
            for div in primes:
                if div > limit:
                    break
                elif candidate % div == 0:
                    is_prime = False
                    break

            if is_prime:
                primes.append(candidate)
                count -= 1

    return primes[-1]


def nth_fibonacci(count: int):
    if count < 1:
        raise ValueError("Count must be higher than 0")
    elif count == 1:
        return 0
    elif count == 2:
        return 1

    a, b = 0, 1
    for _ in range(2, count):
        a, b = b, a + b

    return b


def nth_pow(base: int, exponent: int):
    if exponent < 1:
        raise ValueError("Exponent must be higher than 0")
    return base ** exponent


def nth_factorial(count: int):
    if count < 1:
        raise ValueError("Count must be higher than 0")
    result = 1
    for i in range(2, count + 1):
        result *= i
    return result


def nth_sum_of_natural_numbers(count: int):
    if count < 1:
        raise ValueError("Count must be higher than 0")
    return count * (count + 1) // 2