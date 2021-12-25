from pygame import draw
from numpy import ndarray
from numpy.random import choice
from random import randint


class Cell:
    def __init__(self, color, state):
        self.color = color
        self.state = state

    def draw(self, surface, x, y, scale):
        draw.rect(surface, color=self.color, rect=(x * scale,
                                                   y * scale,
                                                   scale,
                                                   scale))


class HRoad(Cell):
    def __init__(self, color, state, orientation):
        super().__init__(color, state)
        self.state = state
        self.orientation = orientation  # orientation == 1 means right, -1 means left

    def draw(self, surface, x, y, scale):
        width = 0.75 * scale
        x_shift = 0.125 * scale
        height = 0.25 * scale
        y_shift = 0.375 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

    def __copy__(self):
        return HRoad(self.color, self.state, self.orientation)


class VRoad(Cell):
    def __init__(self, color, state, orientation):
        super().__init__(color, state)
        self.state = state
        self.orientation = orientation  # orientation == 1 means down, -1 means up

    def draw(self, surface, x, y, scale):
        width = 0.25 * scale
        x_shift = 0.375 * scale
        height = 0.75 * scale
        y_shift = 0.125 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

    def __copy__(self):
        return VRoad(self.color, self.state, self.orientation)


class Grid:
    def __init__(self, rows, columns, element):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(element)

    def draw(self, surface, scale):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x].draw(surface, x, y, scale)

    def fill(self, element, rows, columns):
        for y in range(rows[0], rows[1] + 1):
            for x in range(columns[0], columns[1] + 1):
                self.cells[y][x] = element.__copy__()

    def fill_randomly(self):
        for y in range(self.rows):
            for x in range(self.columns):
                cell = self.cells[y][x]
                alive = choice([True, False], p=[0.5, 0.5])
                if isinstance(cell, (HRoad, VRoad)) and alive:
                    self.insert(y, x)

    def free(self, y, x):
        cell = self.cells[y][x]
        if isinstance(cell, (HRoad, VRoad)):
            cell.state = 0
            cell.color = (255, 255, 255)

    def insert(self, y, x, color=None):
        cell = self.cells[y][x]
        if cell.state == 0:
            cell.state = 1
            if color is None:
                r = randint(50, 150)
                g = randint(50, 150)
                b = randint(50, 150)
                color = (r, g, b)
            cell.color = color

    def h_neighbours(self, y, x, orientation):
        neighbours = 0
        for n in range(1, 3):
            next_x = x + orientation * n
            if 0 <= next_x < self.columns:
                cell = self.cells[y][next_x]
                if cell.state == 1:
                    neighbours += 1
        return neighbours

    def v_neighbours(self, y, x, orientation):
        neighbours = 0
        for n in range(1, 3):
            next_y = y + orientation * n
            if 0 <= next_y < self.rows:
                cell = self.cells[next_y][x]
                if cell.state == 1:
                    neighbours += 1
        return neighbours

    def next_state(self):
        cells = self.cells
        was_moved = ndarray(shape=cells.shape, dtype=bool)
        was_moved.fill(False)
        r = self.rows
        c = self.columns
        for y in range(r):
            for x in range(c):
                current = cells[y][x]
                if isinstance(current, (HRoad, VRoad)):
                    o = current.orientation
                    if current.state == 1 and not was_moved[y][x]:
                        next_x, next_y = x, y
                        if isinstance(current, HRoad):
                            next_x += o
                        else:
                            next_y += o
                        if 0 <= next_x < c and 0 <= next_y < r:
                            next_cell = cells[next_y][next_x]
                            if next_cell.state == 0:
                                self.insert(next_y, next_x, current.color)
                                self.free(y, x)
                                was_moved[next_y][next_x] = True
                        else:
                            self.free(y, x)
                    elif current.state == 0:
                        alive = choice([True, False], p=[0.5, 0.5])
                        if alive:
                            if isinstance(current, VRoad):
                                if y == 0 and o == 1 or y == r - 1 and o == -1:
                                    self.insert(y, x)
                            else:
                                if x == 0 and o == 1 or x == c - 1 and o == -1:
                                    self.insert(y, x)