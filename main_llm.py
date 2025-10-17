"""
Главный файл для запуска бота с LLM интеграцией
"""

import logging
import asyncio
import json
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import Config
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

class LLMPrisonersDilemmaBot:
    """Основной класс бота с LLM интеграцией"""
    
    def __init__(self):
        self.config = Config()
        self.db = DatabaseManager()
        self.experiment_handler = LLMExperimentHandler()
        self.survey_handler = SurveyHandler(self.db)
        self.admin_handler = AdminHandler()
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await self.experiment_handler.start_experiment(update, context)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
🤖 **Prisoner's Dilemma Experiment Bot**

**Доступные команды:**
/start - Начать эксперимент
/help - Показать эту справку
/status - Показать статус эксперимента
/llm_status - Показать статус LLM анализа
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
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        await self.experiment_handler.get_experiment_status(update, context)
    
    async def llm_status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /llm_status"""
        user_id = update.effective_user.id
        
        if user_id not in self.experiment_handler.active_sessions:
            await update.message.reply_text("Вы не участвуете в эксперименте.")
            return
        
        session_data = self.experiment_handler.active_sessions[user_id]
        
        # Получаем данные LLM анализа
        llm_data = await self.db.get_llm_analysis_data(session_data['participant_id'])
        
        status_text = f"""
🧠 **LLM Анализ статус:**

📊 **Общая информация:**
• Участник: {session_data['participant_id']}
• Группа: {session_data['group']}
• Сообщений проанализировано: {len(llm_data)}

🔍 **Последний анализ:**
"""
        
        if llm_data:
            last_analysis = llm_data[-1]
            analysis = json.loads(last_analysis['analysis_json'])
            
            status_text += f"""
• Эмоция: {analysis.get('emotion', 'неизвестно')}
• Намерение: {analysis.get('intent', 'неизвестно')}
• Уверенность: {analysis.get('confidence', 'неизвестно')}
• Сопротивление убеждению: {analysis.get('persuasion_resistance', 'неизвестно')}
• Эффективность нуджинга: {analysis.get('nudging_effectiveness', 'неизвестно')}
• Риск выхода: {analysis.get('risk_of_dropout', 'неизвестно')}
"""
        else:
            status_text += "• Анализ еще не проводился"
        
        await update.message.reply_text(status_text)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик админских команд"""
        await self.admin_handler.handle_admin_command(update, context)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('lang_'):
            # Обрабатываем выбор языка
            await self.experiment_handler.handle_language_selection(update, context)
        elif data.startswith('survey_'):
            # Обрабатываем ответы на опрос
            await self.survey_handler.handle_survey_response(update, context)
        elif data.startswith('final_decision_'):
            # Обрабатываем финальное решение
            await self.experiment_handler.handle_final_decision(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Проверяем, не находится ли пользователь в процессе опроса
        if user_id in self.survey_handler.survey_sessions:
            survey_data = self.survey_handler.survey_sessions[user_id]
            if survey_data.get('waiting_for_text', False):
                await self.survey_handler.handle_survey_response(update, context)
                return
        
        # Проверяем команды завершения эксперимента
        if message_text.lower() in ['/end', '/finish', '/stop', 'завершить', 'закончить', 'стоп', 'хватит']:
            if user_id in self.experiment_handler.active_sessions:
                await self.experiment_handler._end_experiment(update, context, user_id)
                return
            else:
                await update.message.reply_text("Вы не участвуете в эксперименте. Используйте /start для начала.")
                return
        
        # Обычная обработка сообщений эксперимента
        await self.experiment_handler.handle_user_message(update, context)
    
    def run_polling(self):
        """Запускает бота в режиме polling"""
        logger.info("Запуск бота в режиме polling...")
        
        # Создаем приложение с JobQueue
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("llm_status", self.llm_status_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    def run_webhook(self):
        """Запускает бота в режиме webhook"""
        logger.info("Запуск бота в режиме webhook...")
        
        # Создаем приложение с JobQueue
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("llm_status", self.llm_status_command))
        application.add_handler(CommandHandler("admin", self.admin_command))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_message))
        
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
        # Проверяем конфигурацию
        Config.validate()
        
        # Создаем экземпляр бота
        bot = LLMPrisonersDilemmaBot()
        
        # Определяем режим запуска
        if Config.WEBHOOK_URL:
            bot.run_webhook()
        else:
            bot.run_polling()
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()
