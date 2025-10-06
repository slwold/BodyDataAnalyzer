import os
import shutil
import json
import subprocess
import time
from pathlib import Path

class RestoreTest:
    def __init__(self):
        # 测试目录设置
        self.base_dir = os.path.abspath("test_restore_dir")
        self.input_dir = os.path.join(self.base_dir, "input")
        self.output_dir = os.path.join(self.input_dir, "categorized")
        self.recovery_file = os.path.join(self.output_dir, "recovery_info.json")
        self.test_files = 10  # 测试文件数量
        self.test_results = {}
    
    def setup_test_env(self):
        """设置测试环境，创建测试目录和文件"""
        print("设置测试环境...")
        
        # 清理之前的测试环境
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            print(f"清理旧测试目录: {self.base_dir}")
        
        # 创建测试输入目录
        os.makedirs(self.input_dir, exist_ok=True)
        print(f"创建测试输入目录: {self.input_dir}")
        
        # 创建一些测试文件（模拟角色卡文件）
        test_file_paths = []
        for i in range(self.test_files):
            file_name = f"test_card_{i}.png"
            file_path = os.path.join(self.input_dir, file_name)
            with open(file_path, "w") as f:
                f.write(f"这是测试角色卡文件 {i}")
            test_file_paths.append(file_path)
        
        self.test_results['original_files'] = test_file_paths
        print(f"创建了 {self.test_files} 个测试文件")
    
    def run_analysis_and_categorization(self):
        """运行分析和分类命令"""
        print("\n运行分析和分类...")
        
        # 运行BodyDataAnalyzer.py脚本
        cmd = ["python", "BodyDataAnalyzer.py", self.input_dir]
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 使用subprocess运行命令并捕获输出
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
            
            # 检查命令是否成功执行
            if result.returncode == 0:
                print("分析和分类成功完成")
                self.test_results['categorization_output'] = result.stdout
            else:
                print(f"分析和分类失败，退出码: {result.returncode}")
                print(f"错误输出: {result.stderr}")
                self.test_results['categorization_error'] = result.stderr
                return False
            
            # 验证输出目录和恢复信息文件是否存在
            if os.path.exists(self.output_dir):
                print(f"输出目录已创建: {self.output_dir}")
                
                # 检查分类子目录
                subdirs = [d for d in os.listdir(self.output_dir) if os.path.isdir(os.path.join(self.output_dir, d))]
                print(f"输出目录包含 {len(subdirs)} 个子目录")
                self.test_results['output_subdirs'] = subdirs
                
                # 检查恢复信息文件是否存在
                if os.path.exists(self.recovery_file):
                    print(f"恢复信息文件已创建: {self.recovery_file}")
                    
                    # 读取恢复信息文件内容
                    with open(self.recovery_file, 'r', encoding='utf-8') as f:
                        recovery_info = json.load(f)
                    print(f"恢复信息包含 {len(recovery_info.get('files', []))} 个文件记录")
                    self.test_results['recovery_file_exists'] = True
                else:
                    print("错误: 恢复信息文件不存在")
                    self.test_results['recovery_file_exists'] = False
                    return False
            else:
                print("错误: 输出目录不存在")
                return False
            
            # 验证输入目录中的文件是否被移动
            remaining_files = [f for f in os.listdir(self.input_dir) if os.path.isfile(os.path.join(self.input_dir, f)) and f.endswith('.png')]
            moved_files_count = self.test_files - len(remaining_files)
            print(f"成功移动了 {moved_files_count} 个文件")
            self.test_results['moved_files_count'] = moved_files_count
            
            return True
        except Exception as e:
            print(f"执行命令时出错: {str(e)}")
            self.test_results['categorization_exception'] = str(e)
            return False
    
    def run_restore(self):
        """运行恢复命令"""
        print("\n运行文件恢复...")
        
        # 运行恢复命令
        cmd = ["python", "BodyDataAnalyzer.py", "restore", self.output_dir]
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 使用subprocess运行命令并捕获输出
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)))
            
            # 检查命令是否成功执行
            if result.returncode == 0:
                print("文件恢复成功完成")
                self.test_results['restore_output'] = result.stdout
            else:
                print(f"文件恢复失败，退出码: {result.returncode}")
                print(f"错误输出: {result.stderr}")
                self.test_results['restore_error'] = result.stderr
                return False
            
            # 验证恢复信息文件是否已被删除
            if not os.path.exists(self.recovery_file):
                print("恢复信息文件已被删除")
            else:
                print("警告: 恢复信息文件仍然存在")
                
            return True
        except Exception as e:
            print(f"执行恢复命令时出错: {str(e)}")
            self.test_results['restore_exception'] = str(e)
            return False
    
    def verify_results(self):
        """验证恢复结果"""
        print("\n验证恢复结果...")
        
        # 检查输入目录中的文件数量
        restored_files = [f for f in os.listdir(self.input_dir) if os.path.isfile(os.path.join(self.input_dir, f)) and f.endswith('.png')]
        print(f"输入目录中恢复的文件数量: {len(restored_files)}")
        self.test_results['restored_files_count'] = len(restored_files)
        
        # 检查输出目录是否为空或已被删除
        if not os.path.exists(self.output_dir):
            print("输出目录已被完全删除")
        else:
            output_files = []
            for root, _, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith('.png'):
                        output_files.append(os.path.join(root, file))
            print(f"输出目录中剩余的文件数量: {len(output_files)}")
            self.test_results['remaining_output_files'] = len(output_files)
        
        # 判断测试是否成功
        success = len(restored_files) > 0 and (self.test_files - len(restored_files)) <= 2  # 允许少量文件恢复失败
        self.test_results['success'] = success
        
        return success
    
    def cleanup(self):
        """清理测试环境"""
        print("\n清理测试环境...")
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
            print(f"已删除测试目录: {self.base_dir}")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n========== 测试总结 ==========")
        print(f"测试成功: {'✓' if self.test_results.get('success', False) else '✗'}")
        print(f"原始文件数量: {self.test_files}")
        print(f"移动的文件数量: {self.test_results.get('moved_files_count', 0)}")
        print(f"恢复的文件数量: {self.test_results.get('restored_files_count', 0)}")
        print(f"输出目录剩余文件: {self.test_results.get('remaining_output_files', 0)}")
        print(f"恢复信息文件生成: {'✓' if self.test_results.get('recovery_file_exists', False) else '✗'}")
        
        # 打印错误信息（如果有）
        if 'categorization_error' in self.test_results:
            print("\n分类错误:")
            print(self.test_results['categorization_error'])
        
        if 'restore_error' in self.test_results:
            print("\n恢复错误:")
            print(self.test_results['restore_error'])
        
        if 'categorization_exception' in self.test_results:
            print("\n分类异常:")
            print(self.test_results['categorization_exception'])
        
        if 'restore_exception' in self.test_results:
            print("\n恢复异常:")
            print(self.test_results['restore_exception'])
        
        print("=============================")
        
        # 保存测试结果到文件
        results_file = "test_restore_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"测试结果已保存至: {results_file}")

if __name__ == "__main__":
    print("=== 后悔药功能测试开始 ===")
    test = RestoreTest()
    
    try:
        # 1. 设置测试环境
        test.setup_test_env()
        
        # 2. 运行分析和分类
        categorization_success = test.run_analysis_and_categorization()
        
        if categorization_success:
            # 3. 运行恢复
            restore_success = test.run_restore()
            
            if restore_success:
                # 4. 验证结果
                test.verify_results()
    finally:
        # 5. 打印测试总结
        test.print_summary()
        
        # 6. 清理测试环境（可选，注释掉可以保留测试文件以便查看）
        # test.cleanup()
        
    print("\n=== 后悔药功能测试结束 ===")