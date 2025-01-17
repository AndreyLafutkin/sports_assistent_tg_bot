# Список команд
list_commands = {
    '/start': 'Начать регистрацию',
    '/help': 'Помощь по боту',
    '/menu': 'Главное меню',
    '/profile': 'Мой профиль'
}


# Словарь категорий упражнений
dict_exercises_categories = {
    'Бодибилдинг': 'Bodybuilding'
}


# Параметры базы данных упражнений
path_list_exercise_bodybuilding_db = 'database/DB_list_exercise/Bodybuilding.csv'
parameters_list_exercise_bodybuilding_db = ['Muscle_group', 'Muscle_group_en', 'Exercise', 'Exercise_en']


# Параметры базы данных пользователей
path_users_db = 'database/users.csv'
parameters_users_db = ['user_id', 'name', 'DB_training_plans', 'DB_workout', 'DB_history_AI']


# Параметры базы данных планов тренировок
path_training_plans_db = 'database/DB_training_plans/tp_user_id.csv'
parameters_training_plans_db = ['name', 'description']


# Параметры базы данных тренировок
path_workout_db = 'database/DB_workout/wr_user_id.csv'
parameters_workout_db = ['name', 'data', 'description']

# Параметры базы данных истории запросов ИИ
path_history_AI_db = 'database/DB_history_AI/ha_user_id.csv'
parameters_history_AI_db = ['timestamp', 'role', 'content']
