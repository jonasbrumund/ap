import pandas as pd
import re
import numpy as np
from scipy.spatial import distance
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import Audio, display
import ipywidgets as widgets
import os

# === 1) Daten laden ===
csv_path = os.path.join(os.getcwd(), 'ap', 'samples_data.csv')
df = pd.read_csv(csv_path)

# === 2) Regex Filter ===
regex_input = widgets.Text(
    value='.*',
    description='Regex:',
    placeholder='Regex eingeben',
    layout=widgets.Layout(width='50%')
)

def filter_df(change):
    pattern = regex_input.value
    try:
        mask = df['stem'].str.contains(pattern, regex=True)
        filtered_df.value = df[mask]
    except:
        print("Ungültiger Regex!")

regex_input.observe(filter_df, names='value')

filtered_df = widgets.Output()

# === 3) Scatterplot ===
x_dropdown = widgets.Dropdown(
    options=df.columns,
    description='X:',
)

y_dropdown = widgets.Dropdown(
    options=df.columns,
    description='Y:',
)

z_dropdown = widgets.Dropdown(
    options=['None'] + list(df.columns),
    description='Z:',
)

color_dropdown = widgets.Dropdown(
    options=['None'] + list(df.columns),
    description='Color:',
)

plot_button = widgets.Button(description='Plot')

plot_output = widgets.Output()

def plot_data(b):
    plot_output.clear_output()
    X = df[x_dropdown.value]
    Y = df[y_dropdown.value]
    Z = z_dropdown.value
    C = color_dropdown.value

    with plot_output:
        if Z == 'None':
            plt.scatter(X, Y, c=df[C] if C != 'None' else 'b')
            plt.xlabel(x_dropdown.value)
            plt.ylabel(y_dropdown.value)
            plt.show()
        else:
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(X, Y, df[Z], c=df[C] if C != 'None' else 'b')
            ax.set_xlabel(x_dropdown.value)
            ax.set_ylabel(y_dropdown.value)
            ax.set_zlabel(Z)
            plt.show()

plot_button.on_click(plot_data)

# === 4) Audio-Player ===
file_dropdown = widgets.Dropdown(
    options=df['stem'].tolist(),
    description='File:',
)

start_slider = widgets.FloatSlider(
    min=0, max=10, step=0.1, value=0, description='Start:'
)
end_slider = widgets.FloatSlider(
    min=0, max=10, step=0.1, value=10, description='End:'
)

loop_checkbox = widgets.Checkbox(
    value=False, description='Loop'
)

play_button = widgets.Button(description='Play')

audio_output = widgets.Output()

def play_audio(b):
    filename = file_dropdown.value
    # Annahme: die Datei liegt lokal vor
    # Start/End ignorieren wir hier — ein echter Audio-Schnitt braucht extra Libs
    with audio_output:
        audio_output.clear_output()
        display(Audio(filename=filename, autoplay=True))

play_button.on_click(play_audio)

# === 5) Distanzberechnung ===
feature_dropdown = widgets.SelectMultiple(
    options=df.columns[1:],  # ohne filename
    description='Features:',
)

ref_file_dropdown = widgets.Dropdown(
    options=df['stem'].tolist(),
    description='Reference:'
)

dist_output = widgets.Output()

def calc_distance(b):
    ref_file = ref_file_dropdown.value
    features = feature_dropdown.value
    ref_vec = df.loc[df['stem'] == ref_file, features].values[0]
    df['distance'] = df[features].apply(lambda row: distance.euclidean(row, ref_vec), axis=1)
    sorted_df = df.sort_values(by='distance')
    with dist_output:
        dist_output.clear_output()
        display(sorted_df[['stem', 'distance']].head(10))

dist_button = widgets.Button(description='Berechne Distanz')
dist_button.on_click(calc_distance)

# === Layout ===
display(regex_input)
display(filtered_df)

display(widgets.HBox([x_dropdown, y_dropdown, z_dropdown, color_dropdown]))
display(plot_button)
display(plot_output)

display(file_dropdown, start_slider, end_slider, loop_checkbox, play_button, audio_output)

display(feature_dropdown, ref_file_dropdown, dist_button, dist_output)
