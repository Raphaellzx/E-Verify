#!/usr/bin/env python3
"""
Everify 统一入口文件
负责程序启动和模式选择
"""

import sys
import argparse
from pathlib import Path

# 添加 src/everify 目录到系统路径，以便于导入模块
sys.path.insert(0, str(Path(__file__).parent))

from everify.core.utils.config import AppConfig
from everify.core.utils import logger


def main():
    """统一入口主函数"""
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

    config = AppConfig()

    if args.mode == 'web':
        # 运行Web界面模式
        try:
            if args.verbose:
                logger.info(f"启动Web服务 on {args.host}:{args.port}")

            from everify.web import app

            # 启动Flask应用 - 禁用自动重载以避免监视虚拟环境
            app.run(
                host=args.host,
                port=args.port,
                debug=True,
                use_reloader=False
            )

        except ImportError as e:
            logger.error(f"无法导入Flask应用 - {e}")
            logger.error("请确保已正确安装项目依赖: uv pip install -e .")
            sys.exit(1)
        except Exception as e:
            logger.error(f"启动Web服务失败 - {e}")
            if args.verbose:
                import traceback
                logger.error(traceback.format_exc())
            sys.exit(1)
    else:
        # 运行命令行模式
        try:
            if args.verbose:
                logger.info("启动命令行模式...")

            from everify.main import main as cli_main

            cli_main()

        except ImportError as e:
            logger.error(f"无法导入命令行模块 - {e}")
            logger.error("请确保已正确安装项目依赖: uv pip install -e .")
            sys.exit(1)
        except Exception as e:
            logger.error(f"命令行程序失败 - {e}")
            if args.verbose:
                import traceback
                logger.error(traceback.format_exc())
            sys.exit(1)


if __name__ == '__main__':
    main()
