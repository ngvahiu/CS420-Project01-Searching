import queue

from a_star import A_star
from visualization import Cell, Cell_Type


class Level3:
    def __init__(
        self,
        start_cell: Cell = None,
        goal_cell: Cell = None,
        grid_cells=None,
        go_up=None,
        go_down=None,
    ) -> None:
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.solution = []
        self.solution_order = []
        self.search = None
        self.cell_traverse_count = 0
        self.flood_cells = []
        self.flood_cells.append(start_cell)
        self.current_index = 0
        self.key_set = set()
        self.is_completed = False

        self.current_floor = 1
        self.go_up = go_up
        self.go_down = go_down

    def flood_fill(self, flood_cell: Cell):
        self.current_floor = flood_cell.floor

        flood_cell.visited = True
        current_cell = flood_cell
        _queue = queue.Queue()

        while current_cell:
            neighbors = current_cell.check_neighbors(
                self.grid_cells[self.current_floor]
            )

            for cell in neighbors:
                if cell.type == Cell_Type.KEY or cell.type == Cell_Type.GOAL:
                    if cell not in flood_cell.flood_to:
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                        _queue.put(cell)
                    continue
                if cell.type == Cell_Type.DOOR:
                    if cell not in flood_cell.flood_to:
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                        if cell not in self.flood_cells:
                            self.flood_cells.append(cell)
                    continue
                if cell.type == Cell_Type.UP:
                    if cell not in flood_cell.flood_to:
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                        cell.visited = True
                        # add next DOWN cell of upper floor to flood_cells
                        find_index = lambda x, y: x + y * cell.cols
                        next_down_cell = self.grid_cells[self.current_floor + 1][
                            find_index(cell.x, cell.y)
                        ]
                        cell.flood_to.append(next_down_cell)
                        next_down_cell.flooded_from.append(cell)
                        if next_down_cell not in self.flood_cells:
                            self.flood_cells.append(next_down_cell)
                    continue
                if cell.type == Cell_Type.DOWN:
                    if cell not in flood_cell.flood_to:
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                        cell.visited = True
                    continue

                cell.visited = True
                _queue.put(cell)

            if not _queue.empty():
                current_cell = _queue.get()
            else:
                current_cell = None

    def get_doors_keys(self):
        while self.flood_cells:
            flood_cell = self.flood_cells.pop(0)
            print(
                "Check: ",
                flood_cell.x,
                flood_cell.y,
                flood_cell.floor,
                flood_cell.type,
                flood_cell.cell_value,
            )

            if not flood_cell.flood_to:
                self.flood_fill(flood_cell)

                # Find which cells have same flooding range with flood_cell
                same_flooding_range = []
                for cell in self.flood_cells:
                    if cell in flood_cell.flood_to:
                        # check if two cells are flooded by same cell
                        for c in cell.flooded_from:
                            if c in flood_cell.flooded_from:
                                same_flooding_range.append(cell)
                                break

                for cell in same_flooding_range:
                    cell.flooded_from.remove(flood_cell)
                    flood_cell.flood_to.remove(cell)

                for cell in same_flooding_range:
                    cell.flood_to = flood_cell.flood_to

            for cell in flood_cell.flood_to:
                print(
                    "Flood to: ",
                    cell.x,
                    cell.y,
                    cell.type,
                    cell.cell_value,
                )
            print()

        self.clear_visited_cells()

    def clear_visited_cells(self):
        for index in self.grid_cells:
            for cell in self.grid_cells[index]:
                cell.visited = False
                cell.heuristic = 0
                cell.cost = 0
                cell.parent = None

    def run(self):
        self.get_doors_keys()
