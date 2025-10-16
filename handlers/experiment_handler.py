"""
Обработчик экспериментальных сессий
"""
import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.database import DatabaseManager
from utils.randomization import ParticipantRandomizer
from utils.multilingual import MultilingualManager
from config.nudging_texts import CONFESS_NUDGING_TEXTS, SILENT_NUDGING_TEXTS, COMMON_TEXTS
from config.settings import Config
from handlers.survey_handler import SurveyHandler

logger = logging.getLogger(__name__)

class ExperimentHandler:
    """Обработчик экспериментальных сессий"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.randomizer = ParticipantRandomizer()
        self.multilingual = MultilingualManager()
        self.survey_handler = SurveyHandler(self.db)
        self.active_sessions: Dict[int, Dict[str, Any]] = {}
    
    async def start_experiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начинает эксперимент для нового участника"""
        user_id = update.effective_user.id
        
        # Проверяем, не участвует ли пользователь уже в эксперименте
        existing_participant = self.db.get_participant(user_id)
        if existing_participant:
            await update.message.reply_text(
                "Вы уже участвуете в этом эксперименте. Пожалуйста, дождитесь завершения текущей сессии."
            )
            return
        
        # Показываем выбор языка
        await self._show_language_selection(update, context)
    
    async def _show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает меню выбора языка"""
        keyboard = []
        languages = self.multilingual.get_supported_languages_list()
        
        # Создаем кнопки для языков (по 2 в ряду)
        for i in range(0, len(languages), 2):
            row = []
            for j in range(2):
                if i + j < len(languages):
                    lang_code = list(languages.keys())[i + j]
                    lang_name = languages[lang_code]
                    row.append(InlineKeyboardButton(
                        lang_name, 
                        callback_data=f"lang_{lang_code}"
                    ))
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Определяем язык сообщения для выбора языка
        detected_lang = self.multilingual.detect_language(update.message.text or "")
        welcome_text = COMMON_TEXTS.get(detected_lang, COMMON_TEXTS['en'])['language_selection']
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор языка"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        language = query.data.split('_')[1]
        
        # Генерируем ID участника и назначаем группу
        participant_id = self.randomizer.generate_participant_id(user_id)
        experiment_group = self.randomizer.assign_group(participant_id)
        
        # Создаем участника в базе данных
        success = self.db.create_participant(participant_id, user_id, language, experiment_group)
        
        if not success:
            await query.edit_message_text(
                "Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз."
            )
            return
        
        # Инициализируем сессию
        session_data = {
            'participant_id': participant_id,
            'language': language,
            'experiment_group': experiment_group,
            'start_time': datetime.now(),
            'message_count': 0,
            'current_phase': 'conversation'
        }
        
        self.active_sessions[user_id] = session_data
        
        # Обновляем время начала в базе данных
        self.db.update_participant_session(participant_id, start_time=session_data['start_time'])
        
        # Начинаем разговор
        await self._start_conversation(query, context, session_data)
    
    async def _start_conversation(self, query, context: ContextTypes.DEFAULT_TYPE, session_data: Dict[str, Any]):
        """Начинает разговор с участником"""
        language = session_data['language']
        experiment_group = session_data['experiment_group']
        
        # Выбираем тексты в зависимости от группы
        if experiment_group == 'confess':
            texts = CONFESS_NUDGING_TEXTS.get(language, CONFESS_NUDGING_TEXTS['en'])
        else:
            texts = SILENT_NUDGING_TEXTS.get(language, SILENT_NUDGING_TEXTS['en'])
        
        welcome_message = texts['welcome']
        
        # Выбираем случайный открывающий вопрос
        opening_question = random.choice(texts['opening_questions'])
        
        full_message = f"{welcome_message}\n\n{opening_question}"
        
        await query.edit_message_text(full_message)
        
        # Сохраняем сообщения в базе данных
        self.db.save_chat_message(session_data['participant_id'], 'bot', welcome_message)
        self.db.save_chat_message(session_data['participant_id'], 'bot', opening_question)
        
        # Устанавливаем таймер для завершения сессии
        end_time = session_data['start_time'] + timedelta(minutes=Config.EXPERIMENT_DURATION_MINUTES)
        warning_time = end_time - timedelta(minutes=Config.WARNING_TIME_MINUTES)
        
        # Планируем предупреждение
        context.job_queue.run_once(
            self._send_time_warning,
            when=warning_time,
            data={'user_id': query.from_user.id}
        )
        
        # Планируем завершение сессии
        context.job_queue.run_once(
            self._end_session,
            when=end_time,
            data={'user_id': query.from_user.id}
        )
    
    async def handle_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает сообщения пользователя во время эксперимента"""
        user_id = update.effective_user.id
        
        # Проверяем, активна ли сессия
        if user_id not in self.active_sessions:
            await update.message.reply_text(
                "Пожалуйста, начните эксперимент с помощью команды /start"
            )
            return
        
        session_data = self.active_sessions[user_id]
        
        if session_data['current_phase'] != 'conversation':
            await update.message.reply_text(
                "Эксперимент завершен. Спасибо за участие!"
            )
            return
        
        user_message = update.message.text
        language = session_data['language']
        experiment_group = session_data['experiment_group']
        
        # Сохраняем сообщение пользователя
        self.db.save_chat_message(session_data['participant_id'], 'user', user_message)
        
        # Генерируем ответ на основе группы и контекста
        response = await self._generate_response(user_message, language, experiment_group, session_data)
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
        # Сохраняем ответ бота
        self.db.save_chat_message(session_data['participant_id'], 'bot', response)
        
        # Увеличиваем счетчик сообщений
        session_data['message_count'] += 1
        
        # Проверяем, не пора ли перейти к принятию решения
        if session_data['message_count'] >= 8:  # Примерно после 8 обменов сообщениями
            await self._show_decision_prompt(update, context, session_data)
    
    async def _generate_response(self, user_message: str, language: str, 
                               experiment_group: str, session_data: Dict[str, Any]) -> str:
        """Генерирует ответ бота на основе группы и контекста"""
        # Выбираем тексты в зависимости от группы
        if experiment_group == 'confess':
            texts = CONFESS_NUDGING_TEXTS.get(language, CONFESS_NUDGING_TEXTS['en'])
        else:
            texts = SILENT_NUDGING_TEXTS.get(language, SILENT_NUDGING_TEXTS['en'])
        
        # Простая логика выбора ответа на основе количества сообщений
        message_count = session_data['message_count']
        
        if message_count < 3:
            # Ранние сообщения - задаем вопросы
            return random.choice(texts['opening_questions'])
        elif message_count < 6:
            # Средние сообщения - позитивное фреймирование
            return random.choice(texts['positive_framing'])
        else:
            # Поздние сообщения - подчеркиваем преимущества
            if experiment_group == 'confess':
                return random.choice(texts['benefits_highlighting'])
            else:
                return random.choice(texts['potential_rewards'])
    
    async def _show_decision_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                  session_data: Dict[str, Any]):
        """Показывает приглашение к принятию решения"""
        language = session_data['language']
        texts = COMMON_TEXTS.get(language, COMMON_TEXTS['en'])
        
        # Выбираем тексты в зависимости от группы
        if session_data['experiment_group'] == 'confess':
            group_texts = CONFESS_NUDGING_TEXTS.get(language, CONFESS_NUDGING_TEXTS['en'])
        else:
            group_texts = SILENT_NUDGING_TEXTS.get(language, SILENT_NUDGING_TEXTS['en'])
        
        decision_prompt = group_texts['decision_prompt']
        
        # Создаем кнопки для выбора
        keyboard = [
            [InlineKeyboardButton(
                texts['decision_buttons']['confess'], 
                callback_data='decision_confess'
            )],
            [InlineKeyboardButton(
                texts['decision_buttons']['silent'], 
                callback_data='decision_silent'
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            decision_prompt,
            reply_markup=reply_markup
        )
        
        # Обновляем фазу сессии
        session_data['current_phase'] = 'decision'
    
    async def handle_decision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор участника"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        decision = query.data.split('_')[1]
        
        if user_id not in self.active_sessions:
            await query.edit_message_text("Сессия не найдена.")
            return
        
        session_data = self.active_sessions[user_id]
        session_data['current_phase'] = 'survey'
        
        # Сохраняем решение
        self.db.update_participant_session(
            session_data['participant_id'],
            end_time=datetime.now(),
            final_decision=decision
        )
        
        # Показываем опрос
        await self.survey_handler.start_survey(
            update, context, 
            session_data['participant_id'], 
            session_data['language']
        )
    
    
    async def _send_time_warning(self, context: ContextTypes.DEFAULT_TYPE):
        """Отправляет предупреждение о времени"""
        user_id = context.job.data['user_id']
        
        if user_id in self.active_sessions:
            session_data = self.active_sessions[user_id]
            language = session_data['language']
            texts = COMMON_TEXTS.get(language, COMMON_TEXTS['en'])
            
            warning_text = texts['time_warning']
            
            try:
                await context.bot.send_message(chat_id=user_id, text=warning_text)
            except Exception as e:
                logger.error(f"Ошибка отправки предупреждения: {e}")
    
    async def _end_session(self, context: ContextTypes.DEFAULT_TYPE):
        """Завершает сессию"""
        user_id = context.job.data['user_id']
        
        if user_id in self.active_sessions:
            session_data = self.active_sessions[user_id]
            language = session_data['language']
            texts = COMMON_TEXTS.get(language, COMMON_TEXTS['en'])
            
            end_text = texts['session_ended']
            
            try:
                await context.bot.send_message(chat_id=user_id, text=end_text)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения о завершении: {e}")
            
            # Удаляем сессию
            del self.active_sessions[user_id]
