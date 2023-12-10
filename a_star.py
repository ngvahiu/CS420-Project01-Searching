import heapq

from visualization import Cell, Cell_Type

class A_star:
    def __init__(
        self,
        start_cell: Cell = None,
        goal_cell: Cell = None,
        grid_cells=None,
        key_set=None,
        constraints = [],
        agent = None,
    ) -> None:
        self.grid_cells = grid_cells
        self.goal_cell = goal_cell
        self.start_cell = start_cell
        self.frontier = [start_cell]
        start_cell.time_step = 1
        self.current_cell = start_cell
        self.is_completed = False
        self.cell_traverse_count = 0
        self.solution = []
        self.key_set = key_set
        self.constraints = constraints
        self.current_floor = 1
        self.fail_to_solve = False
        self.agent = agent
        heapq.heapify(self.frontier)

    def manhattan_distance(self, current_cell):
        return abs(current_cell.x - self.goal_cell.x) + abs(
            current_cell.y - self.goal_cell.y
        )

    def run(self):
        from level_4 import Constraint
        if self.current_cell == self.goal_cell:
            self.is_completed = True
            self.set_solution()
            return
        if len(self.frontier) == 0:
            self.fail_to_solve = True
            self.is_completed = True
            return
        self.current_cell = heapq.heappop(self.frontier)
        self.cell_traverse_count += 1
        self.current_cell.visited = True
        self.current_cell.visited_count[self.agent.cell_value] += 1

        for neighbor_cell in self.current_cell.check_neighbors(self.grid_cells):
            if (
                self.key_set != None
                and neighbor_cell.type == Cell_Type.DOOR
                and neighbor_cell.key not in self.key_set
            ):
                # print(neighbor_cell.cell_value)
                continue
            if(
                (neighbor_cell.type == Cell_Type.UP or neighbor_cell.type == Cell_Type.DOWN)
                and neighbor_cell != self.goal_cell
            ):
                continue
            neighbor_cell.time_step = self.current_cell.time_step + 1
            if Constraint(neighbor_cell, neighbor_cell.time_step) in self.constraints:
                continue
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
    
    def search(self):
        from level_4 import Constraint
        self.current_cell.time_step = 1
        while self.is_completed == False:
            if self.current_cell == self.goal_cell:
                self.is_completed = True
                self.set_solution()
                return True
            if len(self.frontier) == 0:
                return False
            self.current_cell = heapq.heappop(self.frontier)
            if(Constraint(self.current_cell,self.current_cell.time_step) in self.constraints):
                continue
            self.cell_traverse_count += 1
            self.current_cell.visited=True
            self.current_cell.visited_count[self.agent.cell_value] += 1

            for neighbor_cell in self.current_cell.check_neighbors(self.grid_cells):
                if (
                    self.key_set != None
                    and neighbor_cell.type == Cell_Type.DOOR
                    and neighbor_cell.key not in self.key_set
                ):
                    continue
                if(
                    (neighbor_cell.type == Cell_Type.UP or neighbor_cell.type == Cell_Type.DOWN)
                    and neighbor_cell != self.goal_cell
                ):
                    continue
                if neighbor_cell == self.start_cell:
                    continue
                neighbor_cell.heuristic = self.manhattan_distance(neighbor_cell)
                neighbor_cell.cost = self.current_cell.cost + 1
                neighbor_cell.parent = self.current_cell
                neighbor_cell.time_step = self.current_cell.time_step + 1
                if neighbor_cell not in self.frontier:
                    heapq.heappush(self.frontier, neighbor_cell)


    def set_solution(self):
        while self.current_cell:
            if(self.current_cell.type == Cell_Type.KEY and self.current_cell.cell_value not in self.key_set):
                self.key_set.add(self.current_cell.cell_value)
            self.solution.insert(0, self.current_cell)
            self.current_cell = self.current_cell.parent
        for cell in self.grid_cells:
            cell.parent = None
            cell.cost = 0
            cell.visited = False
            cell.heuristic = 0
