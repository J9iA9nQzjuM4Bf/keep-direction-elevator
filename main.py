import threading

from sorted_list import get_nearest, SortedList


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


class BaseElevator(object):

    def __init__(self, hardware_elevator_class=None):
        hardware_elevator_class = hardware_elevator_class or HardwareElevator

        self.hw = hardware_elevator_class()
        self.hw.register_close_event_handler(self.on_doors_closed)
        self.hw.register_on_floor_handler(self.on_floor)

        self.requests = {
            Directions.NONE: SortedList(),
            Directions.UP: SortedList(),
            Directions.DOWN: SortedList(),
        }

        self._direction = Directions.NONE
        self._door_closed = False

        self._start_lock = threading.Lock()

    def _get_nearest_request(self, floor, *include):
        requested_floors = [self.requests[direction].get_nearest(floor)
                            for direction in include]

        return get_nearest(floor, *requested_floors)

    def _get_next_request(self, floor, *include):
        requested_floors = [self.requests[direction].get_next_key(floor, self._direction)
                            for direction in include]

        return get_nearest(floor, *requested_floors)

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
        next_floor = self._get_next_stop(floor)

        if next_floor > floor:
            self._direction = Directions.UP
        elif next_floor < floor:
            self._direction = Directions.DOWN
        else:
            self._direction = Directions.NONE

    def _clean_requests(self):
        floor = self.hw.get_current_floor()
        self.requests[Directions.NONE].discard(floor)

        if self._direction == Directions.NONE:
            self.requests[Directions.UP].discard(floor)
            self.requests[Directions.DOWN].discard(floor)
        else:
            self.requests[self._direction].discard(floor)

    def on_doors_closed(self):
        self._door_closed = True
        self._start()

    def on_floor(self):
        floor = self.hw.get_current_floor()

        if self._should_stop(floor):
            self._stop(floor)

    def floor_button_pressed(self, floor, direction):
        self.requests[direction].add(floor)

        if self._direction == Directions.NONE and self._door_closed:
            self._start()

    def cabin_button_pressed(self, floor):
        self.requests[Directions.NONE].add(floor)

        if self._direction == Directions.NONE and self._door_closed:
            self._start()


class DropOffPriorityElevator(BaseElevator):
    def _get_next_stop(self, current_floor):
        if self._direction == Directions.NONE:
            value = self._get_nearest_request(current_floor, Directions.NONE, Directions.UP, Directions.DOWN)

        else:
            value = self._get_next_request(current_floor, Directions.NONE)

        return value or current_floor

    def _should_stop(self, current_floor):
        if self._get_next_request(Directions.NONE):
            valid_directions = [Directions.NONE, self._direction]
        else:
            valid_directions = [Directions.NONE, Directions.UP, Directions.DOWN]

        return any([current_floor in self.requests[direction] for direction in valid_directions])

