string = input("Enter a string: ")
findnumber = []
sum = 0
for Characters in string:
    if Characters.isdigit():
        sum += int(Characters)
        findnumber.append(Characters)
print(f"The number of digits in the string is {findnumber}")
print(f"The digits in the string are {sum}")