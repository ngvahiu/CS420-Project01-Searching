import heapq

from visualization import Cell, Cell_Type


class A_star:
    def __init__(
        self, start_cell: Cell = None, goal_cell: Cell = None, grid_cells=None
    ) -> None:
        self.grid_cells = grid_cells
        self.goal_cell = goal_cell
        self.frontier = [start_cell]
        self.current_cell = start_cell
        self.is_completed = False
        self.cell_traverse_count = 0
        self.solution = []
        heapq.heapify(self.frontier)

    def manhattan_distance(self, current_cell):
        return abs(current_cell.x - self.goal_cell.x) + abs(
            current_cell.y - self.goal_cell.y
        )

    def run(self):
        if self.current_cell.type == Cell_Type.GOAL:
            self.is_completed = True
            self.set_solution()
            return
        self.current_cell = heapq.heappop(self.frontier)
        self.cell_traverse_count += 1
        self.current_cell.visited = True
        self.current_cell.visited_count += 1

        for neighbor_cell in self.current_cell.check_neighbors(self.grid_cells):
            neighbor_cell.heuristic = self.manhattan_distance(neighbor_cell)
            neighbor_cell.cost = self.current_cell.cost + 1
            neighbor_cell.parent = self.current_cell
            if neighbor_cell not in self.frontier:
                heapq.heappush(self.frontier, neighbor_cell)
            else:
                existing_cell = next(
                    cell
                    for cell in self.frontier
                    if cell.x == neighbor_cell.x and cell.y == neighbor_cell.y
                )
                if neighbor_cell.cost < existing_cell.cost:
                    existing_cell.cost = neighbor_cell.cost
                    existing_cell.parent = neighbor_cell.parent

        return False

    def set_solution(self):
        while self.current_cell:
            self.solution.insert(0, self.current_cell)
            self.current_cell = self.current_cell.parent
