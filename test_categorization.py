# -*- coding:utf-8 -*-
"""
测试自动分类到文件夹功能
"""
import os
import sys
from BodyDataAnalyzer import BodyDataAnalyzer


def test_categorization():
    """测试自动分类功能"""
    # 获取当前目录下的measured_cards目录作为测试数据
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(current_dir, "measured_cards")
    
    # 检查测试目录是否存在
    if not os.path.exists(test_dir):
        print(f"测试目录不存在: {test_dir}")
        print("请在BodyDataAnalyzer目录下创建measured_cards文件夹并放入角色卡文件")
        return
    
    # 创建输出目录
    output_dir = os.path.join(current_dir, "test_output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"开始测试自动分类功能...")
    print(f"测试数据目录: {test_dir}")
    print(f"输出目录: {output_dir}")
    
    # 初始化分析器
    analyzer = BodyDataAnalyzer()
    
    # 批量分析
    print("\n开始分析角色卡...")
    results = analyzer.batch_analyze(test_dir)
    
    # 自动分类到文件夹 - 使用移动文件模式和批处理
    move_files = True  # 设置为True表示移动文件，False表示复制文件
    batch_size = 1000  # 每批处理的文件数量
    print(f"\n开始自动分类文件到: {output_dir}")
    print(f"文件处理模式: {'移动' if move_files else '复制'}")
    print(f"批处理大小: {batch_size}")
    categorized_results = analyzer.categorize_files_by_height(results, output_dir, move_files=move_files, batch_size=batch_size)
    
    # 保存分析结果
    output_path = os.path.join(output_dir, 'analysis_results.json')
    analyzer.save_analysis_results(categorized_results, output_path)
    
    # 统计信息
    success_count = sum(1 for r in categorized_results if r['success'])
    error_count = len(categorized_results) - success_count
    
    print(f"\n测试完成:")
    print(f"成功分析: {success_count} 张")
    print(f"分析失败: {error_count} 张")
    print(f"详细结果已保存至: {output_path}")
    print(f"文件已自动分类到: {output_dir}")
    
    # 打印分类结果统计
    category_count = {}
    for result in categorized_results:
        if result['success']:
            category = result['height_category']
            category_count[category] = category_count.get(category, 0) + 1
    
    if category_count:
        print("\n分类统计:")
        for category, count in category_count.items():
            print(f"{category}: {count} 张")


if __name__ == "__main__":
    test_categorization()