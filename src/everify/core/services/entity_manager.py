#!/usr/bin/env python3
"""
主体管理服务模块
负责主体信息的收集、管理和验证
"""
from typing import List, Optional
from everify.core.utils import logger


class EntityManager:
    """主体管理服务"""

    @staticmethod
    def get_entities_from_input() -> List[str]:
        """从命令行输入获取需要核查的主体列表

        用户输入主体名称，回车确认，输入 # 停止

        Returns:
            list: 主体名称列表
        """
        entities = []
        logger.info("请输入需要核查的主体名称（输入 # 停止）：")
        while True:
            entity = input().strip()
            if entity == "#":
                break
            if entity:
                entities.append(entity)
        return entities

    @staticmethod
    def validate_entities(entities: List[str]) -> List[str]:
        """验证主体列表的有效性

        Args:
            entities: 原始主体列表

        Returns:
            list: 验证后的主体列表
        """
        validated = []
        for entity in entities:
            entity = entity.strip()
            if entity and len(entity) <= 100:  # 合理的长度限制
                validated.append(entity)
            else:
                logger.warning(f"无效的主体名称: {entity}")
        return validated

    @staticmethod
    def load_entities_from_file(file_path: str) -> List[str]:
        """从文件加载主体列表

        Args:
            file_path: 文件路径

        Returns:
            list: 主体名称列表
        """
        entities = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    entity = line.strip()
                    if entity:
                        entities.append(entity)
            logger.info(f"从文件成功加载 {len(entities)} 个主体")
        except Exception as e:
            logger.error(f"加载主体文件失败: {e}")
        return entities
