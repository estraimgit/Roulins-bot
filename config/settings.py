"""
Конфигурационные настройки для экспериментального бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Основные настройки приложения"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 8443))
    
    # База данных
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/experiment.db')
    
    # Безопасность
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
    
    # Эксперимент
    EXPERIMENT_DURATION_MINUTES = int(os.getenv('EXPERIMENT_DURATION_MINUTES', 5))
    TOTAL_PARTICIPANTS = int(os.getenv('TOTAL_PARTICIPANTS', 100))
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')
    
    # NLP сервисы
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    # LLM Configuration
    CLOUD_RU_API_KEY = os.getenv('CLOUD_RU_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'GigaChat/GigaChat-2-Max')
    LLM_ENABLED = os.getenv('LLM_ENABLED', 'true').lower() == 'true'
    LLM_ANALYSIS_ENABLED = os.getenv('LLM_ANALYSIS_ENABLED', 'true').lower() == 'true'
    LLM_SYSTEM_PROMPT = os.getenv('LLM_SYSTEM_PROMPT', 'Ты эксперт по анализу человеческого поведения в экспериментах. Анализируй сообщения и возвращай результат в формате JSON.')
    
    # Admin Configuration
    ADMIN_USER_IDS = os.getenv('ADMIN_USER_IDS', '').split(',') if os.getenv('ADMIN_USER_IDS') else []
    ALLOW_MULTIPLE_SESSIONS = os.getenv('ALLOW_MULTIPLE_SESSIONS', 'false').lower() == 'true'
    TESTING_MODE = os.getenv('TESTING_MODE', 'false').lower() == 'true'
    
    # Поддерживаемые языки
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'ru': 'Русский',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'zh': '中文',
        'ja': '日本語',
        'ar': 'العربية'
    }
    
    # Группы эксперимента
    EXPERIMENT_GROUPS = {
        'confess': 'Group A - Nudge to Confess',
        'silent': 'Group B - Nudge to Remain Silent'
    }
    
    # Время предупреждения (в минутах до окончания)
    WARNING_TIME_MINUTES = 1
    
    @classmethod
    def validate(cls):
        """Проверяет корректность конфигурации"""
        errors = []
        
        # Проверка обязательных параметров
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN не установлен")
        
        if not cls.ENCRYPTION_KEY:
            errors.append("ENCRYPTION_KEY не установлен")
        elif len(cls.ENCRYPTION_KEY) < 32:
            errors.append("ENCRYPTION_KEY должен быть не менее 32 символов")
        
        # Проверка числовых параметров
        if cls.EXPERIMENT_DURATION_MINUTES <= 0:
            errors.append("EXPERIMENT_DURATION_MINUTES должен быть больше 0")
        
        if cls.TOTAL_PARTICIPANTS <= 0:
            errors.append("TOTAL_PARTICIPANTS должен быть больше 0")
        
        # Проверка webhook настроек
        if cls.WEBHOOK_URL and not cls.WEBHOOK_URL.startswith('https://'):
            errors.append("WEBHOOK_URL должен использовать HTTPS")
        
        if cls.WEBHOOK_PORT < 1 or cls.WEBHOOK_PORT > 65535:
            errors.append("WEBHOOK_PORT должен быть в диапазоне 1-65535")
        
        if errors:
            raise ValueError(f"Ошибки конфигурации: {'; '.join(errors)}")
        
        return True
