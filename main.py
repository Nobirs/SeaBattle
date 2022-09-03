import time
import curses
from curses import wrapper


from DashboardClass import DashBoard
from DashboardWindowClass import DashBoardWindow


CELL_SYMBOL = "■"
LOAD_SCREEN = """░░░░░░░░░░░▄▄▄████████████▄▄▄░░░░░░░░░░░
░░░░░░▄▄██▀▀▀░░░░▄░░░░▄░░░░▀▀▀██▄▄░░░░░░
░░░░▄█▀▀░▄▄██░░░░██▄▄██░░░░██▄▄░▀▀█▄░░░░
░░▄█▀░▄█████░░░░░██████░░░░░█████▄░▀█▄░░
░██░▄███████▄░░░▄██████▄░░░▄███████▄░██░
██░██████████████████████████████████░██
██░██████████████████████████████████░██
██░██████████████████████████████████░██
░██░▀████▀░░███▀████████▀███░░▀████▀░██░
░░▀█▄░▀██▄░░░▀░░░░████░░░░▀░░░▄██▀░▄█▀░░
░░░░▀█▄▄▀▀░░░░░░░░░██░░░░░░░░░▀▀▄▄█▀░░░░
░░░░░░▀▀██▄▄▄░░░░░░░░░░░░░░▄▄▄██▀▀░░░░░░
░░░░░░░░░░▀▀▀▀████████████▀▀▀▀░░░░░░░░░░""".split("\n")


def print_desk_borders(desk_y, desk_x, desk_width, desk_height, console):
    y, x = desk_y - 1, desk_x - 1
    border_width, border_height = desk_width*4 + 3, desk_height + 2

    for y_coord in range(y, y + border_height):
        console.addstr(y_coord, x, "#")
        console.addstr(y_coord, x + border_width, "#")
        console.addstr(y_coord, x + desk_width*2 + 1, "#")
        console.addstr(y_coord, x + desk_width * 2 + 2, "#")

    for x_coord in range(x, x + border_width):
        console.addstr(y, x_coord, "#")
        console.addstr(y + border_height - 1, x_coord, "#")

    console.addstr(y, x + desk_width, "AI")
    console.addstr(y + border_height - 1, x + desk_width - 1, "DESK")
    console.addstr(y, x + desk_width*3, "USER")
    console.addstr(y + border_height - 1, x + desk_width*3, "DESK")

    console.refresh()


def print_game_result(console, message):
    y, x = curses.LINES//4, curses.COLS//2 - len(message)//2
    message_color = curses.color_pair(4)

    console.addstr(y, x, message, message_color)
    console.refresh()


@wrapper
def main(console):
    # Program not working without two lines below.
    console.clear()
    console.refresh()
    # Init curses background colors.
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_GREEN)

    # Funny screensaver before loading dashboards
    begin_y, x = curses.LINES//2 - len(LOAD_SCREEN)//2 - 1, curses.COLS//2 - len(LOAD_SCREEN[0])//2
    end_y = begin_y + len(LOAD_SCREEN)
    for first_line, last_line in zip(LOAD_SCREEN, LOAD_SCREEN[::-1]):
        console.addstr(begin_y, x, first_line)
        console.addstr(end_y, x, last_line)
        begin_y += 1
        console.refresh()
        time.sleep(.2)
        if begin_y == end_y:
            break
        end_y -= 1

    dashboard_height, dashboard_width = 6, 6
    user_dashboard = DashBoard(dashboard_height, dashboard_width)
    ai_dashboard = DashBoard(dashboard_height, dashboard_width)

    # These coordinates should place two window at the center of the console
    newwin_y, newwin_x = curses.LINES//2 - dashboard_height//2, curses.COLS//2 - dashboard_width*2 - 1

    user_desk = curses.newwin(dashboard_height, dashboard_width * 2, newwin_y, newwin_x)
    ai_desk = curses.newwin(dashboard_height, dashboard_width * 2, newwin_y, newwin_x + dashboard_width*2 + 2)

    ai_window = DashBoardWindow(ai_dashboard, user_desk, console, hidden=True)
    user_window = DashBoardWindow(user_dashboard, ai_desk, console)

    print_desk_borders(newwin_y, newwin_x, dashboard_width, dashboard_height, console)

    ai_window.print_dashboard()
    user_window.print_dashboard()

    player_turn, ai_turn = True, False
    user_y, user_x = 0, 0
    ai_window.move_cursor(user_y, user_x)

    # game loop
    while True:
        if player_turn:
            pressed_key = console.getch()
            user_y, user_x = user_desk.getyx()

            cell_was_empty = ai_window.key_handler(user_y, user_x, pressed_key)
            if cell_was_empty:
                player_turn, ai_turn = ai_turn, player_turn
                user_y, user_x = 0, 0
                ai_window.move_cursor(user_y, user_x)
        elif ai_turn:
            cell_was_empty = user_window.get_random_move()
            user_window.print_dashboard()
            time.sleep(0.5)
            if cell_was_empty:
                player_turn, ai_turn = ai_turn, player_turn
                user_y, user_x = 0, 0
                ai_window.move_cursor(user_y, user_x)

        # Check if winner is determined.
        if user_dashboard.is_destroyed():
            print_game_result(console, "!AI  Win!")
            break
        elif ai_dashboard.is_destroyed():
            print_game_result(console, "!USER Win!")
            break
    console.getch()
