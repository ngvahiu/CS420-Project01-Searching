import argparse
import time

import pygame

from bfs import BFS
from constants import TILE, WINDOW_HEIGHT, WINDOW_WIDTH
from dfs import DFS
from a_star import A_star
from visualization import Matrix

# pygame setup
pygame.init()
font = pygame.font.Font("freesansbold.ttf", 16)
pygame.display.set_caption("CS420-Project01-Searching")
sc = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()
running = True


# instances
matrix = Matrix("inputs/test.txt", sc)
search = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search algorithm")
    parser.add_argument(
        "--algo", type=str, help="Enter search algorithm", default="A_star"
    )

    args = parser.parse_args()
    if args.algo == "DFS":
        search = DFS(matrix.start_cell, matrix.grid_cells)
    elif args.algo == "BFS":
        search = BFS(matrix.start_cell, matrix.grid_cells)
    elif args.algo == "A_star":
        search = A_star(matrix.start_cell, matrix.goal_cell, matrix.grid_cells)

# python main.py --algo DFS
# python main.py --algo BFS

# instructions
instructions = [
    ("red", "Start position"),
    ("green", "Goal position"),
    ("black", "Obstacle"),
]
start = time.time()
end = start


# Show instructions and timer
def show_instructions():
    # show instructions
    for index, (color, note) in enumerate(instructions):
        text = font.render(note, True, (0, 0, 0), (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (WINDOW_WIDTH - 2 * TILE, TILE * (index + 1) + TILE / 2)
        sc.blit(text, textRect)
        pygame.draw.rect(
            sc,
            pygame.Color(color),
            (WINDOW_WIDTH - 4 * TILE - 20, TILE * (index + 1), TILE, TILE),
        )

        index += 1


def show_time(end):
    # show timer
    text = font.render(
        "Running time: " + str(round(end - start, 1)) + "s",
        True,
        (0, 0, 0),
        (255, 255, 255),
    )
    textRect = text.get_rect()
    textRect.center = (WINDOW_WIDTH - 3 * TILE, TILE * 5)
    sc.blit(text, textRect)


# game loop     
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    sc.fill("white")

    # YOUR WORK
    show_instructions()
    matrix.draw()

    if not search.is_completed:
        search.run()
        end = time.time()
    else:
        matrix.draw_solution(search.solution)

    show_time(end)

    # update screen
    pygame.display.update()

    clock.tick(200)

pygame.quit()
