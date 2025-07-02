📝 PaddleOCR 使用说明
本指南介绍如何安装 PaddleOCR 所需环境，并使用 PaddleOCR V3 模型进行文字识别。

📦 1. 安装 Paddle 框架
请根据你的系统和显卡情况（是否使用 GPU）安装对应版本的 PaddlePaddle 框架。

CPU 安装方式（推荐 Python 3.8~3.10）
bash
复制
编辑
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
GPU 安装方式（例如 CUDA 11.7）
bash
复制
编辑
pip install paddlepaddle-gpu==2.5.2.post117 -f https://www.paddlepaddle.org.cn/whl/mkl/avx/stable.html
可通过以下命令验证安装是否成功：

bash
复制
编辑
python -c "import paddle; print(paddle.__version__)"
📁 2. 下载并安装 PaddleOCR
（1）克隆官方仓库
bash
复制
编辑
git clone https://github.com/PaddlePaddle/PaddleOCR.git
cd PaddleOCR
（2）安装依赖
建议使用虚拟环境：

bash
复制
编辑
pip install -r requirements.txt
📂 3. 下载 PaddleOCR V3 模型
进入 PaddleOCR 模型库（或查阅 模型列表页面），下载如下模型并放入 models/ 目录：

模型类型	模型名	下载链接	保存位置
det 检测模型	ch_PP-OCRv3_det	下载地址	models/ch_PP-OCRv3_det_infer/
rec 识别模型	ch_PP-OCRv3_rec	下载地址	models/ch_PP-OCRv3_rec_infer/
方向分类器（可选）	cls 模型	下载地址	models/ch_ppocr_mobile_v2.0_cls_infer/

下载后使用如下方式解压：

bash
复制
编辑
mkdir -p models
tar -xvf ch_PP-OCRv3_det_infer.tar -C models/
tar -xvf ch_PP-OCRv3_rec_infer.tar -C models/
tar -xvf ch_ppocr_mobile_v2.0_cls_infer.tar -C models/
🚀 4. 使用 PaddleOCR 进行推理
可使用 tools/infer/predict_system.py 脚本，调用检测、识别和方向分类功能：

bash
复制
编辑
python tools/infer/predict_system.py \
    --det_model_dir=models/ch_PP-OCRv3_det_infer \
    --rec_model_dir=models/ch_PP-OCRv3_rec_infer \
    --cls_model_dir=models/ch_ppocr_mobile_v2.0_cls_infer \
    --image_dir=your_image.jpg \
    --use_angle_cls=true \
    --use_space_char=True \
    --lang=ch
📌 注意事项
推荐使用 Python 3.8~3.10。

若使用 GPU，请确保 CUDA 和 cuDNN 安装正确。

可修改 predict_system.py 脚本以实现批量处理、图像路径输入或结果保存功能。

📚 参考链接
PaddlePaddle 官网

PaddleOCR GitHub

PaddleOCR 文档中心
