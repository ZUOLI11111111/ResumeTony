#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简历修改应用启动脚本
=====================
这个脚本用于一键启动简历修改应用的前端和后端服务。
提供了美观的界面和详细的状态信息。


"""

import os
import sys
import time
import subprocess
import platform
import socket
import shutil
import signal
import threading
import argparse
from pathlib import Path
import webbrowser
import json
import re

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# 帮助内容
HELP_TEXT = f"""
{Colors.BOLD}{Colors.CYAN}简历修改应用 - 帮助信息{Colors.END}
{Colors.YELLOW}======================{Colors.END}

{Colors.BOLD}常见问题解决方法：{Colors.END}

1. {Colors.BOLD}Java 相关问题：{Colors.END}
   - 确保已安装 JDK 11 或更高版本
   - 配置 JAVA_HOME 环境变量
   - 在 PATH 中添加 Java bin 目录

2. {Colors.BOLD}Node.js 相关问题：{Colors.END}
   - 安装 Node.js 14+ 版本
   - 更新 npm: npm install -g npm

3. {Colors.BOLD}MySQL 相关问题：{Colors.END}
   - 确保 MySQL 服务已启动
   - 检查用户名和密码是否正确
   - 配置文件位置: backend_of_java_for_save/src/main/resources/application.properties

4. {Colors.BOLD}端口冲突问题：{Colors.END}
   - 检查端口 8080(后端) 和 3000(前端) 是否被其他应用占用
   - Windows: netstat -ano | findstr 8080
   - Linux/Mac: lsof -i :8080

5. {Colors.BOLD}前端依赖问题：{Colors.END}
   - 手动安装依赖: cd frontend && npm install
   - 更新 npm 缓存: npm cache clean --force

{Colors.BOLD}命令行选项：{Colors.END}
  --help               显示此帮助信息
  --backend-only       仅启动后端服务
  --frontend-only      仅启动前端服务
  --no-browser         不自动打开浏览器
  --verbose            显示详细日志

{Colors.BOLD}使用示例：{Colors.END}
  python start_resume_app.py             # 正常启动所有服务
  python start_resume_app.py --help      # 显示帮助信息
  python start_resume_app.py --backend-only  # 仅启动后端
"""

# 进度条类
class ProgressBar:
    def __init__(self, total=100, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.length = length
        self.fill = fill
        self.print_end = print_end
        self.iteration = 0
        self.start_time = time.time()
        
    def print(self, iteration=None):
        if iteration is not None:
            self.iteration = iteration
        else:
            self.iteration += 1
            
        percent = ("{0:." + str(self.decimals) + "f}").format(100 * (self.iteration / float(self.total)))
        filled_length = int(self.length * self.iteration // self.total)
        bar = self.fill * filled_length + '-' * (self.length - filled_length)
        elapsed_time = time.time() - self.start_time
        time_str = f"{elapsed_time:.1f}s" if elapsed_time < 60 else f"{elapsed_time/60:.1f}m"
        
        print(f'\r{self.prefix} |{Colors.BLUE}{bar}{Colors.END}| {percent}% {self.suffix} ({time_str})', end=self.print_end)
        sys.stdout.flush()
        
        if self.iteration == self.total:
            print()

# 应用服务类
class ResumeAppService:
    def __init__(self, options=None):
        self.project_root = Path(__file__).parent.absolute()
        self.frontend_dir = self.project_root / 'frontend'
        self.java_backend_dir = self.project_root / 'backend_of_java_for_save'
        
        self.java_process = None
        self.frontend_process = None
        self.processes = []
        
        # 设置选项
        self.options = options or {}
        self.backend_only = self.options.get('backend_only', False)
        self.frontend_only = self.options.get('frontend_only', False)
        self.open_browser_flag = not self.options.get('no_browser', False)
        self.verbose = self.options.get('verbose', False)
        
        # 检测操作系统
        self.is_windows = platform.system() == 'Windows'
        self.terminal_width = shutil.get_terminal_size().columns
        
    def print_header(self):
        """打印美观的标题"""
        print('\n' + '=' * self.terminal_width)
        header = "简历修改应用启动器"
        print(f"{Colors.BOLD}{Colors.CYAN}{header.center(self.terminal_width)}{Colors.END}")
        print('=' * self.terminal_width + '\n')

    def print_section(self, title):
        """打印带有颜色的分节标题"""
        print(f"\n{Colors.BOLD}{Colors.YELLOW}【{title}】{Colors.END}")
        print(f"{Colors.YELLOW}{'-' * (len(title) + 2)}{Colors.END}")

    def check_port(self, port):
        """检查指定端口是否被占用"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
            
    def check_prerequisites(self):
        """检查启动前的必要条件"""
        self.print_section("环境检查")
        
        # 创建进度条
        progress = ProgressBar(total=6, prefix='检查进度:', suffix='完成', length=30)
        
        # 检查Java是否已安装
        try:
            java_version = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT, text=True)
            progress.print()
            # 使用更稳健的方式提取版本号
            version_line = java_version.split('\n')[0]
            if 'version' in version_line:
                # 提取引号之间的内容
                version_match = re.search(r'version "([^"]+)"', version_line)
                version_str = version_match.group(1) if version_match else "未知"
                print(f"{Colors.GREEN}✓ Java已安装: {Colors.END}{version_str}")
            else:
                print(f"{Colors.GREEN}✓ Java已安装{Colors.END}")
        except Exception as e:
            progress.print()
            print(f"{Colors.RED}✗ Java未安装或不在PATH中: {e}{Colors.END}")
            return False
            
        # 检查Node.js是否已安装
        try:
            node_version = subprocess.check_output(['node', '-v'], text=True).strip()
            progress.print()
            print(f"{Colors.GREEN}✓ Node.js已安装: {Colors.END}{node_version}")
        except Exception as e:
            progress.print()
            print(f"{Colors.RED}✗ Node.js未安装或不在PATH中: {e}{Colors.END}")
            return False
            
        # 检查npm是否已安装
        try:
            npm_version = subprocess.check_output(['npm', '-v'], text=True).strip()
            progress.print()
            print(f"{Colors.GREEN}✓ npm已安装: {Colors.END}{npm_version}")
        except Exception as e:
            progress.print()
            print(f"{Colors.RED}✗ npm未安装或不在PATH中: {e}{Colors.END}")
            return False
            
        # 检查MySQL是否已安装/可访问
        try:
            # 尝试使用mysql命令检查版本
            try:
                mysql_version = subprocess.check_output(['mysql', '--version'], text=True).strip()
                progress.print()
                print(f"{Colors.GREEN}✓ MySQL已安装: {Colors.END}{mysql_version}")
            except:
                # 如果mysql命令不可用，检查Java配置中数据库连接是否存在
                db_config_file = self.java_backend_dir / 'src' / 'main' / 'resources' / 'application.properties'
                if db_config_file.exists():
                    progress.print()
                    print(f"{Colors.YELLOW}! MySQL命令不可用，但找到数据库配置文件{Colors.END}")
                else:
                    progress.print()
                    print(f"{Colors.YELLOW}! 无法验证MySQL，可能会影响应用功能{Colors.END}")
        except Exception as e:
            progress.print()
            print(f"{Colors.YELLOW}! 无法验证MySQL: {e}{Colors.END}")
            
        # 检查前端目录是否存在
        if self.frontend_dir.exists():
            progress.print()
            print(f"{Colors.GREEN}✓ 前端目录已找到: {Colors.END}{self.frontend_dir}")
        else:
            progress.print()
            print(f"{Colors.RED}✗ 前端目录不存在: {Colors.END}{self.frontend_dir}")
            return False
            
        # 检查Java后端目录是否存在
        if self.java_backend_dir.exists():
            progress.print()
            print(f"{Colors.GREEN}✓ Java后端目录已找到: {Colors.END}{self.java_backend_dir}")
        else:
            progress.print()
            print(f"{Colors.RED}✗ Java后端目录不存在: {Colors.END}{self.java_backend_dir}")
            return False
            
        print(f"\n{Colors.GREEN}所有先决条件检查通过！{Colors.END}\n")
        return True
    
    def check_port_availability(self):
        """检查需要的端口是否可用"""
        self.print_section("端口检查")
        
        ports_to_check = [8080, 3000]  # Java后端和React前端端口
        all_available = True
        
        for port in ports_to_check:
            if self.check_port(port):
                print(f"{Colors.RED}✗ 端口 {port} 已被占用。请关闭占用此端口的应用后重试。{Colors.END}")
                all_available = False
            else:
                print(f"{Colors.GREEN}✓ 端口 {port} 可用{Colors.END}")
                
        return all_available

    def start_java_backend(self):
        """启动Java后端服务"""
        self.print_section("启动Java后端")
        
        os.chdir(self.java_backend_dir)
        
        # 构建Maven项目
        print(f"{Colors.CYAN}正在构建Java后端...{Colors.END}")
        mvn_cmd = 'mvnw.cmd' if self.is_windows else './mvnw'
        
        if not os.path.exists(mvn_cmd):
            print(f"{Colors.YELLOW}注意: Maven Wrapper不存在，尝试使用系统Maven{Colors.END}")
            mvn_cmd = 'mvn'
            
        try:
            subprocess.run([mvn_cmd, 'clean', 'package', '-DskipTests'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            print(f"{Colors.GREEN}✓ Java后端构建成功{Colors.END}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}✗ Java后端构建失败: {e}{Colors.END}")
            print(f"错误输出: {e.stderr.decode('utf-8')}")
            return False
        
        # 启动Spring Boot应用
        print(f"{Colors.CYAN}正在启动Java后端服务...{Colors.END}")
        jar_files = list(Path('target').glob('*.jar'))
        
        if not jar_files:
            print(f"{Colors.RED}✗ 找不到可执行的JAR文件{Colors.END}")
            return False
            
        jar_file = jar_files[0]
        
        try:
            java_cmd = ['java', '-jar', str(jar_file)]
            self.java_process = subprocess.Popen(java_cmd, 
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            text=True)
            self.processes.append(self.java_process)
            
            # 等待服务启动
            print(f"{Colors.CYAN}等待Java后端启动...{Colors.END}")
            progress = ProgressBar(total=30, prefix='启动进度:', suffix='检查中', length=30)
            
            for i in range(30):
                progress.print()
                if self.check_port(8080):
                    break
                time.sleep(1)
                
            if self.check_port(8080):
                print(f"\n{Colors.GREEN}✓ Java后端已成功启动在端口 8080{Colors.END}")
                return True
            else:
                print(f"\n{Colors.RED}✗ Java后端启动失败或超时{Colors.END}")
                # 检查是否有错误输出
                if self.java_process.stderr:
                    error_output = self.java_process.stderr.read(1024)  # 读取前1024个字符的错误
                    if error_output:
                        print(f"{Colors.RED}错误信息: {error_output}{Colors.END}")
                return False
        except Exception as e:
            print(f"\n{Colors.RED}✗ 启动Java后端时出错: {e}{Colors.END}")
            return False
    
    def start_frontend(self):
        """启动React前端服务"""
        self.print_section("启动React前端")
        
        try:
            os.chdir(self.frontend_dir)
            
            # 检查node_modules是否存在，如果不存在则安装依赖
            if not os.path.exists('node_modules'):
                print(f"{Colors.CYAN}未找到node_modules，正在安装依赖...{Colors.END}")
                print(f"{Colors.YELLOW}这可能需要几分钟时间，请耐心等待...{Colors.END}")
                try:
                    npm_install = subprocess.run(['npm', 'install'], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  check=True)
                    print(f"{Colors.GREEN}✓ 依赖安装成功{Colors.END}")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.RED}✗ 依赖安装失败: {Colors.END}")
                    error_output = e.stderr.decode('utf-8') if hasattr(e, 'stderr') else str(e)
                    print(f"{Colors.RED}错误信息: {error_output[:200]}...{Colors.END}")
                    return False
            
            # 启动前端服务
            print(f"{Colors.CYAN}正在启动React前端服务...{Colors.END}")
            npm_cmd = 'npm.cmd' if self.is_windows else 'npm'
            self.frontend_process = subprocess.Popen([npm_cmd, 'start'], 
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE,
                                                   text=True)
            self.processes.append(self.frontend_process)
            
            # 等待服务启动
            print(f"{Colors.CYAN}等待前端服务启动...{Colors.END}")
            print(f"{Colors.YELLOW}注意: 首次启动可能需要较长时间编译，请耐心等待{Colors.END}")
            progress = ProgressBar(total=60, prefix='启动进度:', suffix='检查中', length=30)
            
            for i in range(60):  # 增加等待时间到60秒
                progress.print()
                if self.check_port(3000):
                    break
                time.sleep(1)
                
                # 检查进程是否仍在运行
                if self.frontend_process.poll() is not None:
                    # 进程已退出
                    stderr = self.frontend_process.stderr.read()
                    print(f"\n{Colors.RED}✗ 前端进程异常退出{Colors.END}")
                    if stderr:
                        print(f"{Colors.RED}错误信息: {stderr[:200]}...{Colors.END}")
                    return False
                
            if self.check_port(3000):
                print(f"\n{Colors.GREEN}✓ React前端已成功启动在端口 3000{Colors.END}")
                return True
            else:
                print(f"\n{Colors.RED}✗ React前端启动失败或超时{Colors.END}")
                return False
        except Exception as e:
            print(f"\n{Colors.RED}✗ 启动前端时出错: {e}{Colors.END}")
            return False
    
    def open_browser(self):
        """在浏览器中打开应用"""
        print(f"\n{Colors.CYAN}在浏览器中打开应用...{Colors.END}")
        webbrowser.open('http://localhost:3000')
        
    def monitor_logs(self):
        """实时显示日志"""
        self.print_section("应用日志")
        
        def read_process_output(process, prefix):
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                print(f"{prefix} {line.strip()}")
                
        if self.java_process:
            java_thread = threading.Thread(
                target=read_process_output, 
                args=(self.java_process, f"{Colors.CYAN}[Java后端]{Colors.END}"),
                daemon=True
            )
            java_thread.start()
            
        if self.frontend_process:
            frontend_thread = threading.Thread(
                target=read_process_output, 
                args=(self.frontend_process, f"{Colors.GREEN}[React前端]{Colors.END}"),
                daemon=True
            )
            frontend_thread.start()
    
    def cleanup(self, signum=None, frame=None):
        """清理资源并关闭进程"""
        print(f"\n\n{Colors.YELLOW}正在关闭服务...{Colors.END}")
        
        for process in self.processes:
            if process:
                if platform.system() == 'Windows':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
        
        print(f"{Colors.GREEN}所有服务已关闭。{Colors.END}")
        
    def show_help(self):
        """显示帮助信息"""
        print(HELP_TEXT)
        
    def run(self):
        """运行启动程序"""
        # 注册信号处理
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        try:
            # 打印标题
            self.print_header()
            
            # 检查必要条件
            if not self.check_prerequisites():
                print(f"{Colors.RED}先决条件检查失败，无法启动应用。{Colors.END}")
                return
                
            # 检查端口可用性
            if not self.check_port_availability():
                print(f"{Colors.RED}端口检查失败，无法启动应用。{Colors.END}")
                return
            
            # 根据选项启动服务
            backend_started = False
            frontend_started = False
            
            # 启动后端服务（除非仅指定前端）
            if not self.frontend_only:
                backend_started = self.start_java_backend()
                if not backend_started:
                    print(f"{Colors.RED}Java后端启动失败，无法继续。{Colors.END}")
                    self.cleanup()
                    return
            
            # 启动前端服务（除非仅指定后端）
            if not self.backend_only:
                frontend_started = self.start_frontend()
                if not frontend_started:
                    print(f"{Colors.RED}前端启动失败。{Colors.END}")
                    if not self.frontend_only:  # 如果不是仅前端模式，就清理
                        self.cleanup()
                        return
            
            # 显示成功信息
            started_services = []
            if backend_started:
                started_services.append("Java后端(端口8080)")
            if frontend_started:
                started_services.append("React前端(端口3000)")
                
            if started_services:
                print(f"\n{Colors.BOLD}{Colors.GREEN}成功启动的服务: {', '.join(started_services)}{Colors.END}")
                
                # 显示访问地址
                if frontend_started:
                    print(f"{Colors.CYAN}应用访问地址: http://localhost:3000{Colors.END}")
                elif backend_started:
                    print(f"{Colors.CYAN}后端API地址: http://localhost:8080/api{Colors.END}")
                
                # 自动打开浏览器（如果启动了前端且未禁用）
                if frontend_started and self.open_browser_flag:
                    self.open_browser()
            else:
                print(f"\n{Colors.YELLOW}没有成功启动任何服务{Colors.END}")
                return
            
            # 监控日志
            self.monitor_logs()
            
            # 等待用户终止程序
            print(f"\n{Colors.YELLOW}按 Ctrl+C 停止所有服务...{Colors.END}")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

# 主程序入口
if __name__ == "__main__":
    # 在Windows命令提示符中启用ANSI颜色
    if platform.system() == 'Windows':
        os.system('color')
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='简历修改应用启动脚本', add_help=False)
    parser.add_argument('--help', action='store_true', help='显示帮助信息')
    parser.add_argument('--backend-only', action='store_true', help='仅启动后端服务')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端服务')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')
    
    args = parser.parse_args()
    
    # 如果请求帮助，显示帮助信息并退出
    if args.help:
        app = ResumeAppService()
        app.show_help()
        sys.exit(0)
    
    # 检查互斥选项
    if args.backend_only and args.frontend_only:
        print(f"{Colors.RED}错误: --backend-only 和 --frontend-only 选项不能同时使用{Colors.END}")
        sys.exit(1)
    
    # 启动应用
    options = {
        'backend_only': args.backend_only,
        'frontend_only': args.frontend_only,
        'no_browser': args.no_browser,
        'verbose': args.verbose
    }
    
    app = ResumeAppService(options)
    app.run() 