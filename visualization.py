from enum import Enum
import queue
import pygame
from PIL import Image, ImageDraw, ImageFont

from constants import TILE, WINDOW_WIDTH, WINDOW_HEIGHT

class Cell_Type(Enum):
    OBSTACLE = "OBSTACLE"
    START = "START"
    GOAL = "GOAL"
    BLANK = "BLANK"
    UP = "UP"
    DOWN = "DOWN"
    KEY = "KEY"
    DOOR = "DOOR"
    SUB_AGENT = "SUB_AGENT"
    SUB_GOAL = "SUB_GOAL"


class Matrix:
    def __init__(self, file_name, sc: pygame.surface) -> None:
        self.file_name = file_name
        self.sc = sc
        self.start_cell = None
        self.goal_cell = None
        self.sub_goal_cell = []
        self.sub_start_cell =[]
        self.grid_cells = {}
        self.key_cells = {}
        self.door_cells = {}
        self.current_solution_step = 0
        self.agent_turn = 1
        self.custom_order = {
            Cell_Type.GOAL: 0,
            Cell_Type.SUB_GOAL: 1,
            Cell_Type.KEY: 2,
            Cell_Type.DOOR: 3,
            Cell_Type.UP: 4,
            Cell_Type.DOWN: 5,
            Cell_Type.BLANK: 6,
            Cell_Type.START: 7,
            Cell_Type.SUB_AGENT: 8,
            Cell_Type.OBSTACLE: 9,
        }
        self.init_matrix()


    def init_matrix(self):
        # file = open(self.file_name, "r")
        with open(self.file_name, "r") as file:
            # Read the dimensions from the first line
            dimensions = file.readline().strip().split()
            rows, cols = int(dimensions[0]), int(dimensions[1])

            current_floor = None
            i = 0
            for line in file:
                line = line.strip()
                if line.startswith("[floor"):
                    current_floor = line.strip("[]")[-1]
                    self.grid_cells[int(current_floor)] = []
                    self.key_cells[int(current_floor)] = []
                    self.door_cells[int(current_floor)] = []
                    i = 0
                elif line:
                    floor_cells = line.split(",")
                    for j, cell_value in enumerate(floor_cells):
                        cell_value = cell_value.strip()
                        if cell_value == "UP" or cell_value == "DO":
                            cell_type = (
                                Cell_Type.UP if cell_value == "UP" else Cell_Type.DOWN
                            )
                            cell = Cell(
                                j,
                                i,
                                self.sc,
                                int(current_floor),
                                rows,
                                cols,
                                cell_type,
                                cell_value=cell_value,
                            )
                            self.grid_cells[int(current_floor)].append(cell)
                        elif cell_value[0] == "K":
                            cell_type = Cell_Type.KEY
                            cell = Cell(
                                j,
                                i,
                                self.sc,
                                int(current_floor),
                                rows,
                                cols,
                                cell_type,
                                cell_value=cell_value,
                            )
                            self.grid_cells[int(current_floor)].append(cell)
                            self.key_cells[int(current_floor)].append(cell)
                        elif cell_value[0] == "D":
                            cell_type = Cell_Type.DOOR
                            cell = Cell(
                                j,
                                i,
                                self.sc,
                                int(current_floor),
                                rows,
                                cols,
                                cell_type,
                                cell_value=cell_value,
                            )
                            self.grid_cells[int(current_floor)].append(cell)
                            self.door_cells[int(current_floor)].append(cell)
                        elif cell_value[0] == "A":
                            if(cell_value[1] == '1'):
                                cell_type = Cell_Type.START
                                cell = Cell(
                                    j,
                                    i,
                                    self.sc,
                                    int(current_floor),
                                    rows,
                                    cols,
                                    cell_type,
                                    cell_value=cell_value,
                                )
                                self.start_cell = cell
                            else:
                                cell_type = Cell_Type.SUB_AGENT
                                cell = Cell(
                                    j,
                                    i,
                                    self.sc,
                                    int(current_floor),
                                    rows,
                                    cols,
                                    cell_type,
                                    cell_value=cell_value,
                                )
                            self.sub_start_cell.append(cell)
                            self.grid_cells[int(current_floor)].append(cell)
                        elif cell_value[0] == 'T':
                            if(cell_value[1] == '1'):
                                cell_type = Cell_Type.GOAL
                                cell = Cell(
                                    j,
                                    i,
                                    self.sc,
                                    int(current_floor),
                                    rows,
                                    cols,
                                    cell_type,
                                    cell_value=cell_value,
                                )
                                self.goal_cell = cell
                            else:
                                cell_type = Cell_Type.SUB_GOAL
                                cell = Cell(
                                    j,
                                    i,
                                    self.sc,
                                    int(current_floor),
                                    rows,
                                    cols,
                                    cell_type,
                                    cell_value=cell_value,
                                )
                            self.sub_goal_cell.append(cell)
                            self.grid_cells[int(current_floor)].append(cell)
                        elif cell_value.isdigit():
                            cell_type = Cell_Type.BLANK
                            cell = Cell(
                                j,
                                i,
                                self.sc,
                                int(current_floor),
                                rows,
                                cols,
                                cell_type,
                                cell_value=cell_value,
                            )
                            self.grid_cells[int(current_floor)].append(cell)

                        else:
                            cell_type = Cell_Type.OBSTACLE
                            cell = Cell(
                                j, i, self.sc, int(current_floor), rows, cols, cell_type
                            )
                            self.grid_cells[int(current_floor)].append(cell)
                    i += 1

        self.sub_start_cell.sort(key = lambda x: x.cell_value[1])
        self.sub_goal_cell.sort(key = lambda x: x.cell_value[1])

    def draw(self, current_floor):
        [cell.draw() for cell in self.grid_cells[current_floor]]

    def get_center_cell(self, x, y):
        return (float(x * TILE + TILE / 2), float(y * TILE + TILE / 2))

    def draw_solution(self, solution: list, characters):
        if isinstance(solution[0], list):
            current_floor = solution[0][self.current_solution_step if self.current_solution_step < len(solution[0]) else len(solution[0])-1].floor
            [cell.draw_heat() for cell in self.grid_cells[current_floor]]
            for idx, sub_solution in enumerate(solution):
                if current_floor > 1 and idx > 0:
                    continue
                if idx < self.agent_turn:
                    (x1, y1) = self.get_center_cell(sub_solution[0].x, sub_solution[0].y)
                    for index in range(
                        1,
                        self.current_solution_step
                        if self.current_solution_step < len(sub_solution)
                        else len(sub_solution),
                    ):
                        
                        (x2, y2) = self.get_center_cell(sub_solution[index].x, sub_solution[index].y)

                        if sub_solution[index].floor == current_floor:
                            pygame.draw.line(self.sc, pygame.Color("#66ccff"), (x1, y1), (x2, y2), 2)
                        (x1, y1) = (x2, y2)

                    self.sc.blit(characters[idx], (x1 - TILE / 2, y1 - TILE / 2))
                else:
                    alternative_step = self.current_solution_step - 1
                    (x1, y1) = self.get_center_cell(sub_solution[0].x, sub_solution[0].y)
                    for index in range(
                        1,
                        alternative_step
                        if alternative_step < len(sub_solution)
                        else len(sub_solution),
                    ):
                        (x2, y2) = self.get_center_cell(sub_solution[index].x, sub_solution[index].y)
                        pygame.draw.line(self.sc, pygame.Color("#66ccff"), (x1, y1), (x2, y2), 2)
                        (x1, y1) = (x2, y2)

                    self.sc.blit(characters[idx], (x1 - TILE / 2, y1 - TILE / 2))

            if self.current_solution_step < 1000:
                if self.agent_turn >= len(solution):
                    self.current_solution_step += 1
                    self.agent_turn = 1
                else:
                    self.agent_turn +=1
        else:
            current_floor = solution[self.current_solution_step
            if self.current_solution_step < len(solution)
            else len(solution) - 1].floor
            [cell.draw_heat() for cell in self.grid_cells[current_floor]]
            (x1, y1) = self.get_center_cell(solution[0].x, solution[0].y)
            for index in range(
                1,
                self.current_solution_step
                if self.current_solution_step < len(solution)
                else len(solution),
            ):
                (x2, y2) = self.get_center_cell(solution[index].x, solution[index].y)

                # draw path between 2 centers
                if solution[index-1].floor == current_floor:
                    pygame.draw.line(self.sc, pygame.Color("#66ccff"), (x1, y1), (x2, y2), 2)

                (x1, y1) = (x2, y2)

            self.sc.blit(characters[0], (x1 - TILE / 2, y1 - TILE / 2))
            if self.current_solution_step < len(solution):
                self.current_solution_step += 1
    
    def export_images(self, solution):
        # Create a new image
        image_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        image = Image.new("RGB", image_size, "green")
        draw = ImageDraw.Draw(image)
        floor_count = len(self.grid_cells.keys())
        # font = ImageFont.load_default()
        if not isinstance(solution[0], list):
            [cell.draw_heat_image(draw) for cell in self.grid_cells[1]]
            for i in range(len(solution)-1):
                start_point = self.get_center_cell(solution[i].x, solution[i].y)
                end_point = self.get_center_cell(solution[i+1].x, solution[i+1].y)
                draw.line([start_point, end_point], fill="blue", width=2)
        else:
            for item in solution:            

                    # Draw the solution path on the image
                    # pass
                for i in range(len(item) - 1):
                    start_point = (item[i].x, item[i].y)
                    end_point = (item[i + 1].x, item[i + 1].y)
                    draw.line([start_point, end_point], fill="blue", width=2)

        # # Save the image
        image.save('test.jpg')

    def flood_fill(self, flood_cell):
        flood_cell.visited = True
        current_cell = flood_cell
        _queue = queue.Queue()

        if current_cell.type == Cell_Type.UP:
            find_index = lambda x, y: x + y * current_cell.cols
            next_down_cell = self.grid_cells[current_cell.floor + 1][
                find_index(current_cell.x, current_cell.y)
            ]
            current_cell.flood_to.append(next_down_cell)
            next_down_cell.flood_to.append(current_cell)

        while current_cell:
            neighbors = current_cell.check_neighbors(
                self.grid_cells[current_cell.floor]
            )
            for cell in neighbors:
                if cell in flood_cell.flood_to:
                    continue
                if cell.type == Cell_Type.UP or cell.type == Cell_Type.DOWN:
                    if flood_cell.type == cell.type:
                        cell.visited = True
                        _queue.put(cell)
                        continue
                if cell.type == Cell_Type.KEY or cell.type == Cell_Type.GOAL or cell.type == Cell_Type.UP or cell.type == Cell_Type.DOWN or cell.type == Cell_Type.SUB_AGENT or cell.type == Cell_Type.SUB_GOAL:
                    flood_cell.flood_to.append(cell)
                elif cell.type == Cell_Type.DOOR:
                    cell.visited = True
                    flood_cell.flood_to.append(cell)
                    continue
                cell.visited = True
                _queue.put(cell)

            if not _queue.empty():
                current_cell = _queue.get()
            else:
                current_cell = None

    def get_doors_keys(self):
        arr = []
        for key in self.grid_cells:
            for cell in self.grid_cells[key]:
                if cell.type != Cell_Type.OBSTACLE and cell.type != Cell_Type.GOAL and cell.type != Cell_Type.BLANK:
                    arr.append(cell)
        for cell in arr:
            self.flood_fill(cell)
            for cell in self.grid_cells[cell.floor]:
                cell.visited = False
            sorted(cell.flood_to, key=lambda cell: self.custom_order.get(cell.type, float('inf')))
        self.clear_visited_cells()

    def clear_visited_cells(self):
        for index in self.grid_cells:
            for cell in self.grid_cells[index]:
                cell.visited = False
                cell.heuristic = 0
                cell.cost = 0
                cell.parent = None
    
     # Define the custom order for Cell_Type
    

    # Define a sorting key function
    def sorting_key(self, cell):
        return self.custom_order.get(cell.type, float('inf'))



class Cell:
    def __init__(
        self,
        x,
        y,
        sc=None,
        floor=1,
        rows=0,
        cols=0,
        type=Cell_Type.BLANK,
        parent=None,
        heuristic=0,
        cost=0,
        cell_value=None,
    ) -> None:
        self.x, self.y = x, y
        self.sc = sc
        self.floor = floor
        self.rows = rows
        self.cols = cols
        self.type = type
        self.visited = False
        self.heuristic = heuristic
        self.visited_count = 0
        self.visited_by = set()
        self.heat_colors = {
            0: "#333333",
            1: "#f7f0a1",
            2: "#f5ec8a",
            3: "#f1e45b",
            4: "#eddd2c",
            5: "#ebd914",
            6: "#d3c312",
            7: "#bcad10",
        }
        self.cost = cost
        self.parent = parent
        self.cell_value = cell_value
        self.flood_to = []
        self.flooded_from = []
        self.children = []
        self.time_step = 0
        self.font = pygame.font.Font(None, 36)

        if type == Cell_Type.DOOR:
            self.key = "K" + self.cell_value[1]
            self.unlocked = False

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)


    def is_next_to(self, other):
        if self.x == other.x and abs(self.y - other.y) == 1:
            return True
        if self.y == other.y and abs(self.x - other.x) ==1:
            return True
        return False

    def __eq__(self, other):
        if other == None:
            return False
        return self.x == other.x and self.y == other.y and self.floor == other.floor

    def draw(self):
        x, y = self.x * TILE, self.y * TILE

        if self.visited:
            pygame.draw.rect(self.sc, pygame.Color("#EBE3D5"), (x, y, TILE, TILE))
        else:
            pygame.draw.rect(
                self.sc, pygame.Color(self.heat_colors[0]), (x, y, TILE, TILE)
            )

        if self.type == Cell_Type.OBSTACLE:
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.START:
            pygame.draw.rect(self.sc, pygame.Color("#e4611b"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.GOAL:
            pygame.draw.rect(self.sc, pygame.Color("#2db300"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.KEY:
            self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (244, 206, 20))
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, TILE, TILE))
            self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (255, 255, 255))

        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y), (x + TILE, y), 2)
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y), (x + TILE, y + TILE), 2
        )
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y + TILE), (x, y + TILE), 2
        )
        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y + TILE), (x, y), 2)
    
    def draw_heat_image(self, draw):
        x, y = self.x * TILE, self.y * TILE
        x2, y2 = self.x*TILE + TILE, self.y*TILE + TILE
        value = [(x,y), (x2,y2)]
        if self.type == Cell_Type.OBSTACLE:
            draw.rectangle(value, fill="#810000", outline=None, width=1)
        elif self.type == Cell_Type.START:
            draw.rectangle(value, fill="#e4611b", outline=None, width=1)
        elif self.type == Cell_Type.GOAL:
            draw.rectangle(value, fill="#2db300", outline=None, width=1)
        # elif self.type == Cell_Type.KEY:
        #     self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (244, 206, 20))
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            draw.rectangle(value, fill="#810000", outline=None, width=1)
            # self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (255, 255, 255))

        draw.line([x, y, x, y2], fill="gray",  width=2)
        draw.line([x, y, x2, y], fill="gray", width=2)
        draw.line([x2, y, x2, y2], fill="gray", width=2)
        draw.line([x, y2, x2, y2], fill="gray", width=2)



    def draw_heat(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(
            self.sc,
            pygame.Color(
                self.heat_colors[self.visited_count if self.visited_count <= 7 else 7]
            ),
            (x, y, TILE, TILE),
        )

        if self.type == Cell_Type.OBSTACLE:
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.START:
            pygame.draw.rect(self.sc, pygame.Color("#e4611b"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.GOAL:
            pygame.draw.rect(self.sc, pygame.Color("#2db300"), (x, y, TILE, TILE))
        elif self.type == Cell_Type.KEY:
            self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (244, 206, 20))
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, TILE, TILE))
            self.draw_text_in_center(self.cell_value, x, y, TILE, TILE, (255, 255, 255))

        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y), (x + TILE, y), 2)
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y), (x + TILE, y + TILE), 2
        )
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y + TILE), (x, y + TILE), 2
        )
        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y + TILE), (x, y), 2)

    def draw_text_in_center(self, text, x, y, width, height, color):
        text_surface = self.font.render(text, True, color)
        if text == "UP" or text == "DO":
            text_rect = text_surface.get_rect(
                center=(x + width // 2, y + height // 2 + 2)
            )
        else:
            text_rect = text_surface.get_rect(
                center=(x + width // 2 + 2, y + height // 2 + 2)
            )
        self.sc.blit(text_surface, text_rect)

    def check_cell(self, x, y, grid_cells: list):
        find_index = lambda x, y: x + y * self.cols
        if x < 0 or y < 0 or x > self.cols - 1 or y > self.rows - 1:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self, grid_cells: list):
        neighbors = []

        top = self.check_cell(self.x, self.y - 1, grid_cells)
        bottom = self.check_cell(self.x, self.y + 1, grid_cells)
        left = self.check_cell(self.x - 1, self.y, grid_cells)
        right = self.check_cell(self.x + 1, self.y, grid_cells)

        top_right = self.check_cell(self.x + 1, self.y - 1, grid_cells)
        bottom_right = self.check_cell(self.x + 1, self.y + 1, grid_cells)
        top_left = self.check_cell(self.x - 1, self.y - 1, grid_cells)
        bottom_left = self.check_cell(self.x - 1, self.y + 1, grid_cells)

        if top and not top.type == Cell_Type.OBSTACLE and top.visited == False:
            neighbors.append(top)
        if bottom and not bottom.type == Cell_Type.OBSTACLE and bottom.visited == False:
            neighbors.append(bottom)
        if left and not left.type == Cell_Type.OBSTACLE and left.visited == False:
            neighbors.append(left)
        if right and not right.type == Cell_Type.OBSTACLE and right.visited == False:
            neighbors.append(right)

        # Diagonal
        if (
            top_right
            and not top_right.type == Cell_Type.OBSTACLE
            and top_right.visited == False
            and not top.type == Cell_Type.OBSTACLE
            and not right.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(top_right)
        if (
            top_left
            and not top_left.type == Cell_Type.OBSTACLE
            and top_left.visited == False
            and not top.type == Cell_Type.OBSTACLE
            and not left.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(top_left)
        if (
            bottom_right
            and not bottom_right.type == Cell_Type.OBSTACLE
            and bottom_right.visited == False
            and not bottom.type == Cell_Type.OBSTACLE
            and not right.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(bottom_right)
        if (
            bottom_left
            and not bottom_left.type == Cell_Type.OBSTACLE
            and bottom_left.visited == False
            and not bottom.type == Cell_Type.OBSTACLE
            and not left.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(bottom_left)

        return neighbors
