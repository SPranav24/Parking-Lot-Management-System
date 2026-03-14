from config import PARKING_LAYOUT
from parking.floor import ParkingFloor
from parking.parking_lot import ParkingLot

def initialize_parking_lot():
    floors = []

    for floor_data in PARKING_LAYOUT["floors"]:
        floor = ParkingFloor(
            floor_data["floor_no"],
            floor_data["slots"]
        )
        floors.append(floor)

    return ParkingLot(floors)