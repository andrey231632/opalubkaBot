from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from .temp_data import * 
from .message_handler import messageHandler
from .callback_handler import callbackHandler
from .database_handler import *
import sqlite3
import logging

BOT_TOKEN = settings.BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(BOT_TOKEN,  parse_mode=types.ParseMode.HTML, disable_web_page_preview=True)
dp = Dispatcher(bot, storage=MemoryStorage())
    

@dp.message_handler(commands = 'start')
async def start(message: types.Message):
    
    with sqlite3.connect('db.sqlite3') as c:
        idList = [i[0] for i in c.execute('SELECT chat_id FROM botModels_profile').fetchall()]

    if message.chat.id not in idList:
        user_state[message.chat.id] = 'get_lang_code'
        print(user_state)
        # user_state[message.chat.id] = 'get_phone_number'
        # print(user_state)
        # markup = ReplyKeyboardMarkup(resize_keyboard=True)
        # markup.add(KeyboardButton(text = 'Отправить номер телефона ☎️', request_contact = True))
        # await bot.send_message(
        #     chat_id = message.chat.id,
        #     text = 'Укажите номер телефона',
        #     reply_markup = markup,
        # )

        markup = InlineKeyboardMarkup(row_width = 2)
        markup.add(
            InlineKeyboardButton(text = '🇷🇺', callback_data = 'reg_lan_code_ru'),
            InlineKeyboardButton(text = '🇺🇿', callback_data = 'reg_lan_code_uz'),
        )
        await bot.send_message(
            chat_id = message.chat.id,
            text = 'Выберите язык\nTilni tanlang',
            reply_markup = markup,
        )     
    
    else:
        lang_code = get_lang_code(message.chat.id)
        button_names = {
            'ru': ('Каталог', 'Новости', 'Связаться с менеджером', 'Часто задаваемые вопросы', 'Поменять язык'),
            'uz': ('Katalog', 'Yangiliklar', 'Menejerga murojaat qiling', "Ko'p so'raladigan savollar", "Tilni o'zgartirish"),
        }
        text = {
            'ru': '''Добро пожаловать в мир New Design Technology! 

С 15-летним опытом, мы - лидеры в сфере производства 
и поставки строительных лесов, опалубки и комплектующих. 
Наши клиенты довольны нашими услугами и разнообразием предложений.
''',
            'uz': '''Yangi dizayn texnologiyasi dunyosiga xush kelibsiz!

15 yillik tajribamiz bilan biz ishlab chiqarish sohasida yetakchimiz
va iskala, qolip va butlovchi qismlarni yetkazib berish.
Mijozlarimiz xizmatlarimiz va turli xil takliflarimizdan mamnun.
''',
}
        markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
        markup.add(*[KeyboardButton(text = button_name) for button_name in button_names[lang_code]])
        
        await bot.send_message(
            chat_id = message.chat.id,
            text = text[lang_code],
            reply_markup = markup,
        )

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact(message: types.Message):

    if user_state.get(message.chat.id) == 'get_phone_number':
     
        phone_number = message.contact.phone_number
        name = message.chat.first_name
        uniq_name = 'None' if message.chat.username == None or message.chat.username == 'None' else message.chat.username
        print(uniq_name)
        lang_code = reg_user_lang_code[message.chat.id]
        with sqlite3.connect('db.sqlite3') as c:
            c.execute('INSERT INTO botModels_profile (name, uniq_name, phone_number, chat_id, language_code) VALUES (?, ?, ?, ?, ?)', (name, uniq_name, phone_number, message.chat.id, lang_code)).fetchall()
            c.commit()        
        del reg_user_lang_code[message.chat.id]

        button_names = {
            'ru': ('Каталог', 'Новости', 'Связаться с менеджером', 'Часто задаваемые вопросы', 'Поменять язык'),
            'uz': ('Katalog', 'Yangiliklar', 'Menejerga murojaat qiling', "Ko'p so'raladigan savollar", "Tilni o'zgartirish"),
        }
        markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
        markup.add(*[KeyboardButton(text = button_name) for button_name in button_names[lang_code]])
        
        text = {
            'ru': '''Добро пожаловать в мир New Design Technology! 
            
С 15-летним опытом, мы - лидеры в сфере производства и поставки строительных лесов, 
опалубки и комплектующих. Наши клиенты довольны нашими услугами и разнообразием предложений.
''',
            'uz': '''Yangi dizayn texnologiyasi dunyosiga xush kelibsiz!
            
15 yillik tajribamiz bilan biz iskala ishlab chiqarish va yetkazib berishda yetakchimiz,
qolip va komponentlar. Mijozlarimiz xizmatlarimiz va turli xil takliflarimizdan mamnun.
''',
}

        await bot.send_message(
            chat_id = message.chat.id,
            text = text[lang_code],
            reply_markup = markup,
        )
        user_state.pop(message.chat.id)


@dp.message_handler()
async def message_handler(message: types.Message):
    await messageHandler(message)


@dp.callback_query_handler()
async def callback_handler(message: types.Message):
    await callbackHandler(message)


class Command(BaseCommand):
    help = "Телеграм бот"
    def handle(self, *args, **options):
        executor.start_polling(dp)
        print(bot.me)