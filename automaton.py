from copy import deepcopy

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

    def explore_one(self, parent):
        '''
        Expand all possible children
        '''
        children = []
        
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

    def expand(self, depth, parent=None):
        if parent is None:
            parent = self.root
            parent.add_children(self.explore_one(parent))
            depth -= 1

        for _ in range(depth):
            for child in parent.children:
                if child.children == []:
                    child.add_children(
                        self.explore_one(parent)
                    )
                else:
                    self.expand(depth-1, parent=child)

        return parent

    def find_leaves(self, depth=0, node=None):
        if node is None:
            node = self.root

        if node.children == []:
            return [(depth, node)]
        else: 
            ret = []
            for child in node.children:
                ret += self.find_roots(depth+1, child)
            return ret

    def minimax(self, root=None):
        if root is None:
            root = self.root 

        roots = self.find_leaves(root)
        maxes = [r[1] for r in roots if not r[0] % 2]
        mins  = [r[1] for r in roots if r[0] % 2]
        

class Node():
    def __init__(self, idx, score, parent, board):
        self.idx = idx
        self.score = score
        self.parent = parent
        self.board = board 
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        child.parent=self

    def add_children(self, children):
        [self.add_child(c) for c in children]


if __name__ == '__main__':
    tree = MiniMaxTree(Board(human_game=False))

    tree.expand(2)
    ret = tree.find_roots()

    print(ret)
