name = str(input("Enter your name: "))
age = int(input("Enter your age: "))
print(f"Hello, {name}!")
print("you are", age, "years old.")
if age < 18:
    print("You are a minor.")
elif age == 18:
    print("You are just an adult.")
elif age > 18 and age < 65:
    print("You are an adult.")
elif age >= 65:
    print("You are a senior citizen.")
print("Have a great day!")
