from pygame import draw
from numpy import ndarray
from numpy.random import choice


# Creates a cell with a color and state.
# When state = 1, this means that cell is filled, o.w. it is empty.
class Cell:
    def __init__(self, color, state):
        self.color = color
        self.state = state

    # We draw the cell here, the surface is the ui screen, x and y are the starting point of the cell.
    # We define the dimensions to be colored starting from that point, multiplied by its scale.
    # rect in draw.rect takes the parameters (left, top, width, height).
    def draw(self, surface, x, y, scale):
        draw.rect(surface, color=self.color, rect=(x * scale,
                                                   y * scale,
                                                   scale,
                                                   scale))

    def __copy__(self):
        return Cell(color=self.color, state=self.state)


# HRoad and VRoad are both subclasses of Cell.
# super().__init__ is called to initialize color and state.
# They have an extra field called orientation, which is the road direction.
# In VRoad -1 is for up, 1 is for down.
# In HRoad -1 is for left, 1 is for right.
class HRoad(Cell):
    def __init__(self, color, state, orientation):
        super().__init__(color, state)
        self.orientation = orientation

    # We don't draw the whole cell in roads, in order to keep the design intact.
    def draw(self, surface, x, y, scale):
        width = 0.75 * scale
        x_shift = 0.125 * scale
        height = 0.25 * scale
        y_shift = 0.375 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

    # We create a copy of self with the same parameters.
    def __copy__(self):
        return HRoad(self.color, self.state, self.orientation)


# Same as HRoad
class VRoad(Cell):
    def __init__(self, color, state, orientation):
        super().__init__(color, state)
        self.orientation = orientation

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


# Here we create the grid, it consists of: rows, columns and a 2D array of cells.
# (normal **OBSTACLE**, VRoad, HRoad)
class Grid:
    def __init__(self, rows, columns, obstacle):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(obstacle)
        self.n = 0  # pointer to control color randomizer

    # This method loops over all the cells in the array and allow them to be drawn,
    # with the color initialized in them.
    # The fun part here is if the cell type is normal (OBSTACLE), it will call the draw method in the Cell class,
    # but if it is an HRoad or VRoad, it will call the draw method in their class,
    # adjusting their sizes and keeping their design intact. :D
    def draw(self, surface, scale):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x].draw(surface, x, y, scale)

    # When the cell moves, we free its previous cell, making its color white and state 0.
    def remove_car(self, y, x):
        cell = self.cells[y][x]
        if isinstance(cell, (HRoad, VRoad)):
            cell.state = 0
            cell.color = (255, 255, 255)

    # Insert a car in the grid, by changing its state to 1 and randomly choosing a color for it
    def insert_car(self, y, x, color=None):
        cell = self.cells[y][x]
        # A statement to make sure that the selected cell is an empty HRoad or VRoad, not an OBSTACLE!
        if isinstance(cell, (HRoad, VRoad)) and cell.state == 0:
            cell.state = 1
            if color is None:
                self.n = (self.n + 1) % 8
                colors = [(0, 186, 153),
                          (255, 0, 0),
                          (0, 255, 0),
                          (0, 0, 255),
                          (254, 149, 0),
                          (64, 100, 55),
                          (206, 100, 50),
                          (176, 100, 50)]
                color = colors[self.n]
            cell.color = color

    # Initializes a copy of the same cell repeatedly.
    def fill(self, element, rows, columns):
        for y in range(rows[0], rows[1] + 1):
            for x in range(columns[0], columns[1] + 1):
                self.cells[y][x] = element.__copy__()

    # Randomly fills the grid with cars.
    def fill_with_cars(self):
        for y in range(self.rows):
            for x in range(self.columns):
                alive = choice([True, False], p=[0.25, 0.75])
                if alive:
                    self.insert_car(y, x)

    # Fills the grid with black obstacles
    def clear_grid(self):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x] = Cell(color=(0, 0, 0), state=1)

    # Makes all roads have a white color and a state of 0.
    def clear_cars(self):
        for y in range(self.rows):
            for x in range(self.columns):
                cell = self.cells[y][x]
                if isinstance(cell, (HRoad, VRoad)):
                    cell.state = 0
                    cell.color = (255, 255, 255)

    # Calculating the horizontal moves of a car, up to 2 cells ahead.
    def h_moves(self, y, x, orientation):
        moves = 0
        for n in range(1, 3):
            # Multiplied by orientation to change the direction.
            # If it's -1, then we step back or go in the opposite direction.
            next_x = x + orientation * n
            # Check if we can take a step.
            if 0 <= next_x < self.columns:
                cell = self.cells[y][next_x]
                # If the next cell is occupied, break, else take a step.
                if cell.state == 1:
                    break
                moves += 1
                # If we step from an HRoad to a VRoad,
                # don't take any more steps to avoid unrealistic jumps.
                if isinstance(cell, VRoad):
                    break
            else:
                # Take one step and let the algorithm remove the cell at the edge.
                return 1
        return moves

    # Method for actually moving the cars to their next position.
    def next_state(self):
        cells = self.cells
        # We initialize a boolean array to keep track of whether a car was moved before.
        # By default, all are set to false.
        was_moved = ndarray(shape=cells.shape, dtype=bool)
        was_moved.fill(False)
        r = self.rows
        c = self.columns
        for y in range(r):
            for x in range(c):
                # We traverse the grid, cell by cell.
                current = cells[y][x]
                # The car has to be on either roads.
                if isinstance(current, (HRoad, VRoad)):
                    o = current.orientation
                    # Check if it's a car and wasn't moved before.
                    if current.state == 1 and not was_moved[y][x]:
                        next_x, next_y = x, y
                        if isinstance(current, HRoad):
                            # speed part
                            next_x += o * self.h_moves(y, x, o)
                        else:
                            next_y += o
                        # If the next step exists on grid and is empty, free the current cell and move the car/
                        # Set its move check to True.
                        if 0 <= next_x < c and 0 <= next_y < r:
                            next_cell = cells[next_y][next_x]
                            if next_cell.state == 0:
                                self.insert_car(next_y, next_x, current.color)
                                self.remove_car(y, x)
                                was_moved[next_y][next_x] = True
                        # If it doesn't exist, free the car.
                        else:
                            self.remove_car(y, x)
                    # If the cell is empty, make a random choice to exist one or not,
                    # with the condition being at the start of the street.
                    elif current.state == 0:
                        alive = choice([True, False], p=[0.25, 0.75])
                        if alive:
                            if isinstance(current, VRoad):
                                if y == 0 and o == 1 or y == r - 1 and o == -1:
                                    self.insert_car(y, x)
                            else:
                                if x == 0 and o == 1 or x == c - 1 and o == -1:
                                    self.insert_car(y, x)