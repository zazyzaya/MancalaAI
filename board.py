
import time 

class Board():
    def __init__(self, num_cups=6):
        self.NUM_CUPS=6
        self.MAX_IDX=self.NUM_CUPS-1

        self.top = [4] * self.NUM_CUPS 
        self.bottom = [4] * self.NUM_CUPS

        self.p1_score = 0
        self.p2_score = 0

        self.p1_turn = True
        self.active_row = self.bottom
        self.beans = 0

    def __str__(self):
        fmt = lambda x : ['| ' + str(v).rjust(2) + ' ' for v in x]
        top_s = '  ' + ''.join(fmt(self.top))
        bottom_s = '  '+ ''.join(fmt(self.bottom[::-1]))
        lines = '  ' + '-'*(len(top_s)-2)
        labels = [' (%d) ' % i for i in range(1,self.NUM_CUPS+1)]
        labels = '\n   ' + ''.join(labels)
        bean_disp = '\t(%d)' % self.beans if self.beans else ''
        
        t = labels + '\n' if not self.p1_turn else ''
        b = labels if self.p1_turn else ''

        outs = t + lines + '\n' \
            + top_s + '|\n' \
            + str(self.p2_score).ljust(2) + lines[2:] \
            + str(self.p1_score).rjust(3) + bean_disp + '\n' \
            + bottom_s + '|\n' \
            + lines \
            + b

        return outs

    def display(self, verbose, *args):
        if verbose:
            print(self)
            if args:
                print(args)
            time.sleep(0.5)

    def turn(self, cup, disp=True):
        cup = self.NUM_CUPS-cup if self.p1_turn else cup 
        self.beans = self.active_row[cup]
        
        # Can't pick from an empty cup
        if self.beans == 0: 
            return False # TODO this will end the game

        self.active_row[cup] = 0
        self.display(disp)
        
        while self.beans: 
            cup += 1 
            row = self.active_row

            # If we're passing over a mancala 
            if cup == self.NUM_CUPS:
                if self.p1_turn and row == self.top: 
                    self.p1_score += 1
                    self.beans -= 1
                    self.display(disp)
                elif not self.p1_turn and row == self.bottom: 
                    self.p2_score += 1 
                    self.beans -= 1 
                    self.display(disp)
                
                # Kind of hacky, but cup is incrimented at the
                # beginning of the loop and needs to be 0
                cup = -1 

                # Then swap rows 
                if row == self.bottom:
                    self.active_row = self.top 
                else: 
                    self.active_row = self.bottom

                continue 

            # Place a bean 
            row[cup] += 1 
            self.beans -= 1 
            self.display(disp) 

            if self.beans == 0: 
                # Grab the beans and keep going
                if row[cup] > 1: 
                    self.beans = row[cup]
                    row[cup] = 0
                
                # Or if your last bean is in an empty cup on 
                # your side, you steal the beans from the cup
                # of your opponent on the other side
                elif row == self.bottom and self.p1_turn:
                    self.p1_score += self.top[self.MAX_IDX-cup]
                    self.top[self.MAX_IDX-cup] = 0
                elif row == self.top and not self.p1_turn:
                    self.p2_score += self.bottom[self.MAX_IDX-cup]
                    self.bottom[self.MAX_IDX-cup] = 0

                # Placing in the empty cup across the board just ends
                # the turn with no fanfare
                else:
                    break

                self.display(disp)
        
        self.p1_turn = not self.p1_turn

        if not sum(self.top) or not sum(self.bottom):
            self.p1_score += sum(self.bottom)
            self.p2_score += sum(self.top)

            self.bottom = [0] * self.NUM_CUPS
            self.top = [0] * self.NUM_CUPS

            if self.p1_score > self.p2_score:
                winner = '  PLAYER 1 WINS  '
            elif self.p2_score > self.p1_score: 
                winner = '  PLAYER 2 WINS  '
            else:
                winner = "   IT'S A TIE!   "

            self.display(disp, '=== GAME OVER ===', winner)
            return False 
        return True