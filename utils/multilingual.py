"""
Модуль для многоязычной поддержки
"""
import logging
from typing import Dict, Optional
from langdetect import detect, LangDetectException

from config.settings import Config

logger = logging.getLogger(__name__)

class MultilingualManager:
    """Менеджер для работы с многоязычностью"""
    
    def __init__(self):
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.default_language = 'en'
    
    def detect_language(self, text: str) -> str:
        """
        Определяет язык текста
        
        Args:
            text: Текст для определения языка
            
        Returns:
            Код языка или 'en' по умолчанию
        """
        try:
            if not text or len(text.strip()) < 3:
                return self.default_language
            
            detected = detect(text)
            
            # Проверяем, поддерживается ли обнаруженный язык
            if detected in self.supported_languages:
                return detected
            
            # Если язык не поддерживается, возвращаем английский
            return self.default_language
            
        except LangDetectException as e:
            logger.warning(f"Не удалось определить язык текста: {e}")
            return self.default_language
        except Exception as e:
            logger.error(f"Ошибка определения языка: {e}")
            return self.default_language
    
    def translate_text(self, text: str, target_language: str, source_language: str = None) -> str:
        """
        Переводит текст на целевой язык (заглушка - переводы отключены)
        
        Args:
            text: Текст для перевода
            target_language: Целевой язык
            source_language: Исходный язык (опционально)
            
        Returns:
            Исходный текст (переводы отключены)
        """
        # Временно отключаем переводы для упрощения развертывания
        # В будущем можно добавить Google Translate API или другой сервис
        logger.info(f"Перевод отключен. Возвращаем исходный текст: {text[:50]}...")
        return text
    
    def get_language_name(self, language_code: str) -> str:
        """
        Получает название языка по коду
        
        Args:
            language_code: Код языка
            
        Returns:
            Название языка
        """
        return self.supported_languages.get(language_code, language_code)
    
    def is_language_supported(self, language_code: str) -> bool:
        """
        Проверяет, поддерживается ли язык
        
        Args:
            language_code: Код языка
            
        Returns:
            True если язык поддерживается
        """
        return language_code in self.supported_languages
    
    def get_supported_languages_list(self) -> Dict[str, str]:
        """
        Возвращает список поддерживаемых языков
        
        Returns:
            Словарь с кодами и названиями языков
        """
        return self.supported_languages.copy()
