import pygame
from grid import *

pygame.display.set_caption("Traffic Simulator")

WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
OBSTACLE = Cell(color=(0, 80, 0), isEmpty=False)
HROAD = HRoad(color=WHITE)
VROAD = VRoad(color=WHITE)
grid = Grid(rows=6, columns=10, element=OBSTACLE)
grid.fillWith(element=HROAD, rows=(2, 3), columns=(0, 9))
grid.fillWith(element=VROAD, rows=(0, 1), columns=(3, 3))
grid.fillWith(element=VROAD, rows=(0, 1), columns=(6, 7))
grid.fillWith(element=VROAD, rows=(4, 5), columns=(4, 5))

surface = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
CLOCK = pygame.time.Clock()
run = True
while run:
    CLOCK.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
    grid.draw(surface, scale=100)
    pygame.display.update()

pygame.quit()