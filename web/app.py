#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Everify Flask 应用 - 向后兼容性入口
转发到 src/everify/web.py
"""
import sys
import os

# 添加 src 目录到系统路径 - 当前脚本在 web/ 目录，src 目录在项目根目录
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from everify.web import app, main
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"当前 Python 路径: {sys.path}")
    raise

if __name__ == '__main__':
    main()
