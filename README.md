# BodyDataAnalyzer

AI-Syoujyo 角色卡片身体数据分析工具，基于XGBoost模型进行高精度身高预测和多维度审美分类。

## 功能特点

- 📏 **高精度身高预测**：基于54组校准数据训练的XGBoost模型，预测误差≤±0.3cm
- 👩‍🏫 **《星穹铁道》特化身高分类**：七档身高分类体系（微型幼幼、幼年、少年、青年、成年、高大魁梧、巨型伟岸）
- 📁 **自动分类到文件夹**：根据身高分类自动将角色卡片移动或复制到对应文件夹
- 🔄 **文件恢复功能**：支持将已分类的文件恢复到原始位置
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

#### 1. 分析并分类角色卡片

最简单的使用方式是通过命令行直接分析角色卡片目录并按身高自动分类：

```bash
python BodyDataAnalyzer.py <角色卡片目录路径>
```

例如，分析并分类当前目录下的test_cards文件夹中的角色卡片：

```bash
python BodyDataAnalyzer.py ../test_cards
```

执行后，程序会：
1. 扫描指定目录下所有PNG格式的角色卡片
2. 分析每张卡片并预测身高
3. 按《星穹铁道》特化七档身高分类体系自动创建对应的分类文件夹
4. 将角色卡片移动到对应的分类文件夹中
5. 生成恢复信息文件，便于后续恢复到分类前状态

#### 2. 恢复文件（后悔药功能）

如果对分类结果不满意，可以使用后悔药功能将文件恢复到分类前的原始位置：

```bash
python BodyDataAnalyzer.py restore <分类输出目录>
```

例如，恢复之前分类到test_cards/categorized目录中的文件：

```bash
python BodyDataAnalyzer.py restore ../test_cards/categorized
```

### 分析结果

- 控制台会显示每张卡片的预测身高和审美分类标签
- 详细结果会保存为`analysis_results.json`文件，存放在被分析的目录中
- 恢复信息会保存为`recovery_info.json`文件，存放在分类输出目录中

JSON结果格式包含以下字段：
- `file_path`：卡片文件路径
- `file_name`：卡片文件名
- `success`：分析是否成功
- `height_cm`：预测身高（厘米）
- `height_category`：身高分类
- `character_name`：角色名称
- `error`：如果分析失败，包含错误信息
- `move_status`或`copy_status`：文件移动或复制状态
- `dest_path`：目标文件路径

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

## 《星穹铁道》特化身高分类标准

HeightClassifier分支实现了《星穹铁道》特化的七档身高分类体系：

- **幼幼**：<130cm
- **玲珑**：130-155cm
- **少年**：155-160cm
- **青年**：160-175cm
- **成年**：175-185cm
- **魁梧**：185-210cm
- **伟岸**：>210cm

## 自动分类到文件夹功能

HeightClassifier分支提供了将角色卡片按身高分类自动整理到文件夹的功能：

- 支持移动（move）和复制（copy）两种模式
- 自动创建对应的身高分类文件夹
- 记录文件操作信息，便于后续恢复
- 包含错误处理和文件覆盖避免机制

## 文件恢复功能

HeightClassifier分支支持将已分类的文件恢复到原始位置：

- 通过recovery_info.json记录的操作信息进行恢复
- 支持目标目录创建和文件冲突处理
- 提供恢复成功/失败统计和进度更新

## 测试脚本

HeightClassifier分支包含两个测试脚本：

- **test_categorization.py**：测试自动分类到文件夹功能
- **test_restore.py**：测试文件恢复功能

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

- **v1.2.0**：《星穹铁道》特化版本
  - 实现了七档身高分类体系（微型幼幼、幼年、少年、青年、成年、高大魁梧、巨型伟岸）
  - 添加了自动分类到文件夹功能，支持移动和复制两种模式
  - 新增文件恢复功能（后悔药），可将已分类文件恢复到原始位置
  - 优化了角色名称提取逻辑，提升不同版本角色卡的兼容性
  - 增加了测试脚本：test_categorization.py和test_restore.py
- **v1.1.0**：增强参数提取能力，添加详细审美分类功能
- **v1.0.0**：初始版本，实现身高预测和基础分类
