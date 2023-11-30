from enum import Enum

import pygame

from constants import TILE


class Matrix:
    def __init__(self, file_name, sc: pygame.surface) -> None:
        self.file_name = file_name
        self.sc = sc
        self.start_cell = None
        self.goal_cell = None
        self.grid_cells = {1: [], 2: []}
        self.key_cells = {1: [], 2: []}
        self.door_cells = {1: [], 2: []}
        self.current_solution_step = 0
        # initialize the matrix
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
                                rows,
                                cols,
                                cell_type,
                                cell_value=cell_value,
                            )
                            self.grid_cells[int(current_floor)].append(cell)
                            self.door_cells[int(current_floor)].append(cell)
                        elif cell_value.isdigit():
                            value = int(cell_value)
                            if value == 1:
                                cell_type = Cell_Type.START
                                cell = Cell(j, i, self.sc, rows, cols, cell_type)
                                self.start_cell = cell
                            elif value == 2:
                                cell_type = Cell_Type.GOAL
                                cell = Cell(j, i, self.sc, rows, cols, cell_type)
                                self.goal_cell = cell
                            else:
                                cell_type = Cell_Type.BLANK
                                cell = Cell(j, i, self.sc, rows, cols, cell_type)

                            self.grid_cells[int(current_floor)].append(cell)
                        else:
                            cell_type = Cell_Type.OBSTACLE
                            cell = Cell(j, i, self.sc, rows, cols, cell_type)
                            self.grid_cells[int(current_floor)].append(cell)
                    i += 1

        # return grid

        # file.close()

    def draw(self, current_floor):
        [cell.draw() for cell in self.grid_cells[current_floor]]

    def get_center_cell(self, x, y):
        return (float(x * TILE + TILE / 2), float(y * TILE + TILE / 2))

    def draw_solution(self, solution: list, current_floor, naruto):
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
            pygame.draw.line(self.sc, pygame.Color("#66ccff"), (x1, y1), (x2, y2), 2)

            (x1, y1) = (x2, y2)

        self.sc.blit(naruto, (x1 - TILE / 2, y1 - TILE / 2))
        if self.current_solution_step < len(solution):
            self.current_solution_step += 1


class Cell_Type(Enum):
    OBSTACLE = "OBSTACLE"
    START = "START"
    GOAL = "GOAL"
    BLANK = "BLANK"
    UP = "UP"
    DOWN = "DOWN"
    KEY = "KEY"
    DOOR = "DOOR"


class Cell:
    def __init__(
        self,
        x,
        y,
        sc=None,
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
        self.rows = rows
        self.cols = cols
        self.type = type
        self.visited = False
        self.heuristic = heuristic
        self.visited_count = 0
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
        self.font = pygame.font.Font(None, 36)

        if type == Cell_Type.DOOR:
            self.key = "K" + self.cell_value[1]
            self.unlocked = False

    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

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

        if top and not top.type == Cell_Type.OBSTACLE and not top.visited:
            neighbors.append(top)
        if bottom and not bottom.type == Cell_Type.OBSTACLE and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.type == Cell_Type.OBSTACLE and not left.visited:
            neighbors.append(left)
        if right and not right.type == Cell_Type.OBSTACLE and not right.visited:
            neighbors.append(right)

        # Diagonal
        if (
            top_right
            and not top_right.type == Cell_Type.OBSTACLE
            and not top_right.visited
            and not top.type == Cell_Type.OBSTACLE
            and not right.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(top_right)
        if (
            top_left
            and not top_left.type == Cell_Type.OBSTACLE
            and not top_left.visited
            and not top.type == Cell_Type.OBSTACLE
            and not left.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(top_left)
        if (
            bottom_right
            and not bottom_right.type == Cell_Type.OBSTACLE
            and not bottom_right.visited
            and not bottom.type == Cell_Type.OBSTACLE
            and not right.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(bottom_right)
        if (
            bottom_left
            and not bottom_left.type == Cell_Type.OBSTACLE
            and not bottom_left.visited
            and not bottom.type == Cell_Type.OBSTACLE
            and not left.type == Cell_Type.OBSTACLE
        ):
            neighbors.append(bottom_left)

        return neighbors
