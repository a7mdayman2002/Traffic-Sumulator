import pygame
from grid import *

CLOCK = pygame.time.Clock()
FPS = 2
SCALE = 100
WIDTH, HEIGHT = 1000, 600

WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
RED = (100, 0, 0)
BLUE = (0, 0, 100)

GREEN_OBSTACLE = Cell(color=GREEN, state=1)
LEFT_ROAD = HRoad(color=WHITE, state=0, orientation=-1)
RIGHT_ROAD = HRoad(color=WHITE, state=0, orientation=1)
UP_ROAD = VRoad(color=WHITE, state=0, orientation=-1)
DOWN_ROAD = VRoad(color=WHITE, state=0, orientation=1)

grid = Grid(rows=6, columns=10, element=GREEN_OBSTACLE)
grid.fill(DOWN_ROAD, rows=(0, 1), columns=(1, 2))
grid.fill(DOWN_ROAD, rows=(0, 1), columns=(4, 4))
grid.fill(RIGHT_ROAD, rows=(2, 2), columns=(0, 9))
grid.fill(LEFT_ROAD, rows=(3, 3), columns=(0, 9))
grid.fill(UP_ROAD, rows=(4, 5), columns=(3, 3))
grid.fill_randomly()

pygame.display.set_caption("Traffic Simulator")
surface = pygame.display.set_mode((WIDTH, HEIGHT))
run = True
pause = False
while run:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        mouse_press = pygame.mouse.get_pressed()
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key == pygame.K_SPACE:
                pause = not pause
            elif pause and event.key == pygame.K_n:
                grid.next_state()
        elif mouse_press[0] or mouse_press[2]:
            x, y = pygame.mouse.get_pos()
            x //= SCALE
            y //= SCALE
            cell = grid.cells[y][x]
            if mouse_press[0]:
                grid.insert(y, x)
            else:
                grid.free(y, x)
    if not pause:
        grid.next_state()
    grid.draw(surface, SCALE)
    pygame.display.update()

pygame.quit()
