from a_star import A_star
from visualization import Cell, Cell_Type


class BlindSearchLevel2:
    def __init__(
        self, start_cell: Cell = None, goal_cell: Cell = None, grid_cells=None
    ) -> None:
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.current_cell = start_cell
        self.grid_cells = grid_cells

        self.solution = []
        self.path = []
        self.path.append(self.start_cell)
        self.cell_traverse_count = 0

        self.key_set = set()
        self.frontier = []
        self.is_completed = False

    def clean_level_2(self):
        for cell in self.grid_cells:
            cell.visited = False
            cell.parent = None
        self.frontier.clear()

    def show_path(self):
        for cell in self.path:
            print(cell.x, cell.y, cell.type, cell.cell_value)

    def update_solution(self):
        self.key_set.clear()

        for i in range(len(self.path) - 1):
            self.clean_level_2()
            search = A_star(
                self.path[i], self.path[i + 1], self.grid_cells, self.key_set
            )
            while not search.is_completed:
                search.run()

            if self.path[i].type == Cell_Type.KEY:
                self.key_set.add(self.path[i].cell_value)
            if self.path[i + 1].type == Cell_Type.KEY:
                self.key_set.add(self.path[i + 1].cell_value)

            self.solution.extend(search.solution)

    def run(self):
        if self.is_completed:
            return True

        if self.current_cell.type == Cell_Type.GOAL:
            self.is_completed = True
            self.path.append(self.current_cell)
            self.cell_traverse_count -= 100
            self.update_solution()
            return True

        self.current_cell.visited = True
        self.current_cell.visited_count += 1
        self.cell_traverse_count += 1
        neighbors = self.current_cell.check_neighbors(self.grid_cells)

        for neighbor in neighbors:
            if neighbor.type == Cell_Type.DOOR:
                if neighbor.key in self.key_set and neighbor not in self.frontier:
                    self.frontier.append(neighbor)
                    if neighbor not in self.path:
                        self.path.append(neighbor)
            elif (
                neighbor.type == Cell_Type.KEY
                and neighbor.cell_value not in self.key_set
            ):
                self.key_set.add(neighbor.cell_value)
                self.path.append(neighbor)
                self.clean_level_2()
                self.current_cell = neighbor
                return
            elif neighbor not in self.frontier:
                self.frontier.append(neighbor)

        if self.frontier:
            self.current_cell = self.frontier.pop(0)
        else:
            print("Can not solve")
