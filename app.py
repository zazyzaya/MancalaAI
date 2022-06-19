from flask import Flask, render_template, request

from mancala.automaton import AlphaBetaPruning
from mancala.board import WebBoard

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('board.html')

@app.route('/move', methods=['POST'])
def move():
    state = request.get_json()
    print(state)

    row, cup = state.pop('cid')[-2:]
    try:
        cup = int(cup); row = int(row)
    # Should never happen
    except: 
        return {'state': 'invalid'}

    # Make sure they're playing a legal row
    if (row == 1 and state['p1_turn']) or (row == 2 and not state['p1_turn']):
        return {'state': 'invalid'}

    board = WebBoard()
    board.build_from_webstate(state)
    moves = board.webturn(cup-1)
    board_state = board.toweb()

    return {
        'state': 'valid',
        'n_updates': len(moves),
        'moves': moves, 
        'board': board_state
    }

@app.route('/bot', methods=['POST'])
def bot():
    req = request.get_json()
    print(req)

    depth = int(req['depth'])
    board = WebBoard(human_game=False)
    board.build_from_webstate(req['state'])
    board.p1_turn = False # on the bots turn in will never be p1 turn 
    
    bot = AlphaBetaPruning(board)
    decision = bot.search(bot.root, depth, True, top=True)

    moves = board.webturn(decision.idx)

    return {
        'n_updates': len(moves),
        'moves': moves
    }