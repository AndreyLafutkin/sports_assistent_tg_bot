import datetime
import asyncio
import pandas as pd

from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message


from src.settings import settings
from src.keyboards import keyboards as kbs

# Создание роутера
router_workout = Router()


# Создание состояний для тренировки
class WorkoutState(StatesGroup):
    name = State()
    approach = State()
    weight = State()
    reps = State()


@router_workout.message(F.text == 'Начать тренировку')
@router_workout.message(Command('start_workout'), State(None))
async def process_start_command(message: Message, state: FSMContext):
    """
    Функция начала тренировки
    """
    await message.answer('Введите название тренировки')
    await state.set_state(WorkoutState.name)


@router_workout.message(WorkoutState.name)
async def process_name_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода названия тренировки
    """
    workout_name = message.text
    await state.update_data(workout_name=workout_name)
    df = pd.read_csv(settings.path_workout_db.replace('user_id', str(message.from_user.id)))
    df.loc[len(df)] = [workout_name, datetime.date.today().isoformat(), 'P']
    df.to_csv(settings.path_workout_db.replace('user_id', str(message.from_user.id)), index=False)
    await message.answer('Выберите план тренировок', reply_markup=kbs.create_training_plans_keyboard(message.from_user.id))
    await state.clear()


@router_workout.callback_query(F.data.startswith('training_plan_'))
async def process_training_plan_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора тренировочного плана и вывода его описания
    """
    user_id = callback_query.from_user.id
    plan_index = int(callback_query.data.split('_')[2])
    df = pd.read_csv(settings.path_training_plans_db.replace('user_id', str(user_id)))

    plan_name = df.iloc[plan_index]['name']
    plan_description = df.iloc[plan_index]['description']
    await callback_query.message.delete()
    await callback_query.message.answer(f'Вы выбрали план:\n{plan_name}\nОписание:\n{plan_description}')

    await callback_query.message.answer('Выберите категорию упражнений', reply_markup=kbs.create_exercises_categories_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data == 'back_to_main_menu')
async def process_back_to_main_menu_callback(callback_query: Message):
    """
    Функция обработки выбора возвращения в главное меню
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Вы вернулись в главное меню', reply_markup=kbs.main_menu)
    await callback_query.answer()


@router_workout.callback_query(F.data == 'continue_without_plan')
async def process_continue_without_plan_callback(callback_query: Message):
    """
    Функция обработки выбора продолжения без плана тренировки
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите категорию упражнений', reply_markup=kbs.create_exercises_categories_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data == 'back_to_training_plans')
async def process_back_to_training_plans_callback(callback_query: Message):
    """
    Функция обработки выбора возвращения к выбору плана тренировки
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите план тренировок', 
                                        reply_markup=kbs.create_training_plans_keyboard(callback_query.from_user.id))
    await callback_query.answer()


@router_workout.callback_query(F.data.startswith('exercises_category_'))
async def process_exercises_category_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора категории упражнений
    """
    await callback_query.message.delete()
    if callback_query.data == 'exercises_category_Bodybuilding':
        await callback_query.message.answer('Выберите группу мышц', 
                                            reply_markup=kbs.create_muscle_groups_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data == 'back_to_choose_exercises_category')
async def process_back_to_choose_exercises_category_callback(callback_query: Message):
    """
    Функция обработки выбора возвращения к выбору категории упражнений
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите категорию упражнений', reply_markup=kbs.create_exercises_categories_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data.startswith('muscle_group_'))
async def process_muscle_group_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора группы мышц
    """
    await callback_query.message.delete()
    muscle_group = callback_query.data.split('_')[2]
    muscle_group = muscle_group.replace(' ', '')
    await callback_query.message.answer('Выберите упражнение', reply_markup=kbs.create_exercises_keyboard(muscle_group))
    await callback_query.answer()


@router_workout.callback_query(F.data == 'back_to_choose_muscle_group')
async def process_back_to_choose_muscle_group_callback(callback_query: Message):
    """
    Функция обработки выбора возвращения к выбору группы мышц
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите группу мышц', reply_markup=kbs.create_muscle_groups_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data.startswith('exercise_'))
async def process_exercise_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора упражнения
    """
    await callback_query.message.delete()
    exercise = callback_query.data.split('_')[1]
    await callback_query.message.answer('Введите количество подходов')
    exercise_name = exercise
    await state.update_data(exercise_name=exercise_name)
    await state.set_state(WorkoutState.approach)
    await callback_query.answer()

@router_workout.message(WorkoutState.approach)
async def process_add_approach_callback(message: Message, state: FSMContext):
    """
    Функция обработки выбора добавления подхода
    """
    approach = message.text
    if not approach.isdigit():
        await message.answer('Ошибка: введите число. Пожалуйста, повторите ввод количества подходов.')
        return
    await state.update_data(approach=approach)
    await message.answer('Введите вес')
    await state.set_state(WorkoutState.weight)



@router_workout.message(WorkoutState.weight)
async def process_weight_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода веса
    """
    weight = message.text
    if not weight.isdigit():
        await message.answer('Ошибка: введите число. Пожалуйста, повторите ввод веса.')
        return
    await state.update_data(weight=weight)
    await message.answer('Введите количество повторений')
    await state.set_state(WorkoutState.reps)


@router_workout.message(WorkoutState.reps)
async def process_reps_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода количества повторений
    """
    reps = message.text
    if not reps.isdigit():
        await message.answer('Ошибка: введите число. Пожалуйста, повторите ввод количества повторений.')
        return
    await state.update_data(reps=reps)

    data = await state.get_data()
    exercise_name = data.get('exercise_name')
    weight = data.get('weight')
    reps = data.get('reps')
    approach = data.get('approach')
    if exercise_name is None or weight is None or reps is None:
        await message.answer('Ошибка: недостающие данные. Пожалуйста, повторите ввод.')
        return
    
    df = pd.read_csv(settings.path_workout_db.replace('user_id', str(message.from_user.id)))
    
    new_description = f"{exercise_name};{approach};{weight};{reps}"
    current_description = df.loc[len(df)-1, 'description']

    if current_description == 'P':
        updated_description = new_description
    else:
        updated_description = f"{current_description}%{new_description}".strip()
    df.loc[len(df)-1, 'description'] = updated_description

    df.to_csv(settings.path_workout_db.replace('user_id', str(message.from_user.id)), index=False)

    await state.clear()

    await message.answer('Упражнение добавлено', reply_markup=kbs.add_timer_keyboard)


@router_workout.callback_query(F.data == 'add_timer')
async def process_add_timer_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора добавления таймера
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите время', reply_markup=kbs.timer_menu)
    await callback_query.answer()


@router_workout.callback_query(F.data == 'skip_timer')
async def process_skip_timer_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора пропуска таймера
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Таймер пропущен', reply_markup=kbs.add_exercise_keyboard)
    await callback_query.answer()


@router_workout.callback_query(F.data == 'add_exercise')
async def process_add_exercise_callback(callback_query: Message, state: FSMContext):
    """
    Функция обработки выбора добавления упражнения
    """
    await callback_query.message.delete()
    await callback_query.message.answer('Выберите категорию упражнений', reply_markup=kbs.create_exercises_categories_keyboard())
    await callback_query.answer()


@router_workout.callback_query(F.data == 'finish_workout')
async def process_finish_workout_callback(callback_query: Message):
    """
    Функция обработки выбора завершения тренировки
    """
    await callback_query.message.delete()
    df = pd.read_csv(settings.path_workout_db.replace('user_id', str(callback_query.from_user.id)))
    current_description = df.loc[len(df)-1, 'description']
    print_description = ''
    for i in current_description.split('%'):
        print_description += f"{i}\n"

    await callback_query.message.answer(f'Ваша тренировка:\n{print_description}', reply_markup=kbs.main_menu)
    await callback_query.answer()