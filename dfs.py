import random

from visualization import Cell, Cell_Type


class DFS:
    def __init__(self, current_cell: Cell = None, grid_cells=None) -> None:
        self.current_cell = current_cell
        self.grid_cells = grid_cells
        self.stack = []

    def run(self):
        if self.current_cell.type == Cell_Type.GOAL:
            return True

        self.current_cell.visited = True
        neighbors = self.current_cell.check_neighbors(self.grid_cells)

        if neighbors:
            self.stack.append(self.current_cell)
            next_cell = random.choice(neighbors)
            self.current_cell = next_cell
        elif self.stack:
            self.current_cell = self.stack.pop()

        return False
