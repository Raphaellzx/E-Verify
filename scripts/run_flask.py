#!/usr/bin/env python3
"""
Flask应用启动脚本
"""

import sys
import os
import subprocess

def main():
    """启动Flask应用"""
    # 添加src和web目录到Python路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    src_path = os.path.join(project_root, 'src')
    web_path = os.path.join(project_root, 'web')

    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    if web_path not in sys.path:
        sys.path.insert(0, web_path)

    try:
        from web.app import app
        print('=== Everify 网页核查自动化系统 ===')
        print(f'启动Flask应用...')
        print(f'访问地址: http://127.0.0.1:5000')
        print(f'按 Ctrl+C 停止服务')
        print('=' * 40)

        app.run(debug=True, host='0.0.0.0', port=5000)

    except ImportError as e:
        print(f'错误: 导入模块失败 - {e}')
        print('请确保已正确安装依赖: uv pip install -e .')
    except Exception as e:
        print(f'错误: 启动失败 - {e}')
        import traceback
        print(f'\n详细错误信息:')
        print(traceback.format_exc())

if __name__ == '__main__':
    main()
