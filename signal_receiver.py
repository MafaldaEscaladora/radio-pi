from datetime import datetime
from datetime import timedelta
from typing import List
import matplotlib.pyplot as pyplot
import RPi.GPIO as GPIO
import json


class Reading:
    def __init__(self, value, time):
        self.value = value
        self.time = time


class SignalReceiver:
    def __init__(self, collecting_signal_period: timedelta, file_name):
        self.collecting_signal_period = collecting_signal_period
        self.file_name = file_name
        self.readings: List[Reading] = []

    def collect_signals(self, mode, receiver_pin):
        print("Signal collection started")
        GPIO.setmode(mode)
        GPIO.setup(receiver_pin, GPIO.IN)
        start_time = datetime.now()
        end_time = start_time + self.collecting_signal_period
        while True:
            current_time = datetime.now()
            if current_time > end_time:
                break
            single_signal_time_point = current_time - start_time
            self.readings.append(Reading(GPIO.input(receiver_pin), single_signal_time_point))
        GPIO.cleanup()
        print("Signal collection ended")
        self.estimate_signals_duration()

    def estimate_signals_duration(self):
        signal_values = []
        signal_durations = []
        start_reading = self.readings[0]

        for index in range(len(self.readings)):
            actual_reading = self.readings[index]
            signal_has_changed = actual_reading.value != start_reading.value
            if signal_has_changed:
                end_reading = self.readings[index - 1]
                signal_duration = end_reading.time - start_reading.time
                signal_values.append(start_reading.value)
                signal_durations.append(time_in_microseconds(signal_duration))
                start_reading = actual_reading

        if signal_values:
            del signal_values[0]
            del signal_durations[0]
            print("Writing data to json")
            self.json_builder(signal_values, signal_durations)
        else:
            print("No signal collected")

    def json_builder(self, signal_values, signal_durations):
        with open(self.file_name, "w") as file:
            json.dump({"signal": signal_values, "duration": signal_durations}, file)

    def plot_signal(self):
        print('Plot processing')
        single_signal_occurrence_times = []
        signal_values = []
        for reading in self.readings:
            single_signal_occurrence_times.append(time_in_microseconds(reading.time))
            signal_values.append(reading.value)

        pyplot.plot(single_signal_occurrence_times, signal_values)
        pyplot.axis([0, self.collecting_signal_period.seconds, 0, 1.5])
        pyplot.show()


def time_in_microseconds(time_point):
    return time_point.seconds + time_point.microseconds / 1000000.0


signal_object = SignalReceiver(timedelta(seconds=5), "signals_on_clasy2.json")
signal_object.collect_signals(mode=GPIO.BCM, receiver_pin=22)
signal_object.plot_signal()
