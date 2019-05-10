''' Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Use the ``bokeh serve`` command to run the example by executing:
    bokeh serve sliders.py
at your command prompt. Then navigate to the URL
    http://localhost:5006/sliders
in your browser.
'''
import numpy as np
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, TextInput, Button, Dropdown, CheckboxButtonGroup, RadioButtonGroup
from bokeh.plotting import figure

# Set up widgets
menu_T = [("T.Stamp 160", "T.Stamp 160"), ("T.Stamp 180", "T.Stamp 180"), ("T.Stamp 200", "T.Stamp 200")]
menu_C = [("Class 1", "Class 1"), ("Class 2", "Class 2"), ("Class 3", "Class 3")]
dropdown1 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown2 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)
dropdown3 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown4 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)
dropdown5 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown6 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)

def update_dropdown1(attrname, old, new):
    dropdown1.label = dropdown1.value
def update_dropdown2(attrname, old, new):
    dropdown2.label = dropdown2.value
def update_dropdown3(attrname, old, new):
    dropdown3.label = dropdown3.value
def update_dropdown4(attrname, old, new):
    dropdown4.label = dropdown4.value
def update_dropdown5(attrname, old, new):
    dropdown5.label = dropdown5.value
def update_dropdown6(attrname, old, new):
    dropdown6.label = dropdown6.value
dropdown1.on_change('value', update_dropdown1)
dropdown2.on_change('value', update_dropdown2)
dropdown3.on_change('value', update_dropdown3)
dropdown4.on_change('value', update_dropdown4)
dropdown5.on_change('value', update_dropdown5)
dropdown6.on_change('value', update_dropdown6)
# Set up layouts and add to document
input1 = widgetbox(dropdown1, dropdown2)
input2 = widgetbox(dropdown3, dropdown4)
input3 = widgetbox(dropdown5, dropdown6)

# Set up data
shap_df_k10 = pd.read_csv("~/Desktop/ISMAP_results/k10_w10_stack02_shap.csv")
shap_df_k10_stack10 = pd.read_csv("~/Desktop/ISMAP_results/k10_w20_stack10_shap.csv")
def select_shapelet(shap_df, t_stamp, Class):
    return shap_df[shap_df["t_stamp"]==t_stamp][shap_df["shap.Class"]==Class]
def draw_shapelet(shap_df, firstK, t_stamp, Class):
    shap_subseq = shap_df['shap.subseq'].tolist()
    shap_score = shap_df['shap.score'].tolist()
    colors = [
        "#75968f", "red", "blue", "green", "orange",
        "black"
    ]
    plot = figure(plot_height=200, plot_width=300, title='Shapelet (Feature) Ranking at Time '+str(t_stamp), x_range=(0, 100), y_range=(0, 30))
    plot.yaxis.visible = False
    i = 1
    for shap in shap_subseq[:firstK]:
        shap_list = shap[1:-1].split()
        shap_list = [float(val)+ 30-5*i for val in shap_list]
        x = list(range(0, len(shap_list)))
        plot.line(x, shap_list, legend="Score: "+ str(round(shap_score[i-1],3)), line_width=2, line_color=colors[i])
        plot.legend.label_text_font_size = '6pt'
        plot.legend.spacing = -3
        i += 1
        #plt.savefig("/Users/Jingwei/Downloads/Shapelet_Time"+str(t_stamp)+"_Class"+str(Class)[:-2]+".eps")
    return plot

plot1 = draw_shapelet(select_shapelet(shap_df_k10, 160, 1), 5, 160, 1)
plot2 = draw_shapelet(select_shapelet(shap_df_k10, 200, 1), 5, 200, 1)
plot3 = draw_shapelet(select_shapelet(shap_df_k10, 200, -1), 5, 200, -1)


curdoc().add_root(row(column(input1, plot1, width=370), column(input2, plot2, width=370), column(input3, plot3, width=370)))
curdoc().title = "Sliders"
