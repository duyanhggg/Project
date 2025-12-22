def solution(year, month):
    answer = 0
    if month == 2:
        if (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0):
            answer = 29
        else:
            answer = 28
    elif month == (4,6,9,11):
        answer = 30
    else:
        answer = 31
    return answer


if __name__ == "__main__":
    year = 1989
    month = 2
    print(solution(year, month))