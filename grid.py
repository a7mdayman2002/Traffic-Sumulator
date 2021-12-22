from random import randint
from pygame import Surface, draw
from numpy import ndarray

class Cell:
    def __init__(self, color: tuple[int, int, int], isEmpty: bool):
        self.color = color
        self.isEmpty = isEmpty

    def draw(self, surface: Surface, x: int, y: int, scale: int):
        draw.rect(surface, color=self.color, rect=(x * scale,
                                                   y * scale,
                                                   scale,
                                                   scale))

class HRoad(Cell):
    def __init__(self, color: tuple[int, int, int]):
        super().__init__(color, isEmpty=True)

    def draw(self, surface: Surface, x: int, y: int, scale: int):
        width = 0.75 * scale
        x_shift = 0.125 * scale
        height = 0.25 * scale
        y_shift = 0.375 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

class VRoad(Cell):
    def __init__(self, color: tuple[int, int, int]):
        super().__init__(color, isEmpty=True)

    def draw(self, surface: Surface, x: int, y: int, scale: int):
        width = 0.25 * scale
        x_shift = 0.375 * scale
        height = 0.75 * scale
        y_shift = 0.125 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

class Grid:
    def __init__(self, rows: int, columns: int, element: Cell = None):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(element)

    def fillWith(self, element: Cell, rows: tuple[int, int], columns: tuple[int, int]):
        for x in range(rows[0], rows[1] + 1):
            for y in range(columns[0], columns[1] + 1):
                self.cells[x][y] = element

    def draw(self, surface: Surface, scale: int):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x].draw(surface, x, y, scale)
