import unittest
from sudoku import SudokuGenerator, SingleAxisIntersectSolver, CouldBeIn

class TestSudoku(unittest.TestCase):

    def setUp(self):
        self.sg = SudokuGenerator()

    def test_must_be_2_id56_18_numbers_filled(self):
        self.sg = CouldBeIn()
        problem =[
            [0, 0, 6, 0, 0, 4, 5, 0, 0],
            [5, 0, 0, 0, 0, 1, 0, 6, 0],
            [0, 0, 0, 7, 5, 6, 0, 9, 2],
            [8, 6, 5, 1, 7, 2, 9, 3, 4],
            [7, 9, 1, 5, 4, 3, 8, 2, 6],
            [0, 0, 4, 9, 6, 8, 0, 0, 5],
            [6, 5, 0, 4, 3, 7, 2, 0, 0],
            [0, 1, 0, 6, 2, 0, 0, 0, 3],
            [0, 0, 2, 8, 1, 0, 6, 0, 0],
        ]
        next_steps =[
            [0, 0, 6, 0, 0, 4, 5, 0, 0],
            [5, 0, 0, 0, 0, 1, 0, 6, 0],
            [1, 0, 0, 7, 5, 6, 0, 9, 2],
            [8, 6, 5, 1, 7, 2, 9, 3, 4],
            [7, 9, 1, 5, 4, 3, 8, 2, 6],
            [0, 0, 4, 9, 6, 8, 0, 0, 5],
            [6, 5, 0, 4, 3, 7, 2, 0, 0],
            [0, 1, 0, 6, 2, 0, 0, 0, 3],
            [0, 0, 2, 8, 1, 0, 6, 0, 0],
        ]
        # 1 in (0, 2)

        actual = self.sg.solve(problem, debug=False, return_stats=True)
        solved, iterations, found_per_interation = actual

        self.assertEqual(found_per_interation, [0])

    def test_must_be_6_id56(self):
        self.sg = SingleAxisIntersectSolver()
        problem = [
            [0, 0, 0, 0, 0, 4, 5, 0, 0],
            [5, 0, 0, 0, 0, 1, 0, 6, 0],
            [0, 0, 0, 7, 5, 6, 0, 9, 2],
            [8, 0, 0, 0, 7, 0, 9, 0, 0],
            [0, 9, 1, 0, 0, 0, 8, 2, 0],
            [0, 0, 4, 0, 6, 0, 0, 0, 5],
            [6, 5, 0, 4, 3, 7, 0, 0, 0],
            [0, 1, 0, 6, 0, 0, 0, 0, 3],
            [0, 0, 2, 8, 0, 0, 0, 0, 0],
        ]

        actual = self.sg.solve(problem, debug=False, return_stats=True)
        solved, iterations, found_per_interation = actual

        self.assertEqual(found_per_interation, [7,5,3,3,0])

    def test_solve_hard_simple_solver(self):
        expected_iterations = 8
        expected_found = [3, 7, 5, 4, 3, 19, 9]
        problem = [
            [2, 0, 7, 5, 0, 0, 0, 0, 0],
            [9, 0, 0, 7, 8, 0, 0, 6, 0],
            [0, 0, 8, 0, 9, 0, 0, 2, 5],
            [6, 8, 3, 0, 0, 5, 0, 9, 0],
            [5, 0, 2, 3, 7, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 8],
            [3, 0, 0, 9, 0, 4, 0, 8, 2],
            [0, 5, 1, 0, 2, 6, 0, 0, 0],
            [8, 0, 0, 0, 0, 0, 0, 0, 0],
        ]

        actual = self.sg.solve(problem, return_stats=True)
        solved, iterations, found_per_interation = actual

        self.assertEqual(found_per_interation, expected_found)
        self.assertEqual(iterations, expected_iterations)
        self.assertTrue(solved)

if __name__ == '__main__':
    unittest.main()