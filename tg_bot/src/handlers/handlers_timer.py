"""
Файл обработки таймера
"""
import asyncio

from aiogram.filters import Command
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

# Импорт файлов проекта
import src.keyboards.keyboards as kbs


# Создание роутера
router_timer = Router()
        

# Состояния для формы
class FSMTimer(StatesGroup):
    timer_input = State()
    timer_running = State()
    timer_stopped = State()


@router_timer.message(Command('timer'))
@router_timer.message(F.text == 'Включить таймер')
async def process_timer_command(message: Message):
    """
    Функция вывода меню таймера
    """
    await message.answer(text='Выберите время:', reply_markup=kbs.timer_menu)


@router_timer.message(F.text == 'Ввести время')
async def process_timer_input_command(message: Message, state: FSMContext):
    """
    Функция обработки нажатия кнопки ввода времени
    """
    await state.set_state(FSMTimer.timer_input)
    await message.answer(text='Введите время в формате MM:SS')


@router_timer.message(FSMTimer.timer_input)
async def process_timer_input(message: Message, state: FSMContext):
    """
    Функция обработки введенного пользователем времени
    """
    if message.text == 'Вернуться в главное меню':
        await state.clear()
        await message.answer('Вы вернулись в главное меню', reply_markup=kbs.main_menu)
        return
    
    time_str = message.text.strip()
    try:
        if ':' not in time_str or len(time_str.split(':')) != 2:
            raise ValueError
            
        minutes, seconds = map(int, time_str.split(':'))
        if not (0 <= minutes < 60 and 0 <= seconds < 60):
            raise ValueError

        await state.clear()
        await start_timer(message, time_str, state)
        
    except ValueError:
        await message.answer(text='Используй формат MM:SS (от 00:00 до 59:59)')


@router_timer.message(F.text.in_(['1:00', '1:30', '2:00', '2:30', '3:00', '3:30', '4:00', '4:30']))
async def process_timer_preset(message: Message, state: FSMContext):
    """
    Функция обработки предустановленного времени
    """
    await start_timer(message, message.text, state)


@router_timer.callback_query(F.data == "cancel_timer")
async def cancel_timer_callback(callback_query: CallbackQuery, state: FSMContext):
    """
    Обработчик нажатия кнопки отмены таймера
    """
    await state.set_state(FSMTimer.timer_stopped)
    await callback_query.message.delete()
    await callback_query.message.answer(text='Таймер отменен!', reply_markup=kbs.add_exercise_keyboard)
    await callback_query.answer()


async def start_timer(message: Message, time_str: str, state: FSMContext):
    """
    Функция запуска и работы таймера
    """
    minutes, seconds = map(int, time_str.split(':'))
    total_seconds = minutes * 60 + seconds
    
    timer_message = await message.answer(
        text=f'Таймер запущен на {time_str}!',
        reply_markup=kbs.cancel_keyboard
    )
    
    await state.set_state(FSMTimer.timer_running)
    
    remaining_seconds = total_seconds
    display_interval = 10 # Интервал обновления сообщения в секундах
    last_display = remaining_seconds

    while remaining_seconds > 0:
        current_state = await state.get_state()
        if current_state == FSMTimer.timer_stopped:
            return
            
        await asyncio.sleep(1)
        remaining_seconds -= 1
        
        if last_display - remaining_seconds >= display_interval:
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60
            
            try:
                await timer_message.edit_text(
                    f'Осталось времени: {minutes:02d}:{seconds:02d}',
                    reply_markup=kbs.cancel_keyboard
                )
                last_display = remaining_seconds
            except Exception:
                pass

    await timer_message.delete()    
    await message.answer(text='Таймер завершен!', reply_markup=kbs.add_exercise_keyboard)