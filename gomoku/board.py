
class board:
    '''
    - only support square boards. easy to support rectangle, but who will ever want that?
    '''

    masu_empty      = " "
    mark_player_1   = "X"
    mark_player_2   = "O"
    win_narabi_cnt  = 5

    # Environment Vars
    verbose = True

    ##################################
    def __init__(self, size = 10):
        self.__board_size = size
        self.__board = [[self.masu_empty for x in range(size)] for y in range(size)]
        self.__history = []
        self.__move_callbacks = []
        self.__finished = False

    ##################################
    def reset(self):
        self.__init__(self.__board_size)

    ##################################
    def __add_move(self, mark, move):
        if self.__finished:
            self.print_log("ERROR: Board finished already!", True)
            return False

        if len(self.__history) > 0 and self.__history[-1]["mark"] == mark:
            self.print_log("ERROR: {} already made last move".format(mark), True)
            return False

        row, col = move

        max_coor = len(self.__board) - 1
        if row > max_coor or col > max_coor:
            self.print_log("ERROR: {} exceeds board size {}".format(move, max_coor), True)
            return False

        if self.__board[row][col] != self.masu_empty:
            self.print_log("ERROR: {} already taken".format(move), True)
            return False

        self.__board[row][col] = mark
        self.__history.append({"mark": mark, "move": move})
        if self.__check_win(move):
            self.print_log("{} => Player [{}] WON! Board finished!".format(move, mark))
            self.__finished = True

        for cb in self.__move_callbacks:
            cb(mark, move)

        return True

    ##################################
    def __check_win_line(self, arr):
        last = self.masu_empty
        cnt = 1
        #print "check => ", arr
        for v in arr:
            #print "  check => cnt[{}] masu[{}]".format(cnt, v)
            if v != self.masu_empty and v == last:
                cnt += 1
                if cnt == self.win_narabi_cnt:
                    return True
            else:
                cnt = 1
            last = v
        return False

    ##################################
    def __get_board_line(self, row, row_step, col, col_step, count):
        # TODO: do something more elegant, don't check boundaries on each iteration
        res = []
        in_range = lambda x: 0 <= x and x < len(self.__board)
        while count > 0:
            #print "cn[{}], [{},{}]".format(count, row, col)
            if in_range(row) and in_range(col):
                res.append(self.__board[row][col])
            row += row_step
            col += col_step
            count -= 1
        return res

    ##################################
    # def test(self, move):
    #     print "-----", move
    #     row, col = move
    #     horz = self.__get_board_line(row, 0, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
    #     print "horz", horz
    #     vert = self.__get_board_line(row - self.win_narabi_cnt + 1, 1, col, 0, self.win_narabi_cnt * 2 - 1)
    #     print "vert", vert
    #     dia1 = self.__get_board_line(row - self.win_narabi_cnt + 1, 1, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
    #     print "dia1", dia1
    #     dia2 = self.__get_board_line(row + self.win_narabi_cnt - 1, -1, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
    #     print "dia2", dia2

    ##################################
    def __check_win(self, move):
        row, col = move

        horz = self.__get_board_line(row, 0, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
        if self.__check_win_line(horz):
            self.print_log("Horizontal MADE!")
            return True

        vert = self.__get_board_line(row - self.win_narabi_cnt + 1, 1, col, 0, self.win_narabi_cnt * 2 - 1)
        if self.__check_win_line(vert):
            self.print_log("Vertical MADE!")
            return True

        # diagonal 1 - migi sagari
        dia1 = self.__get_board_line(row - self.win_narabi_cnt + 1, 1, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
        if self.__check_win_line(dia1):
            self.print_log("Diagonal Migi Sagari MADE!")
            return True

        # diagonal 2 - migi agari
        dia2 = self.__get_board_line(row + self.win_narabi_cnt - 1, -1, col - self.win_narabi_cnt + 1, 1, self.win_narabi_cnt * 2 - 1)
        if self.__check_win_line(dia2):
            self.print_log("Diagonal Migi Agari MADE!")
            return True

    ##################################
    def player_1(self, move):
        return self.__add_move(self.mark_player_1, move)

    ##################################
    def player_2(self, move):
        return self.__add_move(self.mark_player_2, move)

    ##################################
    def print_board(self):
        print [' '] + [str(x) for x in range(len(self.__board))]
        for i in range(len(self.__board)):
            print [str(i)] + self.__board[i]

    ##################################
    def finished(self):
        return self.__finished

    ##################################
    def get_empty_coordinates(self):
        # TODO: maybe precreate and just remove one every move
        ret = []
        for row in range(0, self.__board_size):
            for col in range(0, self.__board_size):
                if self.__board[row][col] == self.masu_empty:
                    ret.append([row, col])
        return ret

    ##################################
    def print_history(self):
        print self.__history

    ##################################
    def board_size(self):
        return self.__board_size

    def print_log(self, string, override_verbose = False):
        if override_verbose or self.verbose:
            print string

    ##################################
    def register_move_callback(self, callback_fn):
        if len(self.__move_callbacks) < 2:
            self.__move_callbacks.append(callback_fn)
        else:
            self.print_log("ERROR: can only add 2 players", True)
            # will that be other non-player that needs the callback?

    def get_masu(self, row, col):
        limit = self.__board_size
        if row >= limit or col >= limit:
            self.print_log("ERROR: row {} col {} outside limit".format(row, col), True)
            return None
        return self.__board[row][col]

    def get_opp_mark(self, mark):
        if mark == self.mark_player_1:
            return self.mark_player_2
        return self.mark_player_1
