import queue
import random
import sys

from visualization import Cell, Cell_Type


class Level2:
    def __init__(
        self,
        start_cell: Cell = None,
        goal_cell: Cell = None,
        grid_cells=None,
    ) -> None:
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.solution = []

        self.flood_cells = []
        self.flood_cells.append(start_cell)

        self.key_set = set()
        self.is_completed = False

    def flood_fill(self, flood_cell: Cell):
        flood_cell.visited = True
        current_cell = flood_cell
        _queue = queue.Queue()

        while current_cell:
            neighbors = current_cell.check_neighbors(self.grid_cells)

            for cell in neighbors:
                if cell.type == Cell_Type.KEY or cell.type == Cell_Type.GOAL:
                    if cell not in flood_cell.flood_to:
                        cell.visited = True
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                    continue
                if cell.type == Cell_Type.DOOR:
                    if cell not in flood_cell.flood_to:
                        cell.flooded_from.append(flood_cell)
                        flood_cell.flood_to.append(cell)
                        if cell not in self.flood_cells:
                            self.flood_cells.append(cell)
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
            print("Check: ", flood_cell.cell_value)

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

            for cell in same_flooding_range:
                cell.flooded_from.remove(flood_cell)
                flood_cell.flood_to.remove(cell)

            for cell in same_flooding_range:
                cell.flood_to = flood_cell.flood_to

            for cell in flood_cell.flood_to:
                print("Flood to: ", cell.cell_value)
            print()

    def manhattan_distance(self, current_cell: Cell, goal_cell: Cell):
        return abs(current_cell.x - goal_cell.x) + abs(current_cell.y - goal_cell.y)

    def find_key(self, key):
        for cell in self.grid_cells:
            if cell.type == Cell_Type.KEY and cell.cell_value == key:
                return cell

    def find_path(self, start_cell: Cell, goal_cell: Cell):
        if(start_cell == goal_cell):
            return [start_cell]
        path = [start_cell]
        for cell in start_cell.flood_to:
            new_path = self.find_path(cell, goal_cell)
            if(len(new_path)>0):
                path.extend(new_path)
                break
        if(len(path) > 1):
            return path
        return[]



    def run(self):
        for cell in self.find_path(self.start_cell, self.goal_cell):
            print(cell.cell_value)
