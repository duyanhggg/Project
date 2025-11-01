# Bài 1
# Count characters and string lengths
from ast import If
import string


def count_characters():
    String = input("Enter a string:")
    char_count = len(String)
    print(f"The number of characters in the string is: {char_count}")
    print("Character frequencies:")
    for char in sorted(set(String)):  # dùng set để loại trùng, sorted để sắp xếp ký tự
        print(f"'{char}': {String.count(char)}")
count_characters()

# Bai 2
# check the symmetric character
def check_symmetric_character():
    String = input("Enter a string:")
    if String == ''.join(reversed(String)):
        print(f"The string '{String}' is symmetric.")
    else:
        print(f"The string '{String}' is not symmetric.")  
check_symmetric_character()

# Bai 3
# Count the number of vowels and consonants in the string
def count_vowels_consonants():
    String = input("Enter a string:")
    vowels = "aeiouAEIOU"
    vowel_count = sum(1 for char in String if char in vowels)
    consonant_count = sum(1 for char in String if char.isalpha() and char not in vowels)
    print(f"The number of vowels in the string is: {vowel_count}")
    print(f"The number of consonants in the string is: {consonant_count}")
count_vowels_consonants()

# Bai 4
# Capitalize the first letter of each word
def capitalize_first_letter():
    String = input("Enter a string:")
    capitalized_string = String.title()
    print(f"The capitalized string is: {capitalized_string}")
capitalize_first_letter()

# Bai 5 
# Replace words in strings
def replace_words_in_string():
    String = input("Enter a string:")
    word_to_replace = "Python"
    replacement_word = "AI"
    new_string = String.replace(word_to_replace, replacement_word)
    print(f"The new string is: {new_string}")
replace_words_in_string()

# Bai 6
# Split and join strings
def split_and_join_strings():
    String = input("Enter a string:")
    words = String.split()
    print("The list of words is:", words)
    joined_string = "-".join(words)
    print(f"The joined string is: {joined_string}")
split_and_join_strings()

# Bai 7
# Count the number of words in the sentence
def count_words_in_sentence():
    Sentence = input("Enter a sentence:")
    words = Sentence.split()
    word_count = len(words)
    print(f"The number of words in the sentence is: {word_count}")
count_words_in_sentence()

# Bai 8
# Sum, average and largest element
def calculate_sum_average_largest():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    total_sum = sum(numbers)
    average = total_sum / len(numbers) if numbers else 0
    largest = max(numbers) if numbers else None
    print(f"The sum of the numbers is: {total_sum}")
    print(f"The average of the numbers is: {average}")
    print(f"The largest number is: {largest}")
calculate_sum_average_largest()

# Bai 9
# Remove duplicate elements
def remove_duplicate_elements():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    unique_numbers = list(set(numbers))
    print(f"The list after removing duplicates is: {unique_numbers}")
remove_duplicate_elements()

# Bai 10
# Reverse the list
def reverse_list():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    numbers.reverse()
    print(f"The reversed list is: {numbers}")
reverse_list()

# Bai 11
# Calculate the sum of even elements
def sum_of_even_elements():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    if all(even_num % 2 == 0 for even_num in numbers):
        even_sum = sum(numbers)
    print(f"The sum of even elements is: {even_sum}")
sum_of_even_elements()

# Bai 12
# Find the element that appears the most
def most_frequent_element():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    most_frequent = max(set(numbers), key=numbers.count)
    frequency = {}
    for num in numbers:
        frequency[num] = frequency.get(num, 0) + 1
    print(f"The element that appears the most is: {most_frequent} (appears {frequency[most_frequent]} times)")
most_frequent_element()

# Bai 13
# Merge two lists
def merge_two_lists():
    list1 = list(map(int, input("Enter the first list of numbers separated by spaces:").split()))
    list2 = list(map(int, input("Enter the second list of numbers separated by spaces:").split()))
    merged_list = list1 + list2
    merged_list = sorted(set(merged_list))
    print(f"The merged list is: {merged_list}")
merge_two_lists()

# Bai 14
# Filter the list
def filter_list():
    numbers = list(map(int, input("Enter a numbers separated by spaces:").split()))
    filtered_list = [num for num in numbers if num >= 10]
    print(f"The filtered list (numbers >= 10) is: {filtered_list}")
filter_list()

# Bai 15
# List of words in string
def list_of_words_in_string():
    String = input("Enter a string:")
    words = String.lower().split()
    words_count = {}
    for delimiter in {".", ",", ";", ":", "!", "?"}:
        words = [word.replace(delimiter, "") for word in words]
    for word in words:
        words_count[word] = words_count.get(word, 0) + 1
    sorted_words = sorted(words_count.items(), key=lambda x: x[1], reverse=True)
    print("The list of words in the string is:", words)
    print("The word count in the string is:", words_count)
    print("The sorted word count in the string is:", {word: count for word, count in sorted_words})
list_of_words_in_string()