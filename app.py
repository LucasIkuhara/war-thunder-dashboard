from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fetchers import TelemetryThread
from utils import graph_as_json
from figures import FigureFactory


app = FastAPI()
app.mount("/static", StaticFiles(directory="templates"), name="pages")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

telemetry_thread = TelemetryThread(9999, 10)
telemetry = telemetry_thread.telemetry


@app.get('/speed')
@graph_as_json
def speed_over_time():

    return FigureFactory.speed_series(
        telemetry.speed,
        telemetry.time
    )


@app.get('/altitude')
@graph_as_json
def altitude_over_time():

    return FigureFactory.altitude_series(
        telemetry.altitude,
        telemetry.time
    )


@app.get('/energy')
@graph_as_json
def energy_over_time():

    return FigureFactory.sme_series(
        telemetry.speed,
        telemetry.altitude,
        telemetry.time
    )


@app.get('/artifical-horizon')
@graph_as_json
def artificial_horizon():

    return FigureFactory.artificial_horizon(
        telemetry.roll[-1],
        telemetry.pitch[-1],
        telemetry.compass[-1]
    )
