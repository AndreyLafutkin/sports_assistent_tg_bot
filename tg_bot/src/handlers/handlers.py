import pandas as pd

from aiogram.filters import CommandStart, Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

# Импорт файлов проекта
import src.settings.settings as settings
import src.keyboards.keyboards as kbs


# Создание роутера
router = Router()


# Состояния для формы
class Form(StatesGroup):
    name = State()


# Обработка команды /start
@router.message(CommandStart(), State(None))
async def process_start_command(message: Message, state: FSMContext):
    """
    Функция регистрации пользователя
    """

    user_id = message.from_user.id
    df = pd.read_csv(settings.path_users_db)

    if user_id in df['user_id'].values:
        await message.answer('Вы уже зарегистрированы!')
        await state.clear()
        return

    await message.answer('Добро пожаловать в наш бот!\n'
                         'Наш бот поможет вам контролировать ваши тренировки\n'
                         'Давай зарегистрируемся!')
    await message.answer("Как мне к вам обращаться?")
    await state.set_state(Form.name)


@router.message(Form.name)
async def process_name_command(message: Message, state: FSMContext):
    """
    Функция обработки ввода имени пользователя и сохранения в БД через pandas
    """
    user_name = message.text
    user_id = message.from_user.id
    DB_training_plans = settings.path_training_plans_db.replace('user_id', str(user_id))
    DB_workout = settings.path_workout_db.replace('user_id', str(user_id))
    DB_history_AI = settings.path_history_AI_db.replace('user_id', str(user_id))

    df = pd.read_csv(settings.path_users_db)
    df.loc[len(df)] = [user_id, user_name, DB_training_plans, DB_workout, DB_history_AI]
    df.to_csv(settings.path_users_db, index=False)

    # Создание файла для планов тренировок
    df_training_plans = pd.DataFrame(columns=settings.parameters_training_plans_db)
    df_training_plans.to_csv(DB_training_plans, index=False)

    # Создание файла для тренировок
    df_workout = pd.DataFrame(columns=settings.parameters_workout_db)
    df_workout.to_csv(DB_workout, index=False)

    # Создание файла для истории запросов ИИ
    df_history_AI = pd.DataFrame(columns=settings.parameters_history_AI_db)
    df_history_AI.to_csv(DB_history_AI, index=False)



    await message.answer('Вы успешно зарегистрированы!', reply_markup=kbs.main_menu)
    await state.clear()



@router.message(Command('menu'), State(None))
@router.message(F.text == 'Вернуться в главное меню')
async def process_main_menu_command(message: Message):
    """
    Функция обработки команды /menu
    """
    await message.answer(text='Выберите действие:', reply_markup=kbs.main_menu)


@router.message(Command('help'), State(None))
async def process_help_command(message: Message):
    """
    Функция вывода списка команд
    """
    string_commands = ''
    for command in settings.list_commands:
        string_commands += f'{command} - {settings.list_commands[command]}\n'
    await message.answer(f'Список комманд:\n{string_commands}')