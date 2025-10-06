#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
BodyDataAnalyzer 使用示例脚本
演示如何使用 BodyDataAnalyzer 类进行角色卡片分析
"""
import os
import json
from BodyDataAnalyzer import BodyDataAnalyzer


def analyze_single_card(card_path):
    """分析单张角色卡片"""
    print(f"\n===== 分析单张卡片: {card_path} =====")
    
    try:
        # 创建分析器实例
        analyzer = BodyDataAnalyzer()
        
        # 分析单张卡片
        result = analyzer.analyze_character_card(card_path)
        
        # 打印结果
        if result['success']:
            print(f"文件名: {result['file_name']}")
            print(f"身高预测: {result['height_cm']} cm ({result['height_category']})")
            print(f"角色名称: {result['character_name']}")
            print(f"审美分类: {result['combined_tag']}")
            print("详细分类参数:")
            for param, category in result['aesthetic_classifications'].items():
                print(f"  - {param}: {category}")
        else:
            print(f"分析失败: {result['error']}")
            
    except Exception as e:
        print(f"发生错误: {str(e)}")


def analyze_directory(cards_dir):
    """批量分析目录中的所有角色卡片"""
    print(f"\n===== 批量分析目录: {cards_dir} =====")
    
    try:
        # 创建分析器实例
        analyzer = BodyDataAnalyzer()
        
        # 批量分析目录中的卡片
        results = analyzer.batch_analyze(cards_dir)
        
        # 打印结果摘要
        success_count = sum(1 for r in results if r['success'])
        print(f"分析完成: 共分析 {len(results)} 张卡片，成功 {success_count} 张")
        
        # 保存结果
        output_file = os.path.join(cards_dir, "analysis_results.json")
        analyzer.save_analysis_results(results, output_file)
        print(f"详细结果已保存至: {output_file}")
        
        # 打印前3个成功的结果作为示例
        print("\n示例结果:")
        for i, result in enumerate(results):
            if result['success']:
                print(f"{result['file_name']} -> {result['height_cm']} cm ({result['combined_tag']})")
                if i >= 2:
                    break
                    
    except Exception as e:
        print(f"发生错误: {str(e)}")


def main():
    """主函数，展示不同的使用方式"""
    print("===== BodyDataAnalyzer 使用示例 =====")
    
    # 这里可以根据实际情况修改为您的角色卡片路径
    # 单张卡片分析示例
    # card_path = "path/to/your/character_card.png"
    # if os.path.exists(card_path):
    #     analyze_single_card(card_path)
    # else:
    #     print(f"示例: 单张卡片分析 (未找到示例卡片)")
    
    # 批量分析示例
    # 如果有示例目录，可以取消下面的注释
    # cards_dir = "path/to/your/cards_directory"
    # if os.path.exists(cards_dir):
    #     analyze_directory(cards_dir)
    # else:
    print("示例: 批量分析目录中的卡片")
    print("使用方法:")
    print("1. 将您的角色卡片放入一个目录")
    print("2. 运行: python BodyDataAnalyzer.py <您的卡片目录路径>")
    print("3. 查看控制台输出和生成的 analysis_results.json 文件")
    
    print("\n===== 高级用法 ======")
    print("如果需要在您的Python代码中集成:")
    print("\nfrom BodyDataAnalyzer import BodyDataAnalyzer")
    print("analyzer = BodyDataAnalyzer()")
    print("results = analyzer.batch_analyze('path/to/cards')")


if __name__ == "__main__":
    main()