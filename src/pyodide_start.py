
# All missing imports below are handled by Pyodide

def for_all_methods(decorator):
    def decorate(cls):
        for attr in cls.__dict__: # there's propably a better way to do this
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate

@for_all_methods(graph_as_json)
class FigureAsJSON(FigureFactory):
    pass


telemetry = HistoricTelemetry(100)
map = MapState()
