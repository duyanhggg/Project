def func_a(value):
    digits = list(str(value))
    digits.sort(reverse=True)
    return int(''.join(digits))

def func_b(value):
    digits = list(str(value))
    digits.sort()
    for i in range(len(digits)):
        if digits[i] != '0':
            digits[0], digits[i] = digits[i], digits[0]
            break
    return int(''.join(digits))

def func_c(value1, value2, value3):
    if abs(value1 - value3) > abs(value2 - value3):
        return value1
    return value2

def solution(num):
    maximum = func_a(num)
    minimum = func_b(num)
    return func_c(maximum, minimum, num)

if __name__ == "__main__":
    num = 9876
    print(solution(num))


    num = 3587
    print(solution(num))