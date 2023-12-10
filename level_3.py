from a_star import A_star
from visualization import Cell, Cell_Type

class Level3:
    def __init__(
        self,
        start_cell: Cell = None,
        goal_cell: Cell = None,
        grid_cells=None,
        solution_order = [],
        sub_solutions = [],
        constraints = [],
        required_length = None
    ) -> None:
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.solution = []
        self.solution_order = solution_order
        self.low_level_search = None
        self.cell_traverse_count = 0
        self.current_index = 0
        self.key_set = set()
        self.is_completed = False
        self.delete_along = {}
        self.stair_set = {}
        self.current_floor = 1
        self.sub_solutions = sub_solutions
        self.constraints = constraints
        self.required_length = required_length
        self.fail_to_solve = False
        self.attempt = 0

    def recursive(self, start_cell, solution, key_set, door_set, is_up, is_down, depth):
        self.attempt += 1
        if(self.attempt >= 2345678):
            if  len(self.solution_order) == 0:
                self.is_completed = True
                self.fail_to_solve=True
                return
            else:
                return
        if(depth == 950):
            if len(self.solution_order) == 0:
                self.is_completed = True
                self.fail_to_solve=True
            return
        for cell in start_cell.flood_to:
            if cell.type == Cell_Type.DOOR:
                if 'K' + cell.cell_value[1] not in key_set:
                    continue
                elif cell.cell_value + str(cell.x) + ' ' + str(cell.y) + ' ' + str(cell.floor) in door_set:
                    continue
                else:
                    new_door_set = door_set.copy()
                    new_door_set.add(cell.cell_value + str(cell.x) + ' ' + str(cell.y) + ' ' + str(cell.floor))
                    new_solution = [item for item in solution]
                    new_solution.append(cell)
                    self.recursive(cell, new_solution, key_set, new_door_set, False, False, depth+1)
            elif cell.type == Cell_Type.KEY:
                if cell.cell_value in key_set:
                    continue
                else:
                    new_key_set = key_set.copy()
                    new_key_set.add(cell.cell_value)
                    new_solution = [item for item in solution]
                    new_solution.append(cell)
                    self.recursive(cell, new_solution, new_key_set ,set(), False, False, depth+1)
            elif cell.type == Cell_Type.UP:
                if is_up:
                    continue
                elif cell.cell_value + ' ' + str(cell.floor) in door_set:
                    continue
                else:
                    for sub_cell in cell.flood_to:
                        if sub_cell.x == cell.x and sub_cell.y == cell.y:
                            new_solution = [item for item in solution]
                            new_solution.append(cell)
                            new_solution.append(sub_cell)
                            new_door_set = door_set.copy()
                            new_door_set.add(cell.cell_value + ' ' + str(cell.floor))
                            new_door_set.add(sub_cell.cell_value + ' ' + str(sub_cell.floor))
                            self.recursive(sub_cell, new_solution, key_set, new_door_set, True, False, depth+1)
                            break
            elif cell.type == Cell_Type.DOWN:
                if is_down:
                    continue
                elif cell.cell_value + ' ' + str(cell.floor) in door_set:
                    continue
                else:
                    for sub_cell in cell.flood_to:
                        if sub_cell.x == cell.x and sub_cell.y == cell.y:
                            new_solution = [item for item in solution]
                            new_solution.append(cell)
                            new_solution.append(sub_cell)
                            new_door_set = door_set.copy()
                            new_door_set.add(cell.cell_value + ' ' + str(cell.floor))
                            new_door_set.add(sub_cell.cell_value + ' ' + str(sub_cell.floor))
                            self.recursive(sub_cell, new_solution, key_set, set(), False, True, depth+1)
                            break
            elif cell == self.goal_cell:
                if len(solution) + 1 < len(self.solution_order) or len(self.solution_order) == 0:
                    self.solution_order = [item for item in solution]
                    self.solution_order.append(cell)

    def run(self):
        if self.is_completed == True:
            return
        if len(self.solution_order) == 0:
            self.recursive(self.start_cell, [self.start_cell], set(), set(), False, False, 0)
            if len(self.solution_order) == 0:
                self.is_completed = True
                self.fail_to_solve = True

        # low_level_search for path for each two adjacent cells in solution order
        if self.current_index < len(self.solution_order) - 1:
            if self.low_level_search == None or self.low_level_search.is_completed:
                if (
                    self.solution_order[self.current_index].floor
                    != self.solution_order[self.current_index + 1].floor
                ):
                    self.current_index += 1
                else:
                    self.current_floor = self.solution_order[self.current_index].floor
                    self.low_level_search = A_star(
                        self.solution_order[self.current_index],
                        self.solution_order[self.current_index + 1],
                        self.grid_cells[self.current_floor],
                        self.key_set, [], self.start_cell
                    )
            else:
                self.low_level_search.run()
                if self.low_level_search.is_completed:
                    if (
                        self.solution_order[self.current_index + 1].type
                        == Cell_Type.KEY
                    ):
                        self.key_set.add(
                            "K"
                            + self.solution_order[self.current_index + 1].cell_value[1]
                        )
                    self.solution.extend(self.low_level_search.solution)
                    self.current_index += 1
        else:
            self.is_completed = True
            self.cell_traverse_count = 100 -  len(self.solution)
    
    def search(self):
        from level_4 import Constraint
        if self.is_completed == True:
            return
        if len(self.solution_order) == 0:
            self.recursive(self.start_cell, [self.start_cell], set(), set(), False, False, 0)
            if len(self.solution_order) == 0:
                self.is_completed = True
                self.fail_to_solve = True

        while self.is_completed == False:
            if self.current_index < len(self.solution_order) - 1:
                if self.low_level_search == None or self.low_level_search.is_completed:
                    if (
                        self.solution_order[self.current_index].floor
                        != self.solution_order[self.current_index + 1].floor
                    ):
                        self.current_index += 1
                    else:
                        self.current_floor = self.solution_order[self.current_index].floor
                        self.low_level_search = A_star(
                            self.solution_order[self.current_index],
                            self.solution_order[self.current_index + 1],
                            self.grid_cells[self.current_floor],
                            self.key_set,
                            [], self.start_cell
                        )
                else:
                    is_success = self.low_level_search.search()
                    if is_success == False:
                        return False
                    if (
                        self.solution_order[self.current_index + 1].type
                        == Cell_Type.KEY
                    ):
                        self.key_set.add(
                            "K"
                            + self.solution_order[self.current_index + 1].cell_value[1]
                        )
                    if self.solution_order[self.current_index].type == Cell_Type.KEY or self.solution_order[self.current_index].type == Cell_Type.DOOR:
                        self.solution.extend(self.low_level_search.solution[1:])
                        self.sub_solutions.append(self.low_level_search.solution[1:])
                    else:
                        self.solution.extend(self.low_level_search.solution)
                        self.sub_solutions.append(self.low_level_search.solution)
                    self.current_index += 1
            else:
                self.is_completed = True
        return True
    
    def update_solution(self):
        from level_4 import Constraint
        self.constraints = sorted(self.constraints, key=lambda x: x.time_step)
        self.low_level_search == None
        for index in range(len(self.sub_solutions)):
            if self.solution_order[index].floor != self.solution_order[index+1].floor:
                continue
            lower = 0
            for i in range(index):
                lower += len(self.sub_solutions[i])
            constraints = []
            for constraint in self.constraints:
                if constraint.time_step >= lower and constraint.time_step <= lower + len(self.sub_solutions[index]):
                    constraints.append(constraint)
            if self.low_level_search == None or set(constraints) != set(self.low_level_search.constraints):
                current_floor = self.solution_order[index].floor
                key_set = set()
                for i in range(index):
                    for cell in self.sub_solutions[i]:
                        if cell.type == Cell_Type.KEY:
                            key_set.add(cell.cell_value)
                self.low_level_search = A_star(self.solution_order[index], self.solution_order[index+1], self.grid_cells[current_floor], key_set, constraints, self.start_cell)
                is_success = self.low_level_search.search()
                if is_success == False:
                    return False
                self.sub_solutions[index] = self.low_level_search.solution
                index-=1
        for sub_solution in self.sub_solutions:
            self.solution.extend(sub_solution)
        return True
