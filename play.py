from board import Board 

JOKES_MADE = []

def get_move():
    global MADE_JOKE
    move = input("Select cup: ")

    try:
        move = int(move)
    except ValueError:
        print("It's gotta be a number, dude")
        return get_move()

    if move < 7 and move > 0:
        return move 
    else: 
        if move in [69, 420, 42, 8675309, 8008132, 80082]:
            if move not in JOKES_MADE:
                print("Heh, very clever.")
                JOKES_MADE.append(move)
                return get_move()
            else: 
                print(
                    "Okay it was funny once but.. " + 
                    (':/ ' * len(JOKES_MADE))
                )
                return get_move()

        print("It's gotta be between 1 and 6")
        return get_move()

def main():
    board = Board()
    board.display(True)

    try:
        move = get_move()
    except KeyboardInterrupt:
        exit() 

    while board.turn(move):
        print('\n\n')
        try:
            move = get_move()
        except KeyboardInterrupt:
            print("gg, no re")
            exit() 

if __name__ == '__main__':
    main()