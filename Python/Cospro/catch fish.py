def solution(fishes, k, n):
    counter = [0] * 61
    for fish in fishes:
        counter[fish] += 1
    
    cnt = 0
    for i in range(1, k+1):
        cnt += counter[i]
    for i in range(k+1, 61):
        if cnt >= n:
            return True
        cnt += i
        cnt -= counter[i - k]
    return False

if __name__ == "__main__":
    fishes = [28, 37 ,28 ,1 ,30, 27 ,42 ,50 ,55 ,31]
    k = 10
    n = 4
    print(solution(fishes, k, n))