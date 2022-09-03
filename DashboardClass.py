from random import randint, shuffle

from ShipClass import *
from ExceptionClasses import *


DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
SURROUNDINGS = [*DIRECTIONS, (1, 1), (1, -1), (-1, 1), (-1, -1)]


class DashBoard:
    def __init__(self, columns, lines):
        self.columns, self.lines = columns, lines
        self.matrix = DashBoard.get_empty_matrix(columns, lines)
        # ~1/20 chance that not all ships can be placed on the dashboard
        while True:
            try:
                self.ships = self.get_ships()
                break
            except NoSuitableCellsError:
                self.matrix = DashBoard.get_empty_matrix(columns, lines)

    @staticmethod
    def get_empty_matrix(columns, lines):
        return [[Cell(y, x, False) for x in range(columns)] for y in range(lines)]

    def get_ships(self):
        ships = [self.get_ship_with_size(3)]
        ships.extend([self.get_ship_with_size(2) for _ in range(2)])
        ships.extend([self.get_ship_with_size(1) for _ in range(4)])
        return ships

    def get_ship_with_size(self, ship_size):
        if ship_size == 1:
            return self.get_one_cell_ship()
        else:
            y, x, direction = self.get_empty_random_place(ship_size)
            ship_cells = self.get_ship_cells(y, x, direction, ship_size)
            return SeaShip(ship_cells)

    def get_one_cell_ship(self):
        # Trying to find random coordinates for one cell ship
        for _ in range(10000):
            y, x = self.get_empty_random_coordinates()
            if self.surroundings_is_empty(y, x):
                self.matrix[y][x].active = True
                return SeaShip([self.matrix[y][x]])
        # Try to find suitable cell
        # If no such cell - raise exception
        cell = self.find_cell_for_one_cell_ship()
        if cell is None:
            raise NoSuitableCellsError("No place to add one cell ship")
        else:
            return SeaShip([cell])

    def get_empty_random_coordinates(self):
        while True:
            y, x = randint(0, self.columns - 1), randint(0, self.lines - 1)
            if not self.matrix[y][x].active:
                return y, x

    def surroundings_is_empty(self, y, x):
        active_surrounding_cells = self.get_surrounding_cells_active_params(y, x)
        if any(active_surrounding_cells):
            return False
        else:
            return True

    def find_cell_for_one_cell_ship(self):
        for row in self.matrix:
            for cell in row:
                if self.cell_is_not_active(cell.y, cell.x) and self.surroundings_is_empty(cell.y, cell.x):
                    return cell
        return None

    def get_surrounding_cells_active_params(self, y, x):
        surrounding_cells = []
        for dy, dx in SURROUNDINGS:
            if self.coord_on_the_dashboard(y + dy, x + dx):
                surrounding_cells.append(self.matrix[y + dy][x + dx].active)
        return surrounding_cells

    def get_surrounding_cells(self, y, x):
        surrounding_cells = []
        for dy, dx in SURROUNDINGS:
            if self.coord_on_the_dashboard(y + dy, x + dx):
                surrounding_cells.append(self.matrix[y + dy][x + dx])
        return surrounding_cells

    def coord_on_the_dashboard(self, y, x):
        if 0 <= y < self.lines and 0 <= x < self.columns:
            return True
        return False

    def get_empty_random_place(self, ship_size):
        while True:
            y, x = self.get_empty_random_coordinates()
            ship_direction = self.get_empty_direction(y, x, ship_size)
            if ship_direction:
                return y, x, ship_direction

    def get_empty_direction(self, y, x, ship_size):
        copy_of_directions = DIRECTIONS.copy()
        shuffle(copy_of_directions)
        for direction in copy_of_directions:
            direction_coord = DashBoard.get_directions_coord(y, x, ship_size, direction)
            if self.direction_coord_is_suitable(direction_coord):
                return direction
        return None

    def is_destroyed(self):
        return not any([ship.is_alive for ship in self.ships])

    @staticmethod
    def get_directions_coord(y, x, ship_size, direction):
        directions_coord = []
        for _ in range(ship_size):
            directions_coord.append((y, x))
            y, x = y + direction[0], x + direction[1]
        return directions_coord

    def direction_coord_is_suitable(self, coord_list):
        for y, x in coord_list:
            if not self.coord_on_the_dashboard(y, x) or \
                    self.cell_is_active(y, x) or \
                    not self.surroundings_is_empty(y, x):
                return False
        return True

    def cell_is_active(self, y, x):
        if self.matrix[y][x].active:
            return True
        return False

    def cell_is_not_active(self, y, x):
        if not self.matrix[y][x].active:
            return True
        return False

    def get_ship_cells(self, y, x, ship_direction, ship_size):
        cells = []
        for _ in range(ship_size):
            self.matrix[y][x].active = True
            cells.append(self.matrix[y][x])
            y, x = y + ship_direction[0], x + ship_direction[1]
        return cells

    def knock_out_cells_around_ship(self, ship):
        for cell in ship.ship_cells:
            surrounding_cells = self.get_surrounding_cells(cell.y, cell.x)
            for nearest_cell in surrounding_cells:
                if not nearest_cell.knocked_out:
                    nearest_cell.knocked_out = True
