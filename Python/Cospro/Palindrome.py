def solution(msg):
    answer = True
    msg_clean=""
    
    for letter in msg:
        if letter not in " ,.?":
            msg_clean += letter
            
    middle = len(msg_clean) // 2
    
    for i in range(middle + 1):
        left_letter = msg_clean[i]
        right_letter = msg_clean[-(i + 1)] 
        
        if left_letter != right_letter:
            answer = False
            break
    
    return answer


if __name__ == "__main__":
    msg = "murder for a jar of red rum."
    print(solution(msg))
    