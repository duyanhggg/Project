def func_a(times):
    hour = int(times[:2])
    minute = int(times[3:])
    return hour*60 + minute

def solution(subway_times, current_time):
    current_minute = func_a(current_time)
    INF = 1000000000
    answer = INF
    for s in subway_times:
        subway_minute = func_a(s)  # Changed from subway_times to s
        if subway_minute >= current_minute:
            answer = subway_minute - current_minute
            break
    if answer == INF:
        return -1
    return answer


if __name__ == "__main__":
    subway_times = ('05:31', '11:59', '13:30', '23:32')
    current_time = '12:00'
    print(solution(subway_times, current_time))