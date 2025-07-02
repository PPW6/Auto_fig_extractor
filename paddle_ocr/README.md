
# 📖 PaddleOCR User Manual (including model download and directory structure)

This project implements text detection and recognition in images based on Paddlepaddle, using the [PaddleOCR V3](https://aistudio.baidu.com/modelsdetail/17/intro) model.

---

## 🔧 Install PaddlePaddle

Please install the corresponding version of PaddlePaddle according to whether you use GPU. For more instructions, see [Official installation page](https://www.paddlepaddle.org.cn/install/quick)。

### ✅ CPU Installation (Python 3.8~3.10 is recommended)

```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

### ✅ GPU installation (taking CUDA 11.7 as an example)

```bash
pip install paddlepaddle-gpu==2.5.2.post117 -f https://www.paddlepaddle.org.cn/whl/mkl/avx/stable.html
```

---

## 🚀 Clone and install PaddleOCR

```bash
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
pip install -r requirements.txt
```

---

## 📦 Download and configure the model (PaddleOCR V3)

Download the model file from the link below and unzip it to the `models/` directory:

| Model Type        | Model Name | Download link                                                                           |
|-------------------|--------|-----------------------------------------------------------------------------------------|
| Detection Model   | en_PP-OCRv3_det_slim_infer | [Click to download](https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_slim_infer.tar) |
| Recognition Model | en_PP-OCRv3_rec_slim_infer | [Click to download](https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar)      |

### 📁 Unzip and place the model

```bash
mkdir models
tar -xvf en_PP-OCRv3_det_slim_infer.tar -C models/
tar -xvf en_PP-OCRv3_rec_slim_infer.tar -C models/
```

The final directory structure should be as follows:

```
.
├── models/
│   ├── en_PP-OCRv3_det_slim_infer/
│   └── en_PP-OCRv3_rec_slim_infer/
└── ...
```

---

## 🖼️ Quick Experience

### Command line usage
```
! wget https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/dygraph/doc/imgs/11.jpg
! paddleocr --image_dir 11.jpg --use_angle_cls true
```

### After the execution is complete, the following results will be output in the terminal:
```
[[[28.0, 37.0], [302.0, 39.0], [302.0, 72.0], [27.0, 70.0]], ('纯臻营养护发素', 0.96588134765625)]
[[[26.0, 81.0], [172.0, 83.0], [172.0, 104.0], [25.0, 101.0]], ('产品信息/参数', 0.9113278985023499)]
[[[28.0, 115.0], [330.0, 115.0], [330.0, 132.0], [28.0, 132.0]], ('（45元/每公斤，100公斤起订）', 0.8843421936035156)]
......
```
