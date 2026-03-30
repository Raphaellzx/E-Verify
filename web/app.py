#!/usr/bin/env python3
"""
Everify Flask 应用 - 向后兼容性入口
转发到 src/everify/web.py
"""
from everify.web import app, main

if __name__ == '__main__':
    main()
