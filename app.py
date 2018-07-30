from flask import Flask, render_template

from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature

app = Flask(__name__)

def Graph_tileNumsPerTimestamp(doc, data_tile, data_fov):
    df1 = data_tile
    df2 = data_fov
    source = ColumnDataSource(data=df1['0'])

    plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Occurrence',
                  title="Every occurred tile # per timestamp")
    plot.line('x', 'y', source=source)

    def callback(attr, old, new):
        curData = df1[str(new)]
        source.data = ColumnDataSource(data=curData).data

    slider = Slider(start=0, end=1000, value=0, step=1000, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

def Graph_MaxOccursTileNumberForWholeTimestamp(doc, data):
    df = data
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type='datetime', y_range=(0, 25), y_axis_label='Occurrence',
                  title="Maximum occurred tile # per timestamp")
    plot.line('x', 'y', source=source)

    doc.add_root(column(plot))

def modify_doc(doc):
    data_graph1 = dict()

    sample_data = dict()
    sample_data['x'] = [i for i in range(0, 16)]
    sample_data['y'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 5, 6, 2, 0, 0]
    data_graph1['0'] = sample_data

    sample_data = dict()
    sample_data['x'] = [i for i in range(0, 16)]
    sample_data['y'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 6, 5, 1, 0, 0]
    data_graph1['1000'] = sample_data

    data_graph2 = dict()
    data_graph2['x'] = [0, 1000, 2000, 3000, 4000]
    data_graph2['y'] = [12, 13, 11, 11, 12]

    data_graph1_fov = dict()

    Graph_MaxOccursTileNumberForWholeTimestamp(doc=doc, data=data_graph2)
    Graph_tileNumsPerTimestamp(doc=doc, data_tile=data_graph1, data_fov=data_graph1_fov)

    doc.theme = Theme(filename="theme.yaml")


@app.route('/', methods=['GET'])
def bkapp_page():
    script = server_document('http://localhost:5006/bkapp')
    return render_template("embed.html", script=script, template="Flask")


def bk_worker():
    # Can't pass num_procs > 1 in this configuration. If you need to run multiple
    # processes, see e.g. flask_gunicorn_embed.py
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(), allow_websocket_origin=["localhost:8000"])
    server.start()
    server.io_loop.start()

from threading import Thread
Thread(target=bk_worker).start()

if __name__ == '__main__':
    print('Opening single process Flask app with embedded Bokeh application on http://localhost:8000/')
    print()
    print('Multiple connections may block the Bokeh app in this configuration!')
    print('See "flask_gunicorn_embed.py" for one way to run multi-process')
    app.run(port=8000)
