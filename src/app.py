from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fetchers import DataThread
from utils import graph_as_json
from figures import FigureFactory
from fastapi.responses import PlainTextResponse
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="../templates"), name="pages")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

data_thread = DataThread(60, 50, 150, 0.5)
telemetry = data_thread.telemetry
radar = data_thread.map


@app.get('/speed')
@graph_as_json
def speed_over_time():

    return PlainTextResponse(FigureFactory.speed_series(
        telemetry.speed_series,
        telemetry.time_series
    ))


@app.get('/altitude')
@graph_as_json
def altitude_over_time():

    return PlainTextResponse(FigureFactory.altitude_series(
        telemetry.altitude_series,
        telemetry.time_series
    ))


@app.get('/energy')
@graph_as_json
def energy_over_time():

    return PlainTextResponse(FigureFactory.sme_series(
        telemetry.speed_series,
        telemetry.altitude_series,
        telemetry.time_series
    ))


@app.get('/artificial-horizon')
@graph_as_json
def artificial_horizon():

    return PlainTextResponse(FigureFactory.artificial_horizon(
        telemetry.roll,
        telemetry.pitch,
        telemetry.compass
    ))


@app.get('/radar-map')
@graph_as_json
def radar_map():

    return PlainTextResponse(FigureFactory.radar_map(
        radar,
        telemetry.compass
    ))


if __name__ == "__main__":
    uvicorn.run("app:app", port=8000, host="0.0.0.0",log_level="info")