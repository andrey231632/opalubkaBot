from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext


BOT_TOKEN = settings.BOT_TOKEN
bot = Bot(BOT_TOKEN, parse_mode="HTML", disable_web_page_preview=True)


class Singleton(object):

    def __new__(cls, *args, **kwargs):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwargs)
        return it

    def init(self, *args, **kwargs):
        pass


class Cart(Singleton):

    def init(self):
        self.cart = dict()


    def add_product(self, chat_id, product_name, quantity):
        items: dict = self.cart.get(chat_id, None)
        if items != None:
            if product_name in items:
                items[product_name] += quantity
            else:
                items[product_name] = quantity
            self.cart[chat_id] = items
        else:
            self.cart[chat_id] = {product_name: quantity}
        return 0


    def del_product(self, chat_id, product_name, quantity): 
        items: dict = self.cart.get(chat_id, None)
        if items != None:
            if product_name in items:
                items[product_name] -= quantity
                if items[product_name] <= 0:
                    del items[product_name]
            self.cart[chat_id] = items
        return 0


    def clear_cart(self, chat_id): 
        self.cart[chat_id] = {}
        return 0
    