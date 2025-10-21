n = int(input("Enter a positive integer n:"))
count = 0
for i in range(1, n + 1):
    if i % 2 == 0:
        count += 1
print(f"The number of even elements is: {count}")   