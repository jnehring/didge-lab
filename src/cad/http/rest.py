import io
import random
from flask import Flask, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from cad.calc.geo import Geo
from cad.calc.didgmo import PeakFile, didgmo_bridge
from cad.calc.visualization import DidgeVisualizer, FFTVisualiser
import matplotlib.pyplot as plt
from cad.calc.conv import note_to_freq, note_name

app = Flask(__name__)

@app.route('/plot.png')
def plot_png():


    shape=[
        [0,32],
        [800, 40],
        [1500, 80]
    ]
    geo=Geo(geo=shape)
    peak, fft=didgmo_bridge(geo)

    target=[-31, -19]

    for t in target:
        freq=note_to_freq(t)
        name=note_name(t)
        print(f"target {name}, {freq}")
    target=[note_to_freq(x) for x in target]
    fig=FFTVisualiser.vis_fft_and_target(fft, target)
    #fig.show()
    #fig = create_figure()
    #output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig
app.run(debug=True)
