import time
import math


class ParkingTicket:
    def __init__(self, vehicle, floor_no, slot, entry_time=None):
        """
        vehicle  : Vehicle object (Car / Bike)
        floor_no : floor number
        slot     : ParkingSlot object
        entry_time : optional timestamp; if None, current time is used.
        """
        self.vehicle = vehicle
        self.floor_no = floor_no
        self.slot = slot
        self.entry_time = entry_time if entry_time is not None else time.time()

    def _duration_seconds(self):
        return max(0, time.time() - self.entry_time)

    def get_duration_minutes(self):
        """
        Return parking duration in whole minutes (at least 1).
        """
        minutes = int(self._duration_seconds() // 60)
        return max(1, minutes)

    def get_human_readable_duration(self):
        """
        Return duration as a friendly string e.g. '1h 20m'.
        """
        total_minutes = self.get_duration_minutes()
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours and minutes:
            return f"{hours}h {minutes}m"
        if hours:
            return f"{hours}h"
        return f"{minutes}m"

    def calculate_fee(self):
        """
        Time-based pricing:
        - First 15 minutes are free
        - After that, charge per minute based on the vehicle's hourly rate
        - Fee is rounded up to the next whole rupee
        """
        total_minutes = self.get_duration_minutes()
        free_minutes = 15

        if total_minutes <= free_minutes:
            return 0

        billable_minutes = total_minutes - free_minutes
        rate_per_hour = self.vehicle.get_rate_per_hour()
        rate_per_minute = rate_per_hour / 60.0
        fee = math.ceil(billable_minutes * rate_per_minute)
        return int(fee)