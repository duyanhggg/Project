def stringMatching(words):
    """
    Find all strings in words that are substrings of another word.
    """
    result = []
    
    for word in words:
        for other_word in words:
            if word != other_word and word in other_word:
                result.append(word)
                break
    
    return result


# Get input from user
print("Enter words separated by commas (e.g., mass,as,hero,superhero):")
user_input = input().strip()

# Parse the input and remove quotes
words = [word.strip().strip('"').strip("'") for word in user_input.split(',')]

# Remove any leftover bracket characters
words = [word.replace('[', '').replace(']', '') for word in words]

# Filter out empty strings
words = [word for word in words if word]

# Find and display results
result = stringMatching(words)

print(f"\nInput: {words}")
print(f"Output: {result}")