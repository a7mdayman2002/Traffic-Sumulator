import pygame
from grid import *

CLOCK = pygame.time.Clock()
FPS = 1
SCALE = 100
WIDTH, HEIGHT = 1000, 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 100, 0)

GREEN_OBSTACLE = Cell(color=GREEN, state=1)
BLACK_OBSTACLE = Cell(color=BLACK, state=1)
LEFT_ROAD = HRoad(color=WHITE, state=0, orientation=-1)
RIGHT_ROAD = HRoad(color=WHITE, state=0, orientation=1)
UP_ROAD = VRoad(color=WHITE, state=0, orientation=-1)
DOWN_ROAD = VRoad(color=WHITE, state=0, orientation=1)

COP_RIGHT = pygame.image.load("cars/cop-right.png")
AMB_RIGHT = pygame.image.load("cars/amb-right.png")
TAXI_RIGHT = pygame.image.load("cars/taxi-right.png")
YELLOW_RIGHT = pygame.image.load("cars/player-right.png")
BLUE_RIGHT = pygame.image.load("cars/BlueCar-right.png")

COP = pygame.transform.scale(COP_RIGHT,(250,225))

grid = Grid(rows=6, columns=10, obstacle=GREEN_OBSTACLE)
grid.fill(DOWN_ROAD, rows=(0, 1), columns=(1, 1))
grid.fill(DOWN_ROAD, rows=(0, 1), columns=(5, 5))
grid.fill(RIGHT_ROAD, rows=(2, 2), columns=(0, 9))
grid.fill(LEFT_ROAD, rows=(3, 3), columns=(0, 9))
grid.fill(UP_ROAD, rows=(4, 5), columns=(3, 3))

pygame.display.set_caption("Traffic Simulator")
surface = pygame.display.set_mode((WIDTH, HEIGHT))
run = True
pause = True
mouse_action = None
while run:
    CLOCK.tick(FPS)
    surface.fill(BLACK)
    for event in pygame.event.get():
        mouse_press = pygame.mouse.get_pressed()
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYUP:
            key = event.key
            if key == pygame.K_ESCAPE:
                run = False
            elif key == pygame.K_SPACE:
                pause = not pause
            elif pause:
                if key == pygame.K_n:
                    grid.next_state()
                elif key == pygame.K_c:
                    grid.clear_cars()
                elif key == pygame.K_r:
                    grid.fill_with_cars()
                elif key == pygame.K_TAB:
                    grid.cells.fill(BLACK_OBSTACLE)
                elif key == pygame.K_UP:
                    mouse_action = "V-1"
                elif key == pygame.K_DOWN:
                    mouse_action = "V1"
                elif key == pygame.K_RIGHT:
                    mouse_action = "H1"
                elif key == pygame.K_LEFT:
                    mouse_action = "H-1"
                elif key == pygame.K_g:
                    mouse_action = "G"
        elif mouse_press[0] or mouse_press[2]:
            x, y = pygame.mouse.get_pos()
            x //= SCALE
            y //= SCALE
            cell = grid.cells[y][x]
            if mouse_press[0]:
                if mouse_action == "V-1":
                    grid.cells[y][x] = UP_ROAD.__copy__()
                elif mouse_action == "V1":
                    grid.cells[y][x] = DOWN_ROAD.__copy__()
                elif mouse_action == "H-1":
                    grid.cells[y][x] = LEFT_ROAD.__copy__()
                elif mouse_action == "H1":
                    grid.cells[y][x] = RIGHT_ROAD.__copy__()
                elif mouse_action == "G":
                    grid.cells[y][x] = GREEN_OBSTACLE
            else:
                grid.cells[y][x] = BLACK_OBSTACLE
    if not pause:
        grid.next_state()
    grid.draw(surface, SCALE)
    surface.blit(COP,(250,250))
    pygame.display.update()

pygame.quit()