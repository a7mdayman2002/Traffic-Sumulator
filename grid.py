from pygame import draw
from numpy import ndarray
from numpy.random import choice


# creating a cell with a color and state
# when state = 1, this means that cell is filled, o.w. empty
class Cell:
    def __init__(self, color, state):
        self.color = color
        self.state = state

    # we draw the cell here, the surface is the ui screen, x and y are the starting point of the cell
    # we define the dimensions to be colored starting from that point, multiplied by its scale
    # rect in draw.rect takes parameters (left, top, width, height)
    def draw(self, surface, x, y, scale):
        draw.rect(surface, color=self.color, rect=(x * scale,
                                                   y * scale,
                                                   scale,
                                                   scale))


# HRoad and VRoad are both subclasses of Cell, (super(). is called in their __init__ )
# They have extra field of orientation which is the road direction,
# In VRoad -1 for up, 1 for down
# In HRoad -1 for left, 1 for right
class HRoad(Cell):
    def __init__(self, color, state, orientation):
        super().__init__(color, state)
        self.state = state
        self.orientation = orientation  # orientation == 1 means right, -1 means left

    # we don't draw the whole cell in roads, in order to keep the design intact
    def draw(self, surface, x, y, scale):
        width = 0.75 * scale
        x_shift = 0.125 * scale
        height = 0.25 * scale
        y_shift = 0.375 * scale
        draw.rect(surface, color=self.color, rect=(x * scale + x_shift,
                                                   y * scale + y_shift,
                                                   width,
                                                   height))

    # we copy here cells, as this function returns the constructor, thus new cells generated
    def __copy__(self):
        return HRoad(self.color, self.state, self.orientation)


# same with HRoad
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


# here we create the grid, it consists of : rows, columns and array of cells filled with cell kind
# (normal **OBSTACLE**, VRoad, HRoad)
class Grid:
    def __init__(self, rows, columns, element):
        self.rows = rows
        self.columns = columns
        self.cells = ndarray(shape=(rows, columns), dtype=Cell)
        self.cells.fill(element)
        self.n = 0  # pointer to control color randomizer

    # this method calls all cells in the array and allow them to be drawn, with the color initialized in them
    # the fun part here is if the cell type is normal (OBSTACLE) it will call the draw method in super method,
    # but if HRoad or VRoad it will call the draw method in them adjusting their sizes and keeping design intact :D
    def draw(self, surface, scale):
        for y in range(self.rows):
            for x in range(self.columns):
                self.cells[y][x].draw(surface, x, y, scale)

    # this is for initializing same cell repeatedly and thus keeping its color unchanged case of randomizing
    def fill(self, element, rows, columns):
        for y in range(rows[0], rows[1] + 1):
            for x in range(columns[0], columns[1] + 1):
                self.cells[y][x] = element.__copy__()

    # this fills the grid randomly at start, to randomly choose if a certain cell should be filled with a car or not
    def fill_randomly(self):
        for y in range(self.rows):
            for x in range(self.columns):
                cell = self.cells[y][x]
                alive = choice([True, False], p=[0.5, 0.5])
                # a statement to make sure that the selected cell is either HRoad or VRoad -- not an OBSTACLE !
                if isinstance(cell, (HRoad, VRoad)) and alive:
                    self.insert(y, x)

    # when cell moves, we free its previous cell
    def free(self, y, x):
        cell = self.cells[y][x]
        if isinstance(cell, (HRoad, VRoad)):
            cell.state = 0
            cell.color = (255, 255, 255)

    # to insert a new cell in the grid, by changing its state to 1 and randomly choosing a color for it
    def insert(self, y, x, color=None):
        cell = self.cells[y][x]
        if cell.state == 0:
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
                # r = randint(50, 150)
                # g = randint(50, 150)
                # b = randint(50, 150)
                # color = (r, g, b)
            cell.color = color

    # calculating the neighbours horizontally 3 cells ahead
    def h_neighbours(self, grid, y, x, orientation):
        neighbour = ndarray(shape=(1, 4), dtype=int)
        neighbour.fill(0)
        move = 0
        for n in range(1, 3):
            # multiplied by orientation to change the direction
            # (if it's -1, then stepping back or going other direction)
            next_x = x + orientation * n
            # if next car is found within range of visible road, and its state =1 , add it to neighbors
            if 0 <= next_x < self.columns:
                cell = grid[y][next_x]
                if cell.state == 1:
                    neighbour[0][n] = 1

        if neighbour[0][1] == 0:
            move += 1
            if neighbour[0][2] == 0:
                move += 1
                if neighbour[0][3] == 0:
                    move += 1
        return move

# same as H_neighbours
    def v_neighbours(self, grid, y, x, orientation):
        neighbour = ndarray(shape=(1, 4), dtype=int)
        neighbour.fill(0)
        move = 0
        for n in range(2, 1, -1):
            next_y = y + orientation * n
            if 0 <= next_y < self.rows:
                cell = grid[next_y][x]
                if cell.state == 1:
                    neighbour[0][n] = 1

        if neighbour[0][1] == 0:
            move += 1
        if neighbour[0][2] == 0:
            move += 1

        return move

# method for actually moving the car to the next state
    def next_state(self):
        cells = self.cells.copy()
        # we initialized a boolean array to keep track if a car was moved before, by default set to false
        was_moved = ndarray(shape=cells.shape, dtype=bool)
        was_moved.fill(False)
        r = self.rows
        c = self.columns
        for y in range(r):
            for x in range(c):
                # we traverse the grid, cell by cell
                current = cells[y][x]
                # the car has to be on either roads
                if isinstance(current, (HRoad, VRoad)):
                    o = current.orientation
                    # if it's a car and wasn't moved before
                    if current.state == 1 and not was_moved[y][x]:
                        next_x, next_y = x, y
                    # these if, else make the car move one step in its direction
                        if isinstance(current, HRoad):
                            # speed part
                            next_x += (o*self.h_neighbours(cells, y, x, o))
                        else:
                            next_y += (o)
                        # if the next step exists on grid and is empty, free the current cell and move the car
                        # set its boolean to True
                        if 0 <= next_x < c and 0 <= next_y < r:
                            next_cell = cells[next_y][next_x]
                            if next_cell.state == 0:
                                self.insert(next_y, next_x, current.color)
                                self.free(y, x)
                                was_moved[next_y][next_x] = True
                        # if doesn't exist, free the car
                        else:
                            self.free(y, x)
                    # if the cell is empty make a choice to exist one or not
                    # with conditions at the start of the street
                    elif current.state == 0:
                        alive = choice([True, False], p=[0.5, 0.5])
                        if alive:
                            if isinstance(current, VRoad):
                                if y == 0 and o == 1 or y == r - 1 and o == -1:
                                    self.insert(y, x)
                            else:
                                if x == 0 and o == 1 or x == c - 1 and o == -1:
                                    self.insert(y, x)
