def func_a(arr):
    answer = [-1]
    for i in range(1, len(arr)):
        answer.append(arr[i] - arr[i-1])
    return answer

def func_b(arr):
    return arr[-1]

def func_c(arr):
    arr.sort()

def solution(sales):
    diff = func_a(sales)
    func_c(sales)
    return func_b(diff)


if __name__ == "__main__":
    sales_input = input("Nhập doanh thu (cách nhau bằng dấu phẩy hoặc khoảng trắng): ")
    # Tách bằng dấu phẩy hoặc khoảng trắng
    sales = list(map(int, sales_input.replace(',', ' ').split()))
    print(solution(sales))