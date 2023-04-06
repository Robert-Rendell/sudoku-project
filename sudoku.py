import random
from copy import deepcopy

class SudokuGenerator(object):
    """
    The board is 9x9 and is generated using a brute force algorithm.
    The difficulty is decided at the end when we have a solution, some numbers are removed
    """
    board_size = 9
    # Difficulties is the number of clues
    difficulties = {'easy': (46, 65),
                    'medium': (35, 45),
                    'hard': (29, 34),
                    'very-hard': (27,29)}  # Minimum is 17

    def __init__(self):
        self.hidden_pairs = {}
        self.max_omit_iterations = 2500

    @staticmethod
    def difficulty_strings():
        return 'easy', 'medium', 'hard'

    def generate(self, difficulty):
        min_clues, max_clues = self.difficulties[difficulty]
        number_of_clues = random.randint(min_clues, max_clues)
        problem = None

        # Solution is generated first then we omit some information to make a sudoku.
        while not problem:
            solution = self._generate_solution()
            problem = self._omit_cells(solution, number_of_clues)

        # We need both the problem and solution for validation
        return problem, solution, number_of_clues

    def _omit_cells(self, solution, number_of_clues):
        # Generate the set of all cells and omit random cells
        solvable = False
        iterations = -1
        while not solvable and iterations < self.max_omit_iterations:
            iterations = iterations + 1
            problem = deepcopy(solution)
            all_cells = [(x, y) for x in range(self.board_size) for y in range(self.board_size)]
            random.shuffle(all_cells)
            for n in range((self.board_size * self.board_size)-number_of_clues):
                x, y = all_cells[n]
                problem[x][y] = 0  # Omitted cells are represented by a 0, the view should handle this.
            solvable = self._is_solvable(problem)
        if not solvable:
            print(f"Reached solving iteration limit ({self.max_omit_iterations})")
            return None
        print(f"Solved! Number of clues: {number_of_clues}")
        return problem

    def _is_solvable(self, problem):
        print("Attempting to solve sudoku problem...")
        return self.solve(problem)

    def _generate_solution(self):
        solution = self._fresh_matrix()
        generated = False
        iterations = 1
        while not generated:
            failed_iteration = False
            for x in range(self.board_size):
                for y in range(self.board_size):
                    if not failed_iteration:
                        potential_numbers = [i + 1 for i in range(9)]
                        random.shuffle(potential_numbers)
                        while potential_numbers:
                            n = potential_numbers[-1]
                            xs = solution[x]
                            ys = [r[y] for r in solution]
                            in_square = self._is_number_in_square(n, x, y, solution)

                            if n not in xs + ys and not in_square:
                                solution[x][y] = n
                                # We can proceed, drop the other potential numbers
                                potential_numbers = []
                            else:
                                potential_numbers = potential_numbers[:-1]
                                if not potential_numbers:
                                    # There are no more possibilities. This brute force iteration must be wiped.
                                    # Let the loop calmly exit
                                    failed_iteration = True
                                    iterations += 1
                                    solution = self._fresh_matrix()
            if not failed_iteration:
                generated = True
        print("Generation completed! [Iterations:" + str(iterations) + "]")
        return solution

    def solve(self, sudoku_problem, debug=False, return_stats=False, return_solved_problem=False):
        problem = deepcopy(sudoku_problem)

        solved = False
        iterations = 1
        found = -1
        found_per_interation = []
        while not solved and found != 0:
            found = 0
            # find a cell that has enough information to make a decision
            found = self.pre_solving_extension(problem, found, debug)
            for x in range(self.board_size):
                for y in range(self.board_size):
                    found = self.solving_algorithm(problem, x, y, found, debug)
            found = self.post_solving_extension(problem, found, debug)
            if found > 0:
                iterations += 1

            if return_stats:
                found_per_interation.append(found)

            if (iterations > 81):
                print("iterations > 81 and found =" + str(found))
                found = -1

            solved = self.is_solved(problem)
        if return_stats:
            if return_solved_problem:
                return solved, iterations, found_per_interation, problem
            else:
                return solved, iterations, found_per_interation
        return solved

    def solving_algorithm(self, problem, x, y, found, debug):
        # information
        # vertical line
        # horizonal line
        # cell

        # numbers it can be
        # numbers it can't be

        # union of both sets
        # if there's one possibility left, that's your number
        # might be useless if it's just generating the solution
        # but based on the rules it'll tell you if it's possible
        # to solve.
        current_cell = problem[x][y]
        if (current_cell == 0):
            potential_numbers = set([i + 1 for i in range(9)])

            xs = [c for c in problem[x] if c > 0]
            ys = [r[y] for r in problem if r[y] > 0]

            cannot_be = self.numbers_cell_cannot_be(x, y, xs, ys, problem)
            can_be = potential_numbers - cannot_be
            #if (len(can_be) == 2):
                #if debug:
                #    print(f"Length 2 ({x},{y}): {can_be}")
            if (len(can_be) == 1):
                found += 1
                problem[x][y] = can_be.pop()
                if debug:
                    self.found_cell(x,y,problem[x][y])
                    self.display_matrix(problem)
        return found 

    def pre_solving_extension(self, problem, found, debug):
        return found

    def post_solving_extension(self, problem, found, debug):
        return found

    def numbers_cell_cannot_be(self, x, y, xs, ys, problem):
        return set(xs + ys + self.numbers_in_square(x, y, problem))

    def found_cell(self, x, y, new_value):
        pass
        # print(f"({x},{y}) ==> {new_value}")

    def is_solved(self, problem):
        for x in range(self.board_size):
            for y in range(self.board_size):
                current_cell = problem[x][y]
                if current_cell < 1:
                    return False
        return True

    @staticmethod
    def display_matrix(matrix):
        for row in matrix:
            print(row)

    @staticmethod
    def get_square_for_cell(x, y):
        square_x = int(3 * int(x / 3))
        square_y = int(3 * int(y / 3))
        return square_x, square_y

    def sq_to_str(self, x, y):
        sx, sy = self.get_square_for_cell(x,y)
        return int(sx+((sy / 3)+1 if sy > 0 else 1))

    @classmethod
    def _is_number_in_square(cls, target, x, y, matrix):
        # Find the square (3x3) that the cell (9x9) belongs to.
        # Take advantage of integer casting dropping the remainder.
        square_x, square_y = cls.get_square_for_cell(x, y)
        for c in range(3):
            for r in range(3):
                if matrix[c + square_x][r + square_y] == target:
                    return True
        return False

    @staticmethod
    def numbers_in_square(x, y, matrix):
        result = []
        square_x = int(3 * int(x / 3))
        square_y = int(3 * int(y / 3))
        for c in range(3):
            for r in range(3):
                cell = matrix[c + square_x][r + square_y]
                if cell > 0:
                    result.append(cell)
        return result

    def count_cells_still_to_find(self, problem):
        zeros = 0
        for x in range(self.board_size):
            for y in range(self.board_size):
                if problem[x][y] == 0:
                    zeros = zeros +1
        return zeros

    def _fresh_matrix(self):
        return [[0 for i in range(self.board_size)] for i in range(self.board_size)]


class ExtendedSolver(SudokuGenerator):
    def find_possible_cells_for_each_number(self, problem):
        possible_cells = { num: set([]) for num in range(1,10) }
        for x in range(self.board_size):
            for y in range(self.board_size):
                current_cell_value = problem[x][y]
                if (current_cell_value == 0):
                    potential_numbers = set([i + 1 for i in range(9)])

                    xs = [c for c in problem[x] if c > 0]
                    ys = [r[y] for r in problem if r[y] > 0]

                    cannot_be = set(xs + ys + self.numbers_in_square(x, y, problem))
                    can_be = potential_numbers - cannot_be
                    for num in can_be:
                        possible_cells[num].add((x, y))
        return possible_cells

class SingleAxisIntersectSolver(ExtendedSolver):

    def find_single_axis_intersection_cell(self, problem):
        single_axis_cells = []
        possible_cells = self.find_possible_cells_for_each_number(problem)
        # print("---")
        for num, cells in possible_cells.items():
            # Look for unique axis
            xc = {}
            yc = {}
            unique_x = -1
            unique_y = -1

            for x, y in cells:
                xc[x] = xc.get(x) + 1 if xc.get(x) else 1
                yc[y] = yc.get(y) + 1 if yc.get(y) else 1

            for x, c in xc.items():
                if c == 1:
                    unique_x = x

            for y, c in yc.items():
                if c == 1:
                    unique_y = y
            for x, y in cells:
                if x == unique_x or y == unique_y:
                    single_axis_cell = (x, y, num)
                    single_axis_cells.append(single_axis_cell)
        return single_axis_cells

    def post_solving_extension(self, problem, found, debug):
        cells = self.find_single_axis_intersection_cell(problem)
        for x, y, num in cells:
            found = found + 1
            problem[x][y] = num
            self.found_cell(x, y, num)
            return found
        return found

class CouldBeIn(SingleAxisIntersectSolver):
    def pre_solving_extension(self, problem, found, debug):
        super().pre_solving_extension(problem, found, debug)
        possible_numbers_in_square = { num: {} for num in range(1,10) }
        for k,v in self.find_possible_cells_for_each_number(problem).items():
            if debug:
                print(f"{k}:")
            for x, y in v:
                square = self.sq_to_str(x, y)
                cells = possible_numbers_in_square[square].get(k)
                cell = x, y
                if not cells:
                    possible_numbers_in_square[square][k] = [cell]
                else:
                    possible_numbers_in_square[square][k].append(cell)
                if debug:
                    print(f"could be in: ({y+1}, {x+1}) [Square: {square}]")
            if debug:
                print("---")

        shared_axis_cells_per_n = {}
        two_numbers_two_cells = {}
        for k, v in possible_numbers_in_square.items():
            if debug:
                print(f"=== For square {k}, possible numbers and cells are")
            for n, cells in v.items():
                if debug:
                    print(f"Number {n} could be in - {cells}")
                two_numbers_two_cells.setdefault(tuple(sorted(cells)), []).append(n)
                # Find coordinates that share the same axis
                shared_axis_cells = self.find_cells_that_share_axis(cells)
                if len(shared_axis_cells) > 0:
                    shared_axis_cells_per_n[n] = shared_axis_cells
                    if debug:
                        print(f"Shared axis cells: {n} - {shared_axis_cells}")

        hidden_pairs = {}
        for k, v in two_numbers_two_cells.items():
            if len(v) == 2 and len(k) == 2:
                hidden_pairs[k] = v
                if debug:
                    print(f"{k} {v}")
        
        if debug:
            print(f"Number of hidden pairs: {len(hidden_pairs)}")

        #filter hidden pairs

        zeros = self.count_cells_still_to_find(problem)
        if debug:
            print(f"{zeros} numbers still to get.")

        self.hidden_pairs = hidden_pairs
        return 0

    def numbers_cell_cannot_be(self, x, y, xs, ys, problem):
        cannot_be = super().numbers_cell_cannot_be(x, y, xs, ys, problem)
        if len(self.hidden_pairs) > 0:
            for cells_set, number_pair in self.hidden_pairs.items():
                current_cell = x, y
                n1, n2 = number_pair
                if not current_cell in cells_set:
                    intersection = self.find_cells_that_share_axis(list(cells_set) + [current_cell])
                    for k, v in intersection.items():
                        # print(f"{current_cell} n:{n1},{n2} {k} {v}")
                        if len(v) > 2:
                            n1, n2 = number_pair
                            cannot_be.add(n1)
                            cannot_be.add(n2)
        return cannot_be

    def find_cells_that_share_axis(self, cells):
        xc = {}
        yc = {}
        shared_x = -1
        shared_y = -1
        shared_axis = {}
        for x, y in cells:
            for i, j in cells:
                if x == i and j == y:
                    continue
                if x == i:
                    axis = (x, "-")
                    cell = (x, y)
                    shared_axis.setdefault(axis, set([])).add(cell)

                if y == j:
                    axis = ("-", y)
                    cell = (x, y)
                    shared_axis.setdefault(axis, set([])).add(cell)
        return shared_axis





