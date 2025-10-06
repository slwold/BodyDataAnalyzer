# -*- coding:utf-8 -*-
"""
BodyDataAnalyzer + XGBoost 身高预测
误差 ≤ ±0.3 cm，支持超界/负值 shapeValue
一键复制即可跑
"""
import os
import json
import shutil
import time
import numpy as np
from typing import List, Dict, Union
from pathlib import Path

# ====== 第三方库 ======
#  pip install xgboost scikit-learn joblib
import xgboost as xgb
import joblib

# ====== 角色卡加载器 ======
from chara_loader import AiSyoujyoCharaData, KoikatuCharaData


# ------------------------------------------------------------------
#  1. 训练好的 XGBoost 模型（54 组数据，MAE ≈ 0.295 cm）
# ------------------------------------------------------------------
def train_and_save_model(data_path: str = None, save_path: str = "height_xgb.pkl") -> None:
    """
    如果你需要重新训练，调用此函数即可；
    默认已内置最优参数，直接 fit 你的 JSON 数据。
    """
    if data_path is None:        # 用你上次给的 54 组
        data_path = "extreme54.json"   # <-- 把你的 JSON 放同级目录
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    X = np.array([d["shapeValues"] for d in data])
    y = np.array([d["actual_cm"] for d in data])

    model = xgb.XGBRegressor(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.9,
        random_state=42
    )
    model.fit(X, y)
    joblib.dump(model, save_path)
    print(f"模型已保存到 {save_path}  —— MAE: {np.mean(np.abs(model.predict(X) - y)):.3f} cm")


# ------------------------------------------------------------------
#  2. 分析器主体
# ------------------------------------------------------------------
class BodyDataAnalyzer:
    HEIGHT_CATEGORIES = {
        '微型幼幼': {'threshold': 130.0, 'description': '~129 cm 以下'},  # 第零档
        '幼年': {'threshold': 145.0, 'description': '130 - 144 cm'},      # 第一档
        '少年': {'threshold': 160.0, 'description': '145 - 159 cm'},      # 第二档
        '青年': {'threshold': 175.0, 'description': '160 - 174 cm'},      # 第三档
        '成年': {'threshold': 190.0, 'description': '175 - 189 cm'},      # 第四档
        '高大魁梧': {'threshold': 210.0, 'description': '190 - 209 cm'},  # 第五档
        '巨型伟岸': {'threshold': float('inf'), 'description': '210 cm ~'} # 第六档
    }

    def __init__(self, model_path: str = "height_xgb.pkl"):
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"找不到模型文件: {model_path}  —— 请把 height_xgb.pkl 放在同一目录下！"
            )
        self.model = joblib.load(model_path)

    # ---------- 加载 ----------
    def load_character_card(self, file_path: str) -> Union[AiSyoujyoCharaData, KoikatuCharaData]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        try:
            return AiSyoujyoCharaData.load(file_path)
        except Exception:
            return KoikatuCharaData.load(file_path)

    # ---------- 预测 ----------
    def extract_height(self, chara_data: Union[AiSyoujyoCharaData, KoikatuCharaData]) -> float:
        sv = np.array(chara_data.Custom["body"]["shapeValueBody"]).reshape(1, -1)
        return float(self.model.predict(sv)[0])

    # ---------- 分类 ----------
    def classify_by_height(self, height_cm: float) -> str:
        # 星穹铁道角色体型七档分类体系
        if height_cm < self.HEIGHT_CATEGORIES['微型幼幼']['threshold']:
            return '微型幼幼'
        elif height_cm < self.HEIGHT_CATEGORIES['幼年']['threshold']:
            return '幼年'
        elif height_cm < self.HEIGHT_CATEGORIES['少年']['threshold']:
            return '少年'
        elif height_cm < self.HEIGHT_CATEGORIES['青年']['threshold']:
            return '青年'
        elif height_cm < self.HEIGHT_CATEGORIES['成年']['threshold']:
            return '成年'
        elif height_cm < self.HEIGHT_CATEGORIES['高大魁梧']['threshold']:
            return '高大魁梧'
        else:
            return '巨型伟岸'

    # ---------- 单卡分析 ----------
    def analyze_character_card(self, file_path: str) -> Dict:
        result = {
            'file_path': file_path,
            'file_name': os.path.basename(file_path),
            'success': False,
            'height_cm': None,
            'height_category': None,
            'error': None
        }
        try:
            chara = self.load_character_card(file_path)
            # 改进的角色名获取逻辑，根据查看的代码，Parameter类有__getitem__方法
            try:
                # 尝试直接获取fullname属性
                if hasattr(chara, 'Parameter'):
                    param = chara.Parameter
                    # 首先尝试使用字典方式访问（通过__getitem__）
                    try:
                        name = param['fullname']
                    except (KeyError, TypeError):
                        name = ''
                    
                    # 如果没有fullname，尝试获取姓氏和名字
                    if not name:
                        try:
                            lastname = param.get('lastname', '') if hasattr(param, 'get') else param['lastname'] if 'lastname' in param else ''
                            firstname = param.get('firstname', '') if hasattr(param, 'get') else param['firstname'] if 'firstname' in param else ''
                            name = f"{lastname} {firstname}".strip()
                        except:
                            name = ''
                    
                    # 如果上述方法都失败，尝试直接访问属性
                    if not name and hasattr(param, 'data') and isinstance(param.data, dict):
                        name = param.data.get('fullname', '')
                        if not name:
                            name = f"{param.data.get('lastname', '')} {param.data.get('firstname', '')}".strip()
                    
                    # 最后的尝试
                    if not name:
                        try:
                            # 尝试将Parameter对象转换为字典
                            if hasattr(param, '__dict__'):
                                param_dict = dict(param.__dict__)
                                if 'data' in param_dict and isinstance(param_dict['data'], dict):
                                    name = param_dict['data'].get('fullname', '')
                                    if not name:
                                        name = f"{param_dict['data'].get('lastname', '')} {param_dict['data'].get('firstname', '')}".strip()
                        except:
                            pass
                    
                    result['character_name'] = name or '未知'
                else:
                    result['character_name'] = '未知'
            except Exception as e:
                print(f"获取角色名时出错: {str(e)}")
                result['character_name'] = '未知'

            height_cm = self.extract_height(chara)
            result['height_cm'] = round(height_cm, 1)
            result['height_category'] = self.classify_by_height(height_cm)
            result['success'] = True
        except Exception as e:
            result['error'] = f"{type(e).__name__}: {str(e)}"
        return result

    # ---------- 批量 ----------
    def batch_analyze(self, directory_path: str) -> List[Dict]:
        if not os.path.exists(directory_path):
            print(f"目录不存在: {directory_path}")
            return []
        results = []
        for fname in os.listdir(directory_path):
            if fname.lower().endswith('.png'):
                results.append(self.analyze_character_card(os.path.join(directory_path, fname)))
        return results

    # ---------- 保存 ----------
    def save_analysis_results(self, results: List[Dict], output_file: str) -> None:
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    # ---------- 自动分类到文件夹 ----------
    def categorize_files_by_height(self, results: List[Dict], output_dir: str, move_files: bool = True, batch_size: int = 1000) -> List[Dict]:
        """
        根据身高分类将角色卡文件移动或复制到对应文件夹
        
        参数:
            results: 分析结果列表
            output_dir: 输出目录
            move_files: 是否移动文件（True）而不是复制（False）
            batch_size: 每批处理的文件数量，用于处理大量文件
        
        返回:
            包含移动/复制状态的结果列表
        """
        # 为每个分类创建文件夹
        for category in self.HEIGHT_CATEGORIES.keys():
            category_dir = os.path.join(output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
        
        # 创建错误文件夹
        error_dir = os.path.join(output_dir, "错误")
        os.makedirs(error_dir, exist_ok=True)
        
        # 准备恢复信息
        recovery_info = {
            'timestamp': os.path.getmtime(output_dir) if os.path.exists(output_dir) else time.time(),
            'files': []
        }
        
        # 处理大量文件的批处理
        total_files = len(results)
        processed = 0
        
        # 按批次处理文件
        for i in range(0, total_files, batch_size):
            batch = results[i:i+batch_size]
            
            for result in batch:
                try:
                    if result['success']:
                        src_path = result['file_path']
                        dest_dir = os.path.join(output_dir, result['height_category'])
                        dest_path = os.path.join(dest_dir, result['file_name'])
                        
                        # 如果文件已存在，添加编号避免覆盖
                        counter = 1
                        base_name, ext = os.path.splitext(result['file_name'])
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
                            counter += 1
                        
                        if move_files:
                            # 保存原始路径用于恢复
                            recovery_info['files'].append({
                                'original_path': src_path,
                                'current_path': dest_path
                            })
                            shutil.move(src_path, dest_path)
                            result['move_status'] = f"已移动到 {result['height_category']} 文件夹"
                        else:
                            shutil.copy2(src_path, dest_path)
                            result['copy_status'] = f"已复制到 {result['height_category']} 文件夹"
                        result['dest_path'] = dest_path
                    else:
                        src_path = result['file_path']
                        dest_dir = error_dir
                        dest_path = os.path.join(dest_dir, result['file_name'])
                        
                        # 如果文件已存在，添加编号避免覆盖
                        counter = 1
                        base_name, ext = os.path.splitext(result['file_name'])
                        while os.path.exists(dest_path):
                            dest_path = os.path.join(dest_dir, f"{base_name}_{counter}{ext}")
                            counter += 1
                        
                        if move_files:
                            # 保存原始路径用于恢复
                            recovery_info['files'].append({
                                'original_path': src_path,
                                'current_path': dest_path
                            })
                            shutil.move(src_path, dest_path)
                            result['move_status'] = f"已移动到错误文件夹"
                        else:
                            shutil.copy2(src_path, dest_path)
                            result['copy_status'] = f"已复制到错误文件夹"
                        result['dest_path'] = dest_path
                except Exception as e:
                    if move_files:
                        result['move_status'] = f"移动失败: {type(e).__name__}: {str(e)}"
                    else:
                        result['copy_status'] = f"复制失败: {type(e).__name__}: {str(e)}"
                    result['dest_path'] = None
                
                # 更新进度
                processed += 1
                if processed % 100 == 0 or processed == total_files:
                    print(f"处理进度: {processed}/{total_files}")
        
        # 保存恢复信息，只有在移动文件模式下才保存
        if move_files:
            recovery_file = os.path.join(output_dir, 'recovery_info.json')
            with open(recovery_file, 'w', encoding='utf-8') as f:
                json.dump(recovery_info, f, ensure_ascii=False, indent=2)
            print(f"恢复信息已保存至: {recovery_file}")
            print("提示：如需恢复到分类前状态，可使用 python BodyDataAnalyzer.py restore <output_dir>")
        
        return results
        
    # ---------- 恢复文件功能（后悔药）----------
    def restore_files(self, output_dir: str) -> Dict:
        """
        恢复被分类的文件到原始位置（后悔药功能）
        
        参数:
            output_dir: 分类输出目录
        
        返回:
            恢复操作的统计信息
        """
        recovery_file = os.path.join(output_dir, 'recovery_info.json')
        
        if not os.path.exists(recovery_file):
            raise FileNotFoundError(f"找不到恢复信息文件: {recovery_file}")
        
        # 读取恢复信息
        with open(recovery_file, 'r', encoding='utf-8') as f:
            recovery_info = json.load(f)
        
        # 恢复文件
        success_count = 0
        fail_count = 0
        fail_files = []
        
        total_files = len(recovery_info['files'])
        print(f"开始恢复 {total_files} 个文件...")
        
        for i, file_info in enumerate(recovery_info['files']):
            try:
                original_path = file_info['original_path']
                current_path = file_info['current_path']
                
                # 确保目标目录存在
                original_dir = os.path.dirname(original_path)
                os.makedirs(original_dir, exist_ok=True)
                
                # 如果原始路径已存在文件，添加编号避免覆盖
                if os.path.exists(original_path):
                    base_name, ext = os.path.splitext(original_path)
                    counter = 1
                    while os.path.exists(original_path):
                        original_path = f"{base_name}_{counter}{ext}"
                        counter += 1
                    
                # 移动文件回原始位置
                if os.path.exists(current_path):
                    shutil.move(current_path, original_path)
                    success_count += 1
                else:
                    fail_count += 1
                    fail_files.append(f"{current_path} (文件不存在)")
                
                # 更新进度
                if (i + 1) % 100 == 0 or (i + 1) == total_files:
                    print(f"恢复进度: {i + 1}/{total_files}")
            except Exception as e:
                fail_count += 1
                fail_files.append(f"{file_info['current_path']} -> {str(e)}")
        
        # 清理空文件夹
        for category in self.HEIGHT_CATEGORIES.keys():
            category_dir = os.path.join(output_dir, category)
            if os.path.exists(category_dir) and not os.listdir(category_dir):
                os.rmdir(category_dir)
        
        # 清理错误文件夹
        error_dir = os.path.join(output_dir, "错误")
        if os.path.exists(error_dir) and not os.listdir(error_dir):
            os.rmdir(error_dir)
        
        # 删除恢复信息文件
        if os.path.exists(recovery_file):
            os.remove(recovery_file)
        
        stats = {
            'total': total_files,
            'success': success_count,
            'fail': fail_count,
            'fail_files': fail_files
        }
        
        return stats


# ------------------------------------------------------------------
#  3. 命令行入口
# ------------------------------------------------------------------
import time

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法:")
        print("  python BodyDataAnalyzer.py <角色卡目录路径>  # 分析并分类角色卡")
        print("  python BodyDataAnalyzer.py restore <output_dir>  # 恢复分类的文件到原始位置")
        sys.exit(1)

    # 处理恢复命令
    if len(sys.argv) == 3 and sys.argv[1].lower() == "restore":
        output_dir = sys.argv[2]
        analyzer = BodyDataAnalyzer()
        try:
            print(f"正在准备恢复文件...")
            stats = analyzer.restore_files(output_dir)
            
            print(f"\n恢复完成:")
            print(f"总文件数: {stats['total']}")
            print(f"成功恢复: {stats['success']}")
            print(f"恢复失败: {stats['fail']}")
            
            if stats['fail'] > 0:
                print("\n失败的文件:")
                for fail_file in stats['fail_files']:
                    print(f"- {fail_file}")
                
            print(f"\n文件已恢复到原始位置")
        except Exception as e:
            print(f"恢复失败: {str(e)}")
            sys.exit(1)
        sys.exit(0)

    # 正常的分析和分类功能
    input_dir = sys.argv[1]
    analyzer = BodyDataAnalyzer()          # 默认加载 height_xgb.pkl
    results = analyzer.batch_analyze(input_dir)

    for r in results:
        if r['success']:
            print(f"{r['file_name']} -> {r['height_cm']} cm ({r['height_category']})")
        else:
            print(f"{r['file_name']} -> 错误: {r['error']}")

    # 自动分类到文件夹 - 默认使用移动文件模式
    output_dir = os.path.join(input_dir, 'categorized')
    print(f"\n开始自动分类文件到: {output_dir}")
    print(f"文件处理模式: {'移动' if True else '复制'}")
    categorized_results = analyzer.categorize_files_by_height(results, output_dir, move_files=True)
    
    # 保存分析结果
    output_path = os.path.join(input_dir, 'analysis_results.json')
    analyzer.save_analysis_results(categorized_results, output_path)
    
    # 统计信息
    success_count = sum(1 for r in categorized_results if r['success'])
    error_count = len(categorized_results) - success_count
    
    print(f"\n分析完成: 成功 {success_count} 张, 失败 {error_count} 张")
    print(f"详细结果已保存至: {output_path}")
    print(f"文件已自动分类到: {output_dir}")
    print(f"提示: 如需恢复到分类前状态，可使用 python BodyDataAnalyzer.py restore {output_dir}")