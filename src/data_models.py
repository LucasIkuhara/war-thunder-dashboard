from dataclasses import dataclass
import numpy as np


class HistoricTelemetry:
    '''
    # HistoricTelemetry
    Stores time-series of different telemetry values as FIFO-like objects.
    The data can be accessed either by the 'series' properties, with all
    stored values, or by the 'non-series' properties, which return the
    last value of the correspondent series. It can also ingest data
    from JSON and store it.
    '''

    def __init__(self, buffer_size) -> None:
        self.speed_series = np.zeros(buffer_size)
        self.altitude_series = np.zeros(buffer_size)
        self.time_series = np.zeros(buffer_size)
        self.compass_series = np.zeros(buffer_size)
        self.roll_series = np.zeros(buffer_size)
        self.pitch_series = np.zeros(buffer_size)

    @property
    def speed(self):
        return self.speed_series[-1]

    @property
    def altitude(self):
        return self.altitude_series[-1]

    @property
    def time(self):
        return self.time_series[-1]

    @property
    def compass(self):
        return self.compass_series[-1]

    @property
    def pitch(self):
        return self.pitch_series[-1]

    @property
    def roll(self):
        return self.roll_series[-1]

    @time.setter
    def time(self, value):
        self.time_series = np.append(self.time_series[1:], value)

    def state_from_json(self, json):
        '''
        # HistoricTelemetry
        ## State from JSON
        This method ingests a JSON with information from War Thunder's state API endpoint
        and stores it.

        Args:
            json: a JSON parsed as a dict containing 'TAS, km/h' and 'H, m' values
        '''

        self.speed_series = np.append(self.speed_series[1:], json['TAS, km/h'])
        self.altitude_series = np.append(self.altitude_series[1:], json['H, m'])

    def indicators_from_json(self, json):
        '''
        # HistoricTelemetry
        ## Indicators from JSON
        This method ingests a JSON with information from War Thunder's indicators API endpoint
        and stores it.

        Args:
            json: a JSON parsed as a dict containing 'compass', 'aviahorizon_roll' and
            'aviahorizon_pitch' values
        '''
        self.compass_series = np.append(self.compass_series, json['compass'])
        self.roll_series = np.append(self.roll_series, json['aviahorizon_roll'])
        self.pitch_series = np.append(self.pitch_series, json['aviahorizon_pitch'])
