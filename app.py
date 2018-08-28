from bokeh.io import curdoc
from flask import Flask, render_template, request

from bokeh.embed import server_document
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, Range1d, HoverTool, Dropdown
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop

import json

import Helper.RestHelper as RestHelper
from Helper.RestHelper import EncoderRestHelper

app = Flask(__name__)

current_videoName = ''
FOV_API_HOST = "http://imes.gachon.ac.kr:5555/"

def Graph_tileNumsPerTimestamp(doc, data_tile, data_fov):
    timestamp_list = [int(i) for i in list(data_fov.keys())]
    timestamp_list = sorted(timestamp_list)
    max_timestamp = max(timestamp_list)

    df_bar = data_tile
    df_scatter = data_fov
    source_bar = ColumnDataSource(data=df_bar['0'])
    source_scatter = ColumnDataSource(data=df_scatter['0'])


    plot_bar = figure(y_range=(0, 25), y_axis_label='Occurrence number', x_axis_label='Tile #',
                  title="시간대별 시야각 분포(타일 번호)", plot_width=600, plot_height=500)
    plot_bar.line('x', 'y', source=source_bar, line_width=3)
    plot_bar.add_tools(HoverTool(
        tooltips=[
            ('Tile #', '@x'),
            ('Occurrence number', '@y'),  # use @{ } for field names with spaces
        ],

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    plot_bar.x_range = Range1d(-2, 17)
    plot_bar.y_range = Range1d(-1, 50)

    plot_scatter = figure(y_range=(0, 25), y_axis_label='Pitch', x_axis_label='Yaw',
                  title="시간대별 시야각 분포(좌표값)", plot_width=600, plot_height=500)
    plot_scatter.circle('x', 'y', source=source_scatter, size=25, alpha=0.1, color='red')
    plot_scatter.add_tools(HoverTool(
        tooltips=[
            ('yaw', '@x'),
            ('pitch #', '@y'),  # use @{ } for field names with spaces
        ],

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    plot_scatter.x_range = Range1d(-180, 180)
    plot_scatter.y_range = Range1d(-180, 180)

    def callback(attr, old, new):
        curData_bar = df_bar[str(new)]
        curData_scatter = df_scatter[str(new)]
        source_bar.data = ColumnDataSource(data=curData_bar).data
        source_scatter.data = ColumnDataSource(data=curData_scatter).data

    slider = Slider(start=0, end=max_timestamp, value=0, step=1000, title="타임 스탬프")
    slider.on_change('value', callback)
    row_layout = row(plot_bar, plot_scatter)
    doc.add_root(column(slider, row_layout))

def Graph_EncodingLevelsPerTimestamp(doc, data):
    # TODO : IMPLEMENTS
    df = data
    source = ColumnDataSource(data=df)

    plot = figure(y_range=(0, 25), y_axis_label='Tile #',
                  title="타임 스탬프별 영상 인코딩 레벨 그래프", plot_width=1400, plot_height=500)
    plot.line('x', 'y', source=source, line_width=3)

    pass

def Graph_MaxOccursTileNumberForWholeTimestamp(doc, data, data_level):
    df = data
    source = ColumnDataSource(data=df)
    df_level = data
    source_level = ColumnDataSource(data=df_level)

    plot = figure(y_range=(0, 25), y_axis_label='Tile #', x_axis_label='timestamp(ms)',
                  title="타임 스탬프별 최빈 타일 넘버 그래프", plot_width=1200, plot_height=500)
    plot.circle('x', 'y', source=source, size=25)

    plot.add_tools(HoverTool(
        tooltips=[
            ('timestamp', '@x'),
            ('tile #', '@y'),  # use @{ } for field names with spaces
        ],

        # display a tooltip whenever the cursor is vertically in line with a glyph
        mode='vline'
    ))

    plot.y_range = Range1d(-1, 16)

    plot_level = figure(y_range=(0, 25), y_axis_label='Pitch', x_axis_label='Yaw',
                  title="타임 스탬프별 영상 인코딩 레벨 그래프")
    plot_level.line('x', 'y', source=source_level, line_width=3)

    row_layout = row(plot, plot_level)
    doc.add_root(column(plot))

def get_fovRawData(json_data):
    total_fov_data = json.loads(json_data)

    result_data = dict()
    data_graph1 = total_fov_data['total_data']

    for each_key in data_graph1.keys():
        result_data[str(each_key)] = dict()

        data_graph1_x = list()
        data_graph1_y = list()

        for each_item in data_graph1[each_key]:
            coord_str = str(each_item).split(' ')
            yaw_str = coord_str[0]
            pitch_str = coord_str[1]

            data_graph1_x.append(float(yaw_str))
            data_graph1_y.append(float(pitch_str))

        result_data[str(each_key)]['x'] = data_graph1_x
        result_data[str(each_key)]['y'] = data_graph1_y

    return result_data



def get_maxTileData(json_data):
    total_fov_data = json.loads(json_data)

    data_graph1 = total_fov_data['max_tile_data']
    data_graph1_x = list()
    data_graph1_y = list()

    for each_key in data_graph1.keys():
        data_graph1_x.append(int(each_key))

    data_graph1_x.sort()

    for each_item in data_graph1_x:
        data_graph1_y.append(int(data_graph1[str(each_item)]))

    result_data = dict()
    result_data['x'] = data_graph1_x
    result_data['y'] = data_graph1_y

    return result_data


def get_occursTileData(json_data):
    total_fov_data = json.loads(json_data)

    result_data = dict()
    data_graph1 = total_fov_data['total_data']
    data_graph1_x = [i for i in range(0, 17)]
    data_graph1_y = list()

    for each_key in data_graph1.keys():
        result_data[str(each_key)] = dict()

        data_graph1_y = list()
        for idx in range(0, 17):
            data_graph1_y.append(0)
        for each_item in data_graph1[each_key]:
            data_graph1_y[int(each_item)] += 1

        result_data[str(each_key)]['x'] = data_graph1_x
        result_data[str(each_key)]['y'] = data_graph1_y


    return result_data

def get_encodingLevelData(json_data):
    total_encode_level_data = json.loads(json_data)

    print(total_encode_level_data)

    data_graph1 = total_encode_level_data['result_data']['timeline']
    data_graph_level = dict()
    data_graph_level['x'] = list()
    data_graph_level['y'] = list()
    data_graph1_x = list()
    data_graph1_y_predata = list()
    data_key_list = list()


def modify_doc(doc):
    global current_videoName

    total_fov_json = RestHelper.req(path=FOV_API_HOST+current_videoName+"/fov", query="", method="GET").text
    total_fov_raw_json = RestHelper.req(path=FOV_API_HOST+current_videoName+"/fov_raw", query="", method="GET").text
    total_encode_level_json = RestHelper.req(path=FOV_API_HOST+current_videoName+"/encode", query="", method="GET").text

    data_for_maxOccurGraph = get_maxTileData(total_fov_json)
    data_for_occursTileGraph = get_occursTileData(total_fov_json)
    data_for_encodeLevelGraph = get_encodingLevelData(total_encode_level_json)

    data_for_fovRawData = get_fovRawData(total_fov_raw_json)

    data_graph1_fov = dict()

    Graph_MaxOccursTileNumberForWholeTimestamp(doc=doc, data=data_for_maxOccurGraph, data_level=data_for_encodeLevelGraph)

    Graph_tileNumsPerTimestamp(doc=doc, data_tile=data_for_occursTileGraph, data_fov=data_for_fovRawData)


@app.route('/')
def index():
    encoderRestHelper = EncoderRestHelper(API_HOST="http://imes.gachon.ac.kr:10100/")
    videoList = encoderRestHelper.get_videoList()
    videoList = ['congo_2048', 'DroneView']

    return render_template('layouts/index.html',
                           videos=videoList)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global current_videoName

    encoderRestHelper = EncoderRestHelper(API_HOST="http://imes.gachon.ac.kr:10100/")
    videoList = encoderRestHelper.get_videoList()
    videoList = ['congo_2048', 'DroneView']

    current_videoName = str(request.args['video_name'])

    if 'video_name' not in request.args.keys():
        if current_videoName is '':
            current_videoName = videoList[0]
    else:
        current_videoName = str(request.args['video_name'])

    script = server_document('http://localhost:5006/bkapp')
    return render_template("layouts/dashboard.html", script=script, template="Flask")


def bk_worker():
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
    app.run(host="0.0.0.0", port=8000)
