import pandas as pd
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import src.settings.settings as settings


# Главное меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Начать тренировку'), KeyboardButton(text='Задать вопрос виртуальному тренеру')],
    [KeyboardButton(text='Мой профиль')]], 
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Воспользуйтесь меню:')


# Меню профиля
profile_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Планы тренировок')],
    [KeyboardButton(text='История тренировок')],
    [KeyboardButton(text='Изменить имя'), KeyboardButton(text='Удалить профиль')],
    [KeyboardButton(text='Вернуться в главное меню')]], 
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Воспользуйтесь меню:')


# Меню удаления профиля
delete_profile_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да, удалить профиль', callback_data='delete_profile')],
    [InlineKeyboardButton(text='Нет, не хочу', callback_data='cancel_delete_profile')]])


# Меню планов тренировок
training_plans_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить план тренировок', callback_data='add_training_plan')],
    [InlineKeyboardButton(text='Удалить план тренировок', callback_data='delete_training_plan')],
    [InlineKeyboardButton(text='Вернуться в мой профиль', callback_data='back_to_profile')]])

# Меню планов тренировок для добавления
training_plans_menu_add = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить план тренировок', callback_data='add_training_plan')],
    [InlineKeyboardButton(text='Вернуться в мой профиль', callback_data='back_to_profile')]])


# Меню отмены виртуального тренера
cancel_virtual_assistant_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выйти с диалога c виртуальным тренером')]], 
    resize_keyboard=True, input_field_placeholder='Выход из диалога:')


# Меню таймера
timer_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='1:00'), KeyboardButton(text='1:30'), KeyboardButton(text='2:00'), KeyboardButton(text='2:30')],
    [KeyboardButton(text='3:00'), KeyboardButton(text='3:30'), KeyboardButton(text='4:00'), KeyboardButton(text='4:30')],
    [KeyboardButton(text='Ввести время'), KeyboardButton(text='Вернуться в главное меню')]], 
    resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите время:')


# Клавиатура отмены таймера
cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить таймер", callback_data="cancel_timer")]])


def create_training_plans_keyboard(user_id):
    """
    Функция создания клавиатуры выбора плана тренировок
    """
    df = pd.read_csv(settings.path_training_plans_db.replace('user_id', str(user_id)))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for index, row in df.iterrows():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=row['name'], 
                                                                callback_data=f'training_plan_{index}')])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Продолжить без плана', 
                                                          callback_data='continue_without_plan')])
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Вернуться в главное меню', 
                                                          callback_data='back_to_main_menu')])
    
    return keyboard


# Клавиатура выбора категории упражнений
def create_exercises_categories_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category, value in settings.dict_exercises_categories.items():
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=category, callback_data=f'exercises_category_{value}')])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Назад', 
                                                          callback_data='back_to_training_plans')])
    
    return keyboard


# Клавиатура выбора группы мышц
def create_muscle_groups_keyboard():
    df = pd.read_csv(settings.path_list_exercise_bodybuilding_db)
    df = df.iloc[:, :2]
    df = df.drop_duplicates(subset=['Muscle_group'])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for i in range(len(df)):
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=str(df.iloc[i, 0]), 
                                                            callback_data=f'muscle_group_{str(df.iloc[i, 1])}')])
    
    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Назад', 
                                                          callback_data='back_to_choose_exercises_category')])
    
    return keyboard


# Клавиатура выбора упражнений
def create_exercises_keyboard(muscle_group):
    df = pd.read_csv(settings.path_list_exercise_bodybuilding_db)
    df = df[df['Muscle_group_en'] == muscle_group]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for i in range(len(df)):
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=str(df.iloc[i, 2]), 
                                                            callback_data=f'exercise_{str(df.iloc[i, 3])}')])

    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Назад', 
                                                          callback_data='back_to_choose_muscle_group')])
    
    return keyboard


# Клавиатура добавления таймера
add_timer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Включить таймер', callback_data='add_timer')],
    [InlineKeyboardButton(text='Пропустить таймер', callback_data='skip_timer')]])


# Клавиатура добавления упражнения
add_exercise_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить упражнение', callback_data='add_exercise')],
    [InlineKeyboardButton(text='Закончить тренировку', callback_data='finish_workout')]])