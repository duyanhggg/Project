import random
score = []
def show_score():
    if len(score) <= 0:
        print("No score yet. Play the game first!")
    else:
        print("Your score is: {}".format(min(score)))
def ramdom_game():
    ramdom_number = random.randint(1, 100)
    print("Welcome to the Random Number Guessing Game!")
    player_name = input("Enter your name: ")
    print("Hello, {}! Let's start the game.".format(player_name))
    wanna_play = input("Do you want to play? (yes/no): ").lower()
    if wanna_play != "yes":
        print("Maybe next time. Goodbye!")
        return
    guess = 0
    attempts = 0
    while guess != ramdom_number:
        guess = int(input("Guess a number between 1 and 100: "))
        if guess < 1 or guess > 100:
            print("Please guess a number between 1 and 100")
            continue
        attempts += 1
        if guess < ramdom_number:
            print("Too low!")
        elif guess > ramdom_number:
            print("Too high!")
    print("You guessed it! The number was {}".format(ramdom_number))
    print("It took you {} attempts to guess the number.".format(attempts))
    score.append(attempts)
    print("You guessed it! The number was {}".format(ramdom_number))
    print("It took you {} attempts to guess the number.".format(attempts))
    score.append(attempts)
    show_score()
    play_again = input("Do you want to play again? (yes/no): ").lower()
    if play_again == "yes":
        ramdom_game()
    else:
        print("Thanks for playing! Goodbye!")
    show_score()
if __name__ == "__main__":
    ramdom_game()