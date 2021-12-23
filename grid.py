from random import randint
from pygame import draw
from numpy import ndarray

class Cell:
    def __init__(self, color, isEmpty):
        self.color = color
        self.isEmpty = isEmpty

    def draw(self, surface, x, y, scale):
        draw.rect(surface, color=self.color, rect=(x * scale,
                                                   y * scale,
                                                   scale,
                                                   scale))

class HRoad(Cell):
    def __init__(self, color):
        super().__init__(color, isEmpty=True)

    def draw(self, surface, x, y, scale):
        width = 0.75 * scale
        x_shift = 0.125 * scale
        height = 0.25 * scale
        y_shift = 0.375 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

class VRoad(Cell):
    def __init__(self, color):
        super().__init__(color, isEmpty=True)

    def draw(self, surface, x, y, scale):
        width = 0.25 * scale
        x_shift = 0.375 * scale
        height = 0.75 * scale
        y_shift = 0.125 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

class Grid:
    def __init__(self, rows, columns, element):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(element)

    def fillWith(self, element, rows, columns):
        for x in range(rows[0], rows[1] + 1):
            for y in range(columns[0], columns[1] + 1):
                self.cells[x][y] = element

    def draw(self, surface, scale):
        for x in range(self.rows):
            for y in range(self.columns):
                self.cells[y][x].draw(surface, y, x, scale)
