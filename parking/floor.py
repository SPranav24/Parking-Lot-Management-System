from .slot import ParkingSlot

class ParkingFloor:
    def __init__(self, floor_no, slot_config):
        """
        floor_no     : floor number (1, 2, ...)
        slot_config  : dict like { "BIKE": 2, "CAR": 3 }
        """
        self.floor_no = floor_no
        self.slots = []

        # Create slots during system initialization
        for slot_type, count in slot_config.items():
            for i in range(count):
                slot_id = f"{slot_type[0]}{i}"
                self.slots.append(ParkingSlot(slot_id, slot_type))

    def get_free_slot(self, vehicle):
        """
        Return the FIRST free slot compatible with the vehicle
        """
        for slot in self.slots:
            if slot.is_free and slot.can_park(vehicle):
                return slot
        return None