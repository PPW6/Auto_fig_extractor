
# Curve Data Extraction - Enhanced Version

This repository is based on the original automated curve data extraction project by [Baibakova, V., Elzouka, M., Lubner, S. et al. Optical emissivity dataset of multi-material heterogeneous designs generated with automated figure extraction. Sci Data 9, 589 (2022). https://doi.org/10.1038/s41597-022-01699-3](https://github.com/ViktoriiaBaib/curvedataextraction.git). Below is a simplified installation and usage guide.

---

## 🔧 Installation (Simplified)

### 1. Create and activate conda environment

```bash
conda create -n imgrec python=3.9
conda activate imgrec
```

### 2. Install dependencies

```bash
pip install tensorflow==2.7 protobuf==3.20.2 easyocr==1.7.1 opencv-python==4.6.0.66
```

### 3. Clone and install TF Object Detection API

```bash
git clone https://github.com/tensorflow/models.git
cd models/research
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .
python -m pip install .
python object_detection/builders/model_builder_tf2_test.py  # Check install
```

### 4. Download Pretrained Assets

Download from (https://drive.google.com/file/d/1e0UTKwhgJN9DuD2qYsLcWcKd6WomvRkl/view?usp=sharing) and place the files accordingly in:
- `inference_graph/`
- `training/`
- `images/`
- `utils/`

### 5. Run Extraction Pipeline

```bash
cd object_detection

# Run axis and legend detection
python object_detection_curves.py

# Run color decomposition
python color_decomposition_.py

# Run final processing
python final_achieve.py
```

---

✅ Modifications and Our Contributions
We made the following enhancements to improve robustness and accuracy:

✅ Reorganized the code into a modular and extensible pipeline.

✅ Introduced the origin_data class for automated batch processing of images and axis parsing.

✅ Improved error handling for axis recognition using EasyOCR with confidence scoring.

🔍 Specific Algorithmic Enhancements
Enhanced Color Decomposition Strategy:
In color_decomposition_, we proposed a novel color segmentation strategy based on region-wise recognition, improving curve separation in overlapping or noise-prone areas.

Robust Curve Extraction with Noise Filtering:
In final_achieve, we incorporated outlier removal and integrated a DBSCAN-based clustering approach to remove noise points, significantly enhancing the accuracy and clarity of extracted curves.

These contributions improve the system’s ability to handle complex plots with multiple overlapping curves or visual artifacts.

---

