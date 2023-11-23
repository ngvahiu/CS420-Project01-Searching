from enum import Enum

import pygame

from constants import TILE


class Matrix:
    def __init__(self, file_name, sc: pygame.surface) -> None:
        self.file_name = file_name
        self.sc = sc
        self.start_cell = None
        self.goal_cell = None
        self.grid_cells = []

        # initialize the matrix
        self.init_matrix()

    def init_matrix(self):
        file = open(self.file_name, "r")

        if file.readable():
            size_inputs = file.readline().split()
            rows = int(size_inputs[0])
            cols = int(size_inputs[1])

            for i in range(rows):
                row = file.readline().split()

                for j in range(cols):
                    if int(row[j]) == -1:  # obstacle
                        cell = Cell(j, i, self.sc, rows, cols, Cell_Type.OBSTACLE)
                        self.grid_cells.append(cell)
                    elif int(row[j]) == 1:  # start cell
                        cell = Cell(j, i, self.sc, rows, cols, Cell_Type.START)
                        self.start_cell = cell
                        self.grid_cells.append(cell)
                    elif int(row[j]) == 2:  # goal cell
                        cell = Cell(j, i, self.sc, rows, cols, Cell_Type.GOAL)
                        self.goal_cell = cell
                        self.grid_cells.append(cell)
                    else:
                        cell = Cell(j, i, self.sc, rows, cols)
                        self.grid_cells.append(cell)

        file.close()

    def draw(self):
        [cell.draw() for cell in self.grid_cells]


class Cell_Type(Enum):
    OBSTACLE = "OBSTACLE"
    START = "START"
    GOAL = "GOAL"
    BLANK = "BLANK"


class Cell:
    def __init__(self, x, y, sc=None, rows=0, cols=0, type=Cell_Type.BLANK, parent = None) -> None:
        self.x, self.y = x, y
        self.sc = sc
        self.rows = rows
        self.cols = cols
        self.type = type
        self.visited = False
        self.parent = parent

    def draw(self):
        x, y = self.x * TILE, self.y * TILE

        if self.visited:
            pygame.draw.rect(self.sc, pygame.Color("yellow"), (x, y, TILE, TILE))
        else:
            if self.type == Cell_Type.OBSTACLE:
                pygame.draw.rect(self.sc, pygame.Color("black"), (x, y, TILE, TILE))
            elif self.type == Cell_Type.START:
                pygame.draw.rect(self.sc, pygame.Color("red"), (x, y, TILE, TILE))
            elif self.type == Cell_Type.GOAL:
                pygame.draw.rect(self.sc, pygame.Color("green"), (x, y, TILE, TILE))

        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y), (x + TILE, y), 2)
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y), (x + TILE, y + TILE), 2
        )
        pygame.draw.line(
            self.sc, pygame.Color("gray"), (x + TILE, y + TILE), (x, y + TILE), 2
        )
        pygame.draw.line(self.sc, pygame.Color("gray"), (x, y + TILE), (x, y), 2)

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
        bottom_left = self.check_cell(self.x - 1 , self.y + 1, grid_cells)

        if top and not top.type == Cell_Type.OBSTACLE and not top.visited:
            neighbors.append(top)
        if bottom and not bottom.type == Cell_Type.OBSTACLE and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.type == Cell_Type.OBSTACLE and not left.visited:
            neighbors.append(left)
        if right and not right.type == Cell_Type.OBSTACLE and not right.visited:
            neighbors.append(right)

        # Diagonal    
        if top_right and not top_right.type == Cell_Type.OBSTACLE and not top_right.visited and not top.type == Cell_Type.OBSTACLE and not right.type ==Cell_Type.OBSTACLE:
            neighbors.append(top_right)
        if top_left and not top_left.type == Cell_Type.OBSTACLE and not top_left.visited and not top.type == Cell_Type.OBSTACLE and not left.type ==Cell_Type.OBSTACLE:
            neighbors.append(top_left)
        if bottom_right and not bottom_right.type == Cell_Type.OBSTACLE and not bottom_right.visited and not bottom.type == Cell_Type.OBSTACLE and not right.type ==Cell_Type.OBSTACLE:
            neighbors.append(bottom_right)
        if bottom_left and not bottom_left.type == Cell_Type.OBSTACLE and not bottom_left.visited and not bottom.type == Cell_Type.OBSTACLE and not left.type ==Cell_Type.OBSTACLE:
            neighbors.append(bottom_left)

        return neighbors
