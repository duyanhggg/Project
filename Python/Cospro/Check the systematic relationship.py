def func_a(value, arr):
    answer = []
    for num1, num2 in arr:
        if value == num2:
            answer.append(num1)
    return answer

def func_b(src, dest, arr1, arr2):
    if arr1[dest]:
        return dest == src
    arr1[dest] = True
    
    connections = func_a(dest, prerequisites)
    for connection in connections:
        if func_b(src, connection, arr1, prerequisites):
            return True
    return False

def solution(prerequisites):
    for i in range(1, 100+1):
        visited = [False] * 101
        if func_b(i, i, visited, prerequisites):
            return True
    return False

if __name__ == "__main__":
    prerequisites = [[3, 2], [2, 1]]
    print(solution(prerequisites))