import pandas as pd
import os

from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

# Импорт файлов проекта
import src.keyboards.keyboards as kbs
import src.settings.settings as settings

# Создание роутера
router_profile = Router()


# Состояния для формы
class Form(StatesGroup):
    change_name = State()
    add_training_plan = State()
    add_training_plan_description = State()
    delete_training_plan = State()
    enter_score = State()
    enter_comment = State()



@router_profile.message(Command('profile'))
@router_profile.message(F.text == 'Мой профиль')
async def process_profile_command(message: Message):
    """
    Функция вывода профиля пользователя
    """
    await message.answer(text='Выберите действие:', reply_markup=kbs.profile_menu)


@router_profile.message(F.text == 'Изменить имя')
async def process_change_name_command(message: Message, state: FSMContext):
    """
    Функция обработки кнопки "Изменить имя"
    """
    user_id = message.from_user.id
    df = pd.read_csv(settings.path_users_db)

    if user_id in df['user_id'].values:
        await message.answer('Введите новое имя:')
        await state.set_state(Form.change_name)
        
    else:
        await message.answer('Вы не зарегистрированы!')


@router_profile.message(Form.change_name)
async def process_change_name_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода нового имени пользователя
    """
    user_name = message.text
    user_id = message.from_user.id

    df = pd.read_csv(settings.path_users_db)
    df.loc[df['user_id'] == user_id, 'name'] = user_name
    df.to_csv(settings.path_users_db, index=False)

    await message.answer('Имя успешно изменено!', reply_markup=kbs.profile_menu)
    await state.clear()


@router_profile.message(F.text == 'Удалить профиль')
async def process_delete_profile_command(message: Message):
    """
    Функция обработки кнопки "Удалить профиль"
    """
    await message.answer('Вы действительно хотите удалить профиль?', reply_markup=kbs.delete_profile_menu)


@router_profile.callback_query(F.data == 'delete_profile')
async def process_delete_profile_command(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки кнопки "Да, удалить профиль"
    """
    await callback.message.answer('Пожалуйста, оцените использование бота от 1 до 10:')
    await state.set_state(Form.enter_score)


@router_profile.message(Form.enter_score)
async def process_score_input(message: Message, state: FSMContext):
    """
    Функция обработки ввода оценки
    """
    score = message.text
    user_id = message.from_user.id

    if score.isdigit() and 1 <= int(score) <= 10:
        await message.answer('Введите комментарий с пожеланиями для разработчиков:')
        await state.update_data(score=score)
        await state.set_state(Form.enter_comment)
    else:
        await message.answer('Пожалуйста, введите корректную оценку от 1 до 10.')

@router_profile.message(Form.enter_comment)
async def process_comment_input(message: Message, state: FSMContext):
    """
    Функция обработки ввода комментария
    """
    comment = message.text
    user_id = message.from_user.id
    data = await state.get_data()
    score = data.get('score')

    df = pd.read_csv("database/form.csv")

    df.loc[len(df)] = [score, comment]
    df.to_csv("database/form.csv", index=False)

    # Удаление профиля
    df = pd.read_csv(settings.path_users_db)
    df = df[df['user_id'] != user_id]
    df.to_csv(settings.path_users_db, index=False)

    os.remove(settings.path_training_plans_db.replace('user_id', str(user_id)))
    os.remove(settings.path_workout_db.replace('user_id', str(user_id)))
    os.remove(settings.path_history_AI_db.replace('user_id', str(user_id)))

    await message.answer('Профиль успешно удален! Спасибо за ваш отзыв!')
    await state.clear()
    

@router_profile.callback_query(F.data == 'cancel_delete_profile')
async def process_cancel_delete_profile_command(callback: CallbackQuery):
    """
    Функция обработки кнопки "Нет, не хочу"
    """
    await callback.message.answer('Вы отменили удаление профиля!', reply_markup=kbs.profile_menu)
    await callback.message.delete()


@router_profile.message(F.text == 'Планы тренировок')
async def process_training_plans_command(message: Message):
    """
    Функция вывода планов тренировок
    """
    user_id = message.from_user.id
    file_path = settings.path_training_plans_db.replace('user_id', str(user_id))

    df = pd.read_csv(file_path)
    if not df['name'].empty:
        await message.answer(f'Ваши планы тренировок:\n{df["name"].to_string(index=False)}', reply_markup=kbs.training_plans_menu)
    else:
        await message.answer('У вас нет планов тренировок', reply_markup=kbs.training_plans_menu_add)


@router_profile.callback_query(F.data == 'add_training_plan')
async def process_add_training_plan_command(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки кнопки "Добавить план тренировок"
    """
    await callback.message.answer('Введите название плана тренировок:')
    await state.set_state(Form.add_training_plan)


@router_profile.message(Form.add_training_plan)
async def process_add_training_plan_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода названия плана тренировок
    """
    training_plan_name = message.text
    await state.update_data(training_plan_name=training_plan_name)
    await message.answer('Введите описание плана тренировок:')
    await state.set_state(Form.add_training_plan_description)


@router_profile.message(Form.add_training_plan_description)
async def process_add_training_plan_description_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода описания плана тренировок
    """
    training_plan_description = message.text
    await state.update_data(training_plan_description=training_plan_description)
    data = await state.get_data()
    user_id = message.from_user.id

    df = pd.read_csv(settings.path_training_plans_db.replace('user_id', str(user_id)))
    df.loc[len(df)] = [data['training_plan_name'], data['training_plan_description']]
    df.to_csv(settings.path_training_plans_db.replace('user_id', str(user_id)), index=False)
    await message.answer('План тренировок успешно добавлен!', reply_markup=kbs.profile_menu)
    await state.clear()


@router_profile.callback_query(F.data == 'delete_training_plan')
async def process_delete_training_plan_command(callback: CallbackQuery, state: FSMContext):
    """
    Функция обработки кнопки "Удалить план тренировок"
    """
    user_id = callback.from_user.id
    await callback.message.delete()
    df = pd.read_csv(settings.path_training_plans_db.replace('user_id', str(user_id)))
    await callback.message.answer('Введите название плана тренировок для удаления:\n'
                                  'Скопируйте название из списка без кавычек:\n'
                                  f'"{df["name"].to_string(index=False)}"')
    await state.set_state(Form.delete_training_plan)


@router_profile.message(Form.delete_training_plan)
async def process_delete_training_plan_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода названия плана тренировок для удаления
    """
    training_plan_name = message.text
    user_id = message.from_user.id
    df = pd.read_csv(settings.path_training_plans_db.replace('user_id', str(user_id)))
    if training_plan_name in df['name'].values:
        df = df[df['name'] != training_plan_name]
        df.to_csv(settings.path_training_plans_db.replace('user_id', str(user_id)), index=False)
        await message.answer('План тренировок успешно удален!', reply_markup=kbs.profile_menu)
        await state.clear()
    else:
        await message.answer('План тренировок не найден!')


@router_profile.callback_query(F.data == 'back_to_profile')
async def process_back_to_profile_command(callback: CallbackQuery):
    """
    Функция обработки кнопки "Вернуться в мой профиль"
    """
    await callback.message.delete()
    await callback.message.answer('Выберите действие:', reply_markup=kbs.profile_menu)


@router_profile.message(F.text == 'История тренировок')
async def process_history_of_workouts_command(message: Message):
    """
    Функция обработки кнопки "История тренировок"
    """
    user_id = message.from_user.id
    history_file_path = settings.path_workout_db.replace('user_id', str(user_id))
    
    try:
        df = pd.read_csv(history_file_path)
        history_message = "Ваша история тренировок:\n"
        
        for index, row in df.iterrows():
            history_message += f"Название: {row['name']}\nДата: {row['data']}\nОписание:\n"
            for i in row['description'].split('%'):
                history_message += f"{i}\n"
            history_message += "\n\n"
        
        await message.answer(history_message)
    except FileNotFoundError:
        await message.answer('История тренировок не найдена.')
    except Exception as e:
        await message.answer(f'Произошла ошибка: {str(e)}')