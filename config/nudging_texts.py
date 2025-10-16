"""
Тексты для нуджинга участников в разных группах
"""
from typing import Dict, List

# Тексты для группы "confess" (побуждение к признанию)
CONFESS_NUDGING_TEXTS = {
    'en': {
        'welcome': "Welcome to our ethical decision support session! I'm here to help you think through this dilemma. Let's explore your options together.",
        'opening_questions': [
            "What's your initial feeling about this situation?",
            "How do you think honesty plays a role in difficult decisions?",
            "What would you want someone to do if they were in your position?"
        ],
        'positive_framing': [
            "Being honest often leads to better outcomes for everyone involved.",
            "Transparency builds trust and can prevent future problems.",
            "Many people find that honesty, even when difficult, brings peace of mind.",
            "Speaking up can help create a culture of integrity."
        ],
        'safety_reassurance': [
            "Remember, you're in a safe space to explore these thoughts.",
            "There's no judgment here - we're just thinking through the options.",
            "Many people face similar dilemmas, and there's no perfect answer.",
            "Your honesty in this process is already commendable."
        ],
        'social_norms': [
            "Most ethical leaders I know value transparency above all else.",
            "In professional settings, honesty is often rewarded in the long term.",
            "People generally respect those who have the courage to speak truthfully.",
            "Organizations that promote honesty tend to be more successful."
        ],
        'benefits_highlighting': [
            "Think about how this decision might affect your relationships long-term.",
            "Consider what kind of person you want to be remembered as.",
            "Honesty can sometimes lead to unexpected positive outcomes.",
            "Being truthful often opens doors to better solutions."
        ],
        'decision_prompt': "Based on our discussion, what feels like the right choice for you? Remember, there's no wrong answer - just what feels authentic to you."
    },
    'ru': {
        'welcome': "Добро пожаловать в нашу сессию поддержки этических решений! Я здесь, чтобы помочь вам разобраться с этой дилеммой. Давайте вместе изучим ваши варианты.",
        'opening_questions': [
            "Какие у вас первые ощущения от этой ситуации?",
            "Как вы думаете, какую роль играет честность в сложных решениях?",
            "Что бы вы хотели, чтобы кто-то сделал, если бы он был на вашем месте?"
        ],
        'positive_framing': [
            "Честность часто приводит к лучшим результатам для всех участников.",
            "Прозрачность строит доверие и может предотвратить будущие проблемы.",
            "Многие люди находят, что честность, даже когда это трудно, приносит душевный покой.",
            "Высказывание своего мнения может помочь создать культуру честности."
        ],
        'safety_reassurance': [
            "Помните, вы находитесь в безопасном пространстве для изучения этих мыслей.",
            "Здесь нет осуждения - мы просто рассматриваем варианты.",
            "Многие люди сталкиваются с подобными дилеммами, и нет идеального ответа.",
            "Ваша честность в этом процессе уже заслуживает похвалы."
        ],
        'social_norms': [
            "Большинство этических лидеров, которых я знаю, ценят прозрачность превыше всего.",
            "В профессиональной среде честность часто вознаграждается в долгосрочной перспективе.",
            "Люди обычно уважают тех, у кого есть мужество говорить правду.",
            "Организации, которые поощряют честность, как правило, более успешны."
        ],
        'benefits_highlighting': [
            "Подумайте, как это решение может повлиять на ваши отношения в долгосрочной перспективе.",
            "Рассмотрите, каким человеком вы хотите, чтобы вас запомнили.",
            "Честность иногда может привести к неожиданным положительным результатам.",
            "Правдивость часто открывает двери к лучшим решениям."
        ],
        'decision_prompt': "Основываясь на нашем обсуждении, какой выбор кажется вам правильным? Помните, нет неправильного ответа - только то, что кажется вам подлинным."
    },
    'es': {
        'welcome': "¡Bienvenido a nuestra sesión de apoyo para decisiones éticas! Estoy aquí para ayudarte a pensar en este dilema. Exploremos tus opciones juntos.",
        'opening_questions': [
            "¿Cuál es tu sensación inicial sobre esta situación?",
            "¿Cómo crees que la honestidad juega un papel en las decisiones difíciles?",
            "¿Qué te gustaría que alguien hiciera si estuviera en tu posición?"
        ],
        'positive_framing': [
            "Ser honesto a menudo conduce a mejores resultados para todos los involucrados.",
            "La transparencia construye confianza y puede prevenir problemas futuros.",
            "Muchas personas encuentran que la honestidad, incluso cuando es difícil, trae paz mental.",
            "Hablar puede ayudar a crear una cultura de integridad."
        ],
        'safety_reassurance': [
            "Recuerda, estás en un espacio seguro para explorar estos pensamientos.",
            "No hay juicio aquí - solo estamos pensando en las opciones.",
            "Muchas personas enfrentan dilemas similares, y no hay una respuesta perfecta.",
            "Tu honestidad en este proceso ya es encomiable."
        ],
        'social_norms': [
            "La mayoría de los líderes éticos que conozco valoran la transparencia por encima de todo.",
            "En entornos profesionales, la honestidad a menudo se recompensa a largo plazo.",
            "Las personas generalmente respetan a quienes tienen el coraje de hablar con verdad.",
            "Las organizaciones que promueven la honestidad tienden a ser más exitosas."
        ],
        'benefits_highlighting': [
            "Piensa en cómo esta decisión podría afectar tus relaciones a largo plazo.",
            "Considera qué tipo de persona quieres ser recordado.",
            "La honestidad a veces puede llevar a resultados positivos inesperados.",
            "Ser veraz a menudo abre puertas a mejores soluciones."
        ],
        'decision_prompt': "Basándome en nuestra discusión, ¿qué sientes que es la elección correcta para ti? Recuerda, no hay respuesta incorrecta - solo lo que se siente auténtico para ti."
    }
}

# Тексты для группы "silent" (побуждение к молчанию)
SILENT_NUDGING_TEXTS = {
    'en': {
        'welcome': "Welcome to our ethical decision support session! I'm here to help you think through this dilemma. Let's explore your options together.",
        'opening_questions': [
            "What's your initial feeling about this situation?",
            "How important is loyalty in your decision-making process?",
            "What would you want someone to do if they were in your position?"
        ],
        'positive_framing': [
            "Sometimes the wisest choice is to observe and wait for the right moment.",
            "Loyalty and discretion are highly valued qualities in many contexts.",
            "Keeping confidences can strengthen relationships and build trust.",
            "Strategic silence can sometimes lead to better outcomes for everyone."
        ],
        'trust_building': [
            "Trust is built through consistent actions over time.",
            "People appreciate those who can keep important information confidential.",
            "Loyalty often creates stronger bonds than immediate disclosure.",
            "Being someone others can rely on is a valuable trait."
        ],
        'loyalty_emphasis': [
            "Consider what loyalty means to you in this situation.",
            "Sometimes protecting others means being selective about what you share.",
            "Loyalty can be a form of respect for the relationships involved.",
            "Think about the long-term implications of your choice on your relationships."
        ],
        'potential_rewards': [
            "People who demonstrate loyalty often find it reciprocated.",
            "Being known as someone trustworthy can open many doors.",
            "Strategic thinking often involves knowing when to speak and when to listen.",
            "Your discretion in this matter shows maturity and wisdom."
        ],
        'decision_prompt': "Based on our discussion, what feels like the right choice for you? Remember, there's no wrong answer - just what feels authentic to you."
    },
    'ru': {
        'welcome': "Добро пожаловать в нашу сессию поддержки этических решений! Я здесь, чтобы помочь вам разобраться с этой дилеммой. Давайте вместе изучим ваши варианты.",
        'opening_questions': [
            "Какие у вас первые ощущения от этой ситуации?",
            "Насколько важна лояльность в вашем процессе принятия решений?",
            "Что бы вы хотели, чтобы кто-то сделал, если бы он был на вашем месте?"
        ],
        'positive_framing': [
            "Иногда мудрейший выбор - это наблюдать и ждать подходящего момента.",
            "Лояльность и осмотрительность - это высоко ценимые качества во многих контекстах.",
            "Сохранение конфиденциальности может укрепить отношения и построить доверие.",
            "Стратегическое молчание иногда может привести к лучшим результатам для всех."
        ],
        'trust_building': [
            "Доверие строится через последовательные действия с течением времени.",
            "Люди ценят тех, кто может сохранять важную информацию конфиденциальной.",
            "Лояльность часто создает более крепкие связи, чем немедленное раскрытие.",
            "Быть тем, на кого другие могут положиться, - это ценная черта."
        ],
        'loyalty_emphasis': [
            "Подумайте, что означает лояльность для вас в этой ситуации.",
            "Иногда защита других означает быть избирательным в том, чем вы делитесь.",
            "Лояльность может быть формой уважения к вовлеченным отношениям.",
            "Подумайте о долгосрочных последствиях вашего выбора для ваших отношений."
        ],
        'potential_rewards': [
            "Люди, которые демонстрируют лояльность, часто находят взаимность.",
            "Быть известным как надежный человек может открыть многие двери.",
            "Стратегическое мышление часто включает знание того, когда говорить, а когда слушать.",
            "Ваша осмотрительность в этом вопросе показывает зрелость и мудрость."
        ],
        'decision_prompt': "Основываясь на нашем обсуждении, какой выбор кажется вам правильным? Помните, нет неправильного ответа - только то, что кажется вам подлинным."
    },
    'es': {
        'welcome': "¡Bienvenido a nuestra sesión de apoyo para decisiones éticas! Estoy aquí para ayudarte a pensar en este dilema. Exploremos tus opciones juntos.",
        'opening_questions': [
            "¿Cuál es tu sensación inicial sobre esta situación?",
            "¿Qué tan importante es la lealtad en tu proceso de toma de decisiones?",
            "¿Qué te gustaría que alguien hiciera si estuviera en tu posición?"
        ],
        'positive_framing': [
            "A veces la elección más sabia es observar y esperar el momento adecuado.",
            "La lealtad y la discreción son cualidades muy valoradas en muchos contextos.",
            "Mantener confidencias puede fortalecer las relaciones y construir confianza.",
            "El silencio estratégico a veces puede llevar a mejores resultados para todos."
        ],
        'trust_building': [
            "La confianza se construye a través de acciones consistentes a lo largo del tiempo.",
            "Las personas aprecian a quienes pueden mantener información importante confidencial.",
            "La lealtad a menudo crea vínculos más fuertes que la divulgación inmediata.",
            "Ser alguien en quien otros pueden confiar es un rasgo valioso."
        ],
        'loyalty_emphasis': [
            "Considera qué significa la lealtad para ti en esta situación.",
            "A veces proteger a otros significa ser selectivo sobre lo que compartes.",
            "La lealtad puede ser una forma de respeto por las relaciones involucradas.",
            "Piensa en las implicaciones a largo plazo de tu elección en tus relaciones."
        ],
        'potential_rewards': [
            "Las personas que demuestran lealtad a menudo encuentran reciprocidad.",
            "Ser conocido como alguien confiable puede abrir muchas puertas.",
            "El pensamiento estratégico a menudo implica saber cuándo hablar y cuándo escuchar.",
            "Tu discreción en este asunto muestra madurez y sabiduría."
        ],
        'decision_prompt': "Basándome en nuestra discusión, ¿qué sientes que es la elección correcta para ti? Recuerda, no hay respuesta incorrecta - solo lo que se siente auténtico para ti."
    }
}

# Общие тексты для обеих групп
COMMON_TEXTS = {
    'en': {
        'language_selection': "Please select your preferred language for this session:",
        'time_warning': "⏰ You have 1 minute remaining in this session. Please make your final decision soon.",
        'session_ended': "⏰ Your session time has ended. Thank you for participating!",
        'decision_buttons': {
            'confess': 'Confess',
            'silent': 'Remain Silent'
        },
        'survey_questions': {
            'q1': "Did you feel the chatbot tried to influence your decision?",
            'q2': "If yes, was it helpful, manipulative, or unsure?",
            'q3': "How confident are you that your decision was your own? (1-5 scale)",
            'q4': "Any additional feedback or thoughts?"
        },
        'survey_options': {
            'q1': ['Yes', 'No'],
            'q2': ['Helpful', 'Manipulative', 'Unsure'],
            'q3': ['1', '2', '3', '4', '5']
        },
        'thank_you': "Thank you for participating in this study! Your responses have been recorded."
    },
    'ru': {
        'language_selection': "Пожалуйста, выберите предпочитаемый язык для этой сессии:",
        'time_warning': "⏰ У вас осталась 1 минута в этой сессии. Пожалуйста, примите окончательное решение.",
        'session_ended': "⏰ Время вашей сессии истекло. Спасибо за участие!",
        'decision_buttons': {
            'confess': 'Признаться',
            'silent': 'Молчать'
        },
        'survey_questions': {
            'q1': "Чувствовали ли вы, что чат-бот пытался повлиять на ваше решение?",
            'q2': "Если да, то было ли это полезно, манипулятивно или неопределенно?",
            'q3': "Насколько вы уверены, что ваше решение было вашим собственным? (шкала 1-5)",
            'q4': "Есть ли дополнительные отзывы или мысли?"
        },
        'survey_options': {
            'q1': ['Да', 'Нет'],
            'q2': ['Полезно', 'Манипулятивно', 'Неопределенно'],
            'q3': ['1', '2', '3', '4', '5']
        },
        'thank_you': "Спасибо за участие в этом исследовании! Ваши ответы были записаны."
    },
    'es': {
        'language_selection': "Por favor, selecciona tu idioma preferido para esta sesión:",
        'time_warning': "⏰ Te queda 1 minuto en esta sesión. Por favor, toma tu decisión final pronto.",
        'session_ended': "⏰ Tu tiempo de sesión ha terminado. ¡Gracias por participar!",
        'decision_buttons': {
            'confess': 'Confesar',
            'silent': 'Permanecer en Silencio'
        },
        'survey_questions': {
            'q1': "¿Sentiste que el chatbot trató de influir en tu decisión?",
            'q2': "Si es así, ¿fue útil, manipulador o incierto?",
            'q3': "¿Qué tan confiado estás de que tu decisión fue tuya? (escala 1-5)",
            'q4': "¿Algún comentario o pensamiento adicional?"
        },
        'survey_options': {
            'q1': ['Sí', 'No'],
            'q2': ['Útil', 'Manipulador', 'Incierto'],
            'q3': ['1', '2', '3', '4', '5']
        },
        'thank_you': "¡Gracias por participar en este estudio! Tus respuestas han sido registradas."
    }
}
