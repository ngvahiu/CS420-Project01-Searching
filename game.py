import time
from enum import Enum

import pygame
from pygame import mixer

from a_star import A_star
from bfs import BFS
from blind_search_level_2 import BlindSearchLevel2
from constants import (
    COLOR_ACTIVE,
    COLOR_INACTIVE,
    COLOR_LIST_ACTIVE,
    COLOR_LIST_INACTIVE,
    GRADIENT_END_COLOR,
    GRADIENT_START_COLOR,
    TILE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from dfs import DFS
from dropdown import DropDown
from level_3 import Level3
from level_4 import Level4
from visualization import Matrix


class Game_State(Enum):
    MENU = "MENU"
    IN_GAME = "IN_GAME"


class Game:
    def __init__(self, screen, characters):
        self.current_level = None
        self.levels = {
            1: ["DFS", "BFS", "A_Star"],
            2: ["Blind Search", "Tree based"],
            3: ["Tree based"],
            4: ["CBS + A_Star"]
        }
        self.current_algorithm = None
        self.current_map = None
        self.state = Game_State.MENU
        self.level_list = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            WINDOW_WIDTH // 2 - 100,
            WINDOW_HEIGHT // 2,
            200,
            35,
            pygame.font.SysFont(None, 30),
            "Select level",
            ["1", "2", "3", "4"],
        )
        self.algorithm_list = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            WINDOW_WIDTH // 2 - 100,
            WINDOW_HEIGHT // 2 + 45,
            200,
            35,
            pygame.font.SysFont(None, 30),
            "Select Algorithm",
            [],
        )
        self.cases_list = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            WINDOW_WIDTH // 2 - 100,
            WINDOW_HEIGHT // 2 + 90,
            200,
            35,
            pygame.font.SysFont(None, 30),
            "Select map",
            ["Map 1", "Map 2", "Map 3", "Map 4", "Map 5"],
        )
        self.font = pygame.font.Font("freesansbold.ttf", 16)
        self.current_floor = 1
        self.screen = screen
        self.matrix = None
        self.search = None
        self.start = None
        self.characters = characters
        self.end = None
        # Load audio file
        mixer.music.load("audio/theme_song.mp3")
        mixer.music.set_volume(0.2)

    def go_up(self):
        self.current_floor += 1

    def go_down(self):
        self.current_floor -= 1

    def display(self, event_list):
        if self.state == Game_State.MENU:
            self.display_menu(event_list)
        else:
            self.display_game(event_list)

    def display_game(self, event_list):
        self.draw_background()
        self.show_instructions(event_list)
        if not self.search.is_completed:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
            self.matrix.draw(self.search.current_floor)
            pygame.display.flip()
            self.search.run()
            self.end = time.time()
            print(str(round(self.end - self.start, 1)))
        #         def show_time(self):
        # text = self.font.render(
        #     "Running time: " + str(round(self.end - self.start, 1)) + "s",
        #     True,
        #     (255, 255, 255),
        # )
        # textRect = text.get_rect()
        # textRect.center = (WINDOW_WIDTH - 3 * TILE + 2, TILE * 5 + 60)
        # self.screen.blit(text, textRect)
        else:
            if self.search.fail_to_solve:
                self.matrix.draw(self.search.current_floor)
                font = pygame.font.Font(None, 100)
                text = font.render("FAIL TO SOLVE", True, (228, 97, 27))
                text_rect = text.get_rect(center=((WINDOW_WIDTH - 230)// 2, (WINDOW_WIDTH - 120) // 2 - 100))
                self.screen.blit(text, text_rect)
            else:
                if not pygame.mixer.music.get_busy():
                    pass
                pygame.time.wait(100)
                self.matrix.draw_solution(
                    self.search.solution, self.characters
                )
                self.show_score()
        return

    def display_menu(self, event_list):
        self.draw_background()
        self.draw_title()
        self.handle_select_level_and_algorithm(event_list)

    def draw_title(self):
        pygame.display.set_caption("MOVE YOUR STEP")
        font = pygame.font.Font(None, 100)
        text = font.render("MOVE YOUR STEP", True, (228, 97, 27))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 100))
        self.screen.blit(text, text_rect)

    def draw_background(self):
        for y in range(WINDOW_HEIGHT):
            color = (
                int(
                    (GRADIENT_END_COLOR[0] - GRADIENT_START_COLOR[0])
                    * (y / WINDOW_HEIGHT)
                    + GRADIENT_START_COLOR[0]
                ),
                int(
                    (GRADIENT_END_COLOR[1] - GRADIENT_START_COLOR[1])
                    * (y / WINDOW_HEIGHT)
                    + GRADIENT_START_COLOR[1]
                ),
                int(
                    (GRADIENT_END_COLOR[2] - GRADIENT_START_COLOR[2])
                    * (y / WINDOW_HEIGHT)
                    + GRADIENT_START_COLOR[2]
                ),
            )
            pygame.draw.line(self.screen, color, (0, y), (WINDOW_WIDTH, y))

    def draw_button(self, color, rect):
        text = "Run algorithm"
        text_color = "white"
        pygame.draw.rect(self.screen, color, rect)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def handle_select_level_and_algorithm(self, event_list, offset=0):
        selected_option = self.level_list.update(event_list)
        if selected_option >= 0:
            self.level_list.main = self.level_list.options[selected_option]
            self.current_level = self.level_list.options[selected_option]
        algorithm_options = self.levels.get(selected_option + 1)
        if algorithm_options is not None:
            self.algorithm_list.options = algorithm_options
            return
        selected_option = self.algorithm_list.update(event_list)
        if selected_option >= 0:
            self.algorithm_list.main = self.algorithm_list.options[selected_option]
            self.current_algorithm = self.algorithm_list.options[selected_option]
            return
        selected_option = self.cases_list.update(event_list)
        if selected_option >= 0:
            self.cases_list.main = self.cases_list.options[selected_option]
            self.current_map = self.cases_list.options[selected_option]
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        rect = pygame.Rect(
            WINDOW_WIDTH // 2 - 100 + offset, WINDOW_HEIGHT // 2 + 135, 200, 35
        )
        for event in event_list:
            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and rect.collidepoint(mouse_x, mouse_y)
            ):
                self.set_up()
                self.draw_background()

        if rect.collidepoint(mouse_x, mouse_y):
            color = COLOR_ACTIVE
        else:
            color = COLOR_INACTIVE

        self.draw_button(color, rect)
        self.cases_list.draw(self.screen)
        self.algorithm_list.draw(self.screen)
        self.level_list.draw(self.screen)

    def show_instructions(self, event_list):
        instructions = [
            ("#e4611b", "Start position"),
            ("#2db300", "Goal position"),
            ("#810000", "Obstacle"),
        ]
        for index, (color, note) in enumerate(instructions):
            text = self.font.render(note, True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = (
                WINDOW_WIDTH - 2 * TILE,
                TILE * (index + 1) + TILE / 2 + 80,
            )
            self.screen.blit(text, textRect)
            pygame.draw.rect(
                self.screen,
                pygame.Color(color),
                (WINDOW_WIDTH - 4 * TILE - 20, TILE * (index + 1) + 80, TILE, TILE),
            )
            index += 1
        font = pygame.font.Font(None, 65)
        text = font.render(
            "21CTT2",
            True,
            (228, 97, 27),
        )
        textRect = text.get_rect()
        textRect.center = (WINDOW_WIDTH - 3 * TILE, TILE + 10)
        self.screen.blit(text, textRect)
        text = self.font.render(
            "Current floor: " + str(self.current_floor),
            True,
            (255, 255, 255),
        )
        textRect = text.get_rect()
        textRect.center = (WINDOW_WIDTH - 3 * TILE + 2, TILE * 5 + 80)
        self.screen.blit(text, textRect)
        self.handle_select_level_and_algorithm(event_list, WINDOW_WIDTH // 2 - 114)

    def show_score(self):
        text = self.font.render(
            "Naruto's score: " + str(100 - self.search.cell_traverse_count) + " pts",
            True,
            (255, 255, 255),
        )
        textRect = text.get_rect()
        textRect.center = (WINDOW_WIDTH - 3 * TILE + 2, TILE * 5 + 100)
        self.screen.blit(text, textRect)

    def set_up(self):
        if self.current_map is None or self.current_level is None or self.current_algorithm is None:
            return

        self.matrix = Matrix(
            "inputs/input"
            + self.current_map[-1]
            + "_level"
            + self.current_level
            + ".txt",
            self.screen,
        )
        if self.current_algorithm == "DFS":
            self.search = DFS(
                self.matrix.start_cell, self.matrix.goal_cell, self.matrix.grid_cells[1]
            )
        elif self.current_algorithm == "BFS":
            self.search = BFS(
                self.matrix.start_cell, self.matrix.goal_cell, self.matrix.grid_cells[1]
            )
        elif self.current_algorithm == "A_Star":
            self.search = A_star(
                self.matrix.start_cell,
                self.matrix.goal_cell,
                self.matrix.grid_cells[1],
            )
        elif self.current_algorithm == "Blind Search":
            self.search = BlindSearchLevel2(
                self.matrix.start_cell,
                self.matrix.goal_cell,
                self.matrix.grid_cells[1],
            )
        elif self.current_algorithm == "Tree based":
            if self.current_level == "2":
                self.matrix.get_doors_keys()
                self.search = Level3(
                    self.matrix.start_cell,
                    self.matrix.goal_cell,
                    self.matrix.grid_cells,
                )
            elif self.current_level == "3":
                self.matrix.get_doors_keys()
                self.search = Level3(
                    self.matrix.start_cell,
                    self.matrix.goal_cell,
                    self.matrix.grid_cells,
                )
        elif self.current_algorithm == "CBS + A_Star":
            self.matrix.get_doors_keys()
            self.search = Level4(
                self.matrix.start_cell,
                self.matrix.goal_cell,
                self.matrix.grid_cells,
                self.matrix.sub_goal_cell,
                self.matrix.sub_start_cell,
            )
        else:
            return
        self.level_list.rect.x = WINDOW_WIDTH - 214
        self.algorithm_list.rect.x = WINDOW_WIDTH - 214
        self.cases_list.rect.x = WINDOW_WIDTH - 214
        self.start = time.time()
        self.end = self.start
        self.state = Game_State.IN_GAME
        return
