import pygame
from numpy import ndarray
from numpy.random import choice

WHITE = (255, 255, 255)
GREEN = (0, 100, 0)

# Creates a cell with a color and state.
# When state = 1, this means that cell is filled, o.w. it is empty.
class Cell:
    def __init__(self, color, state):
        self.color = color
        self.state = state

    # We create a copy of self with the same parameters.
    def __copy__(self):
        return Cell(color=self.color, state=self.state)


# HRoad and VRoad are both subclasses of Cell.
# super().__init__ is called to initialize color and state.
# They have an extra field called orientation, which is the road direction.
# and a right-horizontal-oriented image.
# In VRoad -1 is for up, 1 is for down.
# In HRoad -1 is for left, 1 is for right.
class HRoad(Cell):
    def __init__(self, state, orientation, image=None):
        super().__init__(WHITE, state)
        self.orientation = orientation
        self.image = image

    def __copy__(self):
        return HRoad(self.state, self.orientation, self.image)


# Same as HRoad
class VRoad(Cell):
    def __init__(self, state, orientation, image=None):
        super().__init__(WHITE, state)
        self.orientation = orientation

        self.image = image

    def __copy__(self):
        return VRoad(self.state, self.orientation, self.image)

GREEN_OBSTACLE = Cell(color=GREEN, state=1)
LEFT_ROAD = HRoad(state=0, orientation=-1)
RIGHT_ROAD = HRoad(state=0, orientation=1)
UP_ROAD = VRoad(state=0, orientation=-1)
DOWN_ROAD = VRoad(state=0, orientation=1)

# Here we create the grid, it consists of: rows, columns and a 2D array of cells.
# (normal **OBSTACLE**, VRoad, HRoad)
class Grid:
    def __init__(self, rows, columns, obstacle=GREEN_OBSTACLE):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(obstacle)

    def get_scale(self, screen):
        return screen.get_width() // self.columns

    # This method loops over all the cells in the array and draws them on the screen.
    def draw(self, screen):
        scale = self.get_scale(screen)
        for y in range(self.rows):
            for x in range(self.columns):
                cell = self.cells[y][x]
                width = scale
                height = scale
                x_shift = 0
                y_shift = 0
                x_pos = x * scale
                y_pos = y * scale
                image = None
                if isinstance(cell, (HRoad, VRoad)):
                    image = cell.image
                    width *= 0.7
                    height *= 0.2
                    x_shift = 0.15 * scale
                    y_shift = 0.4 * scale
                    if isinstance(cell, VRoad):
                        width, height = height, width
                        x_shift, y_shift = y_shift, x_shift
                pygame.draw.rect(surface=screen,
                                 color=cell.color,
                                 rect=(x_pos + x_shift, y_pos + y_shift, width, height))
                if image is not None:
                    w = image.get_width() * scale / 250
                    h = image.get_height() * scale / 250
                    image = pygame.transform.scale(image, (w, h))
                    if isinstance(cell, HRoad):
                        if cell.orientation == -1:
                            image = pygame.transform.rotate(image, 180)
                        screen.blit(image, (x_pos - x_shift, y_pos + 0.375 * y_shift))
                    else:
                        if cell.orientation == -1:
                            image = pygame.transform.rotate(image, 90)
                        else:
                            image = pygame.transform.rotate(image, 270)
                        screen.blit(image, (x_pos + 0.375 * x_shift, y_pos - y_shift))

    # Insert a car in the grid, by changing its state to 1 and randomly choosing an image for it.
    def insert_car(self, y, x, image=None):
        current = self.cells[y][x]
        # Make sure that the selected cell is an empty road, not an OBSTACLE!
        if isinstance(current, (HRoad, VRoad)) and current.state == 0:
            if image is None:
                images = [
                    "assets/ambulance.png",
                    "assets/blue.png",
                    "assets/cop.png",
                    "assets/taxi.png",
                    "assets/yellow.png"
                ]
                image = choice(images, p=[1/17, 5/17, 1/17, 5/17, 5/17])
                image = pygame.image.load(image)
            current.state = 1
            current.image = image

    # When the cell moves, we free its previous cell, by removing its image and making its state 0.
    def remove_car(self, y, x):
        cell = self.cells[y][x]
        if isinstance(cell, (HRoad, VRoad)):
            cell.state = 0
            cell.image = None

    # Sets the below elements in the grid equal to a copy of element.
    #         columns[0] .  .  . columns[1]
    # rows[0]
    #   .
    #   .
    #   .
    # rows[1]
    def fill(self, element, rows, columns):
        for y in range(rows[0], rows[1] + 1):
            for x in range(columns[0], columns[1] + 1):
                self.cells[y][x] = element.__copy__()

    # Fills the grid with black obstacles
    def clear_grid(self):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x] = Cell(color=(0, 0, 0), state=1)

    # Fills the grid with assets, with probability p.
    def fill_randomly_with_cars(self, p):
        for y in range(self.rows):
            for x in range(self.columns):
                alive = choice([True, False], p=[p, 1 - p])
                if alive:
                    self.insert_car(y, x)
                else:
                    self.remove_car(y, x)

    # Removes assets from all roads.
    def clear_cars(self):
        for y in range(self.rows):
            for x in range(self.columns):
                self.remove_car(y, x)

    # The method for actually moving the assets to their next position.
    def next_state(self):
        # Calculating the horizontal moves of a car, up to 2 cells ahead.
        def h_moves(r, c, orientation):
            moves = orientation
            # Take a step in the direction orientation.
            nc = c + orientation
            # Check if we can take a step.
            if 0 <= nc < self.columns:
                cell = self.cells[r][nc]
                # If we stepped on an occupied cell, return 0 moves.
                if cell.state == 1:
                    return 0
                # If we step from an HRoad to a VRoad,
                # don't take any more steps to avoid unrealistic jumps.
                if not isinstance(cell, VRoad):
                    # Take one more step.
                    nc += orientation
                    if 0 <= nc < self.columns:
                        cell = self.cells[r][nc]
                        # If the next_cell is an empty HRoad, move another step.
                        if isinstance(cell, HRoad) and cell.state == 0:
                            moves += orientation
            return moves

        # Same as h_moves, but vertical.
        def v_moves(r, c, orientation):
            moves = orientation
            # Take a step in the direction orientation.
            nr = r + orientation
            # Check if we can take a step.
            if 0 <= nr < self.rows:
                cell = self.cells[nr][c]
                # If we stepped on an occupied cell, return 0 moves.
                if cell.state == 1:
                    return 0
                # If we step from an HRoad to a VRoad,
                # don't take any more steps to avoid unrealistic jumps.
                if not isinstance(cell, HRoad):
                    # Take one more step.
                    nr += orientation
                    if 0 <= nr < self.rows:
                        cell = self.cells[nr][c]
                        # If the next_cell is an empty HRoad, move another step.
                        if isinstance(cell, VRoad) and cell.state == 0:
                            moves += orientation
            return moves

        cells = self.cells
        # We initialize a boolean array to keep track of whether a car was moved before.
        # By default, all are set to false.
        was_moved = ndarray(shape=cells.shape, dtype=bool)
        was_moved.fill(False)
        rows = self.rows
        columns = self.columns
        for y in range(rows):
            for x in range(columns):
                # We traverse the grid, cell by cell.
                current = cells[y][x]
                # The car has to be on either roads.
                if isinstance(current, (HRoad, VRoad)):
                    o = current.orientation
                    # Check if it's a car and wasn't moved before.
                    if current.state == 1 and not was_moved[y][x]:
                        nx, ny = x, y
                        if isinstance(current, HRoad):
                            # The speed is determined by the number of steps of a car.
                            nx += h_moves(y, x, o)
                        else:
                            ny += o  # v_moves(y, x, o)
                        # If the next step exists on grid and is empty, free the current cell and move the car.
                        # Set its move check to True.
                        if 0 <= nx < columns and 0 <= ny < rows:
                            next_cell = cells[ny][nx]
                            if next_cell.state == 0:
                                self.insert_car(ny, nx, current.image)
                                self.remove_car(y, x)
                                was_moved[ny][nx] = True
                        # If it doesn't exist, free the car.
                        else:
                            self.remove_car(y, x)
                    # If the cell is empty, make a random choice to exist one or not,
                    # with the condition being at the start of the street.
                    elif current.state == 0:
                        alive = choice([True, False], p=[0.25, 0.75])
                        if alive:
                            if isinstance(current, VRoad):
                                if y == 0 and o == 1 or y == rows - 1 and o == -1:
                                    self.insert_car(y, x)
                            else:
                                if x == 0 and o == 1 or x == columns - 1 and o == -1:
                                    self.insert_car(y, x)