#!/usr/bin/env python3
from shmoopland.base_game import ShmooplandGame

def main():
    """Main entry point for the Shmoopland game."""
    game = ShmooplandGame()

    # Display welcome message
    print("\n" + "="*60)
    print("Welcome to Shmoopland!")
    print("A magical realm where wonder and whimsy await your discovery.")
    print("Type 'help' for a list of commands.")
    print("="*60 + "\n")

    # Start with initial location description
    game.look()

    # Main game loop
    while True:
        try:
            command = input("\n> ")
            game.parse_command(command)
        except KeyboardInterrupt:
            print("\nUse 'quit' to exit the game properly.")
        except Exception as e:
            print(f"\nOops! Something went wrong: {str(e)}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()
