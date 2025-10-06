# BodyDataAnalyzer

AI-Syoujyo 角色卡片身体数据分析工具，基于XGBoost模型进行高精度身高预测和多维度审美分类。

## 功能特点

- 📏 **高精度身高预测**：基于54组校准数据训练的XGBoost模型，预测误差≤±0.3cm
- 👩‍🏫 **多维度审美分类**：该功能暂未实现，计划遵循"正常审美向"自动分类方案，后续将提供5标签组合（身高+围度+风格）
- 🚀 **批量处理**：支持对目录下所有角色卡片进行批量分析
- 💾 **结果导出**：将分析结果以JSON格式保存，方便后续处理和应用
- 🔍 **参数适配**：通过多重访问策略确保兼容不同版本的角色卡片数据结构

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/BodyDataAnalyzer.git
cd BodyDataAnalyzer
```

### 2. 安装依赖

项目基于Python 3.6+开发，需要安装以下依赖包：

```bash
pip install numpy xgboost scikit-learn joblib
```

或者使用requirements.txt（下一步创建）：

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行使用

最简单的使用方式是通过命令行直接分析角色卡片目录：

```bash
python BodyDataAnalyzer.py <角色卡片目录路径>
```

例如：

```bash
python BodyDataAnalyzer.py ../test_cards
```

### 分析结果

- 控制台会显示每张卡片的预测身高和审美分类标签
- 详细结果会保存为`analysis_results.json`文件，存放在被分析的目录中

JSON结果格式包含以下字段：
- `file_path`：卡片文件路径
- `file_name`：卡片文件名
- `success`：分析是否成功
- `height_cm`：预测身高（厘米）
- `height_category`：身高分类（萝莉/普妹/御姐）
- `character_name`：角色名称
- `aesthetic_classifications`：详细审美分类参数
- `combined_tag`：组合标签，方便后续应用

## 项目结构

```
BodyDataAnalyzer/
├── BodyDataAnalyzer.py  # 主程序文件，包含分析器实现
├── chara_loader/        # 角色卡加载器模块
│   ├── __init__.py      # 模块初始化
│   ├── AiSyoujyoCharaData.py  # AI少女角色卡加载器
│   ├── KoikatuCharaData.py    # 恋活角色卡加载器
│   └── funcs.py         # 辅助函数
├── height_xgb.pkl       # 预训练的XGBoost模型
├── .gitignore           # Git忽略文件配置
└── README.md            # 项目说明文档
```

## 模型说明

- 模型基于54组精确测量的校准数据训练
- 平均绝对误差（MAE）约为0.295cm
- 支持超界和负值shapeValue的处理

如果需要重新训练模型，可以使用内置的`train_and_save_model`函数，并提供自己的校准数据JSON文件。

## 训练数据工具

项目包含专门的训练数据处理工具，存放在`training_data`文件夹中。

### full_shapeValues.py

该工具用于从角色卡片中提取完整的33个shapeValue参数，并生成训练数据JSON文件。

#### 功能说明
- 从`measured_cards`目录读取角色卡片文件
- 提取每张卡片的完整33个shapeValue参数
- 从文件名中解析实际身高值（文件名格式应为"身高值.png"，如"148.3.png"）
- 生成包含文件名、实际身高和完整shapeValue的JSON文件

#### 使用方法

1. 将已测量身高的角色卡片放入`measured_cards`目录，并确保文件名格式为"身高值.png"
2. 运行以下命令：
   ```bash
   cd training_data
   python full_shapeValues.py
   ```
3. 程序会生成`full_shapeValues.json`文件，包含所有提取的训练数据

## 审美分类标准

遵循"正常审美向"自动分类方案，基于以下6个维度进行分类：

- **身高**：萝莉(<150cm)、普妹(150-170cm)、御姐(>170cm)
- **胸围**：微乳、适中、丰满
- **腰围**：纤细、标准、肉感
- **臀围**：小臀、匀称、翘臀
- **胸部柔软度**：硬挺、自然、柔软
- **肌肉量**：纤弱、健康、健美

输出标签组合顺序：身高+胸围+臀围+肌肉+柔软度

## 开发说明

### 添加新功能

1. 克隆仓库并创建新分支
2. 实现新功能或修复bug
3. 提交代码并创建Pull Request

### 注意事项

- 项目使用的XGBoost模型已预训练并保存在`height_xgb.pkl`文件中
- 角色卡加载器支持AI少女和恋活两个游戏的角色卡格式
- 对于无法提取参数的卡片，系统会使用合理的默认值进行分类展示

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件

## 致谢

- 感谢所有为项目提供校准数据的贡献者（slwold就是本人）
- 使用了XGBoost框架进行模型训练
- 参考了AI-Syoujyo CharaFile Web Editor 中的角色卡数据结构
- 感谢Facial-Data-Extractor项目，提供了角色卡中面部数据的提取方法，让我有了做下去的基础

## 更新日志

- **v1.0.0**：初始版本，实现身高预测和基础分类
- **v1.1.0**：增强参数提取能力，添加详细审美分类功能