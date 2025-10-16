"""
LLM анализатор для обработки сообщений пользователей
Интеграция с cloud.ru API для анализа эмоций, намерений и контекста
"""

import logging
import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config.settings import Config

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Анализатор сообщений с использованием LLM"""
    
    def __init__(self):
        self.api_key = Config.CLOUD_RU_API_KEY
        self.base_url = "https://api.cloud.ru/v1"
        self.model = "gpt-3.5-turbo"  # Можно изменить на другую модель
        
    def analyze_message(self, message: str, context: Dict = None) -> Dict:
        """
        Анализирует сообщение пользователя
        
        Args:
            message: Текст сообщения
            context: Контекст разговора
            
        Returns:
            Словарь с результатами анализа
        """
        try:
            if not self.api_key:
                logger.warning("Cloud.ru API ключ не настроен, возвращаем базовый анализ")
                return self._basic_analysis(message)
            
            # Формируем промпт для анализа
            prompt = self._create_analysis_prompt(message, context)
            
            # Отправляем запрос к API
            response = self._call_cloud_ru_api(prompt)
            
            if response:
                return self._parse_analysis_response(response)
            else:
                return self._basic_analysis(message)
                
        except Exception as e:
            logger.error(f"Ошибка при анализе сообщения: {e}")
            return self._basic_analysis(message)
    
    def _create_analysis_prompt(self, message: str, context: Dict = None) -> str:
        """Создает промпт для анализа сообщения"""
        
        context_info = ""
        if context:
            context_info = f"""
Контекст разговора:
- Группа: {context.get('group', 'неизвестно')}
- Время в эксперименте: {context.get('time_elapsed', 0)} минут
- Предыдущие сообщения: {context.get('message_count', 0)}
"""
        
        prompt = f"""
Проанализируй следующее сообщение пользователя в контексте эксперимента по дилемме заключенного:

{context_info}

Сообщение пользователя: "{message}"

Пожалуйста, проанализируй и верни результат в формате JSON со следующими полями:

1. "emotion": эмоциональное состояние (positive, negative, neutral, anxious, frustrated, cooperative, defensive)
2. "intent": намерение пользователя (cooperate, defect, question, complaint, confusion, agreement, disagreement)
3. "confidence": уровень уверенности в решении (high, medium, low)
4. "persuasion_resistance": сопротивление убеждению (high, medium, low)
5. "key_themes": основные темы в сообщении (массив строк)
6. "suggested_response": предложение для ответа бота (краткое)
7. "nudging_effectiveness": эффективность нуджинга (high, medium, low)
8. "risk_of_dropout": риск выхода из эксперимента (high, medium, low)

Ответ должен быть только в формате JSON, без дополнительного текста.
"""
        return prompt
    
    def _call_cloud_ru_api(self, prompt: str) -> Optional[Dict]:
        """Вызывает API cloud.ru"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по анализу человеческого поведения в экспериментах. Анализируй сообщения и возвращай результат в формате JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content")
            else:
                logger.error(f"Ошибка API cloud.ru: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при вызове cloud.ru API: {e}")
            return None
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Парсит ответ от LLM"""
        try:
            # Пытаемся извлечь JSON из ответа
            if isinstance(response, str):
                # Ищем JSON в ответе
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    return json.loads(json_str)
            
            # Если не удалось распарсить, возвращаем базовый анализ
            return self._basic_analysis("")
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа: {e}")
            return self._basic_analysis("")
    
    def _basic_analysis(self, message: str) -> Dict:
        """Базовый анализ без LLM"""
        return {
            "emotion": "neutral",
            "intent": "question",
            "confidence": "medium",
            "persuasion_resistance": "medium",
            "key_themes": ["general"],
            "suggested_response": "Понял, продолжаем эксперимент",
            "nudging_effectiveness": "medium",
            "risk_of_dropout": "low",
            "analysis_method": "basic"
        }
    
    def analyze_conversation_flow(self, messages: List[Dict]) -> Dict:
        """
        Анализирует поток разговора
        
        Args:
            messages: Список сообщений в формате [{"text": "...", "timestamp": "...", "sender": "user/bot"}]
            
        Returns:
            Анализ потока разговора
        """
        try:
            if not messages:
                return {"flow_analysis": "no_messages"}
            
            # Анализируем последние несколько сообщений
            recent_messages = messages[-5:] if len(messages) > 5 else messages
            
            conversation_text = "\n".join([
                f"{msg.get('sender', 'unknown')}: {msg.get('text', '')}"
                for msg in recent_messages
            ])
            
            prompt = f"""
Проанализируй поток разговора в эксперименте по дилемме заключенного:

{conversation_text}

Верни анализ в формате JSON:
1. "engagement_level": уровень вовлеченности (high, medium, low)
2. "conversation_quality": качество разговора (good, average, poor)
3. "user_satisfaction": удовлетворенность пользователя (high, medium, low)
4. "experiment_progress": прогресс эксперимента (on_track, struggling, off_track)
5. "recommendations": рекомендации для бота (массив строк)
"""
            
            response = self._call_cloud_ru_api(prompt)
            
            if response:
                return self._parse_analysis_response(response)
            else:
                return {
                    "engagement_level": "medium",
                    "conversation_quality": "average",
                    "user_satisfaction": "medium",
                    "experiment_progress": "on_track",
                    "recommendations": ["Продолжать стандартный протокол"],
                    "analysis_method": "basic"
                }
                
        except Exception as e:
            logger.error(f"Ошибка при анализе потока разговора: {e}")
            return {"flow_analysis": "error", "error": str(e)}
    
    def generate_personalized_response(self, user_message: str, analysis: Dict, context: Dict) -> str:
        """
        Генерирует персонализированный ответ на основе анализа
        
        Args:
            user_message: Сообщение пользователя
            analysis: Результат анализа сообщения
            context: Контекст разговора
            
        Returns:
            Персонализированный ответ
        """
        try:
            if not self.api_key:
                return self._get_default_response(analysis, context)
            
            prompt = f"""
На основе анализа сообщения пользователя, сгенерируй персонализированный ответ бота для эксперимента по дилемме заключенного.

Анализ сообщения:
- Эмоция: {analysis.get('emotion', 'neutral')}
- Намерение: {analysis.get('intent', 'question')}
- Уверенность: {analysis.get('confidence', 'medium')}
- Сопротивление убеждению: {analysis.get('persuasion_resistance', 'medium')}
- Основные темы: {', '.join(analysis.get('key_themes', []))}

Контекст:
- Группа: {context.get('group', 'неизвестно')}
- Время в эксперименте: {context.get('time_elapsed', 0)} минут
- Язык: {context.get('language', 'ru')}

Сообщение пользователя: "{user_message}"

Сгенерируй ответ бота, который:
1. Учитывает эмоциональное состояние пользователя
2. Соответствует группе (confess/silent)
3. Поддерживает эксперимент
4. Естественно звучит на русском языке
5. Не превышает 2-3 предложения

Ответ должен быть только текстом, без дополнительных комментариев.
"""
            
            response = self._call_cloud_ru_api(prompt)
            
            if response and isinstance(response, str):
                # Очищаем ответ от лишних символов
                clean_response = response.strip().strip('"').strip("'")
                return clean_response
            else:
                return self._get_default_response(analysis, context)
                
        except Exception as e:
            logger.error(f"Ошибка при генерации персонализированного ответа: {e}")
            return self._get_default_response(analysis, context)
    
    def _get_default_response(self, analysis: Dict, context: Dict) -> str:
        """Возвращает стандартный ответ на основе анализа"""
        emotion = analysis.get('emotion', 'neutral')
        intent = analysis.get('intent', 'question')
        group = context.get('group', 'unknown')
        
        # Базовые ответы в зависимости от группы и эмоции
        if group == 'confess':
            if emotion in ['anxious', 'frustrated']:
                return "Понимаю ваши сомнения. Помните, что честность - это важное качество, которое поможет вам в долгосрочной перспективе."
            else:
                return "Спасибо за ваше сообщение. Продолжайте размышлять о важности честности в ваших решениях."
        else:  # silent group
            if emotion in ['anxious', 'frustrated']:
                return "Ваши размышления понятны. Иногда молчание может быть мудрым выбором."
            else:
                return "Спасибо за ваше сообщение. Продолжайте обдумывать свои решения."
    
    def log_analysis(self, user_id: int, message: str, analysis: Dict, response: str):
        """Логирует анализ для дальнейшего изучения"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": message,
                "analysis": analysis,
                "generated_response": response
            }
            
            logger.info(f"LLM Analysis: {json.dumps(log_entry, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"Ошибка при логировании анализа: {e}")
