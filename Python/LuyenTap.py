# Bài 1 Cospro
plants = input().split()
collection = input().split()
in_plans = True
for col in collection:
    if col not in plants:
        in_plans = False
        break
def List_of_plants(plants, collection):
    collection_set = set(collection)
    collectibles = 0
    for plant in plants:
        if plant not in collection_set:
            collectibles += 1
    return collectibles
print(List_of_plants(plants, collection))



# Bài 2 Cospro
def solution(msg):
    answer = True
    msg_clean=""
    
    for letter in msg:
        if letter not in " ,.?":
            msg_clean += letter
            
    middle = len(msg_clean) // 2
    
    for i in range(middle + 1):
        left_letter = msg_clean[i]
        right_letter = msg_clean[len(msg_clean) - 1 - i]
        
        if left_letter != right_letter:
            answer = False
            break
    
    return answer

msg = input()
print(solution(msg))