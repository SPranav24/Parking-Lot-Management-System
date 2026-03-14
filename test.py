import time
from system_setup import initialize_parking_lot
from parking.vehicle import Car, Bike

parking_lot = initialize_parking_lot()

car1 = Car("CAR101")
bike1 = Bike("BIKE201")

ticket1 = parking_lot.park_vehicle(car1)
ticket2 = parking_lot.park_vehicle(bike1)

print("Car parked at:", ticket1.slot.slot_id)
print("Bike parked at:", ticket2.slot.slot_id)

time.sleep(2)

_, car_fee = parking_lot.exit_vehicle("CAR101")
_, bike_fee = parking_lot.exit_vehicle("BIKE201")

print("Car parking fee:", car_fee)
print("Bike parking fee:", bike_fee)