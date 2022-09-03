import curses


class BackGroundColor:
    def __init__(self):
        self.white_background = curses.color_pair(1)
        self.green_background = curses.color_pair(2)
        self.red_background = curses.color_pair(3)
