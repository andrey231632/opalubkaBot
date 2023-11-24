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
from .database_handler import *

BOT_TOKEN = settings.BOT_TOKEN
bot = Bot(BOT_TOKEN, parse_mode="HTML", disable_web_page_preview=True)
ct = Cart()


async def changeLanguageMessageButton(message: types.Message):
    lang_code = get_lang_code(message.chat.id)
    new_lang_code = 'uz' if lang_code == 'ru' else 'ru'
    change_lang_code(
        message.chat.id,
        new_lang_code,
    )
    await backMainMenu(message)
    # markup = InlineKeyboardMarkup(row_width = 2)
    # markup.add(z
    #     InlineKeyboardButton(text = '🇷🇺', callback_data = 'ru'),
    #     InlineKeyboardButton(text = '🇺🇿', callback_data = 'uz'),
    # ) 
    # text = {'ru': 'Выберите язык', 'uz': 'Tilni tanlang'}
    # await message.answer(
    #     text = text[lang_code],
    #     reply_markup = markup,
    # )

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
    lang_code = get_lang_code(message.chat.id)
    button_names = {
            'ru': ('Каталог', 'Новости', 'Связаться с менеджером', 'Часто задаваемые вопросы', 'Поменять язык'),
            'uz': ('Katalog', 'Yangiliklar', 'Menejerga murojaat qiling', "Ko'p so'raladigan savollar", "Tilni o'zgartirish"),
        }
    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in button_names[lang_code]])
    
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

    await bot.send_message(
        chat_id = message.chat.id,
        text = text[lang_code],
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
    
    lang_code = get_lang_code(message.chat.id)

    with sqlite3.connect('db.sqlite3') as c:
        global catalog
        catalog = set([i[0] for i in c.execute('SELECT category FROM botModels_products').fetchall()])

    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in catalog])
    cart_button_text = {
        'ru': 'Корзина',
        'uz': 'Savat',
    }
    back_button_text = {
        'ru': 'Назад',
        'uz': 'Orqaga',
    }
    markup.add(KeyboardButton(text = f'🛒 {cart_button_text[lang_code]}'))
    markup.add(KeyboardButton(text = f'◀️ {back_button_text[lang_code]}'))

    category_text = {'ru': 'Выберите категорию товаров', 'uz': 'Mahsulot turini tanlang'}
    
    await bot.send_message( 
        chat_id = message.chat.id,
        text = f'👆🏻 {category_text[lang_code]}',    
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
    lang_code = get_lang_code(message.chat.id)
    with sqlite3.connect('db.sqlite3') as c:
        products = [i[0] for i in c.execute(f'SELECT name_{lang_code} FROM botModels_products WHERE category = ?', (category,)).fetchall()]
        all_products = [i[0] for i in c.execute(f'SELECT name_{lang_code} FROM botModels_products').fetchall()]
    
    cart_button_text = {
        'ru': 'Корзина',
        'uz': 'Savat',
    }
    main_menu_button_text = {
        'ru': 'В главное меню',
        'uz': 'Asosiy menyuga',
    }
    back_button_text = {
        'ru': 'Назад',
        'uz': 'Orqaga',
    }

    markup = ReplyKeyboardMarkup(row_width = 2, resize_keyboard=True)
    markup.add(*[KeyboardButton(text = button_name) for button_name in products])
    markup.add(KeyboardButton(text = f'🛒 {cart_button_text[lang_code]}'))
    markup.add(KeyboardButton(text = f'⏪ {main_menu_button_text[lang_code]}'), KeyboardButton(text = f'◀️ {back_button_text[lang_code]}'))
    text = {
        'ru': 'Выберите товар',
        'uz': 'Mahsulotni tanlang',
    }
    await bot.send_message(
        chat_id = message.chat.id,
        text = f'👆🏻 {text[lang_code]}',    
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

    lang_code = get_lang_code(message.chat.id)
    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name_{lang_code} = ?', (message.text,)).fetchone()
        
    count_products[message.chat.id] = 1
    count = 1

    add_to_cart_text      = {'ru': "📥 Добавить в корзину", "uz": "📥 Savatga qo'shish"}
    del_from_cart_text    = {'ru': "📤 Убрать из корзины", "uz": "📤 Savatdan olib tashlang"}
    sertificate_text      = {'ru': "📄 Сертификат", "uz": "📄 Sertifikat"}
    open_description_text = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{message.text}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{message.text}')
    )
    markup.add(InlineKeyboardButton(text = add_to_cart_text[lang_code], callback_data = f'add_product:{message.text}'))
    
    products: dict = ct.cart.get(message.chat.id, None)

    if products != None and message.text in products.keys():
        markup.add(InlineKeyboardButton(text = del_from_cart_text[lang_code], callback_data = f'del_product:{message.text}'))
    markup.add(InlineKeyboardButton(text = sertificate_text[lang_code], callback_data = f'certificate:{message.text}'))


    image_path = f'media/{product[3]}'
    name = product[-2] if lang_code == 'ru' else product[-1]
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

    lang_code = get_lang_code(message.chat.id)
    call_manager_text = {
        'ru': 'Связаться с менеджером',
        'uz': 'Menejerga murojaat qiling',
    } 
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text = call_manager_text[lang_code], url = 'https://t.me/Andrey_Zolin'))
    
    contact_text = {
        'ru': ('Телефон', 'Почта', 'Адрес', 'Время работы'),
        'uz': ('Telefon', 'Pochta', 'Manzil', 'Ish vaqti'),
    }

    addres_text = {
        'ru': '`г. Ташкент, Мирзо - Улугбекский р-н, ул. М.Юсуфа, д.45`',
        'uz': '`Toshkent, Mirzo - Ulugbek rayoni, M.Yusuf kochasi, 45 uy`',
    }

    time_work_text = {
        'ru': 'Пн. – Пт.: с 9:00 до 18:00',
        'uz': 'Dushanba-Juma.: soat 9:00 dan 18:00gacham',
    }

    await bot.send_message(
        chat_id = message.chat.id,
        text = f'''☎️ {contact_text[lang_code][0]}
├  `+998 90 945-15-75`
├  `+998 90 002-24-34`
└  `+998 90 930-38-38`

📧 {contact_text[lang_code][1]}
└   `havoza@mail.ru`

📫 {contact_text[lang_code][2]}
└   {addres_text[lang_code]}

⌚ {contact_text[lang_code][3]}
└   {time_work_text[lang_code]}
''',
    parse_mode = 'MARKDOWN', 
    reply_markup = markup,
    )


async def cart_menu(message: types.Message): 
    
    lang_code = get_lang_code(message.chat.id)
    userCart: dict = ct.cart.get(message.chat.id, None)
    empty_cart_text = {
        'ru': 'Корзина пуста',
        'uz': 'Arava bo‘sh',
    }
    if userCart is None or userCart == {}: 
        await bot.send_message(
            chat_id = message.chat.id,
            text = f'<b>🛒 {empty_cart_text[lang_code]}</b>', 
            parse_mode = 'html',
        )
        return 0
    
    clear_cart_text = {
        'ru': 'Очистить корзину',
        'uz': "Chiqindini bo'shatish",
    }
    send_order_text = {
        'ru': 'Отправить заказ менеджеру',
        'uz': 'Buyurtmani menejerga yuboring',
    }

    markup = InlineKeyboardMarkup(row_width = 1)
    markup.add(
        InlineKeyboardButton(text = f'🔄️ {clear_cart_text[lang_code]}', callback_data = 'clear_cart'),
        InlineKeyboardButton(text = f'💠 {send_order_text[lang_code]}', callback_data = 'send_order'),
    )
    
    cart_text = {
        'ru': 'Корзина',
        'uz': 'Savat',
    }

    kolovo_text = {'ru': 'Кол-во', 'uz': 'Soni'}

    orderText = ''.join([f'{i[0]}\n{kolovo_text[lang_code]}: {i[1]}\n\n' for i in userCart.items()])
    orderText = f'<b>🛒 {cart_text[lang_code]}:</b>\n\n' + orderText
    await bot.send_message(
            chat_id = message.chat.id,
            text = orderText, 
            parse_mode = 'html',
            reply_markup = markup,
        )


async def messageHandler(message: types.Message):

    match message.text:
        case 'О компании':
            await aboutCompanyMessage(message)

        case 'Контакты':
            await contactMessage(message)

        case text if text in ('Каталог', 'Katalog'):
            await catalogMessage(message)
        
        case text if text in ('Связаться с менеджером', 'Menejerga murojaat qiling'): 
            await contactMessage(message)
    
        case text if text in ('Поменять язык', "Tilni o'zgartirish"):
            await changeLanguageMessageButton(message)

        case text if text in ('◀️ Назад', '◀️ Orqaga'):
            try:
                await backMessage(message)
            except Exception as e:
                print(e)
                pass
        case text if text in ('⏪ В главное меню', '⏪ Asosiy menyuga'):
            await backMainMenu(message)

        case text if text in ('🛒 Корзина', '🛒 Savat'):
            await cart_menu(message)

        case text if text in catalog:
            await subCatalogMessage(message, message.text)

        case text if text in all_products:
            await productMessage(message)
        
        # 'ru': ('Каталог', 'Новости', 'Связаться с менеджером', 'Часто задаваемые вопросы', 'Настройки'),
        # 'uz': ('Katalog', 'Yangiliklar', 'Menejerga murojaat qiling', "Ko'p so'raladigan savollar", 'Sozlamalar'),

        # cart_button_text = {
        # 'ru': 'Корзина',
        # 'uz': 'Savat',
        # }
        # main_menu_button_text = {
        #     'ru': 'В главное меню',
        #     'uz': 'Asosiy menyuga',
        # }
        # back_button_text = {
        #     'ru': 'Назад',
        #     'uz': 'Orqaga',
        # }