import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_gigachat.chat_models import GigaChat

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import tiktoken

# Импорт файлов проекта
import src.keyboards.keyboards as kbs
import src.settings.settings as settings

# Подключение переменной окружения
load_dotenv(os.path.join(os.path.dirname(__file__), '../../config/.env'))
GIGACHAT_API_KEY = os.getenv('GIGACHAT_API_KEY')


llm = GigaChat(
    credentials=GIGACHAT_API_KEY,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
    streaming=False,
)

SYSTEM_MESSAGE = "Ты - высококвалифицированный фитнес-тренер и консультант по спорту. Твоя задача - давать советы и ответы исключительно в области спорта, фитнеса, тренировок, питания и здорового образа жизни. Не отвечай на вопросы, не относящиеся к этой теме. Если вопрос не соответствует данной теме, просто ответь 'Я не могу ответить на этот вопрос, так как он не относится к спорту и фитнесу.' или 'Мне не хватает компетенции в этом вопросе'."

# Создание роутера
router_virtual_assistant = Router()


# Состояния для формы
class Form(StatesGroup):
    ask_question = State()

MAX_TOKENS = 10000  # Максимальное количество токенов в истории
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(message):
    """
    Подсчитывает количество токенов в сообщении.
    """
    if isinstance(message, HumanMessage):
        return len(encoding.encode(message.content))
    elif isinstance(message, (AIMessage, SystemMessage)):
        return len(encoding.encode(message.content))
    else:
        return 0

def save_message_to_history(user_id, role, content):
    """
    Сохраняет сообщение в CSV-файл истории пользователя.
    """
    filename = settings.path_history_AI_db.replace('user_id', str(user_id))
    timestamp = datetime.now().isoformat()
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, role, content])
        
def load_user_history(user_id):
    """
    Загружает историю сообщений пользователя из CSV и удаляет старые, если нужно.
    """
    filename = settings.path_history_AI_db.replace('user_id', str(user_id))
    
    messages_to_keep = []
    total_tokens = 0
    rows_to_keep = [] # Сохраняем только строки которые будем оставлять в файле
    
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader, None)  # Пропускаем заголовок
            rows = list(reader)
            
            for row in reversed(rows):  # Перебираем историю с конца
                if len(row) == 3:
                  _, role, content = row
                  if role == 'human':
                      message = HumanMessage(content=content)
                  elif role == 'ai':
                      message = AIMessage(content=content)
                  else:
                        continue
                  
                  message_tokens = count_tokens(message)
                  
                  if total_tokens + message_tokens > MAX_TOKENS:
                    break
                  
                  messages_to_keep.insert(0, message) # Собираем историю для запроса к модели
                  rows_to_keep.insert(0, row) # Собираем строки для файла
                  total_tokens += message_tokens
                  
        # Перезаписываем файл с урезанной историей
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if header:
              writer.writerow(header)
            writer.writerows(rows_to_keep)
            
    return messages_to_keep

@router_virtual_assistant.message(F.text == 'Задать вопрос виртуальному тренеру')
async def process_ask_question_command(message: Message, state: FSMContext):
    """
    Функция вывода меню задать вопрос виртуальному тренеру
    """
    await message.answer('Пожалуйста, введите ваш вопрос:', reply_markup=kbs.cancel_virtual_assistant_menu)
    await state.set_state(Form.ask_question)


@router_virtual_assistant.message(Form.ask_question)
async def handle_ask_question(message: Message, state: FSMContext):
    """
    Обработка вопроса пользователя
    """
    user_id = message.from_user.id
    user_question = message.text
    if user_question == 'Выйти с диалога c виртуальным тренером':
        await state.clear()
        await message.answer('Вы вышли из диалога с виртуальным тренером', reply_markup=kbs.main_menu)
        return
    
    # Загружаем историю пользователя и удаляем старые сообщения
    messages = load_user_history(user_id)
    
    # Добавляем вопрос пользователя в историю
    messages.append(HumanMessage(content=user_question))
    save_message_to_history(user_id, 'human', user_question)

    messages_with_system = [SystemMessage(content=SYSTEM_MESSAGE)] + messages

    # Получаем ответ от модели

    res = llm.invoke(messages_with_system)
 
    # Добавляем ответ в историю
    messages.append(res)
    save_message_to_history(user_id, 'ai', res.content)

    await message.answer(res.content, reply_markup=kbs.cancel_virtual_assistant_menu)