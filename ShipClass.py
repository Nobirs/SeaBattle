class Cell:
    def __init__(self, y, x, active_status=False):
        self.y, self.x = y, x
        self.__is_active = active_status
        self.knocked_out = False

    @property
    def active(self):
        return self.__is_active

    @active.setter
    def active(self, status):
        if isinstance(status, bool):
            self.__is_active = status

    def __str__(self):
        return f"{self.y}/{self.x}"


class SeaShip:
    def __init__(self, list_of_cells):
        self.ship_cells = list_of_cells
        self.is_alive = True
