# Auto_FDE

![Supported Python versions](https://shields.mitmproxy.org/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Auto_FDE** (Automated Figure Data Extraction) is a pipeline designed for extracting structured data from scientific figures—especially plots related to copper alloys. It supports tasks such as figure classification, data point extraction, and legend-label alignment, enabling high-throughput dataset generation for materials informatics applications.

---

## 🚀 Getting Started

###  1. Install Dependencies

Install required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Inital corpus acquisition
```bash
python copper_article_archive.py
```
### Figure data extraction
```bash
python main.py
```

Data extraction is mainly divided into the following key steps
graph_classification.py It is based on regular rules to select graphs related to the conductivity and strength properties of copper alloys from the graph caption.
scatter.py It is based on heuristic rules to extract key data points of graphics
paddle_ocr/legend_name.py Cross-modal alignment of key graphic data and legend text based on color features

📁 Recommended Folder Structure
Create folders to store and manage data
```bash
mkdir input_graph input_html input_txt input_xml output_graph
```

**Citing**
----------------------
If you use this work (data or code), please cite the following work as appropriate:
```
Pei Y, Hua F, Hong Z, et al. Machine learning ready dataset of Cu-Cr alloys generated with automated figure data extraction. 2025.
```

**License**
----------------------
All source code is licensed under the MIT license.
