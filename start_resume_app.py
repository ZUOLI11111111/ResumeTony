#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import time
import sys
import argparse
import signal
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"resume_app_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ResumeTony")

# 配置参数
DEFAULT_JAVA_PORT = 8080
DEFAULT_PYTHON_PORT = 5000
MAX_RETRY = 15  # 增加重试次数
RETRY_INTERVAL = 1  # 秒

# MySQL配置
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "resume_db"

def print_progress(message, progress=0):
    """显示进度条信息"""
    bar_length = 30
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\r{message}: [{bar}] {progress}%')
    sys.stdout.flush()
    if progress == 100:
        print()

def run_command(command, cwd=None, verbose=False):
    """运行命令并返回进程对象"""
    if verbose:
        logger.info(f"执行命令: {command} 在目录: {cwd or '当前目录'}")
    
    # 设置stdout和stderr重定向
    stdout = None if verbose else subprocess.PIPE
    stderr = None if verbose else subprocess.PIPE
    
    return subprocess.Popen(command, shell=True, cwd=cwd, stdout=stdout, stderr=stderr)

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
    except Exception as e:
        logger.error(f"检查端口 {port} 时出错: {str(e)}")
        return False

def check_java_service_health(port):
    """检查Java服务的健康状态"""
    try:
        result = subprocess.run(
            f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{port}/actuator/health",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.decode().strip() == "200"
    except Exception as e:
        logger.error(f"检查Java服务健康状态时出错: {str(e)}")
        return False

def check_mysql_running():
    """检查MySQL服务是否运行，返回布尔值"""
    try:
        # 使用预设的MySQL用户名和密码检查MySQL状态
        cmd = f"mysql -u{MYSQL_USER} -p{MYSQL_PASSWORD} -e 'SELECT 1;' > /dev/null 2>&1"
        exit_code = subprocess.call(cmd, shell=True)
        return exit_code == 0
    except Exception as e:
        logger.error(f"检查MySQL状态时出错: {str(e)}")
        return False

def print_services_info(processes, java_port, python_port, java_log_file=None, python_log_file=None, frontend_log_file=None):
    """打印所有服务的详细信息"""
    print("\n" + "=" * 50)
    print("ResumeTony 服务状态概览")
    print("=" * 50)
    
    # 服务状态表头
    print(f"{'服务类型':<15}{'状态':<10}{'端口':<10}{'日志文件':<40}")
    print("-" * 75)
    
    # Java后端信息
    java_status = "运行中" if processes.get('java') else "未启动"
    java_log = java_log_file if java_log_file else "N/A"
    print(f"{'Java后端':<15}{java_status:<10}{java_port:<10}{java_log:<40}")
    
    # Python后端信息
    python_status = "运行中" if processes.get('python') else "未启动"
    python_log = python_log_file if python_log_file else "N/A"
    print(f"{'Python后端':<15}{python_status:<10}{python_port:<10}{python_log:<40}")
    
    # 前端信息
    frontend_status = "运行中" if processes.get('frontend') else "未启动"
    frontend_log = frontend_log_file if frontend_log_file else "N/A"
    frontend_port = "3000"  # 前端通常使用3000端口
    print(f"{'前端':<15}{frontend_status:<10}{frontend_port:<10}{frontend_log:<40}")
    
    print("=" * 75)
    
    # 访问URLs
    if processes.get('java'):
        print(f"Java API URL: http://localhost:{java_port}/api")
    if processes.get('python'):
        print(f"Python API URL: http://localhost:{python_port}/api")
    if processes.get('frontend'):
        print(f"前端URL: http://localhost:3000")
    
    print("=" * 50)
    print("管理命令:")
    print("- 查看Java进程: ps -ef | grep resume-service")
    print("- 查看Python进程: ps -ef | grep 'python3 app.py'")
    print("- 查看前端进程: ps -ef | grep 'npm start'")
    print("- 查看端口使用: netstat -tuln | grep -E '8080|5000|3000'")
    print("=" * 50)
    
    # 记录到日志
    logger.info("服务状态概览:")
    logger.info(f"Java后端: {java_status}, 端口: {java_port}, 日志: {java_log}")
    logger.info(f"Python后端: {python_status}, 端口: {python_port}, 日志: {python_log}")
    logger.info(f"前端: {frontend_status}, 端口: 3000, 日志: {frontend_log}")

def main():
    # 声明全局变量
    global MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ResumeTony 应用启动工具')
    parser.add_argument('--java-backend-only', action='store_true', help='仅启动Java后端')
    parser.add_argument('--python-backend-only', action='store_true', help='仅启动Python后端')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端')
    parser.add_argument('--backend-only', action='store_true', help='仅启动所有后端服务')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--verbose', action='store_true', help='显示详细日志')
    parser.add_argument('--java-port', type=int, default=DEFAULT_JAVA_PORT, help=f'Java后端端口 (默认: {DEFAULT_JAVA_PORT})')
    parser.add_argument('--python-port', type=int, default=DEFAULT_PYTHON_PORT, help=f'Python后端端口 (默认: {DEFAULT_PYTHON_PORT})')
    parser.add_argument('--java-opts', type=str, default='', help='Java应用的额外JVM参数')
    parser.add_argument('--skip-build', action='store_true', help='跳过Maven构建步骤')
    parser.add_argument('--mysql-user', type=str, default=MYSQL_USER, help=f'MySQL用户名 (默认: {MYSQL_USER})')
    parser.add_argument('--mysql-password', type=str, default=MYSQL_PASSWORD, help='MySQL密码')
    parser.add_argument('--mysql-database', type=str, default=MYSQL_DATABASE, help=f'MySQL数据库名 (默认: {MYSQL_DATABASE})')
    args = parser.parse_args()

    # 更新MySQL配置
    MYSQL_USER = args.mysql_user
    MYSQL_PASSWORD = args.mysql_password
    MYSQL_DATABASE = args.mysql_database

    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("ResumeTony 系统启动工具")
    logger.info("=" * 50)
    
    # 基础路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    java_backend_path = os.path.join(base_path, "backend_of_java_for_save")
    python_backend_path = os.path.join(base_path, "backend_of_py_for_modify")
    frontend_path = os.path.join(base_path, "frontend")
    
    # 检查目录是否存在
    for path, name in [(java_backend_path, "Java后端"), 
                       (python_backend_path, "Python后端"), 
                       (frontend_path, "前端")]:
        if not os.path.exists(path):
            logger.error(f"{name}目录不存在: {path}")
            if name == "Java后端" and (args.java_backend_only or args.backend_only):
                sys.exit(1)
            if name == "Python后端" and (args.python_backend_only or args.backend_only):
                sys.exit(1)
            if name == "前端" and args.frontend_only:
                sys.exit(1)
    
    # 存储启动的进程
    processes = {
        'java': None,
        'python': None,
        'frontend': None
    }
    
    # 启动Java后端
    if args.java_backend_only or args.backend_only or not (args.python_backend_only or args.frontend_only):
        print_progress("正在启动Java后端", 0)
        logger.info("准备启动Java后端...")
        
        # 检查MySQL是否运行
        if not check_mysql_running():
            logger.info("MySQL服务未运行或连接失败，尝试启动MySQL服务...")
            try:
                # 尝试使用系统服务启动
                subprocess.run("sudo service mysql start", shell=True, check=True)
                time.sleep(2)  # 等待服务启动
                
                if not check_mysql_running():
                    logger.warning("通过系统服务启动MySQL后仍无法连接，尝试其他方法...")
                    # 尝试直接启动mysqld
                    subprocess.run("sudo mysqld --user=mysql &", shell=True)
                    time.sleep(3)  # 等待mysqld启动
                
                # 再次检查
                if check_mysql_running():
                    logger.info("MySQL服务启动成功")
                else:
                    logger.error("无法启动MySQL服务")
                    sys.exit(1)
            except subprocess.CalledProcessError as e:
                logger.error(f"启动MySQL服务失败: {str(e)}")
                sys.exit(1)
        else:
            logger.info("MySQL服务已在运行")
            
        print_progress("正在启动Java后端", 30)
        
        # 检查数据库是否存在
        check_db_cmd = f"mysql -u{MYSQL_USER} -p{MYSQL_PASSWORD} -e \"SHOW DATABASES LIKE '{MYSQL_DATABASE}';\" | grep {MYSQL_DATABASE}"
        db_exists = subprocess.call(check_db_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0
        
        if not db_exists:
            logger.info(f"数据库 {MYSQL_DATABASE} 不存在，正在创建...")
            create_db_cmd = f"mysql -u{MYSQL_USER} -p{MYSQL_PASSWORD} -e \"CREATE DATABASE {MYSQL_DATABASE};\""
            try:
                subprocess.run(create_db_cmd, shell=True, check=True)
                logger.info(f"数据库 {MYSQL_DATABASE} 创建成功")
            except subprocess.CalledProcessError as e:
                logger.error(f"创建数据库失败: {str(e)}")
                sys.exit(1)
        
        # 检查JAR文件是否存在
        jar_path = os.path.join(java_backend_path, "target/resume-service-1.0.0.jar")
        if not os.path.exists(jar_path) and not args.skip_build:
            logger.info("JAR文件不存在，执行Maven构建...")
            try:
                mvn_result = subprocess.run("mvn clean package -DskipTests", 
                                           shell=True, 
                                           cwd=java_backend_path, 
                                           capture_output=not args.verbose)
                if mvn_result.returncode != 0:
                    logger.error("Maven构建失败")
                    if not args.verbose:
                        logger.error(f"错误输出: {mvn_result.stderr.decode()}")
                    sys.exit(1)
                logger.info("Maven构建成功")
            except Exception as e:
                logger.error(f"Maven构建过程中出错: {str(e)}")
                sys.exit(1)
                
        elif args.skip_build:
            logger.info("跳过Maven构建步骤")
        else:
            logger.info(f"JAR文件已存在: {jar_path}")
            
        print_progress("正在启动Java后端", 60)
        
        # 清理可能占用端口的进程
        if check_service_running(args.java_port):
            logger.warning(f"端口 {args.java_port} 已被占用，尝试终止进程...")
            try:
                subprocess.run(f"lsof -ti:{args.java_port} | xargs kill -9", shell=True)
                time.sleep(1)  # 等待进程完全终止
            except Exception as e:
                logger.error(f"终止占用端口 {args.java_port} 的进程时出错: {str(e)}")
        
        # 启动Java应用
        config_path = f"file://{java_backend_path}/src/main/resources/application.properties"
        if not os.path.exists(java_backend_path + "/src/main/resources/application.properties"):
            # 尝试其他可能的路径
            alt_config_path = f"{java_backend_path}/src/main/resourses/application.properties"
            if os.path.exists(alt_config_path):
                config_path = f"file://{alt_config_path}"
                logger.info(f"使用备选配置文件路径: {alt_config_path}")
            else:
                logger.warning(f"找不到配置文件，将使用JAR包内的默认配置")
                config_path = ""
        
        # 添加数据库连接参数
        java_command = f"java {args.java_opts} -jar {jar_path}"
        if config_path:
            java_command += f" --spring.config.location={config_path}"
        java_command += f" --server.port={args.java_port}"
        # 添加数据库连接信息
        java_command += f" --spring.datasource.username={MYSQL_USER}"
        java_command += f" --spring.datasource.password={MYSQL_PASSWORD}"
        java_command += f" --spring.datasource.url=jdbc:mysql://localhost:3306/{MYSQL_DATABASE}?serverTimezone=UTC&useUnicode=true&characterEncoding=utf-8&useSSL=false"
        
        # 使用nohup后台方式启动Java应用
        java_log_file = os.path.join(base_path, f"java_backend_{datetime.now().strftime('%Y%m%d')}.log")
        nohup_command = f"nohup {java_command} > {java_log_file} 2>&1 &"
        
        logger.info(f"启动Java应用: {nohup_command}")
        subprocess.run(nohup_command, shell=True, cwd=java_backend_path)
        logger.info(f"Java后端已启动，日志输出到: {java_log_file}")
        
        # 修改processes字典，不再存储进程对象而是标记服务状态
        processes['java'] = True
        
        # 给Java进程一些时间启动
        time.sleep(3)
        
        # 等待服务启动
        logger.info(f"等待Java服务在端口 {args.java_port} 启动...")
        retry = MAX_RETRY
        while retry > 0:
            if check_service_running(args.java_port):
                logger.info(f"检测到Java服务正在监听端口 {args.java_port}")
                # 等待服务完全初始化
                time.sleep(2)
                break
            
            # 检查进程是否存在
            try:
                # 尝试查找Java进程
                find_process = f"ps -ef | grep '{jar_path}' | grep -v grep"
                process_check = subprocess.run(find_process, shell=True, stdout=subprocess.PIPE)
                if process_check.returncode != 0:
                    logger.error("找不到Java进程，可能启动失败")
                    logger.info(f"请查看日志文件: {java_log_file}")
                    processes['java'] = False
                    break
            except Exception as e:
                logger.error(f"检查Java进程时出错: {str(e)}")
                
            time.sleep(RETRY_INTERVAL)
            retry -= 1
            print_progress("正在启动Java后端", 60 + (MAX_RETRY - retry) * (40 / MAX_RETRY))
            
        if retry == 0:
            logger.error(f"等待Java服务启动超时")
            logger.info(f"请查看日志文件: {java_log_file}")
            processes['java'] = False
            # 不立即退出，继续启动其他服务
            
        if processes['java']:
            logger.info("Java后端启动成功")
            print_progress("正在启动Java后端", 100)
    
    # 启动Python后端
    if args.python_backend_only or args.backend_only or not (args.java_backend_only or args.frontend_only):
        print_progress("正在启动Python后端", 0)
        logger.info("准备启动Python后端...")
        
        # 检查Python环境
        requirements_path = os.path.join(python_backend_path, "requirements.txt")
        if os.path.exists(requirements_path):
            logger.info("检查Python依赖...")
            try:
                subprocess.run("pip install -r requirements.txt", 
                              shell=True, 
                              cwd=python_backend_path, 
                              check=True,
                              capture_output=not args.verbose)
                logger.info("Python依赖安装成功")
            except subprocess.CalledProcessError as e:
                logger.warning(f"安装Python依赖时出现警告: {str(e)}")
                
        python_command = f"python3 app.py --port={args.python_port}"
        # 如果Python后端也需要使用MySQL
        python_command += f" --mysql-user={MYSQL_USER} --mysql-password={MYSQL_PASSWORD} --mysql-database={MYSQL_DATABASE}"
        
        # 使用nohup后台方式启动Python应用
        python_log_file = os.path.join(base_path, f"python_backend_{datetime.now().strftime('%Y%m%d')}.log")
        nohup_command = f"nohup {python_command} > {python_log_file} 2>&1 &"
        
        logger.info(f"启动Python应用: {nohup_command}")
        subprocess.run(nohup_command, shell=True, cwd=python_backend_path)
        logger.info(f"Python后端已启动，日志输出到: {python_log_file}")
        
        # 修改processes字典，标记服务状态
        processes['python'] = True
        
        # 给Python进程一些时间启动
        time.sleep(2)
        
        # 等待服务启动
        logger.info(f"等待Python服务在端口 {args.python_port} 启动...")
        retry = MAX_RETRY
        while retry > 0:
            if check_service_running(args.python_port):
                logger.info(f"检测到Python服务正在监听端口 {args.python_port}")
                break
                
            # 检查进程是否存在
            try:
                # 尝试查找Python进程
                find_process = f"ps -ef | grep 'python3 app.py --port={args.python_port}' | grep -v grep"
                process_check = subprocess.run(find_process, shell=True, stdout=subprocess.PIPE)
                if process_check.returncode != 0:
                    logger.error("找不到Python进程，可能启动失败")
                    logger.info(f"请查看日志文件: {python_log_file}")
                    processes['python'] = False
                    break
            except Exception as e:
                logger.error(f"检查Python进程时出错: {str(e)}")
                
            time.sleep(RETRY_INTERVAL)
            retry -= 1
            print_progress("正在启动Python后端", (MAX_RETRY - retry) * (100 / MAX_RETRY))
            
        if retry == 0:
            logger.error(f"等待Python服务启动超时")
            logger.info(f"请查看日志文件: {python_log_file}")
            processes['python'] = False
            # 不立即退出，继续启动其他服务
            
        if processes['python']:
            logger.info("Python后端启动成功")
            print_progress("正在启动Python后端", 100)
    
    # 启动前端
    if args.frontend_only or not (args.java_backend_only or args.python_backend_only or args.backend_only):
        print_progress("正在启动前端", 0)
        logger.info("准备启动前端...")
        
        # 检查node_modules是否存在
        if not os.path.exists(os.path.join(frontend_path, "node_modules")):
            logger.info("安装前端依赖...")
            try:
                npm_install = subprocess.run("npm install", 
                                           shell=True, 
                                           cwd=frontend_path, 
                                           capture_output=not args.verbose)
                if npm_install.returncode != 0:
                    logger.error("安装前端依赖失败")
                    if not args.verbose:
                        logger.error(f"错误输出: {npm_install.stderr.decode()}")
                    sys.exit(1)
                logger.info("前端依赖安装成功")
            except Exception as e:
                logger.error(f"安装前端依赖时出错: {str(e)}")
                sys.exit(1)
        else:
            logger.info("前端依赖已安装")
            
        print_progress("正在启动前端", 50)
        
        # 生成.env文件配置API地址
        env_file = os.path.join(frontend_path, ".env")
        with open(env_file, "w") as f:
            f.write(f"REACT_APP_JAVA_API_URL=http://localhost:{args.java_port}/api\n")
            f.write(f"REACT_APP_PYTHON_API_URL=http://localhost:{args.python_port}/api\n")
        logger.info(f"已生成前端环境配置文件: {env_file}")
        
        # 启动前端应用
        browser_flag = "--no-browser" if args.no_browser else ""
        frontend_command = f"npm start {browser_flag}"
        
        if args.no_browser:
            # 使用nohup后台方式启动前端应用
            frontend_log_file = os.path.join(base_path, f"frontend_{datetime.now().strftime('%Y%m%d')}.log")
            nohup_command = f"nohup {frontend_command} > {frontend_log_file} 2>&1 &"
            
            logger.info(f"启动前端: {nohup_command}")
            subprocess.run(nohup_command, shell=True, cwd=frontend_path)
            logger.info(f"前端已启动，日志输出到: {frontend_log_file}")
            processes['frontend'] = True
        else:
            # 前台方式启动前端应用，以便自动打开浏览器
            logger.info(f"启动前端(前台模式): {frontend_command}")
            # 启动前端并自动打开浏览器
            frontend_process = run_command(frontend_command, cwd=frontend_path, verbose=args.verbose)
            processes['frontend'] = frontend_process
            
            # 自动打开浏览器作为备份方案
            try:
                time.sleep(5)  # 给前端一些启动时间
                # 尝试使用多种方式打开浏览器
                open_browser_commands = [
                    "xdg-open http://localhost:3000",
                    "sensible-browser http://localhost:3000",
                    "gnome-open http://localhost:3000",
                    "open http://localhost:3000",
                    "start http://localhost:3000"
                ]
                
                logger.info("尝试手动打开浏览器...")
                for cmd in open_browser_commands:
                    try:
                        subprocess.run(cmd, shell=True, timeout=2)
                        logger.info(f"已使用命令打开浏览器: {cmd}")
                        break
                    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                        continue
            except Exception as e:
                logger.warning(f"尝试自动打开浏览器失败: {e}")
                logger.info("请手动打开浏览器访问: http://localhost:3000")
        
        print_progress("正在启动前端", 100)
        print("\n前端已启动，请访问 http://localhost:3000")
    
    active_processes = sum(1 for status in processes.values() if status)
    if active_processes > 0:
        logger.info("\n所有服务已启动！")
        print("\n所有服务已启动！")
        
        # 收集日志文件信息
        java_log_file = os.path.join(base_path, f"java_backend_{datetime.now().strftime('%Y%m%d')}.log") if processes['java'] else None
        python_log_file = os.path.join(base_path, f"python_backend_{datetime.now().strftime('%Y%m%d')}.log") if processes['python'] else None
        frontend_log_file = os.path.join(base_path, f"frontend_{datetime.now().strftime('%Y%m%d')}.log") if isinstance(processes['frontend'], bool) else None
        
        # 再次确认所有服务状态
        print("\n验证服务状态...")
        # 检查Java服务
        if processes['java']:
            processes['java'] = check_service_running(args.java_port)
            if not processes['java']:
                logger.warning("Java服务可能未正确启动，端口未监听")
                
        # 检查Python服务
        if processes['python']:
            processes['python'] = check_service_running(args.python_port)
            if not processes['python']:
                logger.warning("Python服务可能未正确启动，端口未监听")
        
        # 打印服务信息概览
        print_services_info(processes, args.java_port, args.python_port, java_log_file, python_log_file, frontend_log_file)
        
        # 打印端口使用情况
        print("\n当前端口使用情况:")
        subprocess.run("netstat -tuln | grep -E '8080|5000|3000'", shell=True)
        
        print("按Ctrl+C停止所有服务")
        
        # 设置信号处理
        def signal_handler(sig, frame):
            print("\n正在停止所有服务...")
            logger.info("收到停止信号，开始终止所有服务...")
            
            # 停止Java服务
            if processes['java']:
                logger.info("停止Java服务...")
                try:
                    # 查找Java进程并终止
                    subprocess.run(f"pkill -f '{os.path.basename(jar_path)}'", shell=True)
                    logger.info("Java服务已停止")
                except Exception as e:
                    logger.error(f"停止Java服务时出错: {str(e)}")
            
            # 停止Python服务
            if processes['python']:
                logger.info("停止Python服务...")
                try:
                    # 查找Python进程并终止
                    subprocess.run(f"pkill -f 'python3 app.py --port={args.python_port}'", shell=True)
                    logger.info("Python服务已停止")
                except Exception as e:
                    logger.error(f"停止Python服务时出错: {str(e)}")
            
            # 停止前端服务
            if processes['frontend']:
                logger.info("停止前端服务...")
                try:
                    if isinstance(processes['frontend'], bool):
                        # 后台模式，使用pkill终止
                        subprocess.run("pkill -f 'npm start'", shell=True)
                    else:
                        # 前台模式，终止进程对象
                        processes['frontend'].terminate()
                        try:
                            processes['frontend'].wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            processes['frontend'].kill()
                    logger.info("前端服务已停止")
                except Exception as e:
                    logger.error(f"停止前端服务时出错: {str(e)}")
                    
            logger.info("所有服务已停止")
            print("所有服务已停止")
            sys.exit(0)
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 保持脚本运行直到用户中断
        try:
            last_status_print = time.time()
            status_update_interval = 30  # 每30秒更新一次状态
            
            while True:
                current_time = time.time()
                
                # 检查各服务是否还在运行
                # 检查Java服务
                if processes['java']:
                    java_running = check_service_running(args.java_port)
                    if not java_running:
                        # 尝试确认进程是否存在
                        try:
                            find_process = f"ps -ef | grep '{jar_path}' | grep -v grep"
                            process_check = subprocess.run(find_process, shell=True, stdout=subprocess.PIPE)
                            if process_check.returncode != 0:
                                # 进程不存在
                                processes['java'] = False
                                info_msg = "信息: Java服务已停止运行"
                                logger.info(info_msg)
                                print(f"\n{info_msg}")
                        except Exception as e:
                            logger.error(f"检查Java进程时出错: {str(e)}")
                
                # 检查Python服务
                if processes['python']:
                    python_running = check_service_running(args.python_port)
                    if not python_running:
                        # 尝试确认进程是否存在
                        try:
                            find_process = f"ps -ef | grep 'python3 app.py --port={args.python_port}' | grep -v grep"
                            process_check = subprocess.run(find_process, shell=True, stdout=subprocess.PIPE)
                            if process_check.returncode != 0:
                                # 进程不存在
                                processes['python'] = False
                                info_msg = "信息: Python服务已停止运行"
                                logger.info(info_msg)
                                print(f"\n{info_msg}")
                        except Exception as e:
                            logger.error(f"检查Python进程时出错: {str(e)}")
                
                # 检查前端服务
                if processes['frontend']:
                    # 确定前端运行模式
                    if isinstance(processes['frontend'], bool):
                        # 后台模式运行
                        try:
                            find_process = f"ps -ef | grep 'npm start' | grep -v grep"
                            process_check = subprocess.run(find_process, shell=True, stdout=subprocess.PIPE)
                            if process_check.returncode != 0:
                                # 进程不存在
                                processes['frontend'] = False
                                info_msg = "信息: 前端服务已停止运行"
                                logger.info(info_msg)
                                print(f"\n{info_msg}")
                        except Exception as e:
                            logger.error(f"检查前端进程时出错: {str(e)}")
                    else:
                        # 前台模式运行，检查进程对象
                        if processes['frontend'].poll() is not None:
                            # 进程已结束
                            returncode = processes['frontend'].returncode
                            if returncode != 0:
                                error_msg = f"警告: 前端服务异常停止，退出码: {returncode}"
                                logger.error(error_msg)
                                print(f"\n{error_msg}")
                            else:
                                info_msg = "信息: 前端服务已正常结束"
                                logger.info(info_msg)
                                print(f"\n{info_msg}")
                            processes['frontend'] = False
                
                # 检查是否所有服务都已停止
                if not any(processes.values()):
                    logger.info("所有服务已停止，脚本将退出")
                    print("\n所有服务已停止，脚本将退出")
                    break
                
                # 每隔一段时间更新并打印服务状态
                if current_time - last_status_print >= status_update_interval:
                    java_log_file = os.path.join(base_path, f"java_backend_{datetime.now().strftime('%Y%m%d')}.log") if processes['java'] else None
                    python_log_file = os.path.join(base_path, f"python_backend_{datetime.now().strftime('%Y%m%d')}.log") if processes['python'] else None
                    frontend_log_file = os.path.join(base_path, f"frontend_{datetime.now().strftime('%Y%m%d')}.log") if isinstance(processes['frontend'], bool) else None
                    
                    print("\n更新服务状态...")
                    print_services_info(processes, args.java_port, args.python_port, java_log_file, python_log_file, frontend_log_file)
                    last_status_print = current_time
                
                time.sleep(5)  # 检查间隔
        except KeyboardInterrupt:
            signal_handler(signal.SIGINT, None)
    else:
        logger.warning("没有启动任何服务")
        print("没有启动任何服务")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"程序执行过程中发生严重错误: {str(e)}", exc_info=True)
        print(f"错误: {str(e)}")
        sys.exit(1)
