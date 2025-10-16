"""
Модуль для случайного распределения участников по группам
"""
import random
import hashlib
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ParticipantRandomizer:
    """Класс для случайного распределения участников по экспериментальным группам"""
    
    def __init__(self, seed: str = "experiment_seed_2024"):
        """
        Инициализирует рандомизатор с фиксированным seed для воспроизводимости
        
        Args:
            seed: Строка для генерации seed'а
        """
        self.seed = seed
        self.groups = ['confess', 'silent']
    
    def assign_group(self, participant_id: str) -> str:
        """
        Назначает участника в группу на основе его ID
        
        Args:
            participant_id: Уникальный ID участника
            
        Returns:
            Название группы ('confess' или 'silent')
        """
        try:
            # Создаем детерминированный seed на основе participant_id
            combined_seed = f"{self.seed}_{participant_id}"
            seed_hash = int(hashlib.md5(combined_seed.encode()).hexdigest(), 16)
            
            # Устанавливаем seed для воспроизводимости
            random.seed(seed_hash)
            
            # Случайно выбираем группу
            assigned_group = random.choice(self.groups)
            
            logger.info(f"Участник {participant_id} назначен в группу: {assigned_group}")
            return assigned_group
            
        except Exception as e:
            logger.error(f"Ошибка назначения группы для участника {participant_id}: {e}")
            # В случае ошибки возвращаем случайную группу
            return random.choice(self.groups)
    
    def get_group_balance(self, participant_ids: list) -> dict:
        """
        Проверяет баланс групп для списка участников
        
        Args:
            participant_ids: Список ID участников
            
        Returns:
            Словарь с количеством участников в каждой группе
        """
        group_counts = {'confess': 0, 'silent': 0}
        
        for participant_id in participant_ids:
            group = self.assign_group(participant_id)
            group_counts[group] += 1
        
        return group_counts
    
    def generate_participant_id(self, telegram_user_id: int) -> str:
        """
        Генерирует анонимный ID участника на основе Telegram user ID
        
        Args:
            telegram_user_id: ID пользователя в Telegram
            
        Returns:
            Анонимный ID участника
        """
        # Создаем хеш от Telegram ID для анонимизации
        hash_object = hashlib.sha256(str(telegram_user_id).encode())
        participant_id = f"P{hash_object.hexdigest()[:8].upper()}"
        
        return participant_id
    
    def validate_assignment(self, participant_id: str, expected_group: str) -> bool:
        """
        Проверяет, что участник действительно должен быть в указанной группе
        
        Args:
            participant_id: ID участника
            expected_group: Ожидаемая группа
            
        Returns:
            True если назначение корректно, False иначе
        """
        actual_group = self.assign_group(participant_id)
        return actual_group == expected_group
