import board
import random
import eval_func

# maybe good to implement proper interfact
# Some notes:
# - tought about having separate intelligence class, but didn't do because:
#   - virtually nothing would be left inside player
#   - don't think the intelligence class can be plugged in somewhere else anyway
# - so just factor out the eval functions, with signature:
#   - receives masu, series, self/opponent mark, returns value 0 - 100
#   - throws? if masu is not empty
#   - is there a way to enforce this API?

class player:
    '''
    Next steps:
    To make the intelligence:
    1. Board Evaluation - Immediately Actionable
        - Any place that would make 5 of own mark, hence should place?
        - Any place that would make 5 of enemy's mark, hence need to stop?
    2. Board Evaluation - Scoring Based
        - Any place that would add one or multiple new series?
        - Any place that would increase length of one or multiple current series?
        - Any place that would prevent opponent achieving the above?

    Ideas:
    - place above #2 in xy coordinate, and evaluate the possible moves as vectors
    - reward based on this xy dimensional vectors
    '''

    def __init__(self, board, move_fn, mark, evaluators = None):
        self.__move_fn      = move_fn
        self.__own_mark     = mark
        self.__opp_mark     = board.get_opp_mark(mark)
        self.__board        = board
        self.__jump_table   = {}
        board.register_move_callback(self.__eval_move)

        if evaluators == None:
            self.__evaluators = [
            {'fn': eval_func.own_bingo,          'weight': 20.0},
            {'fn': eval_func.opp_bingo,          'weight': 20.0},
            {'fn': eval_func.own_almost_bingo,   'weight': 12.0},
            {'fn': eval_func.opp_almost_bingo,   'weight': 12.0},
            {'fn': eval_func.freedom,            'weight': 1.0},
            {'fn': eval_func.center,             'weight': 1.0},
            ]
        else:
            self.__evaluators = evaluators

        self.__init_board_eval()

    def __register_jump_table(self, masu, series):
        elem = {'series': series, 'score': 0}
        if masu in self.__jump_table:
            self.__jump_table[masu].append(elem)
        else:
            self.__jump_table[masu] = [elem]

    def __init_board_eval(self):
        # brute force, there must be a better way, at least refactor the diagonals
        # horizontal
        size = self.__board.board_size()
        for r in range(size):
            series = [(r, x) for x in range(size)]
            for masu in series: self.__register_jump_table(masu, series)

        # vertical
        for c in range(size):
            series = [(x, c) for x in range(size)]
            for masu in series: self.__register_jump_table(masu, series)

        # migi sagari
        max = size - 1
        row_anchor = max
        col_anchor = 0
        while col_anchor <= max:
            r = row_anchor
            c = col_anchor
            series = []
            while r <= max and c <= max:
                series.append((r, c))
                r += 1
                c += 1
            for masu in series: self.__register_jump_table(masu, series)
            if row_anchor == 0:
                col_anchor += 1
            else:
                row_anchor -= 1

        # migi agari
        row_anchor = 0
        col_anchor = 0
        while col_anchor <= max:
            r = row_anchor
            c = col_anchor
            series = []
            while r >= 0 and c <= max:
                series.append((r, c))
                r -= 1
                c += 1
            for masu in series: self.__register_jump_table(masu, series)
            if row_anchor < max:
                row_anchor += 1
            else:
                col_anchor += 1

        # evaluate all positions
        for coor, elems in self.__jump_table.iteritems():
            #print " -- ", coor
            for elem in elems:
                #print "   -- ", elem['series']
                score = self.__eval_series_coor(elem['series'], coor)
                elem['score'] = score
        return

    def move(self):
        self.__move_fn(self.next_move_suggestion())

    def __get_series_idx(self, series_coordinates, target_coordinate):
        series = []
        idx = -1
        for i in range(len(series_coordinates)):
            coor = series_coordinates[i]
            #print "    ## ", coor
            series.append(self.__board.get_masu(coor[0], coor[1]))
            if coor == target_coordinate:
                idx = i
        if idx == -1:
            print "ERROR: didn't find own place"
            idx = 0
        return [series, idx]

    def __eval_series_coor(self, series, coor):
        weight_denom = float(sum([e['weight'] for e in self.__evaluators]))
        series_vals, idx = self.__get_series_idx(series, coor)
        total_score = 0
        #print " === eval series coor ", coor
        for e in self.__evaluators:
            score = e['fn'](idx, series_vals[:],
                self.__own_mark,
                self.__opp_mark,
                self.__board.masu_empty,
                self.__board.win_narabi_cnt)
            total_score += score * e['weight']
            #print "  - score ", score
        #print " - total / weight ", total_score / weight_denom
        return total_score / weight_denom

    def __eval_move(self, mark, move):
        for series_info in self.__jump_table[move]:
            for coor in series_info['series']:
                if coor == move or coor not in self.__jump_table:
                    continue
                for series_info_coor in self.__jump_table[coor]:
                    if series_info_coor['series'] != series_info['series']:
                        continue       # only update the same series of this
                    score = self.__eval_series_coor(series_info['series'], coor)
                    series_info_coor['score'] = score

        # delete move (no need to evaluate anymore)
        del self.__jump_table[move]
        return

    def next_move_suggestion(self):
        # print '############# MOVE #############', self.__own_mark
        choices = {}
        for choice, elems in self.__jump_table.iteritems():
            score_avg = sum([s['score'] for s in elems]) / float(len(elems))
            rounded_score = eval_func.round_tolerance(score_avg, 0.05)
            #print choice, " -- ", score_avg, " -- ", rounded_score
            if rounded_score in choices:
                choices[rounded_score].append(choice)
            else:
                choices[rounded_score] = [choice]

        # print "--", len(choices), "--", choices
        best_choices = choices[max(choices.keys())]
        # for score, b in choices.iteritems():
        #     print "bb", score, b
        move = best_choices[int(round(random.random() * (len(best_choices) - 1)))]
        # print "==> ", move
        return move

    def mark(self):
        return self.__own_mark

    def dump_jump_table(self):
        print " **** dumping scores ****"
        b_size = self.__board.board_size()
        #blank = '    '
        fmt_v = lambda x: "{:>6.2f}".format(x)
        fmt_i = lambda x: "{:>6d}".format(x)
        blank = fmt_i(0)
        print [blank] + [fmt_i(x) for x in range(b_size)]
        for i in range(b_size):
            col_scores = []
            for j in range(b_size):
                if (i, j) in self.__jump_table:
                    elems = self.__jump_table[(i,j)]
                    score_avg = sum([s['score'] for s in elems]) / float(len(elems))
                    col_scores.append(fmt_v(score_avg))
                else:
                    col_scores.append(blank)
            print [fmt_i(i)] + col_scores

    def test(self):
        for key, value in self.__jump_table.iteritems():
            print "{} - num series {}".format(key, len(value))
            print value

def _test_play(n_times):
    my_board = board.board()
    my_board.verbose = False
    fin_moves = []
    wins = {}
    wins[my_board.mark_player_1] = 0
    wins[my_board.mark_player_2] = 0

    for trial in range(n_times):
        my_board.reset()

        evaluators1 = [
            {'fn': eval_func.own_bingo,          'weight': 5.0},
            {'fn': eval_func.opp_bingo,          'weight': 5.0},
            {'fn': eval_func.own_almost_bingo,   'weight': 2.0},
            {'fn': eval_func.opp_almost_bingo,   'weight': 2.0},
            #{'fn': eval_func.freedom,            'weight': 1.0},
            {'fn': eval_func.center,             'weight': 1.0},
        ]
        p1 = player(my_board, my_board.player_1, my_board.mark_player_1, evaluators1)

        evaluators2 = [
            {'fn': eval_func.own_bingo,          'weight': 5.0},
            {'fn': eval_func.opp_bingo,          'weight': 5.0},
            {'fn': eval_func.own_almost_bingo,   'weight': 2.0},
            {'fn': eval_func.opp_almost_bingo,   'weight': 2.0},
            #{'fn': eval_func.freedom,            'weight': 1.0},
            {'fn': eval_func.center,             'weight': 1.0},
        ]

        p2 = player(my_board, my_board.player_2, my_board.mark_player_2, evaluators2)
        players = [p1, p2]
        for i in range(100):
            p = players[i % 2]
            p.move()
            if my_board.finished():
                #board.print_board()
                print "{} === PLAYER {} WINS === {}".format(trial, p.mark(), i)
                fin_moves.append(i)
                wins[p.mark()] += 1
                break
    my_board.print_board()
    print "avg moves: {}, wins: {}".format(sum(fin_moves) / float(len(fin_moves)), wins)

def _test_print_jump_table():
    my_board = board.board()
    p1 = player(my_board, my_board.player_1, my_board.mark_player_1)
    p1.dump_jump_table()
    print "********** player move ************"
    p1.move()
    p1.dump_jump_table()

if __name__ == '__main__':
    #_test_play(100)
    _test_print_jump_table()
