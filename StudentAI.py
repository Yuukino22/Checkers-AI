from random import randint
from BoardClasses import Move
from BoardClasses import Board
import math
import copy
import time

OPPONENT = {2: 1, 1: 2}
totalTimeElapsed = 0.0

# The following part should be completed by students.
# Students can modify anything except the class name and exisiting functions and varibles.
# python3 AI_Runner.py 8 8 3 l /home/yifengx4/Checkers_Student/src/checkers-python/main.py /home/yifengx4/Checkers_Student/Tools/Sample_AIs/Poor_AI_368/main.py
# python3 AI_Runner.py 8 8 3 l /home/yifengx4/Checkers_Student/Tools/Sample_AIs/Poor_AI_368/main.py /home/yifengx4/Checkers_Student/src/checkers-python/main.py
# python3 AI_Runner.py 8 8 3 l /home/yifengx4/Checkers_Student/src/checkers-python/main.py /home/yifengx4/Checkers_Student/Tools/Sample_AIs/Average_AI_368/main.py
# python3 AI_Runner.py 8 8 3 l /home/yifengx4/Checkers_Student/Tools/Sample_AIs/Average_AI_368/main.py /home/yifengx4/Checkers_Student/src/checkers-python/main.py

class StudentAI():

    def __init__(self, col, row, p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col, row, p)
        self.board.initialize_game()
        self.opponent = {1: 2, 2: 1}
        self.color = 2
        self.root = None
        self.start = True

    def get_move(self, move):
        global totalTimeElapsed
        remainTime = 480 - totalTimeElapsed
        startTime = time.time()
        if len(move) != 0:
            if self.start:
                self.board.make_move(move, self.opponent[self.color])
                self.root = Node(self.opponent[self.color], move)
                self.start = False
            else:
                if self.root.child_num == 0:
                    _generate_children(self.board, self.root)
                self.board.make_move(move, self.opponent[self.color])
                index = _node_index(self.root.children, move)
                self.root = self.root.children[index]
                self.root.parent = None
        else:
            self.color = 1
            self.root = Node(self.opponent[self.color])
            self.start = False
        board = _copy_board(self.board)
        if remainTime < 5:
            if len(self.root.children) != 0:
                move = _max(self.root)
                index = _node_index(self.root.children, move)
                self.root = self.root.children[index]
                self.root.parent = None
                self.board.make_move(move, self.color)
                return move
            else:
                m = self.board.get_all_possible_moves(self.color)
                move = m[randint(0, len(m) - 1)]
                move = move[randint(0, len(move) - 1)]
                self.board.make_move(move, self.color)
                return move
        if self.col * self.row * self.p <= 200:
            move = my_move(board, self.color, self.root, remainTime)
        else:
            move = my_move2(board, self.color, self.root, remainTime, startTime + remainTime)
        index = _node_index(self.root.children, move)
        self.root = self.root.children[index]
        self.root.parent = None
        self.board.make_move(move, self.color)
        endTime = time.time()
        totalTimeElapsed += (endTime - startTime)
        return move


class Node():

    def __init__(self, color, move=None, parent=None):
        self.color = color
        self.move = move
        self.parent = parent
        self.children = []
        self.child_num = 0
        self.win_count = 0
        self.total = 0

    def __eq__(self, other):
        return _move_equal(self.move, other.move)

    def add_child(self, child):
        self.children.append(child)
        self.child_num += 1

    def win_rate(self):
        if self.total == 0:
            return 0
        return self.win_count / self.total

    def uct(self):
        if self.total == 0:
            return 0
        if self.parent.total == 0:
            return float(self.win_count) / self.total
        return float(self.win_count) / self.total + \
               math.sqrt(2) * math.sqrt(math.log(self.parent.total) / self.total)

    def opponent(self):
        return OPPONENT[self.color]

    def win(self):
        self.win_count += 1
        self.total += 1

    def tie(self):
        self.win_count += 0.5
        self.total += 1

    def tie2(self):
        self.win_count += 0.25
        self.total += 1

    def lose(self):
        self.total += 1


def my_move(board, color, root, remainTime):
    m = board.get_all_possible_moves(color)
    if len(m) == 1:
        if len(m[0]) == 1:
            _add_move(root, m[0][0])
            return m[0][0]
    tsStart = time.time()
    expectedEndTime = tsStart + 12
    if remainTime >= 320:
        t, timeOut = random_part(350, board, root, expectedEndTime)
        if timeOut:
            return _max(root)
    elif remainTime <= 60:
        uct_part(250, board, root, expectedEndTime)
        return _max(root)
    else:
        t, timeOut = random_part(100, board, root, expectedEndTime)
        if timeOut:
            return _max(root)
    uct_part(1500, board, root, expectedEndTime)
    return _max(root)


def my_move2(board, color, root, remainTime, endTime):
    m = board.get_all_possible_moves(color)
    if len(m) == 1:
        if len(m[0]) == 1:
            _add_move(root, m[0][0])
            return m[0][0]
    tsStart = time.time()
    expectedEndTime = tsStart + 12
    if remainTime >= 430:
        t, timeOut = random_part2(300, board, root, tsStart + 3, endTime)
        if timeOut:
            return _max(root)
    elif remainTime <= 120:
        uct_part2(250, board, root, tsStart + 20, endTime)
        return _max(root)
    else:
        t, timeOut = random_part2(200, board, root, expectedEndTime, endTime)
        if timeOut:
            return _max(root)
    uct_part2(1500, board, root, tsStart + 12, endTime)
    return _max(root)
    

def random_part(total, board, node, expectedEndTime):
    while total != 0:
        #selection
        while node.child_num != 0:
            node = random_selection(node)
            board.make_move(node.move, node.color)
        #expansion
        while board.is_win(node.color) == 0:
            _generate_children(board, node)
            if node.child_num == 0:
                break
            node = random_selection(node)
            board.make_move(node.move, node.color)
        #simulation
        winner = board.is_win(node.color)
        #backpropagation
        while node.parent is not None:
            if winner == node.color:
                node.win()
            elif winner == -1:
                node.tie()
            elif winner == OPPONENT[node.color]:
                node.lose()
            board.undo()
            node = node.parent
        if time.time() > expectedEndTime:
            return total, True
        total -= 1
    return 0, False


def uct_part(total, board, node, expectedEndTime):
    while total != 0:
        #selection
        while node.child_num != 0:
            node = uct_selection(node)
            board.make_move(node.move, node.color)
        #expansion
        while board.is_win(node.color) == 0:
            _generate_children(board, node)
            if node.child_num == 0:
                break
            node = uct_selection(node)
            board.make_move(node.move, node.color)
        # simulation
        winner = board.is_win(node.color)
        # backpropagation
        while node.parent is not None:
            if winner == node.color:
                node.win()
            elif winner == -1:
                node.tie()
            elif winner == OPPONENT[node.color]:
                node.lose()
            board.undo()
            node = node.parent
        if time.time() > expectedEndTime:
            return total
        total -= 1
    return total



def random_part2(total, board, node, expectedEndTime, endTime):
    while total != 0:
        #selection
        while node.child_num != 0:
            node = random_selection(node)
            board.make_move(node.move, node.color)
        #expansion
        while board.is_win(node.color) == 0:
            _generate_children(board, node)
            if node.child_num == 0:
                break
            node = random_selection(node)
            board.make_move(node.move, node.color)
        #simulation
        winner = board.is_win(node.color)
        #backpropagation
        while node.parent is not None:
            if winner == node.color:
                node.win()
            elif winner == -1:
                node.tie2()
            elif winner == OPPONENT[node.color]:
                node.lose()
            board.undo()
            node = node.parent
        if time.time() > expectedEndTime or time.time() + 5 >= endTime:
            return total, True
        total -= 1
    return 0, False


def uct_part2(total, board, node, expectedEndTime, endTime):
    while total != 0:
        #selection
        while node.child_num != 0:
            node = uct_selection(node)
            board.make_move(node.move, node.color)
        #expansion
        while board.is_win(node.color) == 0:
            _generate_children(board, node)
            if node.child_num == 0:
                break
            node = uct_selection(node)
            board.make_move(node.move, node.color)
        # simulation
        winner = board.is_win(node.color)
        # backpropagation
        while node.parent is not None:
            if winner == node.color:
                node.win()
            elif winner == -1:
                node.tie2()
            elif winner == OPPONENT[node.color]:
                node.lose()
            board.undo()
            node = node.parent
        if time.time() > expectedEndTime or time.time() + 5 >= endTime:
            return total
        total -= 1
    return total

def random_selection(node):
    return node.children[randint(0, node.child_num - 1)]


def uct_selection(node):
    for m in node.children:
        if m.total == 0:
            return m
    return _max_uct(node)


def _add_move(node, move):
    if not _move_in_children(node.children, move):
        node.add_child(Node(node.opponent(), move, node))


def _generate_children(board, root):
    color = root.opponent()
    moves = board.get_all_possible_moves(color)
    for m1 in moves:
        for m2 in m1:
            _add_move(root, m2)


def _move_equal(move1, move2):
    return str(move1) == str(move2)


def _move_in_children(children, move):
    for child in children:
        if _move_equal(child.move, move):
            return True
    return False


def _node_index(children, move):
    for i in range(len(children)):
        if _move_equal(children[i].move, move):
            return i
    return -1


def _max(node):
    max_rate = -1
    max_child = None
    for child in node.children:
        #print(child.move, child.win_count, child.total, child.win_rate())
        if child.win_rate() > max_rate:
            max_rate = child.win_rate()
            max_child = child
    #print("Max: ", max_child.move, max_child.win_rate())
    return max_child.move


def _max_uct(node):
    max_uct = -1
    max_child = None
    for child in node.children:
        if child.uct() > max_uct:
            max_uct = child.uct()
            max_child = child
    return max_child


def _copy_board(board):
    return copy.deepcopy(board)


def _node_in_all_moves(node, all_moves):
    for m in all_moves:
        for move in m:
            if _move_equal(node.move, move):
                return True
    return False