import pyautogui
import time
import win32gui

# local imports
import consts


class Clicker:
    def __init__(self):
        # initialize stuff
        self._active = False
        self._click_counter = 0
        self._seconds_counter = 0
        self._time_last = time.perf_counter()

        self._click_count = 0

        self._cps = consts.DEFAULT_CPS
        self._click_interval_seconds = 1 / self._cps
        self._cur_window = consts.ANYWHERE_HWND

    def update_cps(self, click_speed=consts.DEFAULT_CPS):
        self._cps = click_speed

    def update(self):
        """Update function to be called once every loop of program"""
        self.do_clicking()

    def update_window(self, window=consts.ANYWHERE_HWND):
        """Change the window to be clicked inside of"""
        print(f"Clicker got window: {window} to be set to")
        self._cur_window = window
        print("self._cur_window is now " +
              f"{win32gui.GetWindowText(self._cur_window)}")

    def adjust_speed(self):
        if self._click_counter and self._seconds_counter:
            if (self._click_counter / self._seconds_counter) < self._cps:
                self._click_interval_seconds /= 2
            else:
                self._click_interval_seconds = 1 / self._cps

        if self._click_counter > 63:
            self._click_counter = 0
            self._seconds_counter = 0

    def do_clicking(self):
        if self.should_click():
            pyautogui.click()

            self._click_counter += 1
            cur_time = time.perf_counter()
            if self._time_last:
                self._seconds_counter += cur_time - self._time_last
            self._time_last = cur_time
            self.adjust_speed()
            time.sleep(self._click_interval_seconds)
        else:
            # on last call of this function, reset time_last value
            self._time_last = 0

    def toggle_clicking(self):
        print("clicking toggled to " + str(not self._active))
        self._active = not self._active

        self.change_in_active_state()

    def should_click(self):
        if self._active:
            # ideally we just use one expression and short circuit, but this is
            # clearer, so we can leave it in for now
            click_anywhere = self._cur_window == consts.ANYWHERE_HWND
            foreground_is_selected = (win32gui.GetForegroundWindow() ==
                                      self._cur_window)
            cursor_in_selected = (
                point_in_rect(
                    win32gui.GetCursorPos(),
                    win32gui.GetWindowRect(self._cur_window)
                )
                if self._cur_window != -1
                else False
            )
            cursor_in_target = click_anywhere or (
                foreground_is_selected and cursor_in_selected
            )

            # cursor_in_target = self._cur_window == consts.ANYWHERE_HWND or \
            #     ((win32gui.GetForegroundWindow() == self._cur_window) and
            #      (point_in_rect(win32gui.GetCursorPos(),
            #                     win32gui.GetClientRect(self._cur_window))))
            # TODO: print statement
            consts.dprint(f"foreground: {foreground_is_selected} |" +
                          f"cursor_in: {cursor_in_selected}",
                          1)

            if cursor_in_target:
                return True
        return False

    # these two methods send events outward
    def add_callback_to_active_change(self, callback):
        self._active_change_callback = callback

    def change_in_active_state(self):
        if self._active_change_callback:
            self._active_change_callback(self._active)


# helper methods
def point_in_rect(point, rect):
    """
    Checks if a point is inside a rectangle
    @args
    - point: a point as tuple (x, y)
    - rect: a rectange as tuple (left, top, right, bottom)
    """
    consts.dprint(f"p: {point}, r: {rect}")
    return (
        point[0] >= rect[0]
        and point[0] <= rect[2]
        and point[1] >= rect[1]
        and point[1] <= rect[3]
    )