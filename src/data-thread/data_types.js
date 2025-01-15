
class MapState {

}
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
