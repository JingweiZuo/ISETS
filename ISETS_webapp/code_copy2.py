from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
#from bokeh.embed import autoload_server
from bokeh.embed import server_document, components
from werkzeug.utils import secure_filename
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import ColumnDataSource, AjaxDataSource
from bokeh.models.widgets import Slider, TextInput, Button, Dropdown, CheckboxButtonGroup, RadioButtonGroup
from bokeh.io import show, curdoc
from threading import Thread
import pandas as pd
import utils.utils as util
from ISETS_Web_backend import account_api, blocking_task

app = Flask(__name__)
app.register_blueprint(account_api)
thread = None
TSclass = None
data_directory = "/Users/Jingwei/PycharmProjects/distributed_use/venv/TestDataset/UCR_TS_Archive_2015"
datasetName = data_directory + "/FordA/FordA_TRAIN"
window_size = None
forget_degree = None

@app.route('/')
def index():
    return 'Hello World!'

@app.route("/dashboard/", methods=['POST', 'GET'])
def hello():
    #script=autoload_server(model=None,app_path="/bokeh-sliders",url="http://localhost:5006")
    bokeh_script=server_document("http://localhost:5006/bokeh-sliders")
    bokeh_server = server_document("http://localhost:5006/bokeh-server")
    pl_dataset = plot_dataset()
    pl_conceptDrift = plot_conceptDrift()
    global datasetName, thread, TSclass, window_size, forget_degree
    #webtitle = "ISETS: Incremental Shapelet Extraction fromStreaming Time Series"

    if request.method == 'POST':
        file = request.files['file']
        datasetName = secure_filename(file.filename)
        file.save(datasetName)
        # to start a new Thread for computation, how to the transfer the parameters?
        if thread == None:
            print("window_size is " + str(window_size) + "forget_degree is" + str(forget_degree))
            thread = Thread(target=blocking_task, args=(datasetName, window_size,))
            thread.start()
        TSclass = request.form['TSclass']
    return render_template('hello.html',bokS=bokeh_script, bokeh_server=bokeh_server, pl_conceptDrift = pl_conceptDrift)

def plot_dataset():
    '''data_directory = "/Users/Jingwei/PycharmProjects/distributed_use/venv/TestDataset/UCR_TS_Archive_2015"
    datasetName = "/FordA/FordA_TRAIN"
    list_timeseries = util.load_dataset(data_directory+datasetName)'''
    plot_window = figure(plot_height=150, plot_width=500, title='New Incoming TS micro-batch')
    plot_all = figure(plot_height=150, plot_width=500, title='All historical TS')
    plot_window.axis.visible = False
    plot_all.axis.visible = False

    source = AjaxDataSource(data_url='http://127.0.0.1:5000/ConceptDrift/', polling_interval=1000, mode='replace')
    source.data = dict(inputTSBatch=[], TS_set=[])
    def deserialize(data_string):
        data_set = data_string.split(';')
        data_list = []
        print("data_set is: " + str(data_set))
        for data in data_set:
            print("data is: " + data)
            data_set.append([int(i) for i in data[1:-1].split(',')])
        return data_list
    if len(source.data['inputTSBatch']) !=0:
        inputTSBatch = deserialize(source.data['inputTSBatch'][0])
        TS_set = deserialize(source.data['TS_set'][0])
        for ts_w in inputTSBatch:
            x = range(len(ts_w.timeseries))
            y = ts_w.timeseries
            plot_window.line(x, y, line_width=1)

        for ts_history in TS_set:
            x = range(len(ts_history.timeseries))
            y = ts_history.timeseries
            plot_all.line(x, y, line_width=1)

    '''global datasetName
    list_timeseries = util.load_dataset(datasetName)
    name_dataset = {k: v for ds in list_timeseries for k, v in ds.items()}
    dataset_list = list(name_dataset.values())
    #plot_window: input_TSBatch
    #plot_all: TS_set in "ISETS_Web_backend", how to extract the value? refer to a function which returns an object
    plot_window = figure(plot_height=150, plot_width=500, title='New Incoming TS micro-batch')
    plot_all = figure(plot_height=150, plot_width=500, title='All historical TS')

    plot_window.axis.visible = False
    plot_all.axis.visible = False
    #get the window size
    for ts in dataset_list[:2]:
        x = range(len(ts.timeseries))
        y = ts.timeseries
        plot_window.line(x, y, line_width=1)
    for ts in dataset_list[:50]:
        x = range(len(ts.timeseries))
        y = ts.timeseries
        plot_all.line(x, y, line_width=1)'''
    plot = gridplot([[plot_window], [plot_all]])
    script, div = components(plot)
    return script, div

'''def plot_conceptDrift():
    loss_df = pd.read_csv("~/Desktop/ISMAP_results/k10_w20_stack10_loss_avgtest.csv")
    t_stamp = loss_df["t_stamp"].tolist()
    avg_loss = loss_df["avg_loss"].tolist()
    loss_batch = loss_df["loss_batch"].tolist()
    x_drift = []
    y_drift = []
    nan = float('nan')
    for idx, loss in enumerate(loss_batch):
        if loss > avg_loss[idx]:
            y_drift.append([1])
        else:
            y_drift.append([nan])
    plot = figure(plot_height=300, plot_width=500, x_range=(0, 2000))
    plot.line(t_stamp, avg_loss, legend="avg_loss", line_color="red", line_width=2)
    plot.line(t_stamp, loss_batch, legend="loss_batch", line_color="blue", line_width=2)
    plot.line(t_stamp, y_drift, legend="concept drift area", line_color="orange", line_width=6)
    #radio_button_group = RadioButtonGroup(labels=["Option 1", "Option 2", "Option 3"], active=0)

    script, div = components(plot)
    return script, div'''

def plot_conceptDrift():
    # "append" mode is used to output the concatenated data
    source = AjaxDataSource(data_url='http://127.0.0.1:5000/ConceptDrift/', polling_interval=1000, mode='append')
    source.data = dict(t_stamp=[], drift_num=[], avg_loss=[], loss_batch=[], label_avg_loss=[], label_loss_batch=[],
                       label_concept_drift=[])
    plot = figure(plot_height=300, plot_width=500, x_range=(0, 2000), y_range=(0, 1.1))
    plot.line('t_stamp', 'avg_loss', source=source, line_color="red", legend="label_avg_loss", line_width=2)
    plot.line('t_stamp', 'loss_batch', source=source, line_color="blue", legend="label_loss_batch", line_width=2)
    plot.square('t_stamp', 'drift_num', source=source, color="orange", legend="label_concept_drift", size=5)
    script, div = components(plot)
    return script, div

    #script, div = components(widgetbox(radio_button_group))
    #return components(widgetbox(radio_button_group)), components(plot)

if __name__ == "__main__":
    app.run()
