#!/usr/bin/env python3
"""
Everify 网页核查自动化系统 - 主入口文件
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description='Everify 网页核查自动化系统'
    )

    parser.add_argument(
        '-m', '--mode',
        choices=['web', 'cli'],
        default='cli',
        help='运行模式: web(Web界面) 或 cli(命令行)'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=5000,
        help='Web服务端口 (默认: 5000)'
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Web服务主机地址 (默认: 0.0.0.0)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细信息'
    )

    args = parser.parse_args()

    if args.verbose:
        print("=== Everify 网页核查自动化系统 ===")

    if args.mode == 'web':
        # Web界面模式
        run_web_mode(args.host, args.port, args.verbose)
    else:
        # 命令行模式
        run_cli_mode(args.verbose)

def run_web_mode(host: str, port: int, verbose: bool = False):
    """运行Web界面模式"""
    try:
        if verbose:
            print(f"启动Web服务 on {host}:{port}")

        # 导入Flask应用
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

        from everify.web import app

        # 启动Flask应用 - 禁用自动重载以避免监视虚拟环境
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=False
        )

    except ImportError as e:
        print(f"错误: 无法导入Flask应用 - {e}")
        print("请确保已正确安装项目依赖: uv pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 启动Web服务失败 - {e}")
        if verbose:
            import traceback
            print(traceback.format_exc())
        sys.exit(1)

def run_cli_mode(verbose: bool = False):
    """运行命令行模式"""
    try:
        if verbose:
            print("启动命令行模式...")

        # 导入主程序
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

        from everify.main import main

        main()

    except ImportError as e:
        print(f"错误: 无法导入命令行模块 - {e}")
        print("请确保已正确安装项目依赖: uv pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 命令行程序失败 - {e}")
        if verbose:
            import traceback
            print(traceback.format_exc())
        sys.exit(1)

def start_browser_mode():
    """启动浏览器模式（打开默认浏览器）"""
    import webbrowser
    import time

    # 启动Web服务在后台
    process = subprocess.Popen([
        sys.executable, __file__, '--mode=web'
    ])

    # 等待服务器启动
    time.sleep(2)

    # 打开浏览器
    webbrowser.open('http://127.0.0.1:5000')

    print("Web服务已启动，请在浏览器中访问: http://127.0.0.1:5000")

    # 等待进程结束
    process.wait()

if __name__ == '__main__':
    main()
