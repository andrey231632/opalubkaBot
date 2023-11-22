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


async def get_reg_lang_code(call: types.CallbackQuery):
    try:
        await bot.delete_message(
            call.message.chat.id,
            call.message.message_id
        )
    except:
        pass
    
    lang_code = call.data.split('_')[-1]
    reg_user_lang_code[call.message.chat.id] = lang_code
    user_state[call.message.chat.id] = 'get_phone_number'
    print(user_state)
    text_button = {
        'ru': 'Отправить номер телефона ☎️',
        'uz': 'Telefon raqamini yuboring ☎️',
    }
    text_message = {
        'ru': 'Укажите номер телефона',
        'uz': 'Iltimos, telefon raqamingizni kiriting',
    }
    markup = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)
    markup.add(KeyboardButton(text = text_button[lang_code], request_contact = True))
    await bot.send_message(
        chat_id = call.message.chat.id,
        text = text_message[lang_code],
        reply_markup = markup,
    )

async def change_language(call: types.CallbackQuery):
    change_lang_code(call.message.chat.id, call.data)
    lang_code = get_lang_code(call.message.chat.id)
    markup = InlineKeyboardMarkup(row_width = 2)
    markup.add(
        InlineKeyboardButton(text = '🇷🇺', callback_data = 'ru'),
        InlineKeyboardButton(text = '🇺🇿', callback_data = 'uz'),
    ) 
    text = {'ru': 'Выберите язые', 'uz': 'Tilni tanlang'}
    await call.message.edit_text(
        text = text[lang_code],
        reply_markup = markup,
    )

async def updateCounterProduct(call: types.CallbackQuery, move: str, name_product: str):
    # try:
    #     await bot.delete_message(
    #         call.message.chat.id,
    #         call.message.message_id
    #     )
    # except:
    #     pass
    global all_products
    global count_products

    lang_code = get_lang_code(call.message.chat.id)
    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name_{lang_code} = ?', (name_product,)).fetchone()
        
    count = count_products.get(call.message.chat.id)
    
    match move:
        case '+':
            count += 1
            count_products[call.message.chat.id] = count
        case '-': 
            if count >= 2:
                count -= 1  
                count_products[call.message.chat.id] = count

    
    # image_path = f'media/{product[3]}'
    name = product[-2] if lang_code == 'ru' else product[-1]
    description =  product[-4] if lang_code == 'ru' else product[-3]
    price_text = {'ru': 'Цена', 'uz': 'Narxi'}
    price = '' if product[2] == 0 else f'{price_text[lang_code]}: {product[2]} сум'

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    open_description_text = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    description_text = {'ru': 'Описание', 'uz': 'Tavsif'}
    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))
        desctiption_text = f'''<b>{description_text[lang_code]}:</b>
{description}

{price}'''

    

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    add_to_cart_text   = {'ru': "📥 Добавить в корзину", "uz": "📥 Savatga qo'shish"}
    del_from_cart_text = {'ru': "📤 Убрать из корзины", "uz": "📤 Savatdan olib tashlang"}
    sertificate_text   = {'ru': "📄 Сертификат", "uz": "📄 Sertifikat"}
    
    markup.add(InlineKeyboardButton(text = add_to_cart_text[lang_code], callback_data = f'add_product:{name_product}'))
    products: dict = ct.cart.get(call.message.chat.id, None)
    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = del_from_cart_text[lang_code], callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = sertificate_text[lang_code], callback_data = f'certificate:{name_product}'))


    await call.message.edit_caption(
        caption = f'''{name}

{desctiption_text} 
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def addProductToCart(call: types.CallbackQuery, name_product):

    # try:
    #     await bot.delete_message(
    #         call.message.chat.id,
    #         call.message.message_id
    #     )
    # except:
    #     pass
    
    user_cart = ct.cart.get(call.message.chat.id, None)
    global count_products
    global all_products

    await call.answer(
        text = f'✅ Продукт добавлен в количестве {count_products.get(call.message.chat.id)} шт.',
    )
   
    ct.add_product(
        chat_id = call.message.chat.id,
        product_name = name_product,
        quantity = count_products.get(call.message.chat.id),
    )

    lang_code = get_lang_code(call.message.chat.id)
    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name_{lang_code} = ?', (name_product,)).fetchone()
        
    count_products[call.message.chat.id] = 1
    count = 1

    # image_path = f'media/{product[3]}'
    
    name         = product[-2] if lang_code == 'ru' else product[-1]
    description  =  product[-4] if lang_code == 'ru' else product[-3]
    price_text   = {'ru': 'Цена', 'uz': 'Narxi'}
    price        = '' if product[2] == 0 else f'{price_text[lang_code]}: {product[2]} сум'

    open_description_text   = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    close_description_text  = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    description_text        = {'ru': 'Описание', 'uz': 'Tavsif'}
    
    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)

    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = close_description_text[lang_code], callback_data = f'description'))
        desctiption_text = f'''<b>{description_text[lang_code]}:</b>
{description}

{price}'''

    add_to_cart_text   = {'ru': "📥 Добавить в корзину", "uz": "📥 Savatga qo'shish"}
    del_from_cart_text = {'ru': "📤 Убрать из корзины", "uz": "📤 Savatdan olib tashlang"}
    sertificate_text   = {'ru': "📄 Сертификат", "uz": "📄 Sertifikat"}

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = add_to_cart_text[lang_code], callback_data = f'add_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = del_from_cart_text[lang_code], callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = sertificate_text[lang_code], callback_data = f'certificate:{name_product}'))

    

    await call.message.edit_caption(
        caption = f'''{name}

{desctiption_text}
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def delProductOutCart(call: types.CallbackQuery, name_product):

    # try:
    #     await bot.delete_message(
    #         call.message.chat.id,
    #         call.message.message_id
    #     )
    # except:
    #     pass

    global count_products
    global all_products

    lang_code = get_lang_code(call.message.chat.id)
    del_product_text = {"ru": "Продукт удален в количестве", "uz": "Mahsulot miqdorida olib tashlangan"}

    await call.answer(
        text = f'✅ {del_product_text[lang_code]} {count_products.get(call.message.chat.id)}',
    )
    ct.del_product(
        chat_id = call.message.chat.id,
        product_name = name_product,
        quantity = count_products.get(call.message.chat.id),
    )

    
    with sqlite3.connect('db.sqlite3') as c:    
        product = c.execute(f'SELECT * FROM botModels_products WHERE name_{lang_code} = ?', (name_product,)).fetchone()
       
    count_products[call.message.chat.id] = 1
    count = 1

    # image_path = f'media/{product[3]}'
    name = product[-2] if lang_code == 'ru' else product[-1]
    description =  product[-4] if lang_code == 'ru' else product[-3]
    price_text = {'ru': 'Цена', 'uz': 'Narxi'}
    price = '' if product[2] == 0 else f'{price_text[lang_code]}: {product[2]} сум'

    open_description_text = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    close_description_text = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    description_text = {'ru': 'Описание', 'uz': 'Tavsif'}

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    
    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = close_description_text[lang_code], callback_data = f'description'))
        desctiption_text = f'''<b>{description_text[lang_code]}:</b>
{description}

{price}'''

    

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )

    add_to_cart_text   = {'ru': "📥 Добавить в корзину", "uz": "📥 Savatga qo'shish"}
    del_from_cart_text = {'ru': "📤 Убрать из корзины", "uz": "📤 Savatdan olib tashlang"}
    sertificate_text   = {'ru': "📄 Сертификат", "uz": "📄 Sertifikat"}

    markup.add(InlineKeyboardButton(text = add_to_cart_text[lang_code], callback_data = f'add_product:{name_product}'))
    products: dict = ct.cart.get(call.message.chat.id, None)

    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = del_from_cart_text[lang_code], callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = sertificate_text[lang_code], callback_data = f'certificate:{name_product}'))

    

    await call.message.edit_caption(
        caption = f'''{name}

{desctiption_text}
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def clear_cart(call: types.CallbackQuery): 
    
    lang_code = get_lang_code(call.message.chat.id)

    ct.clear_cart(call.message.chat.id)

    text = {"ru": "Корзина пуста", "uz": "Arava bo‘sh"}

    await bot.edit_message_text(
        chat_id = call.message.chat.id,

        message_id = call.message.message_id,
        text = f'<b>🛒 {text[lang_code]}</b>', 
        parse_mode = 'html',
    )
    

async def send_order(call: types.CallbackQuery):
    
    lang_code = get_lang_code(call.message.chat.id)
    text = {"ru": "Заказ отправлен", "uz": "Buyurtma yuborildi"}

    await bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = f'<b>✅ {text[lang_code]}</b>', 
        parse_mode = 'html',
    )


    with sqlite3.connect('db.sqlite3') as c:
        userInfo = c.execute(f'SELECT * FROM botModels_profile WHERE chat_id = ?', (call.message.chat.id,)).fetchone()
    
    phoneNumber = userInfo[3] if userInfo[3][0] == '+' else '+'+userInfo[3]
    userName = userInfo[1]
    userCart: dict = ct.cart.get(call.message.chat.id, None)
    orderText1 = f'<b>Заказ от пользователя: {userName}</b>\n<b>Номер телефона: {phoneNumber}</b>\n\n<b>Заказ:</b>\n\n'
    orderText2 = ''.join([f'{i[0]}\nКол-во: {i[1]}\n\n' for i in userCart.items()])
    orderText3 = orderText1 + orderText2
  

    await bot.send_message(
        chat_id = settings.MANADGER_ID,
        text = orderText3,
        parse_mode = 'html',
    )
    ct.clear_cart(call.message.chat.id)



async def productCallbackData(call: types.CallbackQuery):

    global all_products
    global count_products

    name_product = last_product[call.message.chat.id]
    lang_code = get_lang_code(call.message.chat.id)

    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name_{lang_code} = ?', (name_product,)).fetchone()
        

    name = product[-2] if lang_code == 'ru' else product[-1]
    description =  product[-4] if lang_code == 'ru' else product[-3]
    price_text = {'ru': 'Цена', 'uz': 'Narxi'}
    price = '' if product[2] == 0 else f'{price_text[lang_code]}: {product[2]} сум'

    open_description_text  = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    close_description_text = {'ru': 'Открыть описание', 'uz': 'Tavsifni ochish'}
    description_text       = {'ru': 'Описание', 'uz': 'Tavsif'}

    count = count_products.get(call.message.chat.id)

    

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    
    if expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = open_description_text[lang_code], callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = close_description_text[lang_code], callback_data = f'description'))
        desctiption_text = f'''<b>{description_text[lang_code]}:</b>
{description}

{price}'''

    expand_message[call.message.chat.id] = 1 if expand_message[call.message.chat.id] == 0 else 0

    add_to_cart_text   = {'ru': "📥 Добавить в корзину", "uz": "📥 Savatga qo'shish"}
    del_from_cart_text = {'ru': "📤 Убрать из корзины", "uz": "📤 Savatdan olib tashlang"}
    sertificate_text   = {'ru': "📄 Сертификат", "uz": "📄 Sertifikat"}

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = add_to_cart_text[lang_code], callback_data = f'add_product:{name_product}'))

    products: dict = ct.cart.get(call.message.chat.id, None)

    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = del_from_cart_text[lang_code], callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = sertificate_text[lang_code], callback_data = f'certificate:{name_product}'))


    await call.message.edit_caption(
        caption = f'''{name}

{desctiption_text} 
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def callbackHandler(call: types.CallbackQuery):
    
    data = call.data

    match data:
        case d if d.split(':')[0] == '+': await updateCounterProduct(call, '+', d.split(':')[1])

        case d if d.split(':')[0] == '-': await updateCounterProduct(call, '-', d.split(':')[1])

        case d if d.split(':')[0] == 'add_product': await addProductToCart(call, d.split(':')[1])

        case d if d.split(':')[0] == 'del_product': await delProductOutCart(call, d.split(':')[1])

        case d if d.split(':')[0] == 'certificate': ...

        case 'description': await productCallbackData(call)

        case 'clear_cart': await clear_cart(call)

        case 'send_order': await send_order(call)

        case 'ru': await change_language(call)

        case 'uz': await change_language(call)
      
        case 'reg_lan_code_ru': await get_reg_lang_code(call)

        case 'reg_lan_code_uz': await get_reg_lang_code(call)