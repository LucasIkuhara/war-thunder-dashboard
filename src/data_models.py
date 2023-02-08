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
        ## state_from_json
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
        ## indicators_from_json
        This method ingests a JSON with information from War Thunder's indicators API endpoint
        and stores it.

        Args:
            json: a JSON parsed as a dict containing 'compass', 'aviahorizon_roll' and
            'aviahorizon_pitch' values
        '''

        # Handle inconsistent API responses by the game.
        try:
            compass = json['compass']

        except KeyError:
            compass = json['compass1']

        self.compass_series = np.append(self.compass_series, compass)
        self.roll_series = np.append(self.roll_series, json['aviahorizon_roll'])
        self.pitch_series = np.append(self.pitch_series, json['aviahorizon_pitch'])


@dataclass(frozen=True)
class MapEntry:
    '''
    # MapEntry
    The base class for radar objects stored in MapState. It has attributes
    common to all radar-detection objects.
    '''

    class_name: str
    is_foe: bool
    position: np.array


@dataclass(frozen=True)
class AircraftEntry(MapEntry):
    '''
    # AircraftEntry
    Represents aircraft objects stored in MapState. It has attributes
    common to all radar-detection objects and additionally the velocity
    of the aircraft.
    '''

    velocity: np.array


@dataclass(frozen=True)
class AirfieldEntry(MapEntry):
    '''
    # AirfieldEntry
    Represents airfield objects stored in MapState. It has attributes
    common to all radar-detection objects. The position attribute denotes
    the start of the runway, and there is and additional one called 'end_postition'
    that stores runway's end coordinates.
    '''

    end_postition: np.array


class MapState:
    '''
    # MapState
    Stores the position and some other attributes of all things
    the player has access to using the map. It has separate attributes
    for airfields, aircraft and ground units. The position of the player is
    held in a separate attribute called 'player_position'. MapState objects
    can also ingest data from JSON and store it.
    '''

    def __init__(self) -> None:

        self.aircraft: list[AircraftEntry] = []
        self.airfields: list[AirfieldEntry] = []
        self.ground_units: list[MapEntry] = []
        self.player_position = np.array([0, 0])

    def clear_entries(self) -> None:
        '''
        # MapState
        ## clear_entries
        Clear all existing entries for aircraft, ground units and airfields.
        '''
        self.aircraft = []
        self.airfields = []
        self.ground_units = []

    def objects_from_json(self, json):
        '''
        # MapState
        ## objects_from_json
        This method ingests a JSON with information from War Thunder's map_obj.json API endpoint
        and stores it.

        Args:
            json: a JSON parsed as a dict containing a list of objects from the players map.
        '''

        self.clear_entries()

        for entry in json:

            match entry['type']:

                case 'airfield':
                    self.airfields.append(AirfieldEntry(
                        class_name='airfield',
                        position=np.array([entry['sx'], entry['sy']]),
                        end_postition=np.array([entry['ex'], entry['ey']]),
                        is_foe=(True if entry['color'] == '#f00C00' else False)
                    ))

                case 'aircraft':
                    if entry['icon'] == 'Player':
                        self.player_position = np.array([entry['x'], entry['y']])

                    else:
                        self.aircraft.append(AircraftEntry(
                            class_name='aircraft',
                            position=np.array([entry['x'], entry['y']]),
                            velocity=np.array([entry['dx'], entry['dy']]),
                            is_foe=(True if entry['color'] == '#f00C00' else False)
                        ))

                case 'ground_model':
                    self.ground_units.append(MapEntry(
                        class_name=entry['icon'],
                        position=np.array([entry['x'], entry['y']]),
                        is_foe=(True if entry['color'] == '#f00C00' else False)
                    ))

                case _:
                    print(f'Unmapped object.')
