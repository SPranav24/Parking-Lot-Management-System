from .ticket import ParkingTicket


class ParkingLot:
    """
    Central controller of the parking system.
    """

    def __init__(self, floors):
        self.floors = floors
        self.active_tickets = {}  # vehicle_number -> ParkingTicket
        self.total_revenue = 0
        self.total_vehicles_served = 0

    def find_slot(self, floor_no, slot_id):
        """
        Find a specific slot by floor number and slot_id.
        """
        for floor in self.floors:
            if floor.floor_no == floor_no:
                for slot in floor.slots:
                    if slot.slot_id == slot_id:
                        return slot
        return None

    def park_vehicle(self, vehicle):
        """
        Allocate first available compatible slot and create ticket
        """
        for floor in self.floors:
            slot = floor.get_free_slot(vehicle)
            if slot:
                slot.park(vehicle)
                ticket = ParkingTicket(vehicle, floor.floor_no, slot)
                self.active_tickets[vehicle.number] = ticket
                return ticket
        return None  # Parking full

    def exit_vehicle(self, vehicle_number):
        """
        Exit vehicle, calculate fee, free slot and update analytics.
        """
        ticket = self.active_tickets.get(vehicle_number)
        if not ticket:
            return None, None

        fee = ticket.calculate_fee()
        ticket.slot.unpark()
        del self.active_tickets[vehicle_number]

        self.total_revenue += fee
        self.total_vehicles_served += 1

        return ticket, fee

    def get_occupancy_summary(self):
        """
        Return high-level occupancy metrics for showcasing in a dashboard.
        """
        floors_summary = []
        total_slots = 0
        total_occupied = 0
        total_car_slots = 0
        total_bike_slots = 0
        total_car_occupied = 0
        total_bike_occupied = 0

        for floor in self.floors:
            floor_slots = len(floor.slots)
            occupied = sum(1 for slot in floor.slots if not slot.is_free)
            free = floor_slots - occupied
            total_slots += floor_slots
            total_occupied += occupied

            car_slots = sum(1 for slot in floor.slots if slot.slot_type == "CAR")
            bike_slots = sum(1 for slot in floor.slots if slot.slot_type == "BIKE")
            car_occupied = sum(
                1
                for slot in floor.slots
                if slot.slot_type == "CAR" and not slot.is_free
            )
            bike_occupied = sum(
                1
                for slot in floor.slots
                if slot.slot_type == "BIKE" and not slot.is_free
            )

            total_car_slots += car_slots
            total_bike_slots += bike_slots
            total_car_occupied += car_occupied
            total_bike_occupied += bike_occupied

            floors_summary.append(
                {
                    "floor_no": floor.floor_no,
                    "total_slots": floor_slots,
                    "occupied": occupied,
                    "free": free,
                    "occupancy_percent": int(
                        (occupied / floor_slots) * 100
                    )
                    if floor_slots
                    else 0,
                    "car_slots": car_slots,
                    "bike_slots": bike_slots,
                    "car_occupied": car_occupied,
                    "bike_occupied": bike_occupied,
                }
            )

        total_free = total_slots - total_occupied
        total_car_free = total_car_slots - total_car_occupied
        total_bike_free = total_bike_slots - total_bike_occupied

        return {
            "floors": floors_summary,
            "total_slots": total_slots,
            "total_occupied": total_occupied,
            "total_free": total_free,
            "car": {
                "slots": total_car_slots,
                "occupied": total_car_occupied,
                "free": total_car_free,
            },
            "bike": {
                "slots": total_bike_slots,
                "occupied": total_bike_occupied,
                "free": total_bike_free,
            },
            "total_revenue": self.total_revenue,
            "total_vehicles_served": self.total_vehicles_served,
        }