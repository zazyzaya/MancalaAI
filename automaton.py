from copy import deepcopy
import time

import json 
from board import Board

'''
Some things to keep in mind: 
    - If one player obtains 25 beans, they win (48 beans total)
    - If one player has significantly more beans on their side 
      of the board, their opponent is at a disadvantage (usually...)
'''

class MiniMaxTree():
    def __init__(self, board):
        self.root = Node(None, 0, None, board)

    def _explore_one(self, parent):
        '''
        Expand all possible children
        '''
        children = []

        if parent.game_over():
            return []
        
        for i in range(parent.board.NUM_CUPS):
            state = deepcopy(parent.board)
            
            valid = state.turn(i, disp=False)
            if not valid:
                continue 

            score = state.p1_score - state.p2_score
            children.append(Node(
                i, score, parent, state
            ))

        return children


    def _heuristic(self, choices, is_min):
        '''
        This will likely be the most important function
        For now I'm saying the priority is: 
            - If winning nodes exist, select the one with the
            highest score
            - A win now is better than a win later
            - Otherwise, select the highest score of what remains
        '''
        wants = lambda x  : x < 0 if is_min else x > 0
        
        # Overwrites wins that occur later. The best option is to win now
        winners = [c for c in choices if c.game_over and wants(c.heuristic)]
        if len(winners):
            choice = min(winners) if is_min else max(winners)
            score = -float('inf') if is_min else float('inf')

        else:
            choice = min(choices) if is_min else max(choices)
            score = choice.score

        return score, choice


    def search(self, node, depth, is_min):
        if depth == 0:
            return self._heuristic([node], is_min)

        node.add_children(self._explore_one(node))
        for child in node.children:
            self.search(child, depth-1, not is_min)
        
        # A solution node
        if node.children == []:
            score, choice = self._heuristic([node], is_min)
        else:
            score, choice = self._heuristic(node.children, is_min)
            
        node.heuristic = score
        return choice


class AlphaBetaPruning(MiniMaxTree):
    '''
    Optimizing MiniMax to look at fewer options
    '''
    def search(self, node, depth, is_min, alpha=-float('inf'), beta=float('inf')):
        if depth == 0:
            return self._heuristic([node], is_min)

        node.add_children(self._explore_one(node))
        if node.children == []:
            return self._heuristic([node], is_min)

        value = float('inf') if is_min else -float('inf')
        better = lambda x,y : min(x,y) if is_min else max(x,y)

        children_I_love = []
        for child in node.children:
            # Calculate child.heuristic
            self.search(child, depth-1, not is_min, alpha, beta)
            
            value = better(value, child.heuristic)
            children_I_love.append(child)

            if is_min: 
                # Prune because we know MAX wouldn't go this route anyway. It's got
                # better prospects on another branch. No need to keep looking here
                if value <= alpha:
                    break 
                beta = min(beta, value)
                
            else:
                # Ditto here. value >= beta means MIN found a better branch a few levels up
                # and would never let us come down this path
                if value >= beta:
                    break 
                alpha = max(alpha, value)

        score, choice = self._heuristic(children_I_love, is_min)
        node.heuristic = score 
        return choice
        

class Node():
    def __init__(self, idx, score, parent, board):
        self.idx = idx
        self.score = score
        self.solution = board.game_over
        self.parent = parent
        self.board = board 
        self.children = []
        self.heuristic = self.score 

    def add_child(self, child):
        self.children.append(child)
        child.parent=self

    def add_children(self, children):
        self.children = []
        [self.add_child(c) for c in children]

    def game_over(self):
        return self.board.game_over

    def display(self):
        self.board.display(True)

    # It really feels like there should be a 
    # better way to do this... 
    def __lt__(self,other):
        return self.heuristic < other.heuristic
    def __gt__(self,other):
        return self.heuristic > other.heuristic
    def __eq__(self,other):
        return self.heuristic == other.heuristic
    def __le__(self,other):
        return self.heuristic <= other.heuristic 
    def __ge__(self,other):
        return self.heuristic >= other.heuristic
    def __ne__(self,other):
        return self.heuristic != other.heuristic


def play_with_yourself(TreeSearch, depth=6):
    b = Board(human_game=False, speed=0)
    tree = TreeSearch(b)
    ts = []

    p2 = False 
    while(not tree.root.game_over()):
        st = time.time()
        move = tree.search(tree.root, depth, p2)
        ts.append(time.time()-st)

        tree.root = move 
        move.display()
        print('Assumed value: ',move.heuristic,'\n\n')

        p2 = not p2

    print("Avg time to search: %0.4f" % (sum(ts) / len(ts)))

if __name__ == '__main__':
    play_with_yourself(
        AlphaBetaPruning
    )
