import queue
import random
import sys
from a_star import A_star
from dfs import DFS
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
        self.solution_order = []
        self.search = None
        self.cell_traverse_count = 0
        self.flood_cells = []
        self.flood_cells.append(start_cell)
        self.current_index = 0
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
        
        self.clear_visited_cells()

    def clear_visited_cells(self):
        for cell in self.grid_cells:
            cell.visited = False
            cell.heuristic = 0
            cell.cost = 0
            cell.parent = None

    def manhattan_distance(self, current_cell: Cell, goal_cell: Cell):
        return abs(current_cell.x - goal_cell.x) + abs(current_cell.y - goal_cell.y)

    def find_key(self, key):
        for cell in self.grid_cells:
            if cell.type == Cell_Type.KEY and cell.cell_value == key:
                return cell

    def find_path(self):
        key_set = set()
        if(self.start_cell == self.goal_cell):
            return [self.start_cell]
        path = [self.start_cell]
        for cell in self.start_cell.flood_to:
            if cell.type == Cell_Type.KEY:
                key_set.add(cell.cell_value)
                index = path.index(self.start_cell)
                path.insert(index+1, cell)
        while(self.goal_cell not in path):
            for cell in self.start_cell.flood_to:
                if cell.type == Cell_Type.DOOR and cell.cell_value == 'D4':
                    print(cell.type)
                if cell.type == Cell_Type.DOOR:
                    key = 'K' + cell.cell_value[1]
                    if key in key_set:
                        self.helper(cell, self.goal_cell, key_set, path)
                        if self.goal_cell in path:
                            break
                elif cell.type == Cell_Type.GOAL:
                    path.append(cell)
                    break

        self.solution_order = path
    
    def helper(self, start_cell, goal_cell, key_set, path):
        if start_cell.type == Cell_Type.DOOR and start_cell.cell_value == 'D4':
            print(start_cell.cell_value)
        if(start_cell not in path):
            path.append(start_cell)
        for cell in start_cell.flood_to:
            if cell.type == Cell_Type.KEY and cell not in path:
                key_set.add(cell.cell_value)
                path.append(cell)
        for cell in start_cell.flood_to:
            if cell.type == Cell_Type.DOOR:
                key = 'K' + cell.cell_value[1]
                if key in key_set:
                    self.helper(cell, goal_cell, key_set, path)
                    if goal_cell in path:
                        return
            elif cell.type == Cell_Type.GOAL:
                    path.append(cell)
                    return

    

    def run(self):
        if self.is_completed == True:
            return
        if len(self.solution_order) == 0:
            self.get_doors_keys()
            self.find_path()
            for cell in self.solution_order:
                if cell.type == Cell_Type.KEY:
                    door_available = False
                    door = 'D' +  cell.cell_value[1]
                    for subcell in self.solution_order:
                        if subcell.type == Cell_Type.DOOR and subcell.cell_value == door:
                            door_available = True
                    if door_available==False:
                        self.solution_order.remove(cell)
        
        if self.current_index < len(self.solution_order) - 1:
            if(self.search == None or self.search.is_completed):
                self.clear_visited_cells()
                self.search = A_star(self.solution_order[self.current_index], self.solution_order[self.current_index+1], self.grid_cells, self.key_set)
            else:
                self.search.run()
                if(self.search.is_completed):
                    if(self.solution_order[self.current_index+1].type == Cell_Type.KEY):
                        self.key_set.add('K' + self.solution_order[self.current_index+1].cell_value[1])
                    self.solution.extend(self.search.solution)
                    self.current_index += 1
        else:
            self.is_completed = True
  
        




        

                
        
        
