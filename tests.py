import unittest
from unittest import mock

from main import Directions, DropOffPriorityElevator


class KeepDirectionElevatorTestCase(unittest.TestCase):

    def setUp(self):
        with mock.patch('main.HardwareElevator') as mock_hardware_elevator:
            self.hardware_elevator = mock_hardware_elevator.return_value
            self.elevator = DropOffPriorityElevator()

    def test_moves(self):
        self.hardware_elevator.get_current_floor.return_value = 0

        self.elevator._direction = Directions.NONE
        self.elevator._door_closed = False

        self.elevator.cabin_button_pressed(6)
        self.elevator.on_doors_closed()

        self.assertTrue(self.hardware_elevator.move_up.called)

    def test_stops_to_drop_off(self):
        self.elevator.cabin_button_pressed(6)
        self.elevator._direction = Directions.UP
        self.elevator._door_closed = True

        self.hardware_elevator.get_current_floor.return_value = 6
        self.elevator.on_floor()

        self.assertTrue(self.hardware_elevator.stop_and_open_doors.called)
        self.assertEqual(self.elevator._direction, Directions.NONE)

    def test_stops_to_pick_up(self):
        self.elevator.cabin_button_pressed(6)
        self.elevator.floor_button_pressed(3, Directions.UP)
        self.elevator._direction = Directions.UP
        self.elevator._door_closed = True

        self.hardware_elevator.get_current_floor.return_value = 3
        self.elevator.on_floor()

        self.assertTrue(self.hardware_elevator.stop_and_open_doors.called)
        self.assertEqual(self.elevator._direction, Directions.UP)

    def test_continues(self):
        self.hardware_elevator.get_current_floor.return_value = 6

        self.elevator.cabin_button_pressed(6)
        self.elevator.cabin_button_pressed(8)
        self.elevator._direction = Directions.UP
        self.elevator._door_closed = False

        self.elevator.on_floor()

        self.assertTrue(self.hardware_elevator.stop_and_open_doors.called)
        self.assertEqual(self.elevator._direction, Directions.UP)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
