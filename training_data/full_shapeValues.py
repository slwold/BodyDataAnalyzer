import os
import json
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chara_loader.AiSyoujyoCharaData import AiSyoujyoCharaData

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 设置输入目录为项目根目录下的measured_cards
input_dir = os.path.join(project_root, 'measured_cards')
results = []

# 检查输入目录是否存在
if not os.path.exists(input_dir):
    print(f"错误: 找不到输入目录 '{input_dir}'")
    print("请确保在项目根目录下创建了measured_cards文件夹，并放入已测量身高的角色卡片")
    sys.exit(1)

print(f"正在从目录 '{input_dir}' 读取角色卡片...")

for fname in os.listdir(input_dir):
    if not fname.endswith('.png'):
        continue
    path = os.path.join(input_dir, fname)
    try:
        chara = AiSyoujyoCharaData.load(path)
        sv = chara.Custom["body"]["shapeValueBody"]
        results.append({
            "filename": fname,
            "actual_cm": float(fname.replace('.png', '')),  # 148.3.png -> 148.3
            "shapeValues": sv  # 全部 33 个值
        })
    except Exception as e:
        print(f"跳过 {fname}: {e}")

# 输出结果到training_data目录下的full_shapeValues.json
output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'full_shapeValues.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"✅ 已输出全部 {len(results)} 个角色卡片的 shapeValue 到 {output_file}")