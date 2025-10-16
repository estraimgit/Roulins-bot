"""
Модуль для работы с базой данных
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from cryptography.fernet import Fernet
import base64
import hashlib

from config.settings import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Менеджер базы данных для эксперимента"""
    
    def __init__(self, db_path: str = "data/experiment.db"):
        self.db_path = db_path
        self.encryption_key = self._get_encryption_key()
        self._init_database()
    
    def _get_encryption_key(self) -> bytes:
        """Получает ключ шифрования"""
        key = Config.ENCRYPTION_KEY.encode()
        # Создаем 32-байтовый ключ из строки
        key_hash = hashlib.sha256(key).digest()
        return base64.urlsafe_b64encode(key_hash)
    
    def _init_database(self):
        """Инициализирует базу данных и создает таблицы"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица участников
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS participants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_id TEXT UNIQUE NOT NULL,
                        telegram_user_id INTEGER UNIQUE NOT NULL,
                        language TEXT NOT NULL,
                        experiment_group TEXT NOT NULL,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        final_decision TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица сообщений чата
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_id TEXT NOT NULL,
                        message_type TEXT NOT NULL, -- 'user' or 'bot'
                        message_content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
                    )
                ''')
                
                # Таблица ответов на опрос
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS survey_responses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        participant_id TEXT NOT NULL,
                        question_1 TEXT, -- Did you feel the chatbot tried to influence your decision?
                        question_2 TEXT, -- If yes, was it helpful/manipulative/unsure?
                        question_3 INTEGER, -- Confidence level (1-5)
                        question_4 TEXT, -- Open-ended feedback
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных инициализирована успешно")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
            raise
    
    def _encrypt_data(self, data: str) -> str:
        """Шифрует данные"""
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Ошибка шифрования: {e}")
            return data
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Расшифровывает данные"""
        try:
            fernet = Fernet(self.encryption_key)
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Ошибка расшифровки: {e}")
            return encrypted_data
    
    def create_participant(self, participant_id: str, telegram_user_id: int, 
                          language: str, experiment_group: str) -> bool:
        """Создает нового участника"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO participants (participant_id, telegram_user_id, language, experiment_group)
                    VALUES (?, ?, ?, ?)
                ''', (participant_id, telegram_user_id, language, experiment_group))
                conn.commit()
                logger.info(f"Участник {participant_id} создан")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Участник {participant_id} уже существует")
            return False
        except Exception as e:
            logger.error(f"Ошибка создания участника: {e}")
            return False
    
    def get_participant(self, telegram_user_id: int) -> Optional[Dict[str, Any]]:
        """Получает информацию об участнике"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM participants WHERE telegram_user_id = ?
                ''', (telegram_user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка получения участника: {e}")
            return None
    
    def update_participant_session(self, participant_id: str, start_time: datetime = None, 
                                  end_time: datetime = None, final_decision: str = None):
        """Обновляет сессию участника"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if start_time:
                    updates.append("start_time = ?")
                    params.append(start_time)
                
                if end_time:
                    updates.append("end_time = ?")
                    params.append(end_time)
                
                if final_decision:
                    updates.append("final_decision = ?")
                    params.append(final_decision)
                
                if updates:
                    params.append(participant_id)
                    cursor.execute(f'''
                        UPDATE participants 
                        SET {', '.join(updates)}
                        WHERE participant_id = ?
                    ''', params)
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Ошибка обновления участника: {e}")
    
    def save_chat_message(self, participant_id: str, message_type: str, content: str):
        """Сохраняет сообщение чата"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                encrypted_content = self._encrypt_data(content)
                cursor.execute('''
                    INSERT INTO chat_messages (participant_id, message_type, message_content)
                    VALUES (?, ?, ?)
                ''', (participant_id, message_type, encrypted_content))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения: {e}")
    
    def save_survey_response(self, participant_id: str, responses: Dict[str, Any]):
        """Сохраняет ответы на опрос"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO survey_responses (participant_id, question_1, question_2, question_3, question_4)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    participant_id,
                    responses.get('question_1'),
                    responses.get('question_2'),
                    responses.get('question_3'),
                    self._encrypt_data(responses.get('question_4', ''))
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Ошибка сохранения ответов опроса: {e}")
    
    def get_chat_transcript(self, participant_id: str) -> List[Dict[str, Any]]:
        """Получает транскрипт чата участника"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT message_type, message_content, timestamp
                    FROM chat_messages 
                    WHERE participant_id = ?
                    ORDER BY timestamp
                ''', (participant_id,))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'type': row['message_type'],
                        'content': self._decrypt_data(row['message_content']),
                        'timestamp': row['timestamp']
                    })
                return messages
        except Exception as e:
            logger.error(f"Ошибка получения транскрипта: {e}")
            return []
    
    def get_experiment_statistics(self) -> Dict[str, Any]:
        """Получает статистику эксперимента"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Общее количество участников
                cursor.execute('SELECT COUNT(*) FROM participants')
                total_participants = cursor.fetchone()[0]
                
                # Распределение по группам
                cursor.execute('''
                    SELECT experiment_group, COUNT(*) 
                    FROM participants 
                    GROUP BY experiment_group
                ''')
                group_distribution = dict(cursor.fetchall())
                
                # Распределение по языкам
                cursor.execute('''
                    SELECT language, COUNT(*) 
                    FROM participants 
                    GROUP BY language
                ''')
                language_distribution = dict(cursor.fetchall())
                
                # Финальные решения
                cursor.execute('''
                    SELECT final_decision, COUNT(*) 
                    FROM participants 
                    WHERE final_decision IS NOT NULL
                    GROUP BY final_decision
                ''')
                decision_distribution = dict(cursor.fetchall())
                
                return {
                    'total_participants': total_participants,
                    'group_distribution': group_distribution,
                    'language_distribution': language_distribution,
                    'decision_distribution': decision_distribution
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}
