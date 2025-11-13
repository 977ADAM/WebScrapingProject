import os
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class AdParserConfig:
    # Настройки браузера
    HEADLESS: bool = True
    WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
    PAGE_LOAD_TIMEOUT: int = 15
    SCRIPT_TIMEOUT: int = 10
    
    # Настройки обнаружения рекламы
    AD_SELECTORS: List[str] = None
    AD_NETWORKS: List[str] = None
    STANDARD_AD_SIZES: List[Tuple[int, int]] = None
    
    # Настройки скриншотов
    SCREENSHOT_QUALITY: int = 85
    ANNOTATION_COLOR: Tuple[int, int, int] = (255, 0, 0)  # Красный
    ANNOTATION_THICKNESS: int = 3
    
    # Настройки отчетов
    OUTPUT_FORMATS: List[str] = None
