# Auto_FDE

![Supported Python versions](https://shields.mitmproxy.org/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)

**Auto_FDE** (Automated Figure Data Extraction Tool) This study proposes an innovative integration strategy that combines heuristic rules, optical character recognition (OCR), and color feature-based cross-modal alignment to address the challenge of extracting high-quality, reliable, and relational data from figures in materials science literature. 

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

## 🔍 Key step

**Auto_FDE** performs a multi-step pipeline to convert scientific figures into machine learning–ready structured data:

- **`graph_classification.py`**  
  Identifies and selects figures related to *conductivity* and *strength* of copper alloys based on rule-based parsing of figure captions.

- **`scatter.py`**  
  Applies heuristic rules to extract key data points from original scientific plots.

- **`paddle_ocr/legend_name.py`**  
  Performs cross-modal alignment between figure data and legend text by leveraging PaddleOCR and color-based matching techniques.


📁 **Recommended Folder Structure**
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
