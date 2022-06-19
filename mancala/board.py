import time 

class Board():
    def __init__(self, num_cups=6, speed=0.5, human_game=True):
        self.NUM_CUPS=num_cups
        self.MAX_IDX=self.NUM_CUPS-1
        
        self.speed = speed
        self.human_game = human_game

        self.top = [4] * self.NUM_CUPS 
        self.bottom = [4] * self.NUM_CUPS

        self.p1_score = 0
        self.p2_score = 0

        self.p1_turn = True
        self.active_row = self.bottom
        self.beans = 0
        self.is_running = False 
        self.game_over = False

        self.last_choice = None

    def __str__(self):
        fmt = lambda x : ['| ' + str(v).rjust(2) + ' ' for v in x]
        top_s = '  ' + ''.join(fmt(self.top))
        bottom_s = '  '+ ''.join(fmt(self.bottom[::-1]))
        lines = '  ' + '-'*(len(top_s)-2)
        labels = [' (%d) ' % i for i in range(1,self.NUM_CUPS+1)]
        labels = '\n   ' + ''.join(labels)
        bean_disp = '\t(%d)' % self.beans if self.beans else ''

        if not self.human_game:
            labels= '\n   ' + ('     ' * self.last_choice) + \
                    ' (%d) '% (self.last_choice+1) + \
                    ('    ' * (self.NUM_CUPS-self.last_choice-1))
        
        # This runs after the turn is complete so.. 
        if not self.human_game:
            self.p1_turn = not self.p1_turn

        t = labels + '\n' if not (self.p1_turn or self.is_running) else ''
        b = labels if self.p1_turn and not self.is_running else '\n'

        # It's hacky, but whatever
        if not self.human_game:
            self.p1_turn = not self.p1_turn

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
                print(*args)
            time.sleep(self.speed)

    def turn(self, cup, disp=True):
        self.is_running = True 

        self.active_row = self.bottom if self.p1_turn else self.top 
        cup = self.MAX_IDX-cup if self.p1_turn else cup 
        self.last_choice = cup 
        
        self.beans = self.active_row[cup]
        
        # Can't pick from an empty cup
        if self.beans == 0: 
            # Need the AI to know this isn't a valid move
            if not self.human_game:
                return False
            # But if a human makes a mistake it's okay
            else:
                print("Come on, don't take from an empty cup")
                self.is_running = False 
                return True 

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
        self.is_running = False

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
            self.game_over = True 

        return True

    def fmt_state(self, cup, row, beans, scoring=False):
        '''
        Formats JSON outs for webapp 
        '''
        cid = self.MAX_IDX - cup if row == self.bottom else cup 
        row = '1' if row == self.top else '2'
        
        if cid is not None:
            cid += 1

        cid = str(cid)
        cid = 'cup'+row+cid if not scoring else scoring+'_goal'
        
        return {
            'state': 'running',
            'id': cid, 
            'beans': beans
        }


class WebBoard(Board):
    def webturn(self, cup):
        '''
        Returns list of board updates 
        used by the web application to update the UI
        Also strips a lot of the bells and whistles used 
        to format output strings and so forth in the cmd version
        '''
        self.active_row = self.bottom if self.p1_turn else self.top 
        cup = self.MAX_IDX-cup if self.p1_turn else cup 
        self.last_choice = cup 
        
        self.beans = self.active_row[cup]
        
        # Can't pick from an empty cup
        if self.beans == 0:
            return []

        states = []
        self.active_row[cup] = 0   
        states.append(self.fmt_state(cup, self.active_row, 0))

        while self.beans: 
            cup += 1 
            row = self.active_row

            # If we're passing over a mancala 
            if cup == self.NUM_CUPS:
                if self.p1_turn and row == self.top: 
                    self.p1_score += 1
                    self.beans -= 1
                    states.append(self.fmt_state(None, None, self.p1_score, 'p1'))

                elif not self.p1_turn and row == self.bottom: 
                    self.p2_score += 1 
                    self.beans -= 1 
                    states.append(self.fmt_state(None, None, self.p2_score, 'p2'))
                
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
            states.append(self.fmt_state(cup, row, row[cup]))

            if self.beans == 0: 
                # Grab the beans and keep going
                if row[cup] > 1: 
                    self.beans = row[cup]
                    row[cup] = 0
                    states.append(self.fmt_state(cup, row, 0))
                
                # Or if your last bean is in an empty cup on 
                # your side, you steal the beans from the cup
                # of your opponent on the other side
                elif row == self.bottom and self.p1_turn:
                    self.p1_score += self.top[self.MAX_IDX-cup]
                    self.top[self.MAX_IDX-cup] = 0
                    
                    states.append(self.fmt_state(self.MAX_IDX-cup, self.top, 0))
                    states.append(self.fmt_state(None, None, self.p1_score, 'p1'))

                elif row == self.top and not self.p1_turn:
                    self.p2_score += self.bottom[self.MAX_IDX-cup]
                    self.bottom[self.MAX_IDX-cup] = 0

                    states.append(self.fmt_state(self.MAX_IDX-cup, self.bottom, 0))
                    states.append(self.fmt_state(None, None, self.p2_score, 'p2'))

                # Placing in the empty cup across the board just ends
                # the turn with no fanfare
                else:
                    break
        
        if not sum(self.top):
            sc = self.p1_score
            for i in range(6):
                if self.bottom[i]:
                    sc += self.bottom[i]
                    states.append(self.fmt_state(i, self.bottom, 0))
                    states.append(self.fmt_state(None, None, sc, 'p1'))

        elif not sum(self.bottom):
            sc = self.p2_score
            for i in range(6):
                if self.top[i]:
                    sc += self.top[i]
                    states.append(self.fmt_state(i, self.top, 0))
                    states.append(self.fmt_state(None, None, sc, 'p1'))

        if not sum(self.top) or not sum(self.bottom):
            winner = '      Player 1      ' if self.p1_score > self.p2_score \
                else '      Player 2      ' if self.p2_score > self.p1_score \
                else "No one,  it's a tie!"
            states.append({'state': 'gameover', 'winner': winner})

        self.p1_turn = not self.p1_turn
        return states

    
    def build_from_webstate(self, webstate):
        self.top = [int(t) for t in webstate['top']]
        self.bottom = [int(b) for b in webstate['bottom']]
        self.p1_turn = webstate['p1_turn']
        self.p1_score = int(webstate['p1_score'])
        self.p2_score = int(webstate['p2_score'])

    
    def toweb(self):
        return dict(
            top=self.top,
            bottom=self.bottom,
            p1_turn=self.p1_turn,
            p1_score=self.p1_score,
            p2_score=self.p2_score
        )