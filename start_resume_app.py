#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import sys
import argparse
import signal

def print_progress(message, progress=0):
    """显示进度条信息"""
    bar_length = 30
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{message}: [{bar}] {progress}%')
    sys.stdout.flush()
    if progress == 100:
        print()

def run_command(command, cwd=None):
    """运行命令并返回进程对象"""
    return subprocess.Popen(command, shell=True, cwd=cwd)

def check_service_running(port):
    """检查指定端口是否有服务在运行"""
    try:
        result = subprocess.run(
            f"netstat -tuln | grep :{port}", 
            shell=True, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ResumeTony 应用启动工具')
    parser.add_argument('--java-backend-only', action='store_true', help='仅启动Java后端')
    parser.add_argument('--python-backend-only', action='store_true', help='仅启动Python后端')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端')
    parser.add_argument('--backend-only', action='store_true', help='仅启动所有后端服务')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')
    args = parser.parse_args()

    print("ResumeTony 系统启动工具")
    print("=" * 50)
    
    # 基础路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    java_backend_path = os.path.join(base_path, "backend_of_java_for_save")
    python_backend_path = os.path.join(base_path, "backend_of_py_for_modify")
    frontend_path = os.path.join(base_path, "frontend")
    
    # 存储启动的进程
    processes = {
        'java': None,
        'python': None,
        'frontend': None
    }
    
    # 启动Java后端
    if args.java_backend_only or args.backend_only or not (args.python_backend_only or args.frontend_only):
        print_progress("正在启动Java后端", 0)
        
        # 检查MySQL是否运行
        mysql_check = subprocess.run("systemctl is-active --quiet mysql", shell=True)
        if mysql_check.returncode != 0:
            print("\n启动MySQL服务...")
            subprocess.run("sudo service mysql start", shell=True, check=True)
        print_progress("正在启动Java后端", 30)
        
        # 检查JAR文件是否存在
        jar_path = os.path.join(java_backend_path, "target/resume-service-1.0.0.jar")
        if not os.path.exists(jar_path):
            print("\n构建Java应用...")
            subprocess.run("mvn clean package", shell=True, cwd=java_backend_path, check=True)
        print_progress("正在启动Java后端", 60)
        
        # 启动Java应用
        config_path = f"file://{java_backend_path}/src/main/resourses/application.properties"
        processes['java'] = run_command(f"java -jar {jar_path} --spring.config.location={config_path}", cwd=java_backend_path)
        
        # 等待服务启动
        retry = 10
        while retry > 0 and not check_service_running(8080):
            time.sleep(1)
            retry -= 1
            print_progress("正在启动Java后端", 60 + (10 - retry) * 4)
        
        print_progress("正在启动Java后端", 100)
    
    # 启动Python后端
    if args.python_backend_only or args.backend_only or not (args.java_backend_only or args.frontend_only):
        print_progress("正在启动Python后端", 0)
        processes['python'] = run_command("python3 app.py", cwd=python_backend_path)
        
        # 等待服务启动
        retry = 10
        while retry > 0 and not check_service_running(5000):
            time.sleep(0.5)
            retry -= 1
            print_progress("正在启动Python后端", (10 - retry) * 10)
            
        print_progress("正在启动Python后端", 100)
    
    # 启动前端
    if args.frontend_only or not (args.java_backend_only or args.python_backend_only or args.backend_only):
        print_progress("正在启动前端", 0)
        
        # 检查node_modules是否存在
        if not os.path.exists(os.path.join(frontend_path, "node_modules")):
            print("\n安装前端依赖...")
            subprocess.run("npm install", shell=True, cwd=frontend_path, check=True)
        print_progress("正在启动前端", 50)
        
        # 启动前端应用
        browser_flag = "--no-browser" if args.no_browser else ""
        processes['frontend'] = run_command(f"npm start {browser_flag}", cwd=frontend_path)
        print_progress("正在启动前端", 100)
    
    active_processes = sum(1 for p in processes.values() if p is not None)
    if active_processes > 0:
        print("\n所有服务已启动！")
        print("=" * 50)
        print("按Ctrl+C停止所有服务")
        
        # 设置信号处理
        def signal_handler(sig, frame):
            print("\n正在停止所有服务...")
            for name, process in processes.items():
                if process:
                    print(f"停止{name}服务...")
                    process.terminate()
                    process.wait()
            print("所有服务已停止")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 保持脚本运行直到用户中断
        try:
            while True:
                time.sleep(1)
                # 检查进程是否还在运行
                for name, process in processes.items():
                    if process and process.poll() is not None:
                        print(f"\n警告: {name}服务已意外停止，退出码: {process.returncode}")
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
    else:
        print("没有启动任何服务")

if __name__ == "__main__":
    main()
