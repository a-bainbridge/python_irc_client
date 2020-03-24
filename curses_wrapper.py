import curses

"""
class that provides intuitive, terminal-like functions for a different layout made for chatting ig
"""
class ClientTerminal:
    def __init__(self):
        self.init()

    def init(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.stdscr.refresh()

        self.input_height = 1
        self.title_box = curses.newwin(1, curses.COLS, 0, 0)
        self.dialog_box = curses.newwin(curses.LINES - self.input_height - 1, curses.COLS, 1, 0)
        self.dialog_box.scrollok(True)
        self.inner_input = curses.newwin(self.input_height, curses.COLS, curses.LINES - self.input_height, 0)
        self.inner_input.keypad(True)
        self.title_box.addstr('TITLE', curses.A_REVERSE)
        self.title_box.refresh()

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def input(self, premessage: str = '') -> str:
        self.print(premessage)
        the_input = ''
        while True:
            k = self.stdscr.getch()
            if k in [curses.KEY_ENTER, curses.KEY_BREAK, ord('\n')]:
                break
            ks = chr(k)
            the_input += ks
            self.inner_input.addstr(ks)
            self.inner_input.refresh()
        self.println(the_input)
        self.inner_input.clear()
        self.inner_input.refresh()
        return the_input

    def pause(self): # wait for any key to be pressed
        self.stdscr.getch()

    def print(self, message: str='') -> str:
        try:
            self.dialog_box.addstr(message, curses.A_BOLD)
            self.dialog_box.refresh()
        except:
            pass
        return message

    def println(self, message: str='') -> None:
        self.print('%s\n' % message)

    def set_title(self, title: str):
        self.title_box.clear()
        self.title_box.addstr(title, curses.A_REVERSE)
        self.title_box.refresh()

    def clear_prints(self):
        self.dialog_box.clear()
        self.dialog_box.refresh()

    def clear_input(self):
        self.inner_input.clear()
        self.inner_input.refresh()

    def refresh_all(self):
        self.title_box.refresh()
        self.dialog_box.refresh()
        self.inner_input.refresh()
        self.stdscr.refresh()

if __name__ == '__main__':
    # for testing, only
    ct = ClientTerminal()
    ct.println('hello, world!')
    name = ct.input("what's your name? enter it here: ")
    ct.println("your name is %s"%name)
    ct.println('thank you and goodbye')
    ct.pause()
    ct.end()