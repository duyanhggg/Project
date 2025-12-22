def func_a(arr, value):
    for i in range(4):
        for j in range(4):
            if arr[i][j] == value:
                return (i, j)

def func_b(val1, val2):
    if val1 > val2:
        return val1 - val2
    return val2 - val1

def func_c(val1, val2):
    answer = func_b(val1[0], val2[0])
    answer += func_b(val1[1], val2[1])
    return answer
            
def solution(board, orders):
    grid = [list(board[i]) for i in range(4)]
    current = (0, 0)
    answer = 0
    for order in orders:
        target = func_a(grid, order)
        answer += func_c(current, target)
        current = target
    return answer

# Bạn có thể thêm code ở dưới đây


if __name__ == "__main__":
    board = ["AJOF", "NICP", "DMBL", "EKHG"]
    orders = "FMJA"
    print(solution(board, orders))