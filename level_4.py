from visualization import Cell, Cell_Type
import random
import heapq
from level_3  import Level3
class Level4:
    def __init__(
        self,
        start_cell: Cell = None,
        goal_cell: Cell = None,
        grid_cells=None,
        sub_goal_cell= None,
        sub_start_cell= None,
        constraints = {},
        solution = [],
        search = []
    ) -> None:
        self.start_cell = start_cell
        self.goal_cell = goal_cell
        self.grid_cells = grid_cells
        self.search = search
        self.cell_traverse_count = 0
        self.key_set = set()
        self.is_completed = False
        self.sub_goal_cell = sub_goal_cell
        self.sub_start_cell = sub_start_cell
        self.fail_to_solve = False
        self.children = []
        self.solution = []
        self.current_floor = 1
        self.fail_to_solve = False
        self.attempt = 0
        for item in solution:
            self.solution.append(item)
        self.constraints = constraints
        if len(self.solution) == 0:
            for i in range(len(self.sub_goal_cell)):
                if i == 0:
                    self.search.append(Level3(self.sub_start_cell[i], self.sub_goal_cell[i], self.grid_cells, [], [], []))
                    self.search[i].search()
                    if self.search[i].fail_to_solve:
                        self.fail_to_solve =True
                        self.is_completed = True
                    self.solution.append(self.search[i].solution)
                else:
                    solution_order = [self.sub_start_cell[i], self.sub_goal_cell[i]]
                    self.search.append(Level3(self.sub_start_cell[i], self.sub_goal_cell[i], self.grid_cells,  solution_order, [], []))
                    self.search[i].search()
                    if self.search[i].fail_to_solve:
                        self.fail_to_solve =True
                        self.is_completed = True
                    self.solution.append(self.search[i].solution)
        self.open = [self]
        heapq.heapify(self.open)
        self.cost = 0
        for item in self.solution:
            self.cost+= len(item)

    def run(self):
        if(self.is_completed):
            return
        count = 0
        while len(self.open) > 0:
            count+=1
            if(count >= 7777):
                self.fail_to_solve = True
                self.is_completed == True
                return
            node = heapq.heappop(self.open)
            conflict_list = node.validate([])
            if len(conflict_list) == 0:
                self.generate_random_path(node.solution, set(), 0)
                if self.is_completed:
                    return
            for conflict in conflict_list:
                new_node = Level4(self.start_cell, self.goal_cell, self.grid_cells,  self.sub_goal_cell, self.sub_start_cell,search = node.search, constraints = {}, solution = node.solution)
                constraint = Constraint(conflict.conflict_cell, conflict.time_step)
                new_node.constraints[conflict.agent.cell_value] = [constraint]
                for key in node.constraints:
                    if new_node.constraints.get(key) is not None:
                        new_node.constraints[key].extend(node.constraints[key])
                    else:
                        new_node.constraints[key] = [item for item in node.constraints[key]]
                is_success = new_node.update_solution()
                if is_success == False:
                    continue
                if new_node.cost < 9000:
                    heapq.heappush(self.open, new_node)
    
    def generate_random_path(self, solution, key_set, depth):
        if depth == 950:
            return
        if self.is_completed:
            return
        self.attempt +=1
        if self.attempt >= 7777:
            self.is_completed = True
            self.fail_to_solve = True
        copy_solution = [[sub_item for sub_item in item] for item in solution]
        full = True
        min = copy_solution[0]
        for i in range(1, len(copy_solution)):
            if len(copy_solution[i]) < len(copy_solution[0]):
                if len(copy_solution[i]) < len(min):
                    full = False
                    min = copy_solution[i]
        
        if min != copy_solution[0]:
            last_cell = min[-1]
            neighbors = last_cell.check_neighbors(self.grid_cells[1])
            random.shuffle(neighbors)
            
            for cell in neighbors:
                if cell.type == Cell_Type.UP:
                    continue
                if cell.type == Cell_Type.DOOR:
                    key = 'K' + cell.cell_value[1]
                    if key not in key_set:
                        continue
                min.append(cell)
                conflict_list = self.validate(copy_solution)
                if len(conflict_list) == 0:
                    cell.visited_count[min[0].cell_value]+=1
                    if cell.type == Cell_Type.KEY:
                        copy_key = key_set.copy()
                        copy_key.add(cell.cell_value)
                        self.generate_random_path(copy_solution, copy_key, depth+1)
                    else:
                        self.generate_random_path(copy_solution, key_set, depth+1)
                min.pop()
            min.append(last_cell)
            conflict_list = self.validate(copy_solution)
            if len(conflict_list) == 0:  
                self.generate_random_path(copy_solution, key_set, depth + 1)
            min.pop()

        if full:
            conflict_list = self.validate(copy_solution)
            if len(conflict_list) == 0:
                self.solution = copy_solution
                self.cell_traverse_count = len(self.solution[0])
                self.is_completed = True


    
    def update_solution(self):
        for i in range(len(self.sub_goal_cell)):
            if self.constraints.get(self.sub_start_cell[i].cell_value) == None:
                self.search[i] =Level3(self.start_cell, self.goal_cell, self.grid_cells,  self.search[i].solution_order, self.search[i].sub_solutions, [])
            else:
                if i == 0:
                    self.search[i] = Level3(self.sub_start_cell[i], self.sub_goal_cell[i], self.grid_cells,  self.search[i].solution_order, self.search[i].sub_solutions, self.constraints[self.sub_start_cell[i].cell_value])
                    is_success = self.search[i].update_solution()
                else:
                    self.search[i] = Level3(self.sub_start_cell[i], self.sub_goal_cell[i], self.grid_cells, self.search[i].solution_order, self.search[i].sub_solutions, self.constraints[self.sub_start_cell[i].cell_value])
                    is_success = self.search[i].update_solution()
                if is_success == False:
                    return False
                self.solution[i] = self.search[i].solution
        self.set_cost()
        return True
    
    
    def __lt__(self, other):
        return self.cost < other.cost
    
    def validate(self, solution):
        if len(solution) == 0:
            solution = self.solution
        conflict_list = []
        for i, array1 in enumerate(solution):
            for j, array2 in enumerate(solution):
                agent_1 = self.sub_start_cell[i]
                if i > j:
                    for index in range(min(len(array1)-1, len(array2)-1)):
                        cell_1 = array1[index]
                        cell_2 = array2[index+1]
                        cell_3 = array1[index+1]
                        if cell_3 == cell_2:
                            conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                            break
                        if cell_1.x == cell_2.x and abs(cell_1.y - cell_2.y) ==1:
                            if cell_3.y == cell_2.y:
                                conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                                break
                        if cell_1.y == cell_2.y and abs(cell_1.x - cell_2.x) == 1:
                            if cell_3.x == cell_2.x:
                                conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                                break
                elif i < j:
                    for index in range(min(len(array1)-1, len(array2)-1)):
                        cell_1 = array1[index]
                        cell_2 = array2[index]
                        cell_3 = array1[index+1]
                        if cell_3 == cell_2:
                            conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                            break
                        if cell_1.x == cell_2.x and abs(cell_1.y - cell_2.y) ==1:
                            if cell_3.y == cell_2.y:
                                conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                                break
                        if cell_1.y == cell_2.y and abs(cell_1.x - cell_2.x) == 1:
                            if cell_3.x == cell_2.x:
                                conflict_list.append(Conflict(agent_1, cell_3, index + 2))
                                break
                else:
                    pass
        return conflict_list
                            
    def set_cost(self):
        self.cost = 0
        for i in range(len(self.solution)):
            self.cost += len(self.solution[i])


class Conflict:
    def __init__(self, agent, conflict_cell, time_step):
        self.agent = agent
        self.conflict_cell = conflict_cell
        self.time_step = time_step
    
    def __eq__(self, other):
        if other is None:
            return False
        return self.agent == other.agent and self.conflict_cell == other.conflict_cell and self.time_step == other.time_step

class Constraint:
    def __init__(self,cell, time_step):
        self.cell = cell
        self.time_step = time_step
    
    def __eq__(self, other):
        return self.cell == other.cell and self.time_step == other.time_step

    def __hash__(self):
        # Use the hash value of a tuple containing the relevant attributes
        return hash((self.cell.x, self.cell.y, self.cell.floor, self.time_step))



