from json import dumps
from plotly.utils import PlotlyJSONEncoder
from fastapi.responses import PlainTextResponse


def graph_as_json(func, *args, **kwargs):

    def decorated():

        graph = func(*args, **kwargs)
        json = dumps(graph, cls=PlotlyJSONEncoder)

        return PlainTextResponse(json)

    decorated_function = decorated
    decorated_function.__name__ = f"{func.__name__}_with_graph_as_json"

    return decorated_function
