from random import randint


from ExceptionClasses import *
from CursesBackgrounds import *


CURSOR_SYMBOL = "X"
KEY_SPACE = 32


class DashBoardWindow:
    def __init__(self, dashboard, window, console, hidden=False):
        self.window = window
        self.hidden = hidden
        self.console = console
        self.dashboard = dashboard
        self.cell_symbol = "■"
        self.backgrounds = BackGroundColor()

    def print_dashboard(self):
        for row in self.dashboard.matrix:
            for cell in row:
                if cell.active and not cell.knocked_out:
                    if self.hidden:
                        self.window.addstr(cell.y, cell.x * 2, " ")
                    else:
                        self.window.addstr(cell.y, cell.x * 2, self.cell_symbol)
                elif not cell.active and not cell.knocked_out:
                    self.window.addstr(cell.y, cell.x * 2, " ")
                elif cell.active and cell.knocked_out:
                    self.window.addstr(cell.y, cell.x * 2, self.cell_symbol, self.backgrounds.green_background)
                elif not cell.active and cell.knocked_out:
                    self.window.addstr(cell.y, cell.x * 2, " ", self.backgrounds.white_background)
        self.print_dead_ships()
        self.window.refresh()

    def print_dead_ships(self):
        for ship in self.dashboard.ships:
            if not ship.is_alive:
                for cell in ship.ship_cells:
                    self.window.addstr(cell.y, cell.x * 2, self.cell_symbol, self.backgrounds.red_background)

    def get_random_move(self):
        y, x = self.get_random_not_knocked_coordinates()
        cell_is_knocked_out = self.try_to_knock_out_cell(y, x*2)
        return cell_is_knocked_out

    def get_random_not_knocked_coordinates(self):
        y, x = randint(0, self.dashboard.lines-1), randint(0, self.dashboard.columns-1)
        while not self.cell_already_knocked(y, x):
            y, x = randint(0, self.dashboard.lines-1), randint(0, self.dashboard.columns-1)
        return y, x

    def cell_already_knocked(self, y, x):
        return not self.dashboard.matrix[y][x].knocked_out

    def move_cursor(self, y, x):
        if self.is_cell_coordinates(y, x):
            self.print_dashboard()
            self.window.addch(y, x, CURSOR_SYMBOL, curses.color_pair(2))
            self.window.move(y, x)
            self.window.refresh()
        else:
            raise CoordOutOfDeskError("[Error]: Coordinates out of window")

    def try_to_knock_out_cell(self, y, x):
        if not self.is_cell_coordinates(y, x):
            raise NoSuitableCellsError("No such cell in the desk")
        cell = self.dashboard.matrix[y][x // 2]
        if not cell.knocked_out:
            cell.knocked_out = True
            self.check_if_any_ship_killed()

            for ship in self.dashboard.ships:
                if cell in ship.ship_cells:
                    if not ship.is_alive:
                        self.dashboard.knock_out_cells_around_ship(ship)
                        break
            return not cell.active
        else:
            raise CellAlreadyKnockedOutError("Cell is already knocked out...")

    def is_cell_coordinates(self, y, x):
        return self.dashboard.coord_on_the_dashboard(y, x//2)

    def check_if_any_ship_killed(self):
        for ship in self.dashboard.ships:
            ship.is_alive = not all([cell.knocked_out for cell in ship.ship_cells])

    def key_handler(self, user_y, user_x, pressed_key):
        if pressed_key == curses.KEY_LEFT:
            try:
                self.move_cursor(user_y, user_x - 2)
            except CoordOutOfDeskError:
                self.console.addstr(1, 0, "Error in left Key")
        elif pressed_key == curses.KEY_RIGHT:
            try:
                self.move_cursor(user_y, user_x + 2)
            except CoordOutOfDeskError:
                self.console.addstr(1, 0, "Error in KEY_RIGHT")
        elif pressed_key == curses.KEY_UP:
            try:
                self.move_cursor(user_y - 1, user_x)
            except CoordOutOfDeskError:
                self.console.addstr(1, 0, "Error in KEY_UP")
        elif pressed_key == curses.KEY_DOWN:
            try:
                self.move_cursor(user_y + 1, user_x)
            except CoordOutOfDeskError:
                self.console.addstr(1, 0, "Error in KEY_DOWN")
        elif pressed_key == KEY_SPACE:
            try:
                cell_was_empty = self.try_to_knock_out_cell(user_y, user_x)
                self.console.addstr(2, 0, "ENTER PRESSED")
                self.print_dashboard()
                self.move_cursor(user_y, user_x)
                return cell_was_empty
            except CellAlreadyKnockedOutError:
                self.console.addstr(1, 0, "Error in knocked cell")
