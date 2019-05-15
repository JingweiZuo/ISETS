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
from bokeh.layouts import row, column, widgetbox, gridplot
from bokeh.models import ColumnDataSource, Legend
from bokeh.models.widgets import Slider, TextInput, Button, Dropdown, CheckboxButtonGroup, RadioButtonGroup
from bokeh.plotting import figure

# Set up widgets
#menu_T = [('160', "TStamp 160"), ('180', "TStamp 180"), ('200', "TStamp 200")]
t_stampList = range(30, 1320, 10)
menu_T = [(str(t), "TStamp "+str(t)) for t in t_stampList]
menu_C = [('1.0', "Class 1"), ('-1.0', "Class -1")]
dropdown1 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown2 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)
dropdown3 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown4 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)
dropdown5 = Dropdown(label="Select Time Stamp", button_type="success", menu=menu_T)
dropdown6 = Dropdown(label="Select Class", button_type="primary", menu=menu_C)
class_1 = '1.0'
class_2 = '1.0'
class_3 = '-1.0'
t_stamp1 = '160'
t_stamp2 = '200'
t_stamp3 = '200'

# Set up data
shap_df_k10 = pd.read_csv("~/Desktop/ISMAP_results/k10_w10_stack02_shap.csv")
shap_df_k10_stack10 = pd.read_csv("~/Desktop/ISMAP_results/k10_w20_stack10_shap.csv")



plot1 = figure(plot_height=200, plot_width=300, title='Shapelet (Feature) Ranking', x_range=(0, 100), y_range=(0, 30))
plot2 =figure(plot_height=200, plot_width=300, title='Shapelet (Feature) Ranking', x_range=(0, 100), y_range=(0, 30))
plot3 = figure(plot_height=200, plot_width=300, title='Shapelet (Feature) Ranking', x_range=(0, 100), y_range=(0, 30))
plot1.yaxis.visible = False
plot2.yaxis.visible = False
plot3.yaxis.visible = False
legend1 = Legend(items=[], location='top_right', spacing=-3, label_text_font_size='6pt')
legend2 = Legend(items=[], location='top_right', spacing=-3, label_text_font_size='6pt')
legend3 = Legend(items=[], location='top_right', spacing=-3, label_text_font_size='6pt')
plot1.add_layout(legend1, 'right')
plot2.add_layout(legend2, 'right')
plot3.add_layout(legend3, 'right')
def select_shapelet(shap_df, t_stamp, Class):
    return shap_df[shap_df["t_stamp"]==int(t_stamp)][shap_df["shap.Class"]==float(Class)]
def draw_shapelet(shap_df, firstK, t_stamp, Class, plot):
    shap_subseq = shap_df['shap.subseq'].tolist()
    shap_score = shap_df['shap.score'].tolist()

    colors = [
        "#75968f", "red", "blue", "green", "orange",
        "black"
    ]
    i = 1
    r = []
    for shap in shap_subseq[:firstK]:
        shap_list = shap[1:-1].split()
        shap_list = [float(val)+ 30-5*i for val in shap_list]
        x = list(range(0, len(shap_list)))

        plot.line(x, shap_list, line_width=2, line_color=colors[i], name=str(t_stamp)+str(Class))
        r.append(plot.line(x, shap_list, line_width=2, line_color=colors[i]))
        #plot1.legend.label_text_font_size = '6pt'
        #plot.legend.spacing = -3
        i += 1
        #plt.savefig("/Users/Jingwei/Downloads/Shapelet_Time"+str(t_stamp)+"_Class"+str(Class)[:-2]+".eps")
    #shap_list2 = [float(val) + 30 - 5 * i for val in shap_list].copy()
    plot.legend.items = [
        (str(round(shap_score[0],3)), [r[0]]),
        (str(round(shap_score[1],3)), [r[1]]),
        (str(round(shap_score[2],3)), [r[2]]),
        (str(round(shap_score[3],3)), [r[3]]),
        (str(round(shap_score[4],3)), [r[4]]),
    ]
    return plot

def update_dropdown1(attrname, old, new):
    global t_stamp1
    dropdown1.label = dropdown1.value
    t_stamp1 = dropdown1.value.split()[1]
def update_dropdown2(attrname, old, new):
    global class_1, t_stamp1, plot1
    dropdown2.label = dropdown2.value
    class_1 = dropdown2.value.split()[1]
    plot1 = draw_shapelet(select_shapelet(shap_df_k10, t_stamp1, class_1), 5, t_stamp1, class_1, plot1)
def update_dropdown3(attrname, old, new):
    global t_stamp2
    dropdown3.label = dropdown3.value
    t_stamp2 = dropdown3.value.split()[1]
def update_dropdown4(attrname, old, new):
    global class_2, t_stamp2, plot2
    dropdown4.label = dropdown4.value
    class_2 = dropdown4.value.split()[1]
    plot2 = draw_shapelet(select_shapelet(shap_df_k10, t_stamp2, class_2), 5, t_stamp2, class_2, plot2)
def update_dropdown5(attrname, old, new):
    global t_stamp3
    dropdown5.label = dropdown5.value
    t_stamp3 = dropdown5.value.split()[1]
def update_dropdown6(attrname, old, new):
    global class_3, t_stamp3, plot3
    dropdown6.label = dropdown6.value
    class_3 = dropdown6.value.split()[1]
    plot3 = draw_shapelet(select_shapelet(shap_df_k10, t_stamp3, class_3), 5, t_stamp3, class_3, plot3)
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

curdoc().add_root(row(column(input1, plot1, width=370), column(input2, plot2, width=370), column(input3, plot3, width=370)))
curdoc().title = "Sliders"
