from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def get_menu_key():
	menu_key = ReplyKeyboardMarkup(resize_keyboard=True)
	menu_key.add(KeyboardButton('Посмотреть товары'), KeyboardButton('Корзина'))
	return menu_key


def get_admin_menu_key():
	menu_key = ReplyKeyboardMarkup(resize_keyboard=True)
	menu_key.add(KeyboardButton('Посмотреть товары'), KeyboardButton('Добавить товары'))
	menu_key.add(KeyboardButton('Заявки'))
	return menu_key


def get_product_menu():
	menu_key = ReplyKeyboardMarkup(resize_keyboard=True)
	menu_key.add(KeyboardButton('Добавить товар в корзину'))
	menu_key.add(KeyboardButton('Назад'))
	return menu_key


def get_basket_key():
	menu_key = ReplyKeyboardMarkup(resize_keyboard=True)
	menu_key.add(KeyboardButton('Отправить заявку'), KeyboardButton('Удалить товар из корзины'))
	menu_key.add(KeyboardButton('Назад'))
	return menu_key


def get_back_key():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	key.add(KeyboardButton('Назад'))
	return key


def get_admin_order_key():
	key = ReplyKeyboardMarkup(resize_keyboard=True)
	key.add(KeyboardButton('Пометить выполненным'), KeyboardButton('Отказать'))
	key.add(KeyboardButton('Назад'))
	return key
