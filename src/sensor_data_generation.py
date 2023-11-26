'''
contributor: Naman Arora

Base script to generate random various sensor data

'''

import random
import numpy as np
import json

class BarometricPressureSensor:
    def __init__(self):
        self.pressure = random.uniform(950, 1050)  # Pressure in hPa

    def update(self):
        # Simulate pressure changes
        self.pressure += random.uniform(-1, 1)

    def read(self):
        return self.pressure

class WindSensor:
    def __init__(self):
        self.speed = random.uniform(0, 100)  # Speed in km/h
        self.direction = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    def update(self):
        self.speed += random.uniform(-5, 5)
        self.speed = max(0, self.speed)  # Wind speed cannot be negative

    def read(self):
        return self.speed, self.direction

class WaveSensor:
    def __init__(self):
        self.height = random.uniform(0, 10)  # Height in meters
        self.frequency = random.uniform(0, 0.5)  # Frequency in Hz

    def update(self):
        self.height += random.uniform(-0.5, 0.5)
        self.height = max(0, self.height)  # Wave height cannot be negative

    def read(self):
        return self.height, self.frequency

class SeaSurfaceTemperatureSensor:
    def __init__(self):
        self.temperature = random.uniform(20, 30)  # Temperature in Celsius

    def update(self):
        self.temperature += random.uniform(-0.5, 0.5)

    def read(self):
        return self.temperature

class CurrentSensor:
    def __init__(self):
        self.speed = random.uniform(0, 5)  # Speed in m/s
        self.direction = random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

    def update(self):
        self.speed += random.uniform(-0.2, 0.2)
        self.speed = max(0, self.speed)  # Current speed cannot be negative

    def read(self):
        return self.speed, self.direction

class RainfallSensor:
    def __init__(self):
        self.rate = 0  # Rainfall rate in mm/h

    def update(self):
        self.rate = random.uniform(0, 100)

    def read(self):
        return self.rate

class HumiditySensor:
    def __init__(self):
        self.humidity = random.uniform(50, 100)  # Humidity in percentage

    def update(self):
        self.humidity += random.uniform(-5, 5)
        self.humidity = min(100, max(0, self.humidity))  # Humidity range 0-100%

    def read(self):
        return self.humidity


def get_measurements() -> dict:
    barometric_pressure_sensor = BarometricPressureSensor()
    wind_sensor = WindSensor()
    wave_sensor = WaveSensor()
    sst_sensor = SeaSurfaceTemperatureSensor()
    current_sensor = CurrentSensor()
    rainfall_sensor = RainfallSensor()
    humidity_sensor = HumiditySensor()


    data_dict = {}
    # Update and read data
    for i in range(1, 11):  # Simulate 10 time steps
        barometric_pressure_sensor.update(), 
        wind_sensor.update(),
        wave_sensor.update(),
        sst_sensor.update(),
        current_sensor.update(),
        rainfall_sensor.update(),
        humidity_sensor.update()

        measurement = [
                barometric_pressure_sensor.read(),
                wind_sensor.read(),
                wave_sensor.read(),
                sst_sensor.read(),
                current_sensor.read(),
                rainfall_sensor.read(),
                humidity_sensor.read()
        ]

        cnt_step = 'step ' + str(i)
        data_dict[cnt_step] = measurement

    return data_dict
    

def debug():
    mes = get_measurements()
    j_out = json.dumps(mes, indent=4)
    print(j_out)