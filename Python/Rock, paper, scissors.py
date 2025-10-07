import random
choice_computer = ["Rock", "Paper", "Scissors"]
def play_game():
    print("Welcome to Rock, Paper, Scissors!")
    print("Enter your choice:")
    print("1. Rock")
    print("2. Paper")
    print("3. Scissors")
    choice = int(input("Enter your choice: "))
    if choice == 1:
        print("You chose Rock")
        return "Rock"
    elif choice == 2:
        print("You chose Paper")
        return "Paper"
    elif choice == 3:
        print("You chose Scissors")
        return "Scissors"
    else:
        print("Invalid choice")
        return None

def get_computer_choice():
    return random.choice(choice_computer)

def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "It's a tie!"
    elif user_choice == "Rock" and computer_choice == "Scissors":
        return "You win!"
    elif user_choice == "Paper" and computer_choice == "Rock":
        return "You win!"
    elif user_choice == "Scissors" and computer_choice == "Paper":
        return "You win!"
    else:
        return "You lose!"

def main():
    print("Welcome to Rock, Paper, Scissors!")
    user_choice = play_game()
    computer_choice = get_computer_choice()
    print(f"You chose {user_choice}")
    print(f"Computer chose {computer_choice}")
    print(determine_winner(user_choice, computer_choice))

if __name__ == "__main__":
    main()
    play_again = input("Do you want to play again? (yes/no): ").lower()
    if play_again == "yes":
        main()
    else:
        print("Thanks for playing! Goodbye!")