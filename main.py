"""
Основной файл Telegram бота для эксперимента по дилемме заключенного
Поддерживает как базовый режим, так и режим с LLM интеграцией
"""
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config.settings import Config
from utils.validation import InputValidator
from handlers.experiment_handler import ExperimentHandler
from handlers.llm_experiment_handler import LLMExperimentHandler
from handlers.survey_handler import SurveyHandler
from handlers.admin_handler import AdminHandler
from utils.database import DatabaseManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PrisonersDilemmaBot:
    """Основной класс бота для эксперимента"""
    
    def __init__(self):
        # Валидируем конфигурацию при инициализации
        try:
            Config.validate()
            logger.info("Конфигурация валидна")
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            raise
        
        self.config = Config()
        self.db = DatabaseManager()
        self.validator = InputValidator()
        
        self.survey_handler = SurveyHandler(self.db, None)  # Сначала создаем без experiment_handler
        
        # Выбираем обработчик эксперимента в зависимости от настроек
        if Config.LLM_ENABLED:
            logger.info("Инициализация бота с LLM поддержкой")
            self.experiment_handler = LLMExperimentHandler(self.survey_handler)
        else:
            logger.info("Инициализация бота в базовом режиме")
            self.experiment_handler = ExperimentHandler()
        
        # Устанавливаем experiment_handler в survey_handler
        self.survey_handler.experiment_handler = self.experiment_handler
        self.admin_handler = AdminHandler()
        
        # Инициализируем активные сессии
        self.active_sessions = getattr(self.experiment_handler, 'active_sessions', {})
    
    async def start_command(self, update: Update, context):
        """Обработчик команды /start"""
        try:
            # Валидируем пользователя
            user_id = update.effective_user.id
            if not self.validator.validate_user_id(user_id):
                await update.message.reply_text("❌ Ошибка: неверный ID пользователя")
                return
            
            await self.experiment_handler.start_experiment(update, context)
        except Exception as e:
            logger.error(f"Ошибка в команде /start: {e}")
            await update.message.reply_text("❌ Произошла ошибка при запуске эксперимента")
    
    async def help_command(self, update: Update, context):
        """Обработчик команды /help"""
        help_text = """
🤖 **Prisoner's Dilemma Experiment Bot**

**Доступные команды:**
/start - Начать эксперимент
/help - Показать эту справку
/status - Показать статус эксперимента
/admin - Админские команды (только для администраторов)

**О эксперименте:**
Это исследование по дилемме заключенного с использованием ИИ для анализа ваших сообщений.
Эксперимент длится 5 минут, после чего вы получите опрос.

**Приватность:**
Все ваши сообщения анонимизированы и используются только для научных целей.

**Тестирование:**
Администраторы могут проходить эксперимент несколько раз для тестирования.
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def status_command(self, update: Update, context):
        """Обработчик команды /status"""
        try:
            if hasattr(self.experiment_handler, 'get_experiment_status'):
                await self.experiment_handler.get_experiment_status(update, context)
            else:
                # Fallback для базового обработчика
                user_id = update.effective_user.id
                if user_id in self.active_sessions:
                    session_data = self.active_sessions[user_id]
                    status_text = f"""
📊 Статус эксперимента:
👤 Группа: {session_data.get('group', 'неизвестно')}
🌍 Язык: {session_data.get('language', 'неизвестно')}
💬 Сообщений: {session_data.get('message_count', 0)}
"""
                    await update.message.reply_text(status_text)
                else:
                    await update.message.reply_text("Вы не участвуете в эксперименте.")
        except Exception as e:
            logger.error(f"Ошибка в команде /status: {e}")
            await update.message.reply_text("❌ Ошибка при получении статуса")
    
    async def admin_command(self, update: Update, context):
        """Обработчик админских команд"""
        try:
            await self.admin_handler.handle_admin_command(update, context)
        except Exception as e:
            logger.error(f"Ошибка в админской команде: {e}")
            await update.message.reply_text("❌ Ошибка при выполнении админской команды")
    
    
    async def handle_message(self, update: Update, context):
        """Обработчик обычных сообщений с валидацией"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            # Валидируем сообщение
            validation_result = self.validator.validate_message(message_text)
            if not validation_result['is_valid']:
                logger.warning(f"Невалидное сообщение от пользователя {user_id}: {validation_result['errors']}")
                await update.message.reply_text("❌ Сообщение содержит недопустимый контент")
                return
            
            # Используем санитизированное сообщение
            sanitized_message = validation_result['sanitized_message']
            if sanitized_message != message_text:
                logger.info(f"Сообщение от пользователя {user_id} было санитизировано")
            
            # Проверяем, не находится ли пользователь в процессе опроса
            if user_id in self.survey_handler.survey_sessions:
                survey_data = self.survey_handler.survey_sessions[user_id]
                if survey_data.get('waiting_for_text', False):
                    await self.survey_handler.handle_survey_response(update, context)
                    return
            
            # Проверяем команды завершения эксперимента
            if sanitized_message.lower() in ['/end', '/finish', '/stop', 'завершить', 'закончить', 'стоп', 'хватит']:
                if user_id in self.active_sessions:
                    if hasattr(self.experiment_handler, '_end_experiment'):
                        await self.experiment_handler._end_experiment(update, context, user_id)
                    else:
                        await update.message.reply_text("Эксперимент завершен. Спасибо за участие!")
                    return
                else:
                    await update.message.reply_text("Вы не участвуете в эксперименте. Используйте /start для начала.")
                    return
            
            # Обычная обработка сообщений эксперимента
            await self.experiment_handler.handle_user_message(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке сообщения")
    
    async def handle_callback(self, update: Update, context):
        """Обработчик callback запросов"""
        try:
            query = update.callback_query
            
            try:
                await query.answer()
            except Exception as e:
                logger.warning(f"Не удалось ответить на callback query: {e}")
            
            data = query.data
            
            # Валидируем callback data
            if not data or len(data) > 100:
                logger.warning(f"Подозрительный callback data: {data}")
                await query.edit_message_text("❌ Неверная команда")
                return
            
            if data.startswith('lang_'):
                await self.experiment_handler.handle_language_selection(update, context)
            elif data.startswith('start_discussion_'):
                await self.experiment_handler.handle_start_discussion(update, context)
            elif data.startswith('survey_'):
                await self.survey_handler.handle_survey_response(update, context)
            elif data.startswith('final_decision_'):
                await self.experiment_handler.handle_final_decision(update, context)
            elif data.startswith('decision_'):
                await self.experiment_handler.handle_decision(update, context)
            else:
                logger.warning(f"Неизвестный callback data: {data}")
                await query.edit_message_text("❌ Неизвестная команда")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback: {e}")
            try:
                await query.edit_message_text("❌ Произошла ошибка при обработке команды")
            except:
                pass
    
    def run_polling(self):
        """Запускает бота в режиме polling"""
        logger.info("Запуск бота в режиме polling...")
        
        # Создаем приложение
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def run_webhook(self):
        """Запускает бота в режиме webhook"""
        logger.info("Запуск бота в режиме webhook...")
        
        # Создаем приложение
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Настраиваем webhook
        if self.config.WEBHOOK_URL:
            application.run_webhook(
                listen="0.0.0.0",
                port=self.config.WEBHOOK_PORT,
                webhook_url=self.config.WEBHOOK_URL
            )
        else:
            # Если webhook URL не настроен, используем polling
            logger.info("Webhook URL не настроен, переключаемся на polling...")
            application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Главная функция"""
    try:
        logger.info("Запуск Prisoner's Dilemma Bot...")
        
        # Создаем экземпляр бота
        bot = PrisonersDilemmaBot()
        
        # Определяем режим запуска
        if Config.WEBHOOK_URL:
            bot.run_webhook()
        else:
            bot.run_polling()
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == '__main__':
    main()
