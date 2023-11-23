import queue
from visualization import Cell, Cell_Type


class BFS:
    def __init__(self, current_cell: Cell = None, grid_cells=None) -> None:
        self.current_cell = current_cell
        self.grid_cells = grid_cells
        self.solution = []
        self.queue = queue.Queue()
        self.is_completed = False

    def run(self):
        if(self.is_completed):
            return True
        self.current_cell.visited = True
        neighbors = self.current_cell.check_neighbors(self.grid_cells)

        for neighbor in neighbors:
            neighbor.parent = self.current_cell
            if(neighbor.type == Cell_Type.GOAL):
                self.set_solution(neighbor)
                self.is_completed = True
                return True
            self.queue.put(neighbor)

        while self.current_cell.visited:
            self.current_cell = self.queue.get()
        return False

    def set_solution(self, last_cell):
        while last_cell is not None:
            self.solution.insert(0, self.last_cell)
            last_cell = last_cell.parent
