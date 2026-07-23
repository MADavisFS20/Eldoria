import os
import sys
import time

_DEBUG_MODE = False

def set_debug_mode(is_debug):
    global _DEBUG_MODE
    _DEBUG_MODE = is_debug

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt, valid_options=None):
    if valid_options:
        option_map = {opt.lower(): opt.lower() for opt in valid_options}
        first_letter_map = {}
        for opt in valid_options:
            fl = opt[0].lower()
            first_letter_map.setdefault(fl, []).append(opt.lower())

    while True:
        user_input = input(f"\n{prompt} ").strip().lower()

        if not valid_options:
            return user_input

        if user_input in option_map:
            return user_input

        if len(user_input) == 1 and user_input in first_letter_map:
            matches = first_letter_map[user_input]
            if len(matches) == 1:
                return matches[0]
            else:
                print(f"'{user_input}' is ambiguous. Options: {', '.join(matches)}")
                continue

        print(f"Invalid option. Choose from: {', '.join(valid_options)}")

def display_message(message, delay=0.02):
    if _DEBUG_MODE:
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    else:
        for char in message:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\n')

def press_enter_to_continue():
    input("\nPress Enter to continue...")
