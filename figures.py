from turtle import fillcolor
from matplotlib.pyplot import legend
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from math import pi


class FigureFactory:
    '''
    # Figure Factory

    A Factory for building Plotly Figures specifically
    made for one visualization. It supports everything from
    line charts and indicators to complex custom-made
    visualizations for application-specific needs. All methods are
    static, so there is no point in instantiating this class in
    order to build Figures.

    ## Example:

    speed = np.array([10, 30, 90])

    time = np.array([1, 2, 3])

    fig = FigureFactory.speed_series(speed, time)

    fig.show()
    '''

    @staticmethod
    def speed_series(speed: np.array, time: np.array):

        fig = px.line(
            x=time,
            y=speed,
            width=400,
            height=400,
            template='plotly_dark',
            title='Speed'
        )

        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Speed (km/h)')

        return fig

    @staticmethod
    def altitude_series(altitude: np.array, time: np.array):

        fig = px.line(
            x=time,
            y=altitude,
            width=400,
            height=400,
            template='plotly_dark',
            title='Altitude'
        )

        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Altitude (m)')

        return fig

    @staticmethod
    def sme_series(speed: np.array, altitude: np.array, time: np.array):
        '''
        # sme_series
        SME stands for Specific Mechanical Energy.
        '''

        speed = speed/3.6
        energy = speed**2/2 + 9.81*altitude

        fig = px.line(
            x=time,
            y=energy,
            width=400,
            height=400,
            template='plotly_dark',
            title='Specific Energy'
        )

        fig.update_xaxes(title_text='Time (s)')
        fig.update_yaxes(title_text='Specific Mechanical Energy (J/kg)')

        return fig

    @staticmethod
    def artificial_horizon(roll: float, pitch: float, yaw: float, fov: int = 40):

        # Convert to radians
        roll = np.radians(roll)

        # Make land portion of the AH
        orange_box = np.array([
            [500, 0],
            [500, -500],
            [-500, -500],
            [-500, 0]
        ])

        # Make sky portion of the AH
        blue_box = np.array([
            [500, 0],
            [500, 500],
            [-500, 500],
            [-500, 0]
        ])

        # Rotate components of the AH
        rot_matrix = np.array([
            [np.cos(roll), np.sin(roll)],
            [-np.sin(roll), np.cos(roll)]
        ])

        blue_box = np.matmul(blue_box, rot_matrix)
        orange_box = np.matmul(orange_box, rot_matrix)

        # Tranlate center of plot to current yaw and pitch
        origin = np.array([yaw, pitch])

        blue_box = blue_box + origin
        orange_box = orange_box + origin

        # Plotting steps
        fig = go.Figure()
        fig.update_layout(
            width=400,
            height=400,
            margin={"l": 10, "r": 10, "b": 10, "t": 10, "pad": 10}
        )

        fig.add_traces([
            # Orange part
            go.Scatter(
                x=orange_box.T[0],
                y=orange_box.T[1],
                fill="toself",
                line_color='rgba(0,0,0,0)',
                fillcolor='orange'
            ),

            # Blue Part
            go.Scatter(
                x=blue_box.T[0],
                y=blue_box.T[1],
                fill="toself",
                line_color='rgba(0,0,0,0)',
                fillcolor='lightblue'
            )
        ])

        fig.update_xaxes(range=[origin[0]-fov, origin[0]+fov])
        fig.update_yaxes(range=[origin[1]-fov, origin[1]+fov])
        fig.update_layout(showlegend=False)

        return fig
