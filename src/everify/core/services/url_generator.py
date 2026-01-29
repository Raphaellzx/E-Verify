#!/usr/bin/env python3
"""
URL生成服务模块
负责根据主体和模板生成待核查的URL列表
"""
from typing import Dict, List
from everify.core.utils import logger
from everify.core.utils.config import VerifyTemplate


class URLGenerator:
    """URL生成服务"""

    @staticmethod
    def generate_verify_urls(
        entities: List[str],
        templates: Dict[str, VerifyTemplate]
    ) -> Dict[str, List[str]]:
        """根据主体和模板生成需要核查的 URL 列表

        Args:
            entities: 主体列表
            templates: 核查模板字典

        Returns:
            dict: {主体名称: [URL1, URL2, ...]}
        """
        entity_urls = {}

        for entity in entities:
            urls = []
            for template_name, template in templates.items():
                try:
                    url = URLGenerator._generate_single_url(entity, template)
                    if url:
                        urls.append(url)
                except Exception as e:
                    logger.error(f"为主体 '{entity}' 生成模板 '{template_name}' 的URL失败: {e}")

            if urls:
                entity_urls[entity] = urls
                logger.debug(f"主体 '{entity}' 生成 {len(urls)} 个核查URL")

        logger.info(f"共为 {len(entity_urls)} 个主体生成核查URL")
        return entity_urls

    @staticmethod
    def _generate_single_url(entity: str, template: VerifyTemplate) -> str:
        """为单个主体和模板生成URL

        Args:
            entity: 主体名称
            template: 核查模板

        Returns:
            str: 生成的URL
        """
        if not template.url_pattern or "{}" not in template.url_pattern:
            logger.warning(f"模板 '{template.name}' 的URL模式无效: {template.url_pattern}")
            return ""

        # 对主体名称进行URL编码
        try:
            import urllib.parse
            encoded_entity = urllib.parse.quote(str(entity))
            url = template.url_pattern.replace("{}", encoded_entity)
            return url
        except Exception as e:
            logger.error(f"编码主体名称 '{entity}' 失败: {e}")
            return ""

    @staticmethod
    def validate_urls(urls: List[str]) -> List[str]:
        """验证URL的有效性

        Args:
            urls: 待验证的URL列表

        Returns:
            list: 有效的URL列表
        """
        valid_urls = []
        for url in urls:
            if URLGenerator._is_url_valid(url):
                valid_urls.append(url)
            else:
                logger.warning(f"无效的URL: {url}")
        return valid_urls

    @staticmethod
    def _is_url_valid(url: str) -> bool:
        """验证单个URL的有效性

        Args:
            url: URL地址

        Returns:
            bool: 是否有效
        """
        import re
        url_pattern = re.compile(
            r'^(?:http|https)://'  # 必须以http或https开头
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # 域名部分
            r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # 域名后缀
            r'localhost|'  # 本地地址
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
            r'(?::\d+)?'  # 可选的端口号
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return bool(url_pattern.match(url))
