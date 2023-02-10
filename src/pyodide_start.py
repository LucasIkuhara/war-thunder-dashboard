
# All missing imports below are handled by Pyodide

import json
from time import time


class GraphJsProxy:
    '''
    This is a mock to the entire API, which is meant to be used deployed on the edge with pyodide.
    '''

    def __init__(self):
        self.telemetry = HistoricTelemetry(100)
        self.radar = MapState()
        self.start_time = time()

    def state_from_json(self, value):
        state = json.loads(value)
        self.telemetry.state_from_json(state)
        self.telemetry.time = time() - self.start_time

    def indicators_from_json(self, value):
        indicators = json.loads(value)
        self.telemetry.indicators_from_json(indicators)
        self.telemetry.time = time() - self.start_time

    def objects_from_json(self, value):
        indicators = json.loads(value)
        self.radar.objects_from_json(indicators)

    @graph_as_json
    def speed_over_time(self):

        return FigureFactory.speed_series(
            self.telemetry.speed_series,
            self.telemetry.time_series
        )

    @graph_as_json
    def altitude_over_time(self):

        return FigureFactory.altitude_series(
            self.telemetry.altitude_series,
            self.telemetry.time_series
        )

    @graph_as_json
    def energy_over_time(self):

        return FigureFactory.sme_series(
            self.telemetry.speed_series,
            self.telemetry.altitude_series,
            self.telemetry.time_series
        )

    @graph_as_json
    def artificial_horizon(self):

        return FigureFactory.artificial_horizon(
            self.telemetry.roll,
            self.telemetry.pitch,
            self.telemetry.compass
        )

    @graph_as_json
    def radar_map(self):

        return FigureFactory.radar_map(
            self.radar,
            self.telemetry.compass
        )


python_proxies = GraphJsProxy()
