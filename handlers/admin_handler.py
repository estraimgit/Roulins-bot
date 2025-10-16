"""
Админский обработчик для управления экспериментом
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config.settings import Config
from utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class AdminHandler:
    """Обработчик админских функций"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.admin_user_ids = []
        for uid in Config.ADMIN_USER_IDS:
            if uid.strip():
                try:
                    self.admin_user_ids.append(int(uid.strip()))
                except ValueError:
                    logger.warning(f"Неверный формат admin user ID: {uid}")
        
    def is_admin(self, user_id: int) -> bool:
        """Проверяет, является ли пользователь админом"""
        logger.info(f"Проверка админских прав для user_id: {user_id}")
        logger.info(f"Список админов: {self.admin_user_ids}")
        logger.info(f"Config.ADMIN_USER_IDS: {Config.ADMIN_USER_IDS}")
        result = user_id in self.admin_user_ids
        logger.info(f"Результат проверки: {result}")
        return result
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик админских команд"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет прав администратора.")
            return
        
        command = context.args[0] if context.args else "help"
        
        if command == "help":
            await self._show_admin_help(update, context)
        elif command == "stats":
            await self._show_statistics(update, context)
        elif command == "reset":
            await self._reset_user_session(update, context)
        elif command == "list":
            await self._list_active_sessions(update, context)
        elif command == "export":
            await self._export_data(update, context)
        elif command == "toggle_testing":
            await self._toggle_testing_mode(update, context)
        else:
            await update.message.reply_text("❌ Неизвестная команда. Используйте /admin help")
    
    async def _show_admin_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает справку по админским командам"""
        help_text = """
🔧 **Админские команды:**

**Основные команды:**
`/admin stats` - Показать статистику эксперимента
`/admin list` - Список активных сессий
`/admin export` - Экспорт данных

**Управление пользователями:**
`/admin reset <user_id>` - Сбросить сессию пользователя
`/admin reset all` - Сбросить все сессии

**Настройки:**
`/admin toggle_testing` - Включить/выключить режим тестирования

**Примеры:**
`/admin reset 123456789` - Сбросить сессию пользователя 123456789
`/admin stats` - Показать статистику
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _show_statistics(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает статистику эксперимента"""
        try:
            stats = self.db.get_experiment_statistics()
            
            stats_text = f"""
📊 **Статистика эксперимента:**

👥 **Участники:**
• Всего: {stats.get('total_participants', 0)}
• Завершили: {stats.get('completed', 0)}

📈 **Распределение по группам:**
"""
            
            for group, count in stats.get('groups', {}).items():
                stats_text += f"• {group}: {count}\n"
            
            stats_text += f"""
🌍 **Языки:**
"""
            for lang, count in stats.get('language_distribution', {}).items():
                stats_text += f"• {lang}: {count}\n"
            
            stats_text += f"""
🎯 **Решения:**
"""
            for decision, count in stats.get('decision_distribution', {}).items():
                stats_text += f"• {decision}: {count}\n"
            
            if 'llm_analyses' in stats:
                stats_text += f"\n🧠 **LLM анализов:** {stats['llm_analyses']}"
            
            await update.message.reply_text(stats_text)
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text("❌ Ошибка при получении статистики.")
    
    async def _reset_user_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сбрасывает сессию пользователя"""
        if len(context.args) < 2:
            await update.message.reply_text("❌ Использование: `/admin reset <user_id>` или `/admin reset all`")
            return
        
        target = context.args[1]
        
        try:
            if target == "all":
                # Сброс всех сессий
                await self._reset_all_sessions(update, context)
            else:
                # Сброс конкретного пользователя
                user_id = int(target)
                await self._reset_single_session(update, context, user_id)
                
        except ValueError:
            await update.message.reply_text("❌ Неверный ID пользователя.")
        except Exception as e:
            logger.error(f"Ошибка при сбросе сессии: {e}")
            await update.message.reply_text("❌ Ошибка при сбросе сессии.")
    
    async def _reset_single_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Сбрасывает сессию одного пользователя"""
        try:
            # Удаляем из активных сессий (если есть)
            if hasattr(context.bot_data, 'active_sessions'):
                if user_id in context.bot_data['active_sessions']:
                    del context.bot_data['active_sessions'][user_id]
            
            # Удаляем из истории разговоров (если есть)
            if hasattr(context.bot_data, 'conversation_history'):
                if user_id in context.bot_data['conversation_history']:
                    del context.bot_data['conversation_history'][user_id]
            
            # Удаляем из сессий опросов (если есть)
            if hasattr(context.bot_data, 'survey_sessions'):
                if user_id in context.bot_data['survey_sessions']:
                    del context.bot_data['survey_sessions'][user_id]
            
            await update.message.reply_text(f"✅ Сессия пользователя {user_id} сброшена. Пользователь может начать эксперимент заново.")
            
        except Exception as e:
            logger.error(f"Ошибка при сбросе сессии пользователя {user_id}: {e}")
            await update.message.reply_text(f"❌ Ошибка при сбросе сессии пользователя {user_id}.")
    
    async def _reset_all_sessions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сбрасывает все активные сессии"""
        try:
            # Очищаем все активные сессии
            if hasattr(context.bot_data, 'active_sessions'):
                count = len(context.bot_data['active_sessions'])
                context.bot_data['active_sessions'].clear()
            else:
                count = 0
            
            # Очищаем историю разговоров
            if hasattr(context.bot_data, 'conversation_history'):
                context.bot_data['conversation_history'].clear()
            
            # Очищаем сессии опросов
            if hasattr(context.bot_data, 'survey_sessions'):
                context.bot_data['survey_sessions'].clear()
            
            await update.message.reply_text(f"✅ Все сессии сброшены. Сброшено {count} активных сессий.")
            
        except Exception as e:
            logger.error(f"Ошибка при сбросе всех сессий: {e}")
            await update.message.reply_text("❌ Ошибка при сбросе всех сессий.")
    
    async def _list_active_sessions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список активных сессий"""
        try:
            if not hasattr(context.bot_data, 'active_sessions') or not context.bot_data['active_sessions']:
                await update.message.reply_text("📋 Нет активных сессий.")
                return
            
            sessions_text = "📋 **Активные сессии:**\n\n"
            
            for user_id, session_data in context.bot_data['active_sessions'].items():
                time_remaining = (session_data['end_time'] - datetime.now()).total_seconds() / 60
                sessions_text += f"""
👤 **Пользователь:** {user_id}
🎯 **Группа:** {session_data.get('group', 'неизвестно')}
🌍 **Язык:** {session_data.get('language', 'неизвестно')}
💬 **Сообщений:** {session_data.get('message_count', 0)}
⏰ **Осталось:** {max(0, time_remaining):.1f} мин
---
"""
            
            # Разбиваем на части, если сообщение слишком длинное
            if len(sessions_text) > 4000:
                parts = [sessions_text[i:i+4000] for i in range(0, len(sessions_text), 4000)]
                for part in parts:
                    await update.message.reply_text(part)
            else:
                await update.message.reply_text(sessions_text)
                
        except Exception as e:
            logger.error(f"Ошибка при получении списка сессий: {e}")
            await update.message.reply_text("❌ Ошибка при получении списка сессий.")
    
    async def _export_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Экспортирует данные эксперимента"""
        try:
            # Получаем статистику
            stats = self.db.get_experiment_statistics()
            
            # Получаем LLM данные
            llm_data = await self.db.get_llm_analysis_data()
            
            export_text = f"""
📤 **Экспорт данных:**

📊 **Статистика:**
• Всего участников: {stats.get('total_participants', 0)}
• Завершили: {stats.get('completed', 0)}
• LLM анализов: {len(llm_data)}

💾 **Данные сохранены в базе данных**
• Участники: таблица `participants`
• LLM анализ: таблица `llm_analysis`
• Поток разговоров: таблица `conversation_flow`
• Опросы: таблица `survey_responses`

🔍 **Для получения данных используйте:**
`/admin stats` - статистика
`/admin list` - активные сессии
"""
            
            await update.message.reply_text(export_text)
            
        except Exception as e:
            logger.error(f"Ошибка при экспорте данных: {e}")
            await update.message.reply_text("❌ Ошибка при экспорте данных.")
    
    async def _toggle_testing_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Переключает режим тестирования"""
        try:
            # В реальном приложении здесь бы обновлялась переменная окружения
            # Для демонстрации просто показываем текущий статус
            
            current_mode = Config.TESTING_MODE
            new_mode = not current_mode
            
            mode_text = "включен" if new_mode else "выключен"
            
            await update.message.reply_text(
                f"🔄 Режим тестирования {mode_text}.\n\n"
                f"**Текущие настройки:**\n"
                f"• Тестирование: {Config.TESTING_MODE}\n"
                f"• Множественные сессии: {Config.ALLOW_MULTIPLE_SESSIONS}\n"
                f"• Админы: {len(self.admin_user_ids)}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при переключении режима тестирования: {e}")
            await update.message.reply_text("❌ Ошибка при переключении режима тестирования.")
    
    async def check_user_eligibility(self, user_id: int) -> Dict:
        """
        Проверяет, может ли пользователь начать эксперимент
        
        Returns:
            Dict с результатом проверки
        """
        try:
            # Если пользователь админ или включен режим тестирования
            if self.is_admin(user_id) or Config.TESTING_MODE or Config.ALLOW_MULTIPLE_SESSIONS:
                return {
                    'can_participate': True,
                    'reason': 'admin_or_testing_mode',
                    'message': None
                }
            
            # Проверяем, участвовал ли пользователь уже
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM participants WHERE telegram_user_id = ?",
                    (user_id,)
                )
                participation_count = cursor.fetchone()[0]
                
                if participation_count > 0:
                    return {
                        'can_participate': False,
                        'reason': 'already_participated',
                        'message': "Вы уже участвовали в эксперименте. Для повторного участия обратитесь к администратору."
                    }
            
            return {
                'can_participate': True,
                'reason': 'first_time',
                'message': None
            }
            
        except Exception as e:
            logger.error(f"Ошибка при проверке права участия: {e}")
            return {
                'can_participate': False,
                'reason': 'error',
                'message': "Произошла ошибка при проверке права участия."
            }
