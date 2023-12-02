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
        self.delete_along = {}
        self.stair_set = {}
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
            # print(
            #     "Check: ",
            #     flood_cell.x,
            #     flood_cell.y,
            #     flood_cell.floor,
            #     flood_cell.type,
            #     flood_cell.cell_value,
            # )

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

            # for cell in flood_cell.flood_to:
            #     print(
            #         "Flood to: ",
            #         cell.x,
            #         cell.y,
            #         cell.type,
            #         cell.cell_value,
            #     )
            # print()

        self.clear_visited_cells()

    def clear_visited_cells(self):
        for index in self.grid_cells:
            for cell in self.grid_cells[index]:
                cell.visited = False
                cell.heuristic = 0
                cell.cost = 0
                cell.parent = None

    def find_path(self):
        key_set = set()
        stair_set = {}
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
                if cell.type == Cell_Type.DOOR:
                    key = 'K' + cell.cell_value[1]
                    if key in key_set:
                        self.helper(cell, self.goal_cell, key_set, path, stair_set)
                        if self.goal_cell in path:
                            break
                elif cell.type == Cell_Type.DOWN or cell.type == Cell_Type.UP:
                    self.helper(cell, self.goal_cell, key_set, path, stair_set)
                    if self.goal_cell in path:
                        break
                elif cell.type == Cell_Type.GOAL:
                    path.append(cell)
                    break
        self.stair_set = stair_set
        self.solution_order = path
   
    def helper(self, start_cell, goal_cell, key_set, path, stair_set):
        added = False
        for cell in start_cell.flood_to:
            if cell.type == Cell_Type.KEY and cell not in path:
                if(start_cell.type == Cell_Type.DOWN or start_cell.type == Cell_Type.UP):
                    if stair_set.get(start_cell.cell_value + ' ' + str(start_cell.floor)) is None:
                        path.append(start_cell)
                        stair_set[start_cell.cell_value + ' ' + str(start_cell.floor)] =start_cell
                        added = True
                else:
                    if start_cell not in path:
                        path.append(start_cell)
                        added=True
                key_set.add(cell.cell_value)
                path.append(cell)
        if added:
            return path.index(start_cell)
        for cell in start_cell.flood_to:
            if cell.type == Cell_Type.DOOR or cell.type == Cell_Type.DOWN or cell.type == Cell_Type.UP:
                if start_cell.type == cell.type and start_cell.cell_value == cell.cell_value:
                        continue
            if cell.type == Cell_Type.DOOR:
                key = 'K' + cell.cell_value[1]
                if key in key_set:
                    index = self.helper(cell, goal_cell, key_set, path, stair_set)
                    if index != -1:
                        if start_cell not in path:
                            path.insert(index, start_cell)
                            stair_set[start_cell.cell_value + ' ' + str(start_cell.floor)] =start_cell
                        return index
            elif cell.type == Cell_Type.DOWN or cell.type == Cell_Type.UP:
                index = self.helper(cell, goal_cell, key_set, path,stair_set)
                if index != -1:
                    if start_cell not in path and (start_cell.cell_value + ' ' + str(start_cell.floor)) not in stair_set:
                        path.insert(index, start_cell)
                        stair_set[start_cell.cell_value + ' ' + str(start_cell.floor)] =start_cell
                    return index
            elif cell.type == Cell_Type.GOAL:
                    if start_cell not in path:
                        if start_cell.type == Cell_Type.DOWN or start_cell.type == Cell_Type.UP:
                            if stair_set.get(start_cell.cell_value + ' ' + str(start_cell.floor)) is None:
                                path.append(start_cell)
                        else:
                            path.append(start_cell)
                    if cell not in path:
                        path.append(cell)
                        return len(path) - 2
                    return len(path) - 1
        return -1

    def run(self):
        if self.is_completed == True:
            return
        if len(self.solution_order) == 0:
            self.get_doors_keys()
            self.find_path()
            
            cells_to_remove = []

            #Clean duplicate door cells:
            for cell in self.solution_order:
                if cell.type == Cell_Type.DOOR:
                    for subcell in self.solution_order:
                        if subcell.type == cell.type and subcell != cell and subcell.cell_value == cell.cell_value and subcell not in cells_to_remove and cell not in cells_to_remove:
                            cells_to_remove.append(subcell)
            
            # Remove the unnecessary cells after the loop
            for cell in cells_to_remove:
                self.solution_order.remove(cell)


            #Clean flood to list of cells in solution order list
            for cell in self.solution_order:
                result_list = [new_cell for new_cell in cell.flood_to if new_cell in self.solution_order]
                cell.flood_to = result_list
            
            #Remove keys that are not used, and DOOR, UP, DOWN node in leaf
            changed = True
            while changed:
                changed = False
                cells_to_remove = []
                for  cell in self.solution_order:
                    if cell.type == Cell_Type.KEY:
                        door_available = False
                        door = 'D' +  cell.cell_value[1]
                        for subcell in self.solution_order:
                            if subcell.type == Cell_Type.DOOR and subcell.cell_value == door:
                                door_available = True
                        if not door_available:
                            cells_to_remove.append(cell)

                if len(cells_to_remove) > 0:
                    changed = True

                # Remove the unnecessary cells after the loop
                for cell in cells_to_remove:
                    self.solution_order.remove(cell)
                
                cells_to_remove = []
                
                for cell in self.solution_order:
                    result_list = [new_cell for new_cell in cell.flood_to if new_cell in self.solution_order]
                    if len(result_list) != len(cell.flood_to):
                       changed=True
                    if len(result_list) == 0 and (cell.type == Cell_Type.UP or cell.type == Cell_Type.DOWN or cell.type==Cell_Type.DOOR):
                        cells_to_remove.append(cell)
                    cell.flood_to = result_list
                
                if len(cells_to_remove) > 0:
                    changed = True
                
                # Remove the unnecessary cells after the loop
                for cell in cells_to_remove:
                    self.solution_order.remove(cell)

            
            #Add UP and DOWN node to travel up down
            changed = True
            while(changed is True):
                changed = False
                previous_cell_index = 0
                for i in range(1, len(self.solution_order)):
                    previous_cell = self.solution_order[previous_cell_index]
                    current_cell = self.solution_order[i]
                    if(previous_cell.floor != current_cell.floor):
                        if(previous_cell.type == Cell_Type.UP and current_cell.type == Cell_Type.DOWN and current_cell.floor - previous_cell.floor == 1):
                            pass
                        elif(previous_cell.type == Cell_Type.DOWN and current_cell.type == Cell_Type.UP and previous_cell.floor - current_cell.floor == 1):
                            pass
                        else:
                            changed = True
                            if(previous_cell.floor > current_cell.floor):
                                floor = current_cell.floor
                                while(floor < previous_cell.floor):
                                    self.solution_order.insert(i, self.stair_set['UP '+ str(floor)])
                                    self.solution_order.insert(i, self.stair_set['DO ' + str(floor+1)])
                                    floor+=1
                            else:
                                floor = current_cell.floor
                                while(floor > previous_cell.floor):
                                    self.solution_order.insert(i, self.stair_set['DO ' + str(floor)])
                                    self.solution_order.insert(i, self.stair_set['UP ' + str(floor-1)])
                                    floor-=1
                            break
                    previous_cell_index = i

        
        #Search for path for each two adjacent cells in solution order
        if self.current_index < len(self.solution_order) - 1:
            if(self.search == None or self.search.is_completed):
                self.clear_visited_cells()
                if(self.solution_order[self.current_index].floor != self.solution_order[self.current_index+1].floor):
                    self.current_index+=1
                else:
                    self.current_floor = self.solution_order[self.current_index].floor
                    self.search = A_star(self.solution_order[self.current_index], self.solution_order[self.current_index+1], self.grid_cells[self.current_floor], self.key_set, self.stair_set)
            else:
                self.search.run()
                if(self.search.is_completed):
                    if(self.solution_order[self.current_index+1].type == Cell_Type.KEY):
                        self.key_set.add('K' + self.solution_order[self.current_index+1].cell_value[1])
                    self.solution.extend(self.search.solution)
                    self.current_index += 1
        else:
            self.is_completed = True
