from flask import Flask, flash, redirect, render_template, request, session, abort
#from bokeh.embed import autoload_server
from bokeh.embed import server_document, components
from werkzeug.utils import secure_filename
from bokeh.plotting import figure
from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.models import ColumnDataSource, AjaxDataSource
from bokeh.models.widgets import Slider, TextInput, Button, Dropdown, CheckboxButtonGroup, RadioButtonGroup
from bokeh.io import show, curdoc

import pandas as pd
import utils.utils as util

app = Flask(__name__)

@app.route("/")
def hello():
    #script=autoload_server(model=None,app_path="/bokeh-sliders",url="http://localhost:5006")
    bokeh_script=server_document("http://localhost:5006/bokeh-sliders")

    pl_dataset = plot_dataset()
    pl_conceptDrift = plot_conceptDrift()
    global datasetName
    #webtitle = "ISETS: Incremental Shapelet Extraction fromStreaming Time Series"
    if request.method == 'POST':
        file = request.files['file']
        datasetName = file.filename
        file.save(datasetName)
    return render_template('hello.html',bokS=bokeh_script, pl_dataset = pl_dataset, pl_conceptDrift = pl_conceptDrift)

def plot_dataset():
    data_directory = "/Users/Jingwei/PycharmProjects/distributed_use/venv/TestDataset/UCR_TS_Archive_2015"
    datasetName = "/FordA/FordA_TRAIN"
    list_timeseries = util.load_dataset(data_directory+datasetName)
    name_dataset = {k: v for ds in list_timeseries for k, v in ds.items()}
    dataset_list = list(name_dataset.values())
    plot_window = figure(plot_height=150, plot_width=500, title='New Incoming TS micro-batch')
    plot_all = figure(plot_height=150, plot_width=500, title='All historical TS')

    plot_window.axis.visible = False
    plot_all.axis.visible = False
    for ts in dataset_list[:2]:
        x = range(len(ts.timeseries))
        y = ts.timeseries
        plot_window.line(x, y, line_width=1)
    for ts in dataset_list[:50]:
        x = range(len(ts.timeseries))
        y = ts.timeseries
        plot_all.line(x, y, line_width=1)
    plot = gridplot([[plot_window], [plot_all]])
    script, div = components(plot)
    return script, div

def plot_conceptDrift():
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
    return script, div

    #script, div = components(widgetbox(radio_button_group))
    #return components(widgetbox(radio_button_group)), components(plot)

if __name__ == "__main__":
    app.run()
