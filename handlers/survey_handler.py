"""
Обработчик опроса после эксперимента
"""
import logging
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.database import DatabaseManager
from config.nudging_texts import COMMON_TEXTS

logger = logging.getLogger(__name__)

class SurveyHandler:
    """Обработчик опроса после эксперимента"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.survey_sessions: Dict[int, Dict[str, Any]] = {}
    
    async def start_survey(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                          participant_id: str, language: str):
        """Начинает опрос для участника"""
        user_id = update.effective_user.id
        
        # Инициализируем сессию опроса
        survey_data = {
            'participant_id': participant_id,
            'language': language,
            'current_question': 1,
            'responses': {}
        }
        
        self.survey_sessions[user_id] = survey_data
        
        # Показываем первый вопрос
        await self._show_question(update, context, survey_data)
    
    async def _show_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                           survey_data: Dict[str, Any]):
        """Показывает текущий вопрос опроса"""
        language = survey_data['language']
        current_q = survey_data['current_question']
        
        texts = COMMON_TEXTS.get(language, COMMON_TEXTS['en'])
        
        if current_q == 1:
            # Вопрос 1: Чувствовали ли вы влияние?
            question = texts['survey_questions']['q1']
            options = texts['survey_options']['q1']
            
            keyboard = []
            for option in options:
                keyboard.append([InlineKeyboardButton(
                    option, 
                    callback_data=f"survey_q1_{option.lower()}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"📋 Опрос:\n\n{question}",
                reply_markup=reply_markup
            )
            
        elif current_q == 2:
            # Вопрос 2: Было ли это полезно/манипулятивно?
            question = texts['survey_questions']['q2']
            options = texts['survey_options']['q2']
            
            keyboard = []
            for option in options:
                keyboard.append([InlineKeyboardButton(
                    option, 
                    callback_data=f"survey_q2_{option.lower()}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"📋 Опрос:\n\n{question}",
                reply_markup=reply_markup
            )
            
        elif current_q == 3:
            # Вопрос 3: Уровень уверенности (1-5)
            question = texts['survey_questions']['q3']
            options = texts['survey_options']['q3']
            
            keyboard = []
            for option in options:
                keyboard.append([InlineKeyboardButton(
                    option, 
                    callback_data=f"survey_q3_{option}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                f"📋 Опрос:\n\n{question}",
                reply_markup=reply_markup
            )
            
        elif current_q == 4:
            # Вопрос 4: Открытый вопрос
            question = texts['survey_questions']['q4']
            
            await update.callback_query.edit_message_text(
                f"📋 Опрос:\n\n{question}\n\nПожалуйста, напишите ваш ответ текстом."
            )
            
            # Обновляем состояние для ожидания текстового ответа
            survey_data['waiting_for_text'] = True
    
    async def handle_survey_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает ответы на опрос"""
        query = update.callback_query
        user_id = update.effective_user.id
        
        if user_id not in self.survey_sessions:
            await query.answer("Сессия опроса не найдена.")
            return
        
        survey_data = self.survey_sessions[user_id]
        
        # Проверяем, ждем ли мы текстовый ответ
        if survey_data.get('waiting_for_text', False):
            await self._handle_text_response(update, context, survey_data)
            return
        
        # Обрабатываем ответ с кнопки
        data_parts = query.data.split('_')
        question_num = int(data_parts[1][1])  # q1 -> 1
        answer = '_'.join(data_parts[2:])  # Остальная часть ответа
        
        # Сохраняем ответ
        survey_data['responses'][f'question_{question_num}'] = answer
        
        # Переходим к следующему вопросу
        survey_data['current_question'] += 1
        
        if survey_data['current_question'] <= 4:
            await self._show_question(update, context, survey_data)
        else:
            # Завершаем опрос
            await self._complete_survey(update, context, survey_data)
    
    async def _handle_text_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  survey_data: Dict[str, Any]):
        """Обрабатывает текстовый ответ на открытый вопрос"""
        user_id = update.effective_user.id
        text_response = update.message.text
        
        # Сохраняем текстовый ответ
        survey_data['responses']['question_4'] = text_response
        survey_data['waiting_for_text'] = False
        
        # Завершаем опрос
        await self._complete_survey(update, context, survey_data)
    
    async def _complete_survey(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                             survey_data: Dict[str, Any]):
        """Завершает опрос и сохраняет данные"""
        participant_id = survey_data['participant_id']
        language = survey_data['language']
        responses = survey_data['responses']
        
        # Подготавливаем данные для сохранения
        survey_responses = {
            'question_1': responses.get('question_1'),
            'question_2': responses.get('question_2'),
            'question_3': int(responses.get('question_3', 0)) if responses.get('question_3') else None,
            'question_4': responses.get('question_4', '')
        }
        
        # Сохраняем в базу данных
        self.db.save_survey_response(participant_id, survey_responses)
        
        # Показываем благодарность
        texts = COMMON_TEXTS.get(language, COMMON_TEXTS['en'])
        thank_you_message = texts['thank_you']
        
        try:
            if hasattr(update, 'callback_query') and update.callback_query:
                await update.callback_query.edit_message_text(thank_you_message)
            else:
                await update.message.reply_text(thank_you_message)
        except Exception as e:
            logger.error(f"Ошибка отправки благодарности: {e}")
            # Пытаемся отправить новое сообщение
            try:
                user_id = update.effective_user.id
                await context.bot.send_message(chat_id=user_id, text=thank_you_message)
            except Exception as e2:
                logger.error(f"Критическая ошибка отправки сообщения: {e2}")
        
        # Удаляем сессию опроса
        user_id = update.effective_user.id
        if user_id in self.survey_sessions:
            del self.survey_sessions[user_id]
        
        logger.info(f"Опрос завершен для участника {participant_id}")
    
    def get_survey_statistics(self) -> Dict[str, Any]:
        """Получает статистику опроса"""
        try:
            # Здесь можно добавить запросы к базе данных для получения статистики опроса
            # Пока возвращаем базовую информацию
            return {
                'total_surveys': len(self.survey_sessions),
                'active_surveys': len(self.survey_sessions)
            }
        except Exception as e:
            logger.error(f"Ошибка получения статистики опроса: {e}")
            return {}
