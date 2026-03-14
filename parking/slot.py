class ParkingSlot:
    def __init__(self,slot_id,slot_type):
        self.slot_id=slot_id
        self.slot_type=slot_type
        self.is_free=True
        self.vehicle=None

    def can_park(self,vehicle):
        return self.slot_type==vehicle.get_type()
    
    def park(self,vehicle):
        self.vehicle=vehicle
        self.is_free=False

    def unpark(self):
        self.vehicle=None
        self.is_free=True
        