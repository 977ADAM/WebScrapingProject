

from CONFIG import AdParserConfig


class AdDetector:
    """Модуль обнаружения рекламных элементов"""
    def __init__(self, config):
        self.config = config or AdParserConfig()
        self.detected_ads = []

