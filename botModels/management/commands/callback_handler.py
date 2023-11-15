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

    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name = ?', (name_product,)).fetchone()

    count = count_products.get(call.message.chat.id)
    
    match move:
        case '+':
            count += 1
            count_products[call.message.chat.id] = count
        case '-': 
            if count >= 2:
                count -= 1  
                count_products[call.message.chat.id] = count

    
    image_path = f'media/{product[4]}'
    name = product[2]
    description = product[5]
    price = '' if product[3] == 0 else f'Цена: {product[3]} сум'

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)

    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = 'Открыть описание', callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = 'Скрыть описание', callback_data = f'description'))
        desctiption_text = f'''<b>Описание:</b>
{description}

{price}'''

    

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = '📥 Добавить в корзину', callback_data = f'add_product:{name_product}'))
    products: dict = ct.cart.get(call.message.chat.id, None)
    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = '📥 Убрать из корзины', callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = '📄 Сертификат', callback_data = f'certificate:{name_product}'))


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

    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name = ?', (name_product,)).fetchone()
    
    count_products[call.message.chat.id] = 1
    count = 1

    image_path = f'media/{product[4]}'
    name = product[2]
    description = product[5]
    price = '' if product[3] == 0 else f'Цена: {product[3]} сум'

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)

    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = 'Открыть описание', callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = 'Скрыть описание', callback_data = f'description'))
        desctiption_text = f'''<b>Описание:</b>
{description}

{price}'''

    

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = '📥 Добавить в корзину', callback_data = f'add_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = '📤 Убрать из корзины', callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = '📄 Сертификат', callback_data = f'certificate:{name_product}'))

    

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

    await call.answer(
        text = f'✅ Продукт удален в количестве {count_products.get(call.message.chat.id)} шт.',
    )
    ct.del_product(
        chat_id = call.message.chat.id,
        product_name = name_product,
        quantity = count_products.get(call.message.chat.id),
    )

    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name = ?', (name_product,)).fetchone()

    
    count_products[call.message.chat.id] = 1
    count = 1

    image_path = f'media/{product[4]}'
    name = product[2]
    description = product[5]
    price = '' if product[3] == 0 else f'Цена: {product[3]} сум'

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    
    if expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = 'Открыть описание', callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = 'Скрыть описание', callback_data = f'description'))
        desctiption_text = f'''<b>Описание:</b>
{description}

{price}'''

    

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = '📥 Добавить в корзину', callback_data = f'add_product:{name_product}'))
    products: dict = ct.cart.get(call.message.chat.id, None)

    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = '📥 Убрать из корзины', callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = '📄 Сертификат', callback_data = f'certificate:{name_product}'))

    

    await call.message.edit_caption(
        caption = f'''{name}

{desctiption_text}
''',    
        parse_mode = 'html',
        reply_markup = markup,
    )


async def clear_cart(call: types.CallbackQuery): 
    
    ct.clear_cart(call.message.chat.id)
    await bot.edit_message_text(
        chat_id = call.message.chat.id,

        message_id = call.message.message_id,
        text = '<b>🛒 Корзина пуста</b>', 
        parse_mode = 'html',
    )
    

async def send_order(call: types.CallbackQuery):
 
    await bot.edit_message_text(
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        text = '<b>✅ Заказ отправлен</b>', 
        parse_mode = 'html',
    )


    with sqlite3.connect('db.sqlite3') as c:
        userInfo = c.execute(f'SELECT * FROM botModels_profile WHERE chat_id = ?', (call.message.chat.id,)).fetchone()
    
    phoneNumber = userInfo[2]
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

    with sqlite3.connect('db.sqlite3') as c:
        product = c.execute(f'SELECT * FROM botModels_products WHERE name = ?', (name_product,)).fetchone()

    name = product[2]
    description = product[5]
    price = '' if product[3] == 0 else f'Цена: {product[3]} сум'

    count = count_products.get(call.message.chat.id)

    markup = InlineKeyboardMarkup(row_width = 3, resize_keyboard=True)
    
    if expand_message[call.message.chat.id] == 0:
        markup.add(InlineKeyboardButton(text = 'Открыть описание', callback_data = f'description'))
        desctiption_text = ''

    elif expand_message[call.message.chat.id] == 1:
        markup.add(InlineKeyboardButton(text = 'Скрыть описание', callback_data = f'description'))
        desctiption_text = f'''<b>Описание:</b>
{description}

{price}'''

    expand_message[call.message.chat.id] = 1 if expand_message[call.message.chat.id] == 0 else 0

    markup.add(
        InlineKeyboardButton(text = '-', callback_data = f'-:{name_product}'), 
        InlineKeyboardButton(text = f'{count}', callback_data = 'c'),
        InlineKeyboardButton(text = '+', callback_data = f'+:{name_product}')
    )
    markup.add(InlineKeyboardButton(text = '📥 Добавить в корзину', callback_data = f'add_product:{name_product}'))

    products: dict = ct.cart.get(call.message.chat.id, None)

    if products != None and name_product in products.keys():
        markup.add(InlineKeyboardButton(text = '📥 Убрать из корзины', callback_data = f'del_product:{name_product}'))
    markup.add(InlineKeyboardButton(text = '📄 Сертификат', callback_data = f'certificate:{name_product}'))


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

      