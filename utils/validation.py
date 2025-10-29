"""
Модуль для валидации входных данных
"""
import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class InputValidator:
    """Класс для валидации пользовательского ввода"""
    
    # Максимальная длина сообщения
    MAX_MESSAGE_LENGTH = 4000
    
    # Разрешенные символы для participant_id
    PARTICIPANT_ID_PATTERN = re.compile(r'^P[A-F0-9]{8}$')
    
    # Разрешенные группы эксперимента
    ALLOWED_GROUPS = {'confess', 'silent'}
    
    # Разрешенные языки
    ALLOWED_LANGUAGES = {'en', 'ru', 'es', 'fr', 'de', 'zh', 'ja', 'ar'}
    
    @staticmethod
    def validate_message(message: str) -> Dict[str, Any]:
        """
        Валидирует сообщение пользователя
        
        Args:
            message: Сообщение для валидации
            
        Returns:
            Словарь с результатом валидации
        """
        result = {
            'is_valid': True,
            'errors': [],
            'sanitized_message': message
        }
        
        if not message:
            result['is_valid'] = False
            result['errors'].append('Сообщение не может быть пустым')
            return result
        
        # Проверка длины
        if len(message) > InputValidator.MAX_MESSAGE_LENGTH:
            result['is_valid'] = False
            result['errors'].append(f'Сообщение слишком длинное (максимум {InputValidator.MAX_MESSAGE_LENGTH} символов)')
            result['sanitized_message'] = message[:InputValidator.MAX_MESSAGE_LENGTH]
        
        # Проверка на потенциально опасные паттерны
        dangerous_patterns = [
            r'<script.*?>.*?</script>',  # XSS
            r'javascript:',  # JavaScript injection
            r'data:text/html',  # Data URI injection
            r'vbscript:',  # VBScript injection
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                result['is_valid'] = False
                result['errors'].append('Сообщение содержит потенциально опасный контент')
                break
        
        # Базовая санитизация
        result['sanitized_message'] = re.sub(r'[<>]', '', result['sanitized_message'])
        
        return result
    
    @staticmethod
    def validate_participant_id(participant_id: str) -> bool:
        """
        Валидирует ID участника
        
        Args:
            participant_id: ID участника
            
        Returns:
            True если ID валиден
        """
        if not participant_id:
            return False
        
        return bool(InputValidator.PARTICIPANT_ID_PATTERN.match(participant_id))
    
    @staticmethod
    def validate_experiment_group(group: str) -> bool:
        """
        Валидирует группу эксперимента
        
        Args:
            group: Группа эксперимента
            
        Returns:
            True если группа валидна
        """
        return group in InputValidator.ALLOWED_GROUPS
    
    @staticmethod
    def validate_language(language: str) -> bool:
        """
        Валидирует код языка
        
        Args:
            language: Код языка
            
        Returns:
            True если язык поддерживается
        """
        return language in InputValidator.ALLOWED_LANGUAGES
    
    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        """
        Валидирует Telegram user ID
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            True если ID валиден
        """
        return isinstance(user_id, int) and user_id > 0
    
    @staticmethod
    def validate_survey_response(response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Валидирует ответ на опрос
        
        Args:
            response: Ответы на опрос
            
        Returns:
            Словарь с результатом валидации
        """
        result = {
            'is_valid': True,
            'errors': [],
            'sanitized_response': response.copy()
        }
        
        # Валидация question_1
        if 'question_1' in response:
            if response['question_1'] not in ['yes', 'no']:
                result['is_valid'] = False
                result['errors'].append('Неверный ответ на вопрос 1')
        
        # Валидация question_2
        if 'question_2' in response:
            if response['question_2'] not in ['helpful', 'manipulative', 'unsure']:
                result['is_valid'] = False
                result['errors'].append('Неверный ответ на вопрос 2')
        
        # Валидация question_3 (уровень уверенности)
        if 'question_3' in response:
            try:
                confidence = int(response['question_3'])
                if confidence < 1 or confidence > 5:
                    result['is_valid'] = False
                    result['errors'].append('Уровень уверенности должен быть от 1 до 5')
                else:
                    result['sanitized_response']['question_3'] = confidence
            except (ValueError, TypeError):
                result['is_valid'] = False
                result['errors'].append('Неверный формат уровня уверенности')
        
        # Валидация question_4 (текстовый ответ)
        if 'question_4' in response:
            message_validation = InputValidator.validate_message(str(response['question_4']))
            if not message_validation['is_valid']:
                result['is_valid'] = False
                result['errors'].extend(message_validation['errors'])
            result['sanitized_response']['question_4'] = message_validation['sanitized_message']
        
        return result
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Санитизирует имя файла
        
        Args:
            filename: Исходное имя файла
            
        Returns:
            Санитизированное имя файла
        """
        # Удаляем опасные символы
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Ограничиваем длину
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
