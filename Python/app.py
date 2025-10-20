string = input("Enter a string: ")
def process_string(string):
    string = " ".join(string.split()).lower()
    string = string + "."
    string = string.capitalize()
    
    return string
print(process_string(string))