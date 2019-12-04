# ISETS
## Incremental Shapelet Extraction from Streaming Time Series
<p align="right">-Jingwei ZUO, Karine ZEITOUNI, Yehia TAHER</p>
<p align="right">DAVID Lab, University of Versailles Saint-Quentin, Unverisy of Paris-Sacaly</p>

This web application is intended to provide users an intuitive understanding about the feature extraction process in a combined context of **Time Series** and **Data Streams**. With ISETS, users can monitor the occurence of Concept Drift and the Shapelet Ranking at different Time Points.

###[Project Page: Incremental and Adaptive Feature Exploration over Time Series Stream](https://github.com/JingweiZuo/TSStreamMining)

### Demo 1 -> [ISETS Tutorial](https://drive.google.com/file/d/1IIHi0nu89ZNpZWxeUAsuX7MzyquoJZ_o/view?usp=sharing)

### Demo 2 ->[ISETS and Adaptive Features](https://drive.google.com/open?id=1-7RpKNIdMLYUuv1Fg7X7IlJMUrmkKwAb)

### Configurations (demo)

- **Input File**: the name should be end with "Train.csv"
- **dataset_folder**: in each file, change the location of the datasets in the background. The selected input file will be saved/uploaded into this folder.
- **Data Augmentation**: refer to *preprocessing/TS_stream_preprocess.py*. As Shapelet-based methods (e.g., SMAP) are noise resistant, we put randomly the noise of random durations into the original TS data to augment the data volume. 

####Web application (demo)

- **ISETS_webapp.py**: main program, a web application based on Flask and Bokeh
- **ISETS_webbackend.py**: the program for adaptive shapelet extraction and Concept Drift detection
- **draw_adaptive_shapelets.py**: show the adaptive shapelets in the web interface
- **draw_TS_Stream.py**: show in real time the input TS instances in the stream

###Core algorithms

- **utils/**: the repository which contains the basic file operations and similairty measure functions
- **memory_block.py**: the caching mechanism including the computation of Matrix Profile for cached instance
- **SMAP_block.py**: Shapelet extraction on MAtrix Profile
- **evaluation_block.py**: the loss computation and the Concept Drift detection on TS Stream
- **adaptive_features/adaptive_features.py**: Concept Drift detection and adaptive feature extraction
- **ISMAP/ISAMP.py**: incremental Shapelet extraction on MAtrix Profile
