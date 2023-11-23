import queue
from visualization import Cell, Cell_Type


class BFS:
    def __init__(self, current_cell: Cell = None, grid_cells=None) -> None:
        self.current_cell = current_cell
        self.grid_cells = grid_cells
        self.solution = []
        self.queue = queue.Queue()

    def run(self):
        self.current_cell.visited = True
        neighbors = self.current_cell.check_neighbors(self.grid_cells)

        for neighbor in neighbors:
            neighbor.parent = self.current_cell
            if(neighbor.type == Cell_Type.GOAL):
                while not  self.queue.empty():
                    self.solution.insert(0, self.queue.get())
                return True
            self.queue.put(neighbor)

        while self.current_cell.visited:
            self.current_cell = self.queue.get()
        return False

    def solution(self):
        if(len(self.solution)>0):
            return self.solution
