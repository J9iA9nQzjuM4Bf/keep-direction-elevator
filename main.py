import threading

from sorted_dict import SortedDict


class Directions:
    UP = 1
    DOWN = -1
    NONE = 0


class HardwareElevator(object):
    # hardware api you can just use
    # no need to implement
    def register_close_event_handler(self, func):
        pass

    def register_on_floor_handler(self, func):
        pass

    def move_up(self):
        pass

    def move_down(self):
        pass

    def stop_and_open_doors(self):
        pass

    def get_current_floor(self):
        pass

    def get_current_direction(self):
        pass


class KeepDirectionElevator(object):

    def __init__(self, hardware_elevator_class=None):
        hardware_elevator_class = hardware_elevator_class or HardwareElevator

        self.hw = hardware_elevator_class()
        self.hw.register_close_event_handler(self.on_doors_closed)
        self.hw.register_on_floor_handler(self.on_floor)

        self._drop_offs = SortedDict()
        self._pick_ups = SortedDict()

        self._direction = Directions.NONE
        self._door_closed = False

        self._start_lock = threading.Lock()

    def _start(self):
        self._clean_requests()

        with self._start_lock:
            if self._direction == Directions.NONE:
                self._update_direction()

                if self._direction == Directions.UP:
                    self.hw.move_up()
                elif self._direction == Directions.DOWN:
                    self.hw.move_down()

    def _stop(self, floor):
        self._update_direction()

        self._door_closed = False
        self.hw.stop_and_open_doors()

    def _update_direction(self):
        floor = self.hw.get_current_floor()

        if self._direction == Directions.NONE:
            next_floor = self._get_next_stop(floor)
            if next_floor > floor:
                self._direction = Directions.UP
                return True
            else:
                self._direction = Directions.DOWN
                return True

        else:

            if not self._drop_offs.get_next(floor, self._direction):
                self._direction = Directions.NONE
                return True

    def _get_next_stop(self, current_floor):
        if self._drop_offs:
            if self._direction == Directions.NONE:
                return self._drop_offs.get_nearest(current_floor)
            else:
                return self._drop_offs.get_next(current_floor, self._direction)

        elif self._pick_ups:
            return self._pick_ups.get_nearest(current_floor)

        else:
            return current_floor

    def _clean_requests(self):
        floor = self.hw.get_current_floor()
        self._drop_offs.pop(floor, None)

        if self._direction == Directions.NONE:
            self._pick_ups.pop(floor, None)
        else:
            try:
                with self._pick_ups.lock:
                    self._pick_ups[floor].remove(self._direction)
                    if not self._pick_ups[floor]:
                        del self._pick_ups[floor]
            except KeyError:
                pass

    def on_doors_closed(self):
        self._door_closed = True
        self._start()

    def on_floor(self):
        floor = self.hw.get_current_floor()

        try:
            should_stop = floor in self._drop_offs or self._direction in self._pick_ups[floor]
        except KeyError:
            should_stop = False

        if should_stop:
            self._stop(floor)

    def floor_button_pressed(self, floor, direction):
        with self._pick_ups.lock:
            try:
                self._pick_ups[floor].add(direction)
            except KeyError:
                self._pick_ups[floor] = {direction}

        if self._direction == Directions.NONE and self._door_closed:
            self._start()

    def cabin_button_pressed(self, floor):
        self._drop_offs[floor] = True

        if self._direction == Directions.NONE and self._door_closed:
            self._start()
