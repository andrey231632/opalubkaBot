import sqlite3
from django.conf import settings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from .temp_data import *
from .cart import Cart


BOT_TOKEN = settings.BOT_TOKEN
bot = Bot(BOT_TOKEN, parse_mode="HTML", disable_web_page_preview=True)
ct = Cart()

async def backMessage(message: types.Message):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass

    match user_state[message.chat.id]:
        case 'catalog': await backMainMenu(message)
        case 'sub_catalog': await catalogMessage(message)
        case 'product': await subCatalogMessage(message, last_category[message.chat.id])


async def backMainMenu(message: types.Message):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass
    button_names = ['Каталог', 'Новости', 'Связаться с менеджером', 'Часто задаваемые вопросы']
    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in button_names])
    
    await bot.send_message(
        chat_id = message.chat.id,
        text = '''Добро пожаловать в мир New Design Technology! 

С 15-летним опытом, мы - лидеры в сфере производства 
и поставки строительных лесов, опалубки и комплектующих. 
Наши клиенты довольны нашими услугами и разнообразием предложений.
''',
        reply_markup = markup,
    )

async def catalogMessage(message: types.Message):
    user_state[message.chat.id] = 'catalog'
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass
    
    with sqlite3.connect('db.sqlite3') as c:
        global catalog
        catalog = set([i[0] for i in c.execute('SELECT category FROM botModels_products').fetchall()])

    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in catalog])
    markup.add(KeyboardButton(text = '🛒 Корзина'))
    markup.add(KeyboardButton(text = '◀️ Назад'))

    await bot.send_message(
        chat_id = message.chat.id,
        text = '''👆🏻 Выберите категорию товаров''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def subCatalogMessage(message: types.Message, category):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass
    
    
    user_state[message.chat.id] = 'sub_catalog'
    last_category[message.chat.id] = category 

    global all_products
    with sqlite3.connect('db.sqlite3') as c:
        products = [i[0] for i in c.execute('SELECT name FROM botModels_products WHERE category = ?', (category,)).fetchall()]
        all_products = [i[0] for i in c.execute('SELECT name FROM botModels_products').fetchall()]


    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in products])
    markup.add(KeyboardButton(text = '🛒 Корзина'))
    markup.add(KeyboardButton(text = '⏪ В главное меню'), KeyboardButton(text = '◀️ Назад'))

    await bot.send_message(
        chat_id = message.chat.id,
        text = '''👆🏻 Выберите товар''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def productMessage(message: types.Message):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass

    last_product[message.chat.id] = message.text
    # user_state[message.chat.id] = 'product'
    expand_message[message.chat.id] = 1

    global all_products
    global count_products
    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name = ?', (message.text,)).fetchone()

    count_products[message.chat.id] = 1
    count = 1

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    markup.add(InlineKeyboardButton(text = 'Открыть описание', callback_data = f'description'))

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{message.text}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{message.text}')
    )
    markup.add(InlineKeyboardButton(text = '📥 Добавить в корзину', callback_data = f'add_product:{message.text}'))
    
    products: dict = ct.cart.get(message.chat.id, None)

    if products != None and message.text in products.keys():
        markup.add(InlineKeyboardButton(text = '📥 Убрать из корзины', callback_data = f'del_product:{message.text}'))
    markup.add(InlineKeyboardButton(text = '📄 Сертификат', callback_data = f'certificate:{message.text}'))


    image_path = f'media/{product[4]}'
    name = product[2]
    # description = product[5]
    # price = '' if product[3] == 0 else f'Цена: {product[3]} сум'

    await bot.send_photo(
        chat_id = message.chat.id,
        photo = open(image_path, 'rb'),
        caption = f'''{name}
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def aboutCompanyMessage(message: types.Message):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass

    await bot.send_message(
        chat_id = message.chat.id,
        text = '''<b>О компании</b>

Компания «New Design Technology» является одним из ведущих специалистов в сфере производства и поставке строительных лесов, опалубки и комплектующих.

Приобретенный нами опыт работы в данной сфере, неоднократное выполнение крупных заказов и проектов являются свидетельством того, что наши клиенты остаются довольны сотрудничеством с нами.

Наша организация занимается производством и поставкой строительных материалов и оборудования уже более 15 лет, за это время были отработаны все технологии. Так же, мы предоставляем широкий спектр услуг в сфере аренды и продажи, являемся поставщиками строительного гидравлических подъемников в Узбекистане.
''',    
    parse_mode = 'html',
    )

async def contactMessage(message: types.Message):
    try:
        await bot.delete_message(
            message.chat.id,
            message.message_id
        )
    except:
        pass

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text = 'Связаться с менеджером', url = 'https://t.me/Andrey_Zolin'))
    
    await bot.send_message(
        chat_id = message.chat.id,
        text = '''☎️ Телефон
├  `+998 90 945-15-75`
├  `+998 90 002-24-34`
└  `+998 90 930-38-38`

📧 Почта
└   `havoza@mail.ru`

📫 Адрес
└   `г. Ташкент, Мирзо - Улугбекский р-н, ул. М.Юсуфа, д.45`

⌚ Время работы
└   Пн. – Пт.: с 9:00 до 18:00
''',
    parse_mode = 'MARKDOWN', 
    reply_markup = markup,
    )


async def cart_menu(message: types.Message): 
    
    userCart: dict = ct.cart.get(message.chat.id, None)
    if userCart is None or userCart == {}: 
        await bot.send_message(
            chat_id = message.chat.id,
            text = '<b>🛒 Корзина пуста</b>', 
            parse_mode = 'html',
        )
        return 0
    
    markup = InlineKeyboardMarkup(row_width = 2)
    markup.add(
        InlineKeyboardButton(text = '🔄️ Очистить корзину', callback_data = 'clear_cart'),
        InlineKeyboardButton(text = '💠Отправить заказ менеджеру', callback_data = 'send_order'),
    )
    
    orderText = ''.join([f'{i[0]}\nКол-во: {i[1]}\n\n' for i in userCart.items()])
    orderText = '<b>🛒 Корзина:</b>\n\n' + orderText
    await bot.send_message(
            chat_id = message.chat.id,
            text = orderText, 
            parse_mode = 'html',
            reply_markup = markup,
        )
    
# async def catalogMessage(message: types.Message):
#     bot.send_message(
#         chat_id = message.chat.id,
#         text = ''
#     )


async def messageHandler(message: types.Message):

    match message.text:
        case 'О компании':
            await aboutCompanyMessage(message)

        case 'Контакты':
            await contactMessage(message)

        case 'Каталог':
            await catalogMessage(message)
        
        case 'Связаться с менеджером': 
            await contactMessage(message)
    
        case '◀️ Назад':
            await backMessage(message)

        case '⏪ В главное меню':
            await backMainMenu(message)

        case '🛒 Корзина':
            await cart_menu(message)

        case text if text in catalog:
            await subCatalogMessage(message, message.text)

        case text if text in all_products:
            await productMessage(message)
        

        