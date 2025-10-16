"""
Основной файл Telegram бота для эксперимента по дилемме заключенного
"""
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config.settings import Config
from handlers.experiment_handler import ExperimentHandler

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
        self.config = Config()
        self.experiment_handler = ExperimentHandler()
        
        # Валидируем конфигурацию
        try:
            self.config.validate()
        except ValueError as e:
            logger.error(f"Ошибка конфигурации: {e}")
            raise
    
    async def start_command(self, update: Update, context):
        """Обработчик команды /start"""
        await self.experiment_handler.start_experiment(update, context)
    
    async def help_command(self, update: Update, context):
        """Обработчик команды /help"""
        help_text = """
🤖 Бот для эксперимента по дилемме заключенного

Доступные команды:
/start - Начать эксперимент
/help - Показать эту справку
/status - Показать статистику эксперимента (только для администраторов)

Этот бот проводит исследование этических решений в контексте дилеммы заключенного.
Эксперимент займет примерно 5 минут вашего времени.

Для начала введите /start
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context):
        """Обработчик команды /status (только для администраторов)"""
        # Здесь можно добавить проверку прав администратора
        user_id = update.effective_user.id
        
        # Простая проверка - в реальном проекте используйте более надежную систему
        admin_ids = [123456789]  # Замените на реальные ID администраторов
        
        if user_id not in admin_ids:
            await update.message.reply_text("У вас нет прав для выполнения этой команды.")
            return
        
        # Получаем статистику
        stats = self.experiment_handler.db.get_experiment_statistics()
        
        status_text = f"""
📊 Статистика эксперимента:

👥 Всего участников: {stats.get('total_participants', 0)}

📈 Распределение по группам:
{self._format_group_stats(stats.get('group_distribution', {}))}

🌍 Распределение по языкам:
{self._format_language_stats(stats.get('language_distribution', {}))}

🎯 Финальные решения:
{self._format_decision_stats(stats.get('decision_distribution', {}))}

🔄 Активных сессий: {len(self.experiment_handler.active_sessions)}
        """
        
        await update.message.reply_text(status_text)
    
    def _format_group_stats(self, group_dist: dict) -> str:
        """Форматирует статистику по группам"""
        if not group_dist:
            return "Нет данных"
        
        result = []
        for group, count in group_dist.items():
            group_name = "Признание" if group == "confess" else "Молчание"
            result.append(f"  {group_name}: {count}")
        
        return "\n".join(result)
    
    def _format_language_stats(self, lang_dist: dict) -> str:
        """Форматирует статистику по языкам"""
        if not lang_dist:
            return "Нет данных"
        
        result = []
        for lang, count in lang_dist.items():
            lang_name = self.config.SUPPORTED_LANGUAGES.get(lang, lang)
            result.append(f"  {lang_name}: {count}")
        
        return "\n".join(result)
    
    def _format_decision_stats(self, decision_dist: dict) -> str:
        """Форматирует статистику по решениям"""
        if not decision_dist:
            return "Нет данных"
        
        result = []
        for decision, count in decision_dist.items():
            decision_name = "Признание" if decision == "confess" else "Молчание"
            result.append(f"  {decision_name}: {count}")
        
        return "\n".join(result)
    
    async def handle_message(self, update: Update, context):
        """Обработчик обычных сообщений"""
        user_id = update.effective_user.id
        
        # Проверяем, не находится ли пользователь в процессе опроса
        if user_id in self.experiment_handler.survey_handler.survey_sessions:
            survey_data = self.experiment_handler.survey_handler.survey_sessions[user_id]
            if survey_data.get('waiting_for_text', False):
                await self.experiment_handler.survey_handler.handle_survey_response(update, context)
                return
        
        # Обычная обработка сообщений эксперимента
        await self.experiment_handler.handle_user_message(update, context)
    
    async def handle_callback(self, update: Update, context):
        """Обработчик callback запросов"""
        query = update.callback_query
        data = query.data
        
        if data.startswith('lang_'):
            await self.experiment_handler.handle_language_selection(update, context)
        elif data.startswith('decision_'):
            await self.experiment_handler.handle_decision(update, context)
        elif data.startswith('survey_'):
            # Обрабатываем ответы на опрос
            await self.experiment_handler.survey_handler.handle_survey_response(update, context)
    
    def run_polling(self):
        """Запускает бота в режиме polling"""
        logger.info("Запуск бота в режиме polling...")
        
        # Создаем приложение
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
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
