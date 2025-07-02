from pathlib import Path

# Markdown content
md_content = """# Automated Curve Data Extraction Tool

This tool automates the extraction of curve data from scientific figures, including axes detection, legend parsing, color decomposition, and cluster segmentation.

## 🔧 Installation Guide

### Part I: Setup Environment and Install Dependencies

1. **Create Conda Environment**:

```bash
conda create -n imgrec python=3.9
conda activate imgrec
conda install pip
