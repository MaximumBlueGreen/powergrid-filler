import re
from copy import deepcopy


"""
probably want to pass a linked list of items to this function, and recursively call this function
after filling a an entry space. In doing so, call with the next item on the list. If list is empty, output
the completed board with a score and pop a word off (1 up the call stack). If no word can be placed, pop off
the most recent word. If we can place a word, place and recurse down.

Idea: set up a class for the cells on a board, with fields prev/next_across, prev/next_down, value (char),
and maybe which number(s) they full under. Can iterate through these until reaching None (null) or a '.'
both when creating the word and filling it in
also better for a dynamically updated word list if we chose to use that
"""


def _create_numbered_board(board):
    numbered_board = []
    for i in range(len(board)):
        row = []
        for j in range(len(board[i])):
            row.append((None, None))
        numbered_board.append(row)
    return numbered_board


def number(board, numbered_board):
    across_index = 1
    down_index = 1
    for i in range(len(board)):
        for j in range(len(board[i])):
            across_elem = None
            down_elem = None
            if i - 1 < 0 or board[i - 1][j] == '.':
                across_elem = across_index
                across_index += 1
            if j - 1 < 0 or board[i][j - 1] == '.':
                down_elem = down_index
                down_index += 1
            numbered_board[i][j] = (across_elem, down_elem)


def get_numbered_indices(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == '.':
                continue
            if i - 1 < 0 or board[i - 1][j] == '.':
                yield (i, j), 'down'
            if j - 1 < 0 or board[i][j - 1] == '.':
                yield (i, j), 'across'


class LL:
    def __init__(self, value=None, next_node=None, prev_node=None):
        self.value = value
        self.next_node = next_node


def _get_direction_iterator(direction):
    if direction == 'across':
        return lambda coords: (coords[0], coords[1] + 1)  # next col
    elif direction == 'down':
        return lambda coords: (coords[0] + 1, coords[1])  # next row
    else:
        raise Exception('disallowed direction ' + direction)


def _get_word(board, start_coords, next_coord):
    word = []
    x, y = start_coords
    while x < len(board) and y < len(board[x]) and board[x][y] != '.':
        word.append(board[x][y])
        x, y = next_coord((x, y))
    return word


def _insert_word(board, word, start_coords, next_coord):
    x, y = start_coords
    index = 0
    while x < len(board) and y < len(board[x]) and board[x][y] != '.':
        board[x][y] = word[index]
        index += 1
        x, y = next_coord((x, y))


def _create_LL(board):
    head = LL()
    prev = head
    for start_coords, direction in get_numbered_indices(board):
        curr = LL((start_coords, direction))
        prev.next_node = curr
        prev = curr
    return head.next_node


def _print_boards(boards):
    for board in boards:
        for row in board:
            print(''.join(row))
        print()


def get_all_boards(board, word_list_file):
    head = _create_LL(board)
    all_boards = []
    word_list = None
    with open(word_list_file, 'r') as f:
        word_list = f.read()

    def get_all_boards_rec(board, entry_iterator, score=0):
        if entry_iterator is None:
            all_boards.append((board, score))
            return

        curr_coords, curr_dir = entry_iterator.value
        next_coord = _get_direction_iterator(curr_dir)
        word = _get_word(board, curr_coords, next_coord)
        pattern = '^' + ''.join(word).replace('-', '.') + '$'  # replace empty squares with wild card
        match_objects = re.finditer(pattern, word_list, re.MULTILINE)

        if match_objects is None:
            return
        else:
            for match in match_objects:
                potential_word = match.group(0)
                board_copy = deepcopy(board)
                _insert_word(board_copy, potential_word, curr_coords, next_coord)
                get_all_boards_rec(board_copy, entry_iterator.next_node, score)  # add to score

    get_all_boards_rec(board, head)
    _print_boards(map(lambda x: x[0], all_boards))


if __name__ == '__main__':
    example_word_list_file = 'word_list.txt'
    example_board = [
        ['-', '-', '.'],
        ['-', '-', '-'],
        ['.', '-', '-']
    ]

    get_all_boards(example_board, example_word_list_file)
