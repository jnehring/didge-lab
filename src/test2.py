import curses

try:
    # The `screen` is a window that acts as the master window
    # that takes up the whole screen. Other windows created
    # later will get painted on to the `screen` window.
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    num_rows, num_cols = screen.getmaxyx()

    # lines, columns, start line, start column
    win1 = curses.newwin(20, 20, 0, 0)
    win2 = curses.newwin(20, 20, 0, 20)

    # Long strings will wrap to the next line automatically
    # to stay within the window
    win1.addstr("Hello",curses.color_pair(1))
    win2.addstr("World")

    # Print the window to the screen
    win1.refresh()
    win2.refresh()
    curses.napms(2000)

    # Clear the screen, clearing my_window contents that were printed to screen
    # my_window will retain its contents until my_window.clear() is called.
    screen.clear()
    screen.refresh()

finally:
    curses.endwin()
