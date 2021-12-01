import curses
import time

stdscr = curses.initscr()

stdscr.addstr("line 1\n")
stdscr.addstr("line 2\n")
stdscr.refresh()
time.sleep(1)

stdscr.erase()
stdscr.addstr("edited line 1\n")
stdscr.addstr("edited line 2\n")
stdscr.refresh()
time.sleep(1)

curses.endwin()
