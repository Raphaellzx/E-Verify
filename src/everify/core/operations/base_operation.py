"""
基础操作模型
定义所有操作的公共接口和基类
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path


class BaseOperation(ABC):
    """操作基类，定义所有操作的公共接口"""

    @abstractmethod
    def execute(self, *args, **kwargs):
        """执行操作的抽象方法"""
        pass


class OperationResult:
    """操作结果类，统一管理操作的执行结果"""

    def __init__(self, success: bool = False, data: Optional[Dict] = None, error: Optional[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error

    def to_dict(self) -> Dict:
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error
        }

    @classmethod
    def success_result(cls, data: Optional[Dict] = None) -> 'OperationResult':
        return cls(success=True, data=data)

    @classmethod
    def error_result(cls, error: str) -> 'OperationResult':
        return cls(success=False, error=error)
