from enum import Enum
import queue
import pygame
from PIL import Image, ImageDraw, ImageFont
import re
from constants import TILE, WINDOW_WIDTH, WINDOW_HEIGHT
import os

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
    def __init__(self, file_name, sc: pygame.surface, characters) -> None:
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
        self.cell_width = TILE
        self.characters = characters
        self.current_floor = 1
        self.init_matrix()
        

    def init_matrix(self):
        # file = open(self.file_name, "r")
        with open(self.file_name, "r") as file:
            # Read the dimensions from the first line
            dimensions = file.readline().strip().split()
            rows, cols = int(dimensions[0]), int(dimensions[1])
            self.cell_width = min(16/rows, 18/cols)*TILE
            for i in range(0, len(self.characters)):
                self.characters[i] = pygame.transform.scale(self.characters[i], (self.cell_width, self.cell_width))
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
        self.get_doors_keys()

    def draw(self, current_floor):
        self.current_floor = current_floor
        [cell.draw(self.cell_width) for cell in self.grid_cells[current_floor]]

    def get_center_cell(self, x, y):
        return (float(x * self.cell_width + self.cell_width / 2), float(y * self.cell_width + self.cell_width / 2))

    def draw_solution(self, solution: list):
        if isinstance(solution[0], list):
            current_floor = solution[0][self.current_solution_step if self.current_solution_step < len(solution[0]) else len(solution[0])-1].floor
            self.current_floor =current_floor
            [cell.draw_heat(self.cell_width) for cell in self.grid_cells[current_floor]]
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
                    self.sc.blit(self.characters[idx], (x1 - self.cell_width / 2, y1 - self.cell_width / 2))
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

                    self.sc.blit(self.characters[idx], (x1 - self.cell_width / 2, y1 - self.cell_width / 2))

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
            [cell.draw_heat(self.cell_width) for cell in self.grid_cells[current_floor]]
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

            self.sc.blit(self.characters[0], (x1 - self.cell_width / 2, y1 - self.cell_width / 2))
            if self.current_solution_step < len(solution):
                self.current_solution_step += 1
    
    def export_images(self, solution):
        # Create a new image
        match = re.search(r'level(\d+)', self.file_name)
        level = match.group(0)
        directory = f'{level}-images/'
        floor_count = len(self.grid_cells.keys())
        image_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        if not isinstance(solution[0], list):
            for floor in range(1, floor_count+1):
                image = Image.new("RGB", image_size, "white")
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype("Arial.ttf", 30)
                draw.text((WINDOW_WIDTH- 125,  50), f'Level: {level[-1]}\nAgent: 1\nFloor:{floor}', font=font, fill=(0,0,0), anchor="ms")
                [cell.draw_heat_image(draw, self.cell_width) for cell in self.grid_cells[floor]]
                for i in range(len(solution)-1):
                    if solution[i].floor != floor or solution[i+1].floor !=floor:
                        continue
                    start_point = self.get_center_cell(solution[i].x, solution[i].y)
                    end_point = self.get_center_cell(solution[i+1].x, solution[i+1].y)
                    draw.line([start_point, end_point], fill="blue", width=2)
                if not os.path.exists(directory):
                    os.mkdir(directory)
                image.save(directory + 'floor_' +str(floor) + '.jpg')
        else:
            for index, item in enumerate(solution):  
                for floor in range(1, floor_count+1):
                    image = Image.new("RGB", image_size, "white")
                    draw = ImageDraw.Draw(image)
                    font = ImageFont.truetype("Arial.ttf", 30)
                    draw.text((WINDOW_WIDTH- 125,  50), f'Level: {level[-1]}\nAgent: {str(index+1)}\nFloor:{floor}', font=font, fill=(0,0,0), anchor="ms")
                    [cell.draw_heat_image(draw, self.cell_width, 'A' + str(index+1)) for cell in self.grid_cells[floor]]
                    for i in range(len(item)-1):
                        if item[i].floor != floor or item[i+1].floor !=floor:
                            continue
                        start_point = self.get_center_cell(item[i].x, item[i].y)
                        end_point = self.get_center_cell(item[i+1].x, item[i+1].y)
                        draw.line([start_point, end_point], fill="blue", width=2)
                    sub_directory = directory+'agent'+ str(index+1) + '/'
                    if not os.path.exists(directory):
                        os.mkdir(directory)
                    if not os.path.exists(sub_directory):
                        os.mkdir(sub_directory)
                    image.save(sub_directory + str(floor) + '.jpg')

       

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
        self.visited_count = {
            'A1': 0,
            'A2': 0,
            'A3': 0,
            'A4': 0,
            'A5': 0,
            'A6': 0,
            'A7': 0,
            'A8': 0,
            'A9': 0,
        }
        self.visited_by = set()
        self.heat_colors = [{
            0: "#333333",
            1: "#fbf7d0",
            2: "#f7f0a1",
            3: "#f5ec8a",
            4: "#f1e45b",
            5: "#eddd2c",
            6: "#ebd914",
            7: "#d3c312",
            8: "#bcad10",
        },{
            0: "#333333",
            1: "#ccffdd",
            2: "#99ffbb",
            3: "#66ff99",
            4: "#33ff77",
            5: "#00ff55",
            6: "#00e64d",
            7: "#00cc44",
            8: "#009933",
        }, 
        {
            0: "#333333",
            1: "#ffd1b3",
            2: "#ffb380",
            3: "#ff944d",
            4: "#ff8533",
            5: "#ff6600",
            6: "#e65c00",
            7: "#cc5200",
            8: "#b34700",
        },
        {
            0: "#333333",
            1: "#b3c6ff",
            2: "#99b3ff",
            3: "#668cff",
            4: "#3366ff",
            5: "#0040ff",
            6: "#0039e6",
            7: "#0033cc",
            8: "#002db3",
        },
        {
            0: "#333333",
            1: "#ff99ff",
            2: "#ff66ff",
            3: "#ff4dff",
            4: "#ff1aff",
            5: "#ff00ff",
            6: "#e600e6",
            7: "#b300b3",
            8: "#990099",
        },
        {
            0: "#333333",
            1: "#cc99ff",
            2: "#b366ff",
            3: "#a64dff",
            4: "#9933ff",
            5: "#8000ff",
            6: "#7300e6",
            7: "#6600cc",
            8: "#5900b3",
        },
        {
            0: "#333333",
            1: "#b3ffff",
            2: "#80ffff",
            3: "#4dffff",
            4: "#00ffff",
            5: "#00e6e6",
            6: "#00b3b3",
            7: "#009999",
            8: "#006666",
        },
        {
            0: "#333333",
            1: "#ffe6f7",
            2: "#ffb3e6",
            3: "#ff80d5",
            4: "#ff4dc4",
            5: "#ff1ab3",
            6: "#e60099",
            7: "#cc0088",
            8: "#b30077",
        },
        {
            0: "#333333",
            1: "#d1d1e0",
            2: "#b3b3cc",
            3: "#9494b8",
            4: "#7575a3",
            5: "#666699",
            6: "#5c5c8a",
            7: "#52527a",
            8: "#47476b",
        }]
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

    def draw(self, cell_width):
        x, y = self.x * cell_width, self.y * cell_width

        if self.visited:
            pygame.draw.rect(self.sc, pygame.Color("#EBE3D5"), (x, y, cell_width, cell_width))
        else:
            pygame.draw.rect(
                self.sc, pygame.Color("#333333"), (x, y, cell_width, cell_width)
            )

        if self.type == Cell_Type.OBSTACLE:
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.START:
            pygame.draw.rect(self.sc, pygame.Color("#e4611b"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.GOAL:
            pygame.draw.rect(self.sc, pygame.Color("#2db300"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.KEY:
            self.draw_text_in_center(self.cell_value, x, y, cell_width, cell_width, (244, 206, 20))
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, cell_width, cell_width))
            self.draw_text_in_center(self.cell_value, x, y, cell_width, cell_width, (255, 255, 255))

        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y), (x + cell_width, y), 2)
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + cell_width, y), (x + cell_width, y + cell_width), 2
        )
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + cell_width, y + cell_width), (x, y + cell_width), 2
        )
        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y + cell_width), (x, y), 2)
    
    def hex_to_rgp(self, hex):
        hex = hex[1:]
        return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))     

    def draw_heat_image(self, draw, cell_width, agent = 'A1'):
        x, y = self.x * cell_width, self.y * cell_width
        x2, y2 = self.x*cell_width + cell_width, self.y*cell_width + cell_width
        value = [(x,y), (x2,y2)]
        font = ImageFont.truetype("Arial.ttf", 16)
        
        draw.rectangle(
            value,
            fill= self.hex_to_rgp(self.heat_colors[int(agent[-1])-1][self.visited_count[agent] if self.visited_count[agent] <= 8 else 8]),
            width = 1
        )
        if self.type == Cell_Type.OBSTACLE:
            draw.rectangle(value, fill=(129, 0, 0), outline=None, width=1)
        elif self.type == Cell_Type.START:
            draw.rectangle(value, fill=self.hex_to_rgp("#e4611b"), outline=None, width=1)
        elif self.type == Cell_Type.GOAL:
            draw.rectangle(value, fill=self.hex_to_rgp("#2db300"), outline=None, width=1)
        elif self.type == Cell_Type.KEY:
            draw.text(((x+x2)/2, (y+y2)/2), self.cell_value, font=font, fill=(244, 206, 20), anchor="ms")
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            draw.rectangle(value, fill="#810000", outline=None, width=1)
            draw.text(((x+x2)/2, (y+y2)/2), self.cell_value, font=font, fill=(255, 255, 255), anchor="ms")

        draw.line([x, y, x, y2], fill="gray",  width=1)
        draw.line([x, y, x2, y], fill="gray", width=1)
        draw.line([x2, y, x2, y2], fill="gray", width=1)
        draw.line([x, y2, x2, y2], fill="gray", width=1)



    def draw_heat(self, cell_width, agent='A1'):
        x, y = self.x * cell_width, self.y * cell_width
        pygame.draw.rect(
            self.sc,
            pygame.Color(
                self.heat_colors[int(agent[-1])-1][self.visited_count[agent] if self.visited_count[agent] <= 8 else 8]
            ),
            (x, y, cell_width, cell_width),
        )

        if self.type == Cell_Type.OBSTACLE:
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.START:
            pygame.draw.rect(self.sc, pygame.Color("#e4611b"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.GOAL:
            pygame.draw.rect(self.sc, pygame.Color("#2db300"), (x, y, cell_width, cell_width))
        elif self.type == Cell_Type.KEY:
            self.draw_text_in_center(self.cell_value, x, y, cell_width, cell_width, (244, 206, 20))
        elif (
            self.type == Cell_Type.DOOR
            or self.type == Cell_Type.UP
            or self.type == Cell_Type.DOWN
        ):
            pygame.draw.rect(self.sc, pygame.Color("#810000"), (x, y, cell_width, cell_width))
            self.draw_text_in_center(self.cell_value, x, y, cell_width, cell_width, (255, 255, 255))

        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y), (x + cell_width, y), 1)
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + cell_width, y), (x + cell_width, y + cell_width), 1
        )
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + cell_width, y + cell_width), (x, y + cell_width), 1
        )
        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y + cell_width), (x, y), 1)

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
