from json import dumps
from plotly.utils import PlotlyJSONEncoder
import numpy as np


def graph_as_json(func, *args, **kwargs):

    def decorated(*args, **kwargs):

        graph = func(*args, **kwargs)
        json = dumps(graph, cls=PlotlyJSONEncoder)

        return json

    decorated_function = decorated
    decorated_function.__name__ = f"{func.__name__}_with_graph_as_json"

    return decorated_function


class LinAlgUtils:

    @staticmethod
    def to_polar(vector: np.array):
        '''
        Converts a vector from Cartesian coordinates to polar coordinates.

        Args:
            vector: the vector that will be converted.

        Returns:
            r = the distance from the origin.

            theta = the angle between the vector and the x axis.
        '''

        r = np.linalg.norm(vector)
        theta = np.arctan2(vector[1], vector[0])

        return (r, theta)
