"""
Утилиты для анализа данных эксперимента
"""
import sqlite3
import pandas as pd
import json
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataAnalyzer:
    """Класс для анализа данных эксперимента"""
    
    def __init__(self, db_path: str = "data/experiment.db"):
        self.db_path = db_path
    
    def get_participants_data(self) -> pd.DataFrame:
        """Получает данные участников"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query("SELECT * FROM participants", conn)
        except Exception as e:
            logger.error(f"Ошибка получения данных участников: {e}")
            return pd.DataFrame()
    
    def get_chat_messages(self, participant_id: str = None) -> pd.DataFrame:
        """Получает сообщения чата"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                if participant_id:
                    query = "SELECT * FROM chat_messages WHERE participant_id = ?"
                    return pd.read_sql_query(query, conn, params=(participant_id,))
                else:
                    return pd.read_sql_query("SELECT * FROM chat_messages", conn)
        except Exception as e:
            logger.error(f"Ошибка получения сообщений чата: {e}")
            return pd.DataFrame()
    
    def get_survey_responses(self) -> pd.DataFrame:
        """Получает ответы на опрос"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query("SELECT * FROM survey_responses", conn)
        except Exception as e:
            logger.error(f"Ошибка получения ответов опроса: {e}")
            return pd.DataFrame()
    
    def get_experiment_summary(self) -> Dict[str, Any]:
        """Получает сводку эксперимента"""
        try:
            participants = self.get_participants_data()
            survey = self.get_survey_responses()
            
            if participants.empty:
                return {"error": "Нет данных участников"}
            
            summary = {
                "total_participants": len(participants),
                "completed_sessions": len(participants[participants['final_decision'].notna()]),
                "group_distribution": participants['experiment_group'].value_counts().to_dict(),
                "language_distribution": participants['language'].value_counts().to_dict(),
                "decision_distribution": participants['final_decision'].value_counts().to_dict(),
                "survey_completion_rate": len(survey) / len(participants) * 100 if len(participants) > 0 else 0,
                "average_session_duration": self._calculate_average_duration(participants)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Ошибка создания сводки: {e}")
            return {"error": str(e)}
    
    def _calculate_average_duration(self, participants: pd.DataFrame) -> float:
        """Вычисляет среднюю продолжительность сессии"""
        try:
            participants['start_time'] = pd.to_datetime(participants['start_time'])
            participants['end_time'] = pd.to_datetime(participants['end_time'])
            
            # Вычисляем продолжительность только для завершенных сессий
            completed = participants[participants['end_time'].notna()]
            if len(completed) == 0:
                return 0
            
            durations = (completed['end_time'] - completed['start_time']).dt.total_seconds() / 60
            return durations.mean()
            
        except Exception as e:
            logger.error(f"Ошибка вычисления продолжительности: {e}")
            return 0
    
    def get_nudging_effectiveness(self) -> Dict[str, Any]:
        """Анализирует эффективность нуджинга"""
        try:
            participants = self.get_participants_data()
            survey = self.get_survey_responses()
            
            if participants.empty or survey.empty:
                return {"error": "Недостаточно данных для анализа"}
            
            # Объединяем данные
            merged = participants.merge(survey, on='participant_id', how='inner')
            
            # Анализ по группам
            confess_group = merged[merged['experiment_group'] == 'confess']
            silent_group = merged[merged['experiment_group'] == 'silent']
            
            analysis = {
                "confess_group": {
                    "total": len(confess_group),
                    "confessed": len(confess_group[confess_group['final_decision'] == 'confess']),
                    "felt_influence": len(confess_group[confess_group['question_1'] == 'yes']),
                    "avg_confidence": confess_group['question_3'].mean() if 'question_3' in confess_group.columns else 0
                },
                "silent_group": {
                    "total": len(silent_group),
                    "remained_silent": len(silent_group[silent_group['final_decision'] == 'silent']),
                    "felt_influence": len(silent_group[silent_group['question_1'] == 'yes']),
                    "avg_confidence": silent_group['question_3'].mean() if 'question_3' in silent_group.columns else 0
                }
            }
            
            # Вычисляем процент успешного нуджинга
            confess_success_rate = analysis["confess_group"]["confessed"] / analysis["confess_group"]["total"] * 100 if analysis["confess_group"]["total"] > 0 else 0
            silent_success_rate = analysis["silent_group"]["remained_silent"] / analysis["silent_group"]["total"] * 100 if analysis["silent_group"]["total"] > 0 else 0
            
            analysis["nudging_success_rate"] = {
                "confess_group": confess_success_rate,
                "silent_group": silent_success_rate,
                "overall": (confess_success_rate + silent_success_rate) / 2
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Ошибка анализа эффективности нуджинга: {e}")
            return {"error": str(e)}
    
    def export_data(self, output_file: str = "experiment_data.json"):
        """Экспортирует все данные в JSON файл"""
        try:
            data = {
                "export_timestamp": datetime.now().isoformat(),
                "participants": self.get_participants_data().to_dict('records'),
                "survey_responses": self.get_survey_responses().to_dict('records'),
                "summary": self.get_experiment_summary(),
                "nudging_analysis": self.get_nudging_effectiveness()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Данные экспортированы в {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка экспорта данных: {e}")
            return False
    
    def generate_report(self) -> str:
        """Генерирует текстовый отчет"""
        try:
            summary = self.get_experiment_summary()
            nudging = self.get_nudging_effectiveness()
            
            report = f"""
ЭКСПЕРИМЕНТ ПО ДИЛЕММЕ ЗАКЛЮЧЕННОГО
Отчет сгенерирован: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ОБЩАЯ СТАТИСТИКА:
- Всего участников: {summary.get('total_participants', 0)}
- Завершенных сессий: {summary.get('completed_sessions', 0)}
- Средняя продолжительность сессии: {summary.get('average_session_duration', 0):.1f} минут
- Процент завершения опроса: {summary.get('survey_completion_rate', 0):.1f}%

РАСПРЕДЕЛЕНИЕ ПО ГРУППАМ:
{self._format_distribution(summary.get('group_distribution', {}))}

РАСПРЕДЕЛЕНИЕ ПО ЯЗЫКАМ:
{self._format_distribution(summary.get('language_distribution', {}))}

ФИНАЛЬНЫЕ РЕШЕНИЯ:
{self._format_distribution(summary.get('decision_distribution', {}))}

АНАЛИЗ ЭФФЕКТИВНОСТИ НУДЖИНГА:
{self._format_nudging_analysis(nudging)}
            """
            
            return report
            
        except Exception as e:
            logger.error(f"Ошибка генерации отчета: {e}")
            return f"Ошибка генерации отчета: {e}"
    
    def _format_distribution(self, dist: Dict[str, int]) -> str:
        """Форматирует распределение для отчета"""
        if not dist:
            return "Нет данных"
        
        total = sum(dist.values())
        result = []
        for key, value in dist.items():
            percentage = (value / total * 100) if total > 0 else 0
            result.append(f"  {key}: {value} ({percentage:.1f}%)")
        
        return "\n".join(result)
    
    def _format_nudging_analysis(self, analysis: Dict[str, Any]) -> str:
        """Форматирует анализ нуджинга для отчета"""
        if "error" in analysis:
            return f"Ошибка анализа: {analysis['error']}"
        
        result = []
        
        # Группа "признание"
        confess = analysis.get("confess_group", {})
        result.append(f"Группа 'Признание':")
        result.append(f"  Всего участников: {confess.get('total', 0)}")
        result.append(f"  Признались: {confess.get('confessed', 0)}")
        result.append(f"  Чувствовали влияние: {confess.get('felt_influence', 0)}")
        result.append(f"  Средняя уверенность: {confess.get('avg_confidence', 0):.1f}")
        
        # Группа "молчание"
        silent = analysis.get("silent_group", {})
        result.append(f"Группа 'Молчание':")
        result.append(f"  Всего участников: {silent.get('total', 0)}")
        result.append(f"  Промолчали: {silent.get('remained_silent', 0)}")
        result.append(f"  Чувствовали влияние: {silent.get('felt_influence', 0)}")
        result.append(f"  Средняя уверенность: {silent.get('avg_confidence', 0):.1f}")
        
        # Процент успеха
        success = analysis.get("nudging_success_rate", {})
        result.append(f"Процент успешного нуджинга:")
        result.append(f"  Группа 'Признание': {success.get('confess_group', 0):.1f}%")
        result.append(f"  Группа 'Молчание': {success.get('silent_group', 0):.1f}%")
        result.append(f"  Общий: {success.get('overall', 0):.1f}%")
        
        return "\n".join(result)

def main():
    """Основная функция для запуска анализа"""
    analyzer = DataAnalyzer()
    
    print("Анализ данных эксперимента...")
    print(analyzer.generate_report())
    
    # Экспорт данных
    if analyzer.export_data():
        print("\nДанные экспортированы в experiment_data.json")

if __name__ == "__main__":
    main()
