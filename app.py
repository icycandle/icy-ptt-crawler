from curses import wrapper
import time
import threading

def update_time(screen):
    while 1:
        screen.addstr(12, 12, time.strftime("%a, %d %b %Y %H:%M:%S"))
        screen.refresh()
        time.sleep(1)

def main(screen):
    screen.addstr("This is a Sample Curses Script\n\n")
    screen.refresh()
    clock = threading.Thread(target=update_time, args=(screen,))
    clock.daemon = True
    clock.start()
    while 1:
        event = screen.getch()
        if event == ord("q"):
            break

wrapper(main)
