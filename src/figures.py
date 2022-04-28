import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_models import MapState
from utils import LinAlgUtils


class FigureFactory:
    '''
    # FigureFactory

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
        '''
        # FigureFactory
        ## speed_series

        Create a time-series line graph of speed.

        Args:
            speed: array of speed values.

            time: array of timestamps/generic time values.

        Returns:
            A plotly figure containing the graph.
        '''

        fig = px.line(
            x=time,
            y=speed,
            width=400,
            height=400,
            template='plotly_dark',
            title=f'Speed: {speed[-1]:.1f} km/h'
        )

        fig.update_xaxes(title_text='Time')
        fig.update_yaxes(title_text='Speed (km/h)')

        return fig

    @staticmethod
    def altitude_series(altitude: np.array, time: np.array):
        '''
        # FigureFactory
        ## altitude_series

        Create a time-series line graph of altitude.

        Args:
            speed: array of speed values.

            time: array of timestamps/generic time values.

        Returns:
            A plotly figure containing the graph.
        '''
        fig = px.line(
            x=time,
            y=altitude,
            width=400,
            height=400,
            template='plotly_dark',
            title=f'Altitude: {altitude[-1]:.1f} m'
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
            title=f'Specific Energy: {energy[-1]:.0f} J/kg'
        )

        fig.update_xaxes(title_text='Time (s)')
        fig.update_yaxes(title_text='Specific Mechanical Energy (J/kg)')

        return fig

    @staticmethod
    def radar_map(radar_detections: MapState, compass_heading: float):

        # This root detection is a trick to force the figure to render as polar,
        # even if there are no detections
        radius = np.array([0])
        angles = np.array([0])
        display_type = np.array(['root'])
        compass_heading = np.array(compass_heading)

        # Get the positions of all aircraft
        for aircraft in radar_detections.aircraft:

            r, theta = LinAlgUtils.to_polar(aircraft.position - radar_detections.player_position)

            radius = np.append(radius, r)
            angles = np.append(angles, theta)
            display_type = np.append(
                display_type,
                'Enemy Aircraft' if aircraft.is_foe else 'Friendly Aircraft'
            )

        # Get the positions of all ground units
        for ground_object in radar_detections.ground_units:

            r, theta = LinAlgUtils.to_polar(
                ground_object.position - radar_detections.player_position)

            radius = np.append(radius, r)
            angles = np.append(angles, theta)
            display_type = np.append(
                display_type,
                'Enemy Ground Unit' if ground_object.is_foe else 'Friendly Ground Unit'
            )

        # Adjust angles to be relative and use degrees
        angles = np.rad2deg(angles) + 90

        # Create plot
        fig = px.scatter_polar(
            r=radius,
            theta=angles,
            color=display_type,
            color_discrete_map={
                'Enemy Aircraft': 'red',
                'Friendly Aircraft': 'green',
                'Enemy Ground Unit': 'darkred',
                'Friendly Ground Unit': 'darkgreen',
                'Enemy Airfield': 'pink',
                'Friendly Airfield': 'blue',
                'root': 'rgba(0, 0, 0, 0)'
            },
            start_angle=compass_heading+90,
            template='plotly_dark'
        )

        # Add airfields
        for airfield in radar_detections.airfields:

            r_start, theta_start = LinAlgUtils.to_polar(
                airfield.position - radar_detections.player_position)

            r_end, theta_end = LinAlgUtils.to_polar(
                airfield.end_postition - radar_detections.player_position)

            theta = np.rad2deg([theta_start, theta_end]) + 90

            fig.add_trace(go.Scatterpolar(
                r=np.array([r_start, r_end]),
                theta=theta,
                mode='lines',
                line_color=('red' if airfield.is_foe else 'green')
            ))

        fig.update_layout(
            width=400,
            height=400,
            showlegend=False,
            margin={"l": 25, "r": 25, "b": 25, "t": 25, "pad": 0},
            polar={

                'radialaxis': {
                    'showticklabels': False
                },

                'angularaxis': {
                    'tickmode': 'array',
                    'tickvals': list(range(0, 360, 45)),
                    'ticktext': ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
                }
            }
        )

        return fig

    @staticmethod
    def artificial_horizon(
        roll: float,
        pitch: float,
        yaw: float,
        fov_h: int = 80,
        fov_v: int = 80,
    ):

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

        # Make lines on the display

        # Fixed Markings
        fixed_markings = np.array([
            [-10, 0],
            [-5, 0],
            [0, -5],
            [5, 0],
            [10, 0]
        ])

        # Dynamic markings
        # Get all increments of 10 and match them to two points for each line
        dynamic_markings_y = [y for y in range(-180, 180, 10)]
        line_width_base = np.tile(10, len(dynamic_markings_y)) * \
            np.power(np.cos(np.radians(dynamic_markings_y)), 0.6)*4

        right_markings = np.stack((line_width_base, dynamic_markings_y), axis=1)
        left_markings = np.stack((line_width_base*-1, dynamic_markings_y), axis=1)

        # Rotate components of the AH
        # Generate a rotation matrix
        rot_matrix = np.array([
            [np.cos(roll), np.sin(roll)],
            [-np.sin(roll), np.cos(roll)]
        ])

        # Apply rotation to all dynamic components
        blue_box = np.matmul(blue_box, rot_matrix)
        orange_box = np.matmul(orange_box, rot_matrix)
        right_markings = np.matmul(right_markings, rot_matrix)
        left_markings = np.matmul(left_markings, rot_matrix)

        # Tranlate center of plot to current yaw and pitch
        origin = np.array([yaw, pitch])

        blue_box = blue_box + origin
        orange_box = orange_box + origin
        right_markings = right_markings + origin
        left_markings = left_markings + origin
        fixed_markings = fixed_markings + np.array([yaw, 0])

        # Plotting steps
        fig = go.Figure()

        # Add background
        fig.add_traces([
            # Orange part
            go.Scatter(
                x=orange_box.T[0],
                y=orange_box.T[1],
                fill="toself",
                line_color='rgba(0,0,0,0)',
                fillcolor='orange',
                hoverinfo='skip'
            ),

            # Blue Part
            go.Scatter(
                x=blue_box.T[0],
                y=blue_box.T[1],
                fill="toself",
                line_color='rgba(0,0,0,0)',
                fillcolor='lightblue',
                hoverinfo='skip'
            ),

            # Add fixed markings

            go.Scatter(
                x=fixed_markings.T[0],
                y=fixed_markings.T[1],
                line_color='white',
                mode='lines',
                line_width=5,
                hoverinfo='skip'
            ),
        ])

        # Add Dynamic Markings
        for left, right, altitude in zip(left_markings, right_markings, dynamic_markings_y):
            fig.add_trace(go.Scatter(
                x=[left[0], right[0]],
                y=[left[1], right[1]],
                line_color='white',
                mode='lines+text',
                text=f'{altitude:.0f}',
                textposition=["top left", "top right"],
                hoverinfo='skip'
            ))

        # Figure layout
        fig.update_layout(
            width=400,
            height=400,
            margin={"l": 10, "r": 10, "b": 30, "t": 10, "pad": 10},
            showlegend=False,
            paper_bgcolor='#111111',
            plot_bgcolor='#111111',
            font_color='#f2f5fa'
        )

        # Set range of the axes
        fig.update_xaxes(
            range=[origin[0]-fov_h, origin[0]+fov_h],
            tickmode='array',
            tickvals=list(range(-360, 361, 45)),
            ticktext=[
                'N',
                'NE',
                'E',
                'SE',
                'S',
                'SW',
                'W',
                'NW',
                'N',
                'NE',
                'E',
                'SE',
                'S',
                'SW',
                'W',
                'NW',
                'N']
        )

        fig.update_yaxes(range=[-fov_v, fov_v], showticklabels=False)

        return fig
