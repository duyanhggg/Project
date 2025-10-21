def change_temperature():
    print("The project converts the temperature")
    print("1. Celsius to Fahrenheit")
    print("2. Fahrenheit to Celsius")
    choice = input("Enter your choice (1 or 2): ")
    if choice == '1':
        celsius = float(input("Enter temperature in Celsius: "))
        fahrenheit = (celsius * 9/5) + 32
        return f"{celsius}°C is equal to {fahrenheit}°F"
    elif choice == '2':
        fahrenheit = float(input("Enter temperature in Fahrenheit: "))
        celsius = (fahrenheit - 32) * 5/9
        return f"{fahrenheit}°F is equal to {celsius}°C"
    else:
        return "Invalid choice. Please select 1 or 2."
print(change_temperature())
