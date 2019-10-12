from math import exp as exp
import sys
import unittest

eval_score_max = 100
eval_score_min = 0

def round_tolerance(val, tolerance):
    return int(val / tolerance) * tolerance

def has_serial_cnt(series, mark, cnt):
    c = 0
    for v in series:
        if v == mark:
            c += 1
            if c == cnt:
                return True
        else:
            c = 0
    return False

def has_sub_array(array, subarray):
    # perfect place for dynamic programming? longest common substring
    if len(array) * len(subarray) == 0:
        return False
    s = 0
    while s < len(array):
        if len(array) - s < len(subarray):
            return False
        all_match = True
        sc = s
        for p in subarray:
            if p != array[sc]:
                all_match = False
                break
            sc += 1
        if all_match:
            return True
        s += 1
    return False

def _eval_bingo(idx, series, mark, win_narabi_cnt):
    # assume not already win_narabi_cnt, if adding one makes it, return full score
    series[idx] = mark
    if has_serial_cnt(series, mark, win_narabi_cnt):
        return eval_score_max
    return eval_score_min

def own_bingo(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    return _eval_bingo(idx, series, own_mark, win_narabi_cnt)

def opp_bingo(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    return _eval_bingo(idx, series, opp_mark, win_narabi_cnt)

def _eval_almost_bingo(idx, series, mark, empty_mark, win_narabi_cnt):
    # if there's any place that bingo - 1 with both sides empty
    series[idx] = mark
    if has_sub_array(series, [empty_mark] + [mark] * (win_narabi_cnt - 1) + [empty_mark]):
        return eval_score_max
    return eval_score_min

def own_almost_bingo(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    return _eval_almost_bingo(idx, series, own_mark, empty_mark, win_narabi_cnt)

def opp_almost_bingo(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    return _eval_almost_bingo(idx, series, opp_mark, empty_mark, win_narabi_cnt)

def _sigmoid_raw(x, steepness, mid, x_min, x_max):
    base = 1 / (1 + exp((-1 / float(steepness)) * (x - mid)))
    return base * (x_max - x_min) - x_min

def _sigmoid100(x):
    return _sigmoid_raw(x, 10,
        (eval_score_max - eval_score_min) / 2.0,
        eval_score_min,
        eval_score_max)

def freedom(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    # only count empty, compare againts 3 win_narabi_cnt, as we don't have board size
    # maybe we should just get a dict with everything here
    empty_cnt = len([x for x in series if x == empty_mark])
    return _sigmoid100(100 * empty_cnt / (3.0 * win_narabi_cnt))

def center(idx, series, own_mark, opp_mark, empty_mark, win_narabi_cnt):
    # closer to center is better
    half = len(series) / float(2)
    return 100 - _sigmoid100(100 * abs(idx - half) / half)



class test_eval_func(unittest.TestCase):
    def test_has_sub_array(self):
        print "======", sys._getframe().f_code.co_name
        tests = [
            [[1, 2, 3, 4, 5], [1, 2, 3], True],
            [[1, 2, 3, 4, 5], [1, 2, 4], False],
            [[1, 2, 3, 4, 5], [1, 2, 4], False],
        ]
        for case in tests:
            res = has_sub_array(case[0], case[1])
            print "testing {}".format(case)
            self.assertEqual(case[2], res)

    def test_has_sub_array(self):
        print "======", sys._getframe().f_code.co_name
        tests = [
            [[1, 2, 3, 4, 5], [1, 2, 3], True],
            [[1, 2, 3, 4, 5], [1, 2, 4], False],
            [[1, 2, 2, 4, 5], [2, 2, 4], True],
        ]
        for case in tests:
            res = has_sub_array(case[0], case[1])
            print "testing {}".format(case)
            self.assertEqual(case[2], res)

    def test_freedom(self):
        print "======", sys._getframe().f_code.co_name
        empty = '_'
        tests = [
            [[empty] * 5, 0.0],
        ]
        for case in tests:
            res = freedom(0, case[0], 'X', '_', empty, 5)
            print "testing {}".format(case)
            self.assertEqual(case[1], res)
# eval proximity - score higher when closer to own mark
if __name__ == '__main__':
    #unittest.main()

    print "sigmoid", _sigmoid100(100)

    print "**** bingo"
    series = [0, 1, 1, 1, 1, 0, 0]
    res = []
    for i in range(len(series)):
        res.append(_eval_bingo(i, series[:], 1, 5))
    print series
    print res

    print "**** bingo almost"
    series = [0, 1, 1, 0, 1, 0, 0]
    res = []
    for i in range(len(series)):
        res.append(_eval_almost_bingo(i, series[:], 1, 0, 5))
    print series
    print res

    print "**** freedom"
    series = [0, 1, 1, 0, 1, 0, 0, 0]
    res = []
    for i in range(len(series)):
        res.append(freedom(i, series[:], 1, 2, 0, 5))
    print series
    print res
