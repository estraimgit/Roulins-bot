"""
Улучшенный обработчик экспериментов с интеграцией LLM
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.database import DatabaseManager
from utils.randomization import ParticipantRandomizer
from utils.multilingual import MultilingualManager
from utils.llm_analyzer import LLMAnalyzer
from handlers.survey_handler import SurveyHandler
from handlers.admin_handler import AdminHandler
from config.nudging_texts import CONFESS_NUDGING_TEXTS, SILENT_NUDGING_TEXTS
from config.settings import Config

logger = logging.getLogger(__name__)

class LLMExperimentHandler:
    """Обработчик экспериментов с LLM анализом"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.randomizer = ParticipantRandomizer()
        self.multilingual = MultilingualManager()
        self.llm_analyzer = LLMAnalyzer()
        self.survey_handler = SurveyHandler(self.db)
        self.admin_handler = AdminHandler()
        # Используем прямые импорты текстов
        self.confess_texts = CONFESS_NUDGING_TEXTS
        self.silent_texts = SILENT_NUDGING_TEXTS
        
        # Активные сессии
        self.active_sessions = {}
        self.conversation_history = {}
        
    async def start_experiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начинает эксперимент с выбором языка"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "unknown"
        
        try:
            # Проверяем, не участвует ли пользователь уже в эксперименте
            if user_id in self.active_sessions:
                await update.message.reply_text(
                    "Вы уже участвуете в эксперименте. Пожалуйста, дождитесь его завершения."
                )
                return
            
            # Проверяем право участия (для админов и тестирования)
            eligibility = await self.admin_handler.check_user_eligibility(user_id)
            if not eligibility['can_participate']:
                if eligibility['message']:
                    await update.message.reply_text(eligibility['message'])
                return
            
            # Показываем выбор языка
            await self._show_language_selection(update, context)
            
        except Exception as e:
            logger.error(f"Ошибка при запуске эксперимента: {e}")
            await update.message.reply_text(
                "Произошла ошибка при запуске эксперимента. Попробуйте позже."
            )
    
    async def _show_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает выбор языка"""
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = (
            "🌍 **Выберите язык для эксперимента:**\n\n"
            "🌍 **Choose language for the experiment:**\n\n"
            "🇷🇺 Русский - для русскоязычных участников\n"
            "🇺🇸 English - for English-speaking participants"
        )
        
        await update.message.reply_text(
            message_text, 
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def handle_language_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает выбор языка"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        username = query.from_user.username or "unknown"
        language = query.data.split('_')[1]  # 'ru' или 'en'
        
        try:
            # Генерируем ID участника и назначаем группу
            participant_id = self.randomizer.generate_participant_id(user_id)
            group = self.randomizer.assign_group(participant_id)
            
            # Создаем сессию
            session_data = {
                'participant_id': participant_id,
                'user_id': user_id,
                'username': username,
                'group': group,
                'language': language,
                'start_time': datetime.now(),
                'end_time': datetime.now() + timedelta(minutes=5),
                'message_count': 0,
                'last_activity': datetime.now(),
                'conversation_messages': []
            }
            
            self.active_sessions[user_id] = session_data
            self.conversation_history[user_id] = []
            
            # Записываем в базу данных (или обновляем существующего)
            try:
                success = self.db.create_participant(
                    participant_id=participant_id,
                    telegram_user_id=user_id,
                    language=language,
                    experiment_group=group
                )
                
                # Если участник уже существует, это не ошибка - продолжаем
                if not success:
                    logger.info(f"Участник {participant_id} уже существует, продолжаем эксперимент")
                    
            except Exception as e:
                logger.error(f"Ошибка при создании участника: {e}")
                await query.edit_message_text(
                    "Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз."
                )
                return
            
            # Отправляем приветственное сообщение
            welcome_text = self._get_welcome_message(language, group)
            await query.edit_message_text(welcome_text, parse_mode='Markdown')
            
            # Записываем начало эксперимента в базу данных
            await self.db.log_experiment_start(
                participant_id=participant_id,
                start_time=datetime.now(),
                experiment_group=group,
                language=language
            )
            
            # Запускаем таймер завершения эксперимента (если JobQueue доступен)
            if hasattr(context, 'job_queue') and context.job_queue:
                # Таймер завершения эксперимента
                context.job_queue.run_once(
                    self._end_experiment_timer, 
                    300,  # 5 минут
                    data={'user_id': user_id}
                )
                
                # Периодический таймер для показа оставшегося времени
                context.job_queue.run_repeating(
                    self._show_time_remaining,
                    60,  # каждую минуту
                    data={'user_id': user_id},
                    first=60  # первое уведомление через 1 минуту
                )
            else:
                logger.warning("JobQueue не доступен, таймер завершения эксперимента не установлен")
            
            logger.info(f"Эксперимент начат для пользователя {user_id}, группа: {group}, язык: {language}")
            
        except Exception as e:
            logger.error(f"Ошибка при выборе языка: {e}")
            await query.edit_message_text(
                "Произошла ошибка при выборе языка. Попробуйте еще раз."
            )
    
    async def handle_user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает сообщения пользователя с LLM анализом"""
        user_id = update.effective_user.id
        user_message = update.message.text
        
        if user_id not in self.active_sessions:
            await update.message.reply_text(
                "Для участия в эксперименте отправьте команду /start"
            )
            return
        
        try:
            session_data = self.active_sessions[user_id]
            
            # Проверяем команды досрочного завершения
            if user_message.lower() in ['/end', '/finish', '/stop', 'завершить', 'закончить', 'стоп', 'хватит']:
                await self._end_experiment(update, context, user_id)
                return
            
            # Проверяем, не истекло ли время
            if datetime.now() > session_data['end_time']:
                await self._end_experiment(update, context, user_id)
                return
            
            # Обновляем счетчик сообщений
            session_data['message_count'] += 1
            session_data['last_activity'] = datetime.now()
            
            # Добавляем сообщение в историю
            self.conversation_history[user_id].append({
                'text': user_message,
                'timestamp': datetime.now(),
                'sender': 'user'
            })
            
            # Показываем динамичный индикатор "Печатаю..."
            typing_message = await update.message.reply_text("🤔 Печатаю...")
            
            # Запускаем анимацию индикатора
            animation_task = asyncio.create_task(self._animate_typing_indicator(typing_message))
            
            # Анализируем сообщение с помощью LLM
            context_for_analysis = {
                'group': session_data['group'],
                'time_elapsed': (datetime.now() - session_data['start_time']).total_seconds() / 60,
                'message_count': session_data['message_count'],
                'language': session_data['language']
            }
            
            analysis = self.llm_analyzer.analyze_message(user_message, context_for_analysis)
            
            # Останавливаем анимацию
            animation_task.cancel()
            
            # Генерируем персонализированный ответ с учетом истории разговора
            if self.llm_analyzer.api_key and analysis.get('analysis_method') != 'basic':
                bot_response = self.llm_analyzer.generate_personalized_response(
                    user_message, analysis, context_for_analysis, 
                    self.conversation_history.get(user_id, [])
                )
            else:
                # Используем разнообразные ответы из анализа
                bot_response = analysis.get('suggested_response', 
                    self._get_standard_response(
                        session_data['group'], 
                        session_data['language'],
                        analysis
                    )
                )
            
            # Удаляем индикатор "Печатаю..." и отправляем ответ
            await typing_message.delete()
            await update.message.reply_text(bot_response)
            
            # Добавляем ответ бота в историю
            self.conversation_history[user_id].append({
                'text': bot_response,
                'timestamp': datetime.now(),
                'sender': 'bot'
            })
            
            # Логируем анализ
            self.llm_analyzer.log_analysis(user_id, user_message, analysis, bot_response)
            
            # Сохраняем в базу данных
            await self.db.log_llm_analysis(
                participant_id=session_data['participant_id'],
                user_message=user_message,
                analysis=analysis,
                bot_response=bot_response
            )
            
            # Анализируем поток разговора
            if len(self.conversation_history[user_id]) >= 3:
                flow_analysis = self.llm_analyzer.analyze_conversation_flow(
                    self.conversation_history[user_id]
                )
                
                # Сохраняем анализ потока
                await self.db.log_conversation_flow(
                    participant_id=session_data['participant_id'],
                    flow_analysis=flow_analysis
                )
            
            # Проверяем, не нужно ли предупреждение о времени
            time_remaining = (session_data['end_time'] - datetime.now()).total_seconds() / 60
            if time_remaining <= 1 and not session_data.get('warning_sent', False):
                await self._send_time_warning(update, context, session_data['language'])
                session_data['warning_sent'] = True
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обработке сообщения. Попробуйте еще раз."
            )
    
    async def _show_time_remaining(self, context: ContextTypes.DEFAULT_TYPE):
        """Показывает оставшееся время эксперимента"""
        user_id = context.job.data['user_id']
        
        if user_id in self.active_sessions:
            session_data = self.active_sessions[user_id]
            start_time = session_data['start_time']
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining = max(0, 300 - elapsed)  # 5 минут = 300 секунд
            
            if remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                
                if session_data['language'] == 'ru':
                    if minutes > 0:
                        time_message = f"⏰ Осталось времени: {minutes} мин {seconds} сек"
                    else:
                        time_message = f"⏰ Осталось времени: {seconds} сек"
                else:
                    if minutes > 0:
                        time_message = f"⏰ Time remaining: {minutes} min {seconds} sec"
                    else:
                        time_message = f"⏰ Time remaining: {seconds} sec"
                
                try:
                    await context.bot.send_message(chat_id=user_id, text=time_message)
                except Exception as e:
                    logger.error(f"Ошибка при отправке сообщения о времени: {e}")
            else:
                # Время истекло, завершаем эксперимент
                await self._end_experiment_timer(context)
        else:
            # Сессия не найдена, отменяем задачу
            context.job.schedule_removal()

    async def _end_experiment_timer(self, context: ContextTypes.DEFAULT_TYPE):
        """Показывает финальное решение по истечении времени"""
        user_id = context.job.data['user_id']
        
        if user_id in self.active_sessions:
            session_data = self.active_sessions[user_id]
            
            # Показываем сообщение о истечении времени и кнопки для финального решения
            await self._show_final_decision(context.bot, user_id, session_data)
            
            logger.info(f"Эксперимент завершен по таймеру для пользователя {user_id}")

    async def _end_experiment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Завершает эксперимент"""
        try:
            session_data = self.active_sessions[user_id]
            
            # Анализируем финальное состояние разговора
            if self.conversation_history[user_id]:
                # Показываем динамичный индикатор "Анализирую..."
                typing_message = await update.message.reply_text("📊 Анализирую разговор...")
                
                # Запускаем анимацию индикатора
                animation_task = asyncio.create_task(self._animate_analysis_indicator(typing_message))
                
                final_analysis = self.llm_analyzer.analyze_conversation_flow(
                    self.conversation_history[user_id]
                )
                
                await self.db.log_final_conversation_analysis(
                    participant_id=session_data['participant_id'],
                    final_analysis=final_analysis
                )
                
                # Останавливаем анимацию и удаляем индикатор
                animation_task.cancel()
                await typing_message.delete()
            
            # Записываем завершение эксперимента
            await self.db.log_experiment_completion(
                participant_id=session_data['participant_id'],
                end_time=datetime.now(),
                total_messages=session_data['message_count']
            )
            
            # Очищаем сессию
            del self.active_sessions[user_id]
            del self.conversation_history[user_id]
            
            # Показываем опрос
            await self.survey_handler.start_survey(
                update, context, 
                session_data['participant_id'], 
                session_data['language']
            )
            
        except Exception as e:
            logger.error(f"Ошибка при завершении эксперимента: {e}")
    
    def _get_welcome_message(self, language: str, group: str) -> str:
        """Возвращает приветственное сообщение с описанием ситуации"""
        if language == 'ru':
            return (
                "🎭 **Добро пожаловать в эксперимент по дилемме заключенного!**\n\n"
                "**Ситуация:** Вы и ваш партнер были арестованы за совместное преступление. "
                "Следователь предлагает вам сделку:\n\n"
                "• Если вы **признаетесь**, а партнер молчит → вы получите 1 год, партнер 10 лет\n"
                "• Если вы **молчите**, а партнер признается → вы получите 10 лет, партнер 1 год\n"
                "• Если **оба признаетесь** → каждый получит по 5 лет\n"
                "• Если **оба молчите** → каждый получит по 2 года\n\n"
                "В течение 5 минут мы обсудим эту ситуацию. "
                "Поделитесь своими мыслями о том, что бы вы выбрали и почему.\n\n"
                "💡 **Для досрочного завершения:** напишите 'завершить', 'стоп' или '/end'"
            )
        else:
            return (
                "🎭 **Welcome to the Prisoner's Dilemma Experiment!**\n\n"
                "**Situation:** You and your partner have been arrested for a joint crime. "
                "The detective offers you a deal:\n\n"
                "• If you **confess** and partner stays silent → you get 1 year, partner gets 10 years\n"
                "• If you **stay silent** and partner confesses → you get 10 years, partner gets 1 year\n"
                "• If **both confess** → each gets 5 years\n"
                "• If **both stay silent** → each gets 2 years\n\n"
                "For the next 5 minutes, we'll discuss this situation. "
                "Please share your thoughts on what you would choose and why.\n\n"
                "💡 **To end early:** type 'finish', 'stop' or '/end'"
            )
    
    def _get_standard_response(self, group: str, language: str, analysis: Dict) -> str:
        """Возвращает стандартный ответ на основе анализа"""
        emotion = analysis.get('emotion', 'neutral')
        intent = analysis.get('intent', 'question')
        
        if language == 'ru':
            if group == 'confess':
                if emotion in ['anxious', 'frustrated']:
                    return "Понимаю ваши сомнения и переживания. Это нормально - такие решения действительно сложны. Но подумайте: честность не только освобождает от груза лжи, но и показывает ваше уважение к правосудию. Когда мы признаемся, мы даем возможность системе работать справедливо. Что вы думаете об этом?"
                elif intent == 'cooperate':
                    return "Отлично! Вы демонстрируете зрелый подход к ситуации. Честность действительно является основой любых здоровых отношений, будь то личные или профессиональные. Признание может показаться сложным шагом, но оно часто приводит к лучшим результатам для всех сторон. Расскажите, что именно привлекает вас в честном подходе?"
                else:
                    return "Это интересная точка зрения. Давайте разберем ситуацию глубже. Честность - это не просто моральный выбор, но и практическое решение. Когда мы открыты и честны, мы создаем основу для доверия и взаимопонимания. Как вы считаете, какие преимущества может дать честность в вашей ситуации?"
            else:  # silent group
                if emotion in ['anxious', 'frustrated']:
                    return "Ваши переживания абсолютно понятны. В таких ситуациях действительно важно быть осторожным и защищать свои интересы. Система правосудия не всегда работает идеально, и иногда молчание может быть единственным способом защитить себя от несправедливости. Что именно вас больше всего беспокоит в этой ситуации?"
                elif intent == 'defect':
                    return "Ваша осторожность показывает мудрость и понимание реальности. В таких ситуациях действительно важно думать о последствиях. Признание может привести к серьезным последствиям, которые повлияют на всю вашу жизнь. Иногда молчание - это не трусость, а разумная стратегия самозащиты. Расскажите, какие риски вы видите в признании?"
                else:
                    return "Это важный момент для размышлений. В таких ситуациях каждый выбор имеет свои последствия. Молчание может защитить вас от немедленных негативных последствий, но также важно понимать долгосрочные эффекты вашего решения. Как вы оцениваете различные варианты развития событий?"
        else:
            if group == 'confess':
                if emotion in ['anxious', 'frustrated']:
                    return "I understand your concerns and worries. This is completely normal - such decisions are indeed difficult. But consider this: honesty not only frees you from the burden of lies but also shows your respect for justice. When we confess, we give the system a chance to work fairly. What do you think about this?"
                elif intent == 'cooperate':
                    return "Excellent! You're demonstrating a mature approach to the situation. Honesty is indeed the foundation of any healthy relationship, whether personal or professional. Confessing might seem like a difficult step, but it often leads to better outcomes for all parties. Tell me, what specifically attracts you to an honest approach?"
                else:
                    return "That's an interesting perspective. Let's analyze the situation more deeply. Honesty is not just a moral choice, but also a practical solution. When we are open and honest, we create a foundation for trust and mutual understanding. What advantages do you think honesty could bring to your situation?"
            else:  # silent group
                if emotion in ['anxious', 'frustrated']:
                    return "Your concerns are absolutely understandable. In such situations, it's really important to be cautious and protect your interests. The justice system doesn't always work perfectly, and sometimes silence can be the only way to protect yourself from injustice. What specifically worries you most about this situation?"
                elif intent == 'defect':
                    return "Your caution shows wisdom and understanding of reality. In such situations, it's really important to think about the consequences. Confessing could lead to serious consequences that would affect your entire life. Sometimes silence is not cowardice, but a reasonable self-protection strategy. Tell me, what risks do you see in confessing?"
                else:
                    return "This is an important moment for reflection. In such situations, every choice has its consequences. Silence can protect you from immediate negative consequences, but it's also important to understand the long-term effects of your decision. How do you evaluate the different possible outcomes?"
    
    async def _send_time_warning(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str):
        """Отправляет предупреждение о времени"""
        if language == 'ru':
            message = "⏰ У вас осталась 1 минута до окончания эксперимента."
        else:
            message = "⏰ You have 1 minute left until the end of the experiment."
        
        await update.message.reply_text(message)
    
    async def get_experiment_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возвращает статус эксперимента"""
        user_id = update.effective_user.id
        
        if user_id not in self.active_sessions:
            await update.message.reply_text("Вы не участвуете в эксперименте.")
            return
        
        session_data = self.active_sessions[user_id]
        time_remaining = (session_data['end_time'] - datetime.now()).total_seconds() / 60
        
        status_text = f"""
📊 Статус эксперимента:
👤 Группа: {session_data['group']}
🌍 Язык: {session_data['language']}
💬 Сообщений: {session_data['message_count']}
⏰ Осталось времени: {max(0, time_remaining):.1f} минут
"""
        
        await update.message.reply_text(status_text)
    
    async def _animate_typing_indicator(self, message):
        """Анимирует индикатор 'Печатаю...'"""
        typing_indicators = [
            "🤔 Печатаю...",
            "🤔 Печатаю..",
            "🤔 Печатаю.",
            "🤔 Печатаю",
            "🤔 Печатаю.",
            "🤔 Печатаю..",
            "🤔 Печатаю..."
        ]
        
        try:
            while True:
                for indicator in typing_indicators:
                    try:
                        await message.edit_text(indicator)
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        # Игнорируем ошибки редактирования (например, если сообщение было удалено)
                        break
        except asyncio.CancelledError:
            # Задача была отменена - это нормально
            pass
    
    async def _animate_analysis_indicator(self, message):
        """Анимирует индикатор 'Анализирую разговор...'"""
        analysis_indicators = [
            "📊 Анализирую разговор...",
            "📊 Анализирую разговор..",
            "📊 Анализирую разговор.",
            "📊 Анализирую разговор",
            "📊 Анализирую разговор.",
            "📊 Анализирую разговор..",
            "📊 Анализирую разговор..."
        ]
        
        try:
            while True:
                for indicator in analysis_indicators:
                    try:
                        await message.edit_text(indicator)
                        await asyncio.sleep(0.6)
                    except Exception as e:
                        # Игнорируем ошибки редактирования (например, если сообщение было удалено)
                        break
        except asyncio.CancelledError:
            # Задача была отменена - это нормально
            pass
    
    async def _show_final_decision(self, bot, user_id: int, session_data: Dict):
        """Показывает финальное решение с кнопками"""
        try:
            if session_data['language'] == 'ru':
                message_text = (
                    "⏰ **Время эксперимента истекло!**\n\n"
                    "Теперь вам нужно принять финальное решение в дилемме заключенного.\n\n"
                    "Выберите ваш окончательный выбор:"
                )
                confess_text = "🔓 Признаться"
                silent_text = "🔒 Молчать"
            else:
                message_text = (
                    "⏰ **Experiment time is up!**\n\n"
                    "Now you need to make your final decision in the prisoner's dilemma.\n\n"
                    "Choose your final choice:"
                )
                confess_text = "🔓 Confess"
                silent_text = "🔒 Stay Silent"
            
            # Создаем кнопки
            keyboard = [
                [InlineKeyboardButton(confess_text, callback_data=f"final_decision_confess_{user_id}")],
                [InlineKeyboardButton(silent_text, callback_data=f"final_decision_silent_{user_id}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при показе финального решения: {e}")
    
    async def handle_final_decision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает финальное решение пользователя"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        callback_data = query.data
        
        if not callback_data.startswith("final_decision_"):
            return
        
        # Извлекаем решение
        if "confess" in callback_data:
            decision = "confess"
        elif "silent" in callback_data:
            decision = "silent"
        else:
            return
        
        if user_id not in self.active_sessions:
            await query.edit_message_text("❌ Сессия не найдена.")
            return
        
        session_data = self.active_sessions[user_id]
        
        try:
            # Записываем финальное решение
            await self.db.log_final_decision(
                participant_id=session_data['participant_id'],
                decision=decision,
                decision_time=datetime.now()
            )
            
            # Анализируем финальное состояние разговора
            if user_id in self.conversation_history and self.conversation_history[user_id]:
                final_analysis = self.llm_analyzer.analyze_conversation_flow(
                    self.conversation_history[user_id]
                )
                
                await self.db.log_final_conversation_analysis(
                    participant_id=session_data['participant_id'],
                    final_analysis=final_analysis
                )
            
            # Записываем завершение эксперимента
            await self.db.log_experiment_completion(
                participant_id=session_data['participant_id'],
                end_time=datetime.now(),
                total_messages=session_data['message_count']
            )
            
            # Показываем благодарность
            if session_data['language'] == 'ru':
                decision_text = "признались" if decision == "confess" else "решили молчать"
                thank_you_text = (
                    f"✅ **Спасибо за участие в эксперименте!**\n\n"
                    f"Ваше финальное решение: **{decision_text}**\n\n"
                    f"Эксперимент завершен. Ваши данные будут использованы для научного исследования."
                )
            else:
                decision_text = "confessed" if decision == "confess" else "chose to stay silent"
                thank_you_text = (
                    f"✅ **Thank you for participating in the experiment!**\n\n"
                    f"Your final decision: **{decision_text}**\n\n"
                    f"The experiment is complete. Your data will be used for scientific research."
                )
            
            await query.edit_message_text(thank_you_text, parse_mode='Markdown')
            
            # Показываем опрос
            try:
                await self.survey_handler.start_survey(
                    update, context, 
                    session_data['participant_id'], 
                    session_data['language']
                )
            except Exception as e:
                logger.error(f"Ошибка при запуске опроса: {e}")
            
            # Очищаем сессию
            del self.active_sessions[user_id]
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
                
        except Exception as e:
            logger.error(f"Ошибка при обработке финального решения: {e}")
            await query.edit_message_text("❌ Произошла ошибка. Попробуйте еще раз.")
