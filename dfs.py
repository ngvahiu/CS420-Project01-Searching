import random

from visualization import Cell, Cell_Type


class DFS:
    def __init__(self, start_cell, goal_cell: Cell = None, grid_cells=None) -> None:
        self.current_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.stack = []
        self.solution = []
        self.is_completed = False
        self.cell_traverse_count = 0
        self.current_floor = 1
        self.fail_to_solve = False

    def run(self):
        if self.is_completed:
            return
        if self.current_cell.visited is False:
            self.cell_traverse_count +=1
            self.current_cell.visited = True
            self.current_cell.visited_count['A1'] += 1
        neighbors = self.current_cell.check_neighbors(self.grid_cells)

        for cell in neighbors:
            if cell == self.goal_cell:
                self.stack.append(self.current_cell)
                self.stack.append(cell)  # append goal
                self.is_completed = True
                self.set_solution()

                return

        if neighbors:
            self.stack.append(self.current_cell)
            next_cell = random.choice(neighbors)
            self.current_cell = next_cell
        elif self.stack:
            self.current_cell = self.stack.pop()
        else:
            self.is_completed = True
            self.fail_to_solve = True

    def set_solution(self):
        while self.stack:
            cell = self.stack.pop()
            self.solution.insert(0, cell)
