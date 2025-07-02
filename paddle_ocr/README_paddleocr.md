
# 📖 PaddleOCR 使用说明（含模型下载与目录结构）

本项目基于 [PaddleOCR](https://aistudio.baidu.com/modelsdetail/17/intro) 实现图像中的文字检测与识别，使用 PaddleOCR V3 模型。

---

## 🔧 安装 PaddlePaddle

请根据是否使用 GPU 安装相应版本的 PaddlePaddle。更多说明见 [官方安装页面](https://www.paddlepaddle.org.cn/install/quick)。

### ✅ CPU 安装（推荐使用 Python 3.8~3.10）

```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

### ✅ GPU 安装（以 CUDA 11.7 为例）

```bash
pip install paddlepaddle-gpu==2.5.2.post117 -f https://www.paddlepaddle.org.cn/whl/mkl/avx/stable.html
```

---

## 🚀 克隆并安装 PaddleOCR

```bash
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
pip install -r requirements.txt
```

---

## 📦 下载并配置模型（PaddleOCR V3）

从下方链接下载模型文件并解压到 `models/` 目录：

| 模型类型 | 模型名 | 下载地址 |
|----------|--------|----------|
| 检测模型 | en_PP-OCRv3_det_slim_infer | [点击下载](https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_slim_infer.tar) |
| 识别模型 | en_PP-OCRv3_rec_slim_infer | [点击下载](https://paddleocr.bj.bcebos.com/PP-OCRv3/english/en_PP-OCRv3_det_infer.tar) |

### 📁 解压并放置模型

```bash
mkdir models
tar -xvf en_PP-OCRv3_det_slim_infer.tar -C models/
tar -xvf en_PP-OCRv3_rec_slim_infer.tar -C models/
```

最终的目录结构应如下：

```
.
├── models/
│   ├── en_PP-OCRv3_det_slim_infer/
│   └── en_PP-OCRv3_rec_slim_infer/
└── ...
```

---

## 🖼️ 快速体验

# 命令行使用

! wget https://raw.githubusercontent.com/PaddlePaddle/PaddleOCR/dygraph/doc/imgs/11.jpg
! paddleocr --image_dir 11.jpg --use_angle_cls true

# 运行完成后，会在终端输出如下结果：

[[[28.0, 37.0], [302.0, 39.0], [302.0, 72.0], [27.0, 70.0]], ('纯臻营养护发素', 0.96588134765625)]
[[[26.0, 81.0], [172.0, 83.0], [172.0, 104.0], [25.0, 101.0]], ('产品信息/参数', 0.9113278985023499)]
[[[28.0, 115.0], [330.0, 115.0], [330.0, 132.0], [28.0, 132.0]], ('（45元/每公斤，100公斤起订）', 0.8843421936035156)]
......
