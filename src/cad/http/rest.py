from flask import Flask, request, send_from_directory, Response
import os
import io
from cad.calc.geo import Geo
from cad.calc.visualization import DidgeVisualizer

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__, static_url_path='')

@app.route('/plot.png')
def plot_png():

    shape=[[0,32], [100, 65, 500, 72]]
    geo=Geo(geo=shape)

    fig=DidgeVisualizer.vis_didge(geo)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/html/<path:path>')
def send_js(path):

    print(path)
    print(os.path.exists("html/" + path))
    return send_from_directory('html', "./", filename="index.html")

if __name__ == "__main__":
    app.run()
