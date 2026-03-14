class Vehicle:
    def __init__(self, number):
        """
        number : vehicle number (unique ID)
        """
        self.number = number

    def get_type(self):
        raise NotImplementedError

    def get_rate_per_hour(self):
        raise NotImplementedError


class Car(Vehicle):
    def get_type(self):
        return "CAR"

    def get_rate_per_hour(self):
        return 40   # ₹40 per hour


class Bike(Vehicle):
    def get_type(self):
        return "BIKE"

    def get_rate_per_hour(self):
        return 20   # ₹20 per hour