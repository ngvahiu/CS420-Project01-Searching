import queue

from visualization import Cell, Cell_Type


class BFS:
    def __init__(self, start_cell, goal_cell, grid_cells=None) -> None:
        self.current_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.solution = []
        self.queue = queue.Queue()
        self.added_cells = set()
        self.is_completed = False
        self.cell_traverse_count = 0
        self.current_floor = 1
        self.fail_to_solve = False

    def run(self):
        if self.is_completed:
            return

        self.current_cell.visited = True
        self.current_cell.visited_count['A1'] += 1
        neighbors = self.current_cell.check_neighbors(self.grid_cells)
        self.cell_traverse_count += 1
        for neighbor in neighbors:
            if (str(neighbor.x) + " " + str(neighbor.y)) in self.added_cells:
                continue
            self.added_cells.add(str(neighbor.x) + " " + str(neighbor.y))
            neighbor.parent = self.current_cell
            if neighbor == self.goal_cell:
                self.set_solution(neighbor)
                self.is_completed = True
                return

            self.queue.put(neighbor)
        if self.queue.empty():
            self.is_completed = True
            self.fail_to_solve = True
        else:
            self.current_cell = self.queue.get()

    def set_solution(self, cell: Cell):
        while cell is not None:
            self.solution.insert(0, cell)
            cell = cell.parent