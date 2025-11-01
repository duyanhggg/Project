# Bai 1
# Print personal information
def personal_info():
    name = input("Enter your name:")
    age = input("Enter your age:")
    school = input("Enter your school name:")
    print(f"Hello, my name is {name}. I am {age} years old and I study at {school}.")   
personal_info()

# Bai 2
# Calculate area and perimeter of a rectangle
def calculate_rectangle():
        length = float(input("Enter the length of the rectangle:"))
        width = float(input("Enter the width of the rectangle:"))
        area = length * width
        perimeter = 2 * (length + width)
        print(f"The area of the rectangle is: {area}")
        print(f"The perimeter of the rectangle is: {perimeter}")
calculate_rectangle()

# Bai 3
# Convert Celsius to Fahrenheit
def change_temperature():
    print("Choice 1: Convert Celsius to Fahrenheit")
    print("Choice 2: Convert Fahrenheit to Celsius")
    choice = input("Enter your choice (1 or 2):")
    if choice == '1':
        celsius = float(input("Enter temperature in Celsius:"))
        fahrenheit = (celsius * 9/5) + 32
        print(f"{celsius}°C is equal to {fahrenheit}°F")
    elif choice == '2':
        fahrenheit = float(input("Enter temperature in Fahrenheit:"))
        celsius = (fahrenheit - 32) * 5/9
        print(f"{fahrenheit}°F is equal to {celsius}°C")
    else:
        print("Invalid choice. Please select 1 or 2.")
change_temperature()

# Bai 4
# Cauculate the average of numbers
def calculate_average():
    math = float(input("Enter your Math score:"))
    literature = float(input("Enter your Literature score:"))
    english = float(input("Enter your English score:"))
    average = (math + literature + english) / 3
    print(f"Your average score is: {average}")
calculate_average()

# Bai 5
# String concatenation
def string_concatenation():
    str1 = input("Enter the first string:")
    str2 = input("Enter the second string:")
    concatenated_str = str1 + " " + str2
    print(f"The concatenated string is: {concatenated_str}")
string_concatenation()

# Bai 6
# Check even or odd
def check_even_odd():
    number = int(input("Enter an integer:"))
    if number % 2 == 0:
        print(f"{number} is an even number.")
    else:
        print(f"{number} is an odd number.")
check_even_odd()

# Bai 7
# Compare two numbers
def compare_numbers():
    number_1 = float(input("Enter the first number:"))
    number_2 = float(input("Enter the second number:"))
    if number_1 > number_2:
        print(f"{number_1} is greater than {number_2}.")
    elif number_1 < number_2:
        print(f"{number_1} is less than {number_2}.")
    else:
        print(f"{number_1} is equal to {number_2}.")
compare_numbers()

# Bai 8
# Acdermic rank
def academic_rank():
    score = float(input("Enter your score (0-10):"))
    if score >= 8:
        rank = "Good"
    elif score >= 6.5 and score < 7.9:
        rank = "Rather"
    elif score >= 5 and score < 6.4:
        rank = "Average"
    else:
        rank = "Weak"
    print(f"Your academic rank is: {rank}")
academic_rank()

# Bai 9
# Calulate electricity bill
def calculate_electricity_bill():
    kWh_consumed = float(input("Enter the number of kWh consumed:"))
    if kWh_consumed <= 50:
        bill = kWh_consumed * 1800
    elif kWh_consumed > 50 and kWh_consumed <= 100:
        bill = (50 * 1800) + ((kWh_consumed - 50) * 2000)
    else:
        bill = (50 * 1800) + (50 * 2000) + ((kWh_consumed - 100) * 2500)
    print(f"Your electricity bill is: {bill} VND")
calculate_electricity_bill()

# Bai 10
# Check leap year
def check_leap_year():
    year = int(input("Enter a year:"))
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        print(f"{year} is a leap year.")
    else:
        print(f"{year} is not a leap year.")
check_leap_year()

# Bai 11
# Print multiplication table
def multiplication_table():
    number = int(input("Enter an integer to print its multiplication table (0- 9):"))
    print(f"Multiplication table for {number}:")
    for i in range(1, 11):
        print(f"{number} x {i} = {number * i}")
multiplication_table()

# Bai 12
# Cauculate the sum from 1 to n
def sum_from_1_to_n():
    number = int(input("Enter a positive integer n:"))
    total = sum(range(1, number + 1))
    print(f"The sum from 1 to {number} is: {total}")
sum_from_1_to_n()

# Bai 13
# Count even numbers in a sequence
def count_even_numbers():
    number = int(input("Enter the number of elements in the sequence:"))
    even_count = 0
    for i in range(1, number + 1):
        if i % 2 == 0:
            even_count += 1
    print(f"The number of even elements is: {even_count}")
count_even_numbers()

# Bai 14
# Guess the secret number
import random
def guess_secret_number():
    secret_number = random.randint(1, 100)
    attempts = 0
    while True:
        guess = int(input("Guess the secret number (between 1 and 100):"))
        attempts += 1
        if guess < secret_number:
            print("Too low! Try again.")
        elif guess > secret_number:
            print("Too high! Try again.")
        else:
            print(f"Congratulations! You've guessed the secret number {secret_number} in {attempts} attempts.")
            break
guess_secret_number()

# End of app.py
# Draw a star triangle
def draw_star_triangle():
    rows = int(input("Enter the number of rows for the star triangle:"))
    for i in range(1, rows + 1):
        print('*' * i)      
draw_star_triangle()