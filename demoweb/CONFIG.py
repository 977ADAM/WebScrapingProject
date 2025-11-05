import os
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class AdParserConfig:
    # Настройки браузера
    HEADLESS: bool = True
    WINDOW_SIZE: Tuple[int, int] = (1920, 1080)
    PAGE_LOAD_TIMEOUT: int = 30
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
    
    def __post_init__(self):
        if self.AD_SELECTORS is None:
            self.AD_SELECTORS = [
                'div.banner__content'
            ]
        
        if self.AD_NETWORKS is None:
            self.AD_NETWORKS = [
                'googleads', 'doubleclick', 'googlesyndication',
                'yandex.ru/ads', 'adfox', 'myarget', 'vk.com/ads',
                'facebook.com/ads', 'amazon-adsystem'
            ]
        
        if self.STANDARD_AD_SIZES is None:
            self.STANDARD_AD_SIZES = [
                (300, 250),   # Medium Rectangle
                (728, 90),    # Leaderboard
                (160, 600),   # Skyscraper
                (300, 600),   # Half Page
                (970, 250),   # Large Leaderboard
                (320, 50),    # Mobile Banner
                (320, 100),   # Large Mobile Banner
                (468, 60),    # Banner
                (234, 60),    # Half Banner
                (120, 600),   # Skyscraper
                (120, 240),   # Vertical Banner
                (250, 250),   # Square
                (200, 200),   # Small Square
                (180, 150),   # Small Rectangle
                (125, 125),   # Button
                (240, 400),   # Vertical Rectangle
                (336, 280),   # Large Rectangle
                (300, 100),   # 3:1 Rectangle
                (720, 300),   # Pop-Under
                (300, 1050),  # Portrait
                (970, 90),    # Large Leaderboard
                (970, 66),    # Large Leaderboard
                (418, 60),    # Super Banner
                (300, 50),    # Mobile Banner
                (320, 480),   # Mobile Interstitial
            ]
        
        if self.OUTPUT_FORMATS is None:
            self.OUTPUT_FORMATS = ['json']