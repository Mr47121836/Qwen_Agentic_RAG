# 三、快速开始

## 1. 环境要求

### 必备环境
- **Python 3.12** 或更高版本
- **Miniconda/Anaconda** - Python环境管理工具
- **Ollama** - 用于本地部署大模型
- **FAISS** - 向量数据库库

### 推荐配置
- **NVIDIA GPU 24GB** (推荐配置，但非必需)
- 足够的内存和存储空间

## 2. 虚拟环境配置

### 2.1 使用 Conda 管理环境（推荐）

Conda 是一个开源的包管理器和环境管理系统，特别适合科学计算和机器学习项目。

#### 1. 安装 Miniconda：

**Windows 用户**：
1. 访问 [Miniconda官网](https://docs.conda.io/en/latest/miniconda.html)
2. 下载 Windows 64位安装程序
3. 运行安装程序并按照提示安装

**Linux/Mac 用户**：
```bash
# 下载 Miniconda 安装脚本（以 Linux 64位为例）
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 运行安装脚本
bash Miniconda3-latest-Linux-x86_64.sh

# 按照提示完成安装，通常需要重启终端或运行
source ~/.bashrc  # 或 source ~/.zshrc
```

**验证安装**：
```bash
conda --version
```

#### 2. 创建虚拟环境：
```bash
# 创建名为 rag 的虚拟环境，指定 Python 3.12
conda create -n rag python=3.12

# 激活虚拟环境
conda activate rag
```

#### 3. 安装项目依赖：
```bash
# 使用 pip 安装 requirements.txt 中的依赖
pip install -r requirements.txt

# 或者使用 conda 安装特定包（如果需要）
# conda install package_name
```

### 2.2 使用 Ollama 安装所需模型

#### Ollama 安装指南

首先确保 Ollama 已正确安装并运行，然后安装以下模型：

```bash
# 安装 Qwen3 模型（8B版本）
ollama pull qwen3:8b

# 安装嵌入模型
ollama pull bge-m3:latest
```

#### 可选：验证模型安装
```bash
# 查看已安装的模型
ollama list

# 运行模型测试
ollama run qwen3:8b "你好"
```

### 2.3 启动应用

```bash
# 确保在正确的 conda 环境中
conda activate tgltommy

# 启动 Streamlit 应用
streamlit run app.py --server.port 6006
```

启动后，在浏览器中访问：
```
http://localhost:6006
```

## 环境管理常用命令

### Conda 基本命令
```bash
# 查看所有环境
conda env list

# 激活环境
conda activate tgltommy

# 退出当前环境
conda deactivate

# 删除环境
conda env remove -n tgltommy

# 导出环境配置
conda env export > environment.yml

# 从配置文件创建环境
conda env create -f environment.yml
```

### 环境更新和维护
```bash
# 更新 conda 本身
conda update conda

# 更新环境中所有包
conda update --all

# 安装特定版本的包
conda install package_name=版本号
```


## 注意事项

1. **Conda 与 pip 的配合使用**：
   - 建议先用 conda 安装基础包
   - 再用 pip 安装 requirements.txt 中的特定包
   - 避免混合使用可能导致的依赖冲突

2. **GPU 支持**：
   - 如需 GPU 支持，可能需要额外安装 CUDA 相关包：
   ```bash
   conda install cudatoolkit=11.8
   ```

3. **磁盘空间**：
   - Conda 环境会占用一定磁盘空间
   - 模型文件较大，确保有足够存储空间

4. **网络问题**：
   - 国内用户可使用 Conda 镜像源加速下载：
   ```bash
   conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
   conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
   conda config --set show_channel_urls yes
   ```

5. **问题排查**：
   - 如遇环境问题，可尝试重建环境
   - 检查 Python 版本是否符合要求
   - 确保所有依赖版本兼容
