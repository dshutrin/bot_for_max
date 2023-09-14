import telebot
from base import Base
from keys import *
from config import *


bot = telebot.TeleBot(token=token)
db = Base()
db.init_tables()
print('Started!')


@bot.message_handler(commands=['start'])
def start_function(message: telebot.types.Message):
	uid = message.chat.id

	if not db.get_user_info(uid):
		db.add_new_user(uid)

	if uid != admin_id:
		user_info = db.get_user_info(uid)
		if not user_info['phone'] and not user_info['email']:
			bot.send_message(uid, 'Приветствую тебя!\nДля начала, заполни форму!')
			bot.send_message(uid, 'Введи свой номер телефона, чтобы менеджер мог уточнить детали заказа')
			db.update_user_mode(uid, 'init_phone')
		else:
			if uid != admin_id:
				bot.send_message(uid, 'Выбери действие', reply_markup=get_menu_key())
			db.update_user_mode(uid, 'start')
	else:
		db.update_user_mode(uid, 'start')
		bot.send_message(uid, 'Выбери действие', reply_markup=get_admin_menu_key())


@bot.message_handler(content_types=['photo'])
def photo_handler(message: telebot.types.Message):
	if message.chat.id == admin_id:

		if db.get_user_info(admin_id)['mode'] == 'input_new_product_photo':
			file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
			downloaded_file = bot.download_file(file_info.file_path)
			src = int(str(message.photo[1].__hash__())[:50])

			with open('photos/' + str(src), 'wb') as new_file:
				new_file.write(downloaded_file)
			db.add_temp('new_product_photo_path', src)

			if db.add_product():
				pid = db.get_new_product()[0]['id']
				bot.send_message(admin_id, f"Товар успешно добавлен!\nКод продукта: {pid}", reply_markup=get_admin_menu_key())
			else:
				bot.send_message(admin_id, "Не удалось добавить товар!\nПопробуйте заново!", reply_markup=get_admin_menu_key())
			db.update_user_mode(admin_id, 'start')


@bot.message_handler(content_types=['text'])
def main_function(message: telebot.types.Message):
	uid = message.chat.id
	text = message.text

	user_info = db.get_user_info(uid)
	if user_info:
		if uid == admin_id:
			if user_info['mode'] == 'start':

				if text == 'Посмотреть товары':
					names = db.get_all_products_names()

					text = 'Вот наш ассортимент:\n\n'
					for product in names:
						text = f'{text}{product["title"]}\nКод продукта: <{product["id"]}>\n\n'

					bot.send_message(admin_id, text)
					bot.send_message(admin_id, 'Выберите товар для удаления\nНужно ввести код товара', reply_markup=get_back_key())
					db.update_user_mode(uid, 'choice_delete_product')

				elif text == 'Добавить товары':
					bot.send_message(uid, 'Хорошо, давайте добавим товары!\nВведите название товара', reply_markup=get_back_key())
					db.clear_temp()
					db.update_user_mode(uid, 'input_new_product_name')

				elif text == 'Заявки':
					orders = db.get_order()
					if orders:
						orders = orders[0]
						bot.send_message(uid, orders['description'], reply_markup=get_admin_order_key())
						db.update_user_mode(uid, f'in_order_{orders["id"]}')
					else:
						bot.send_message(uid, 'На данный момент нет заказов от пользователей!')

			elif user_info['mode'].startswith('in_order_'):
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text == 'Пометить выполненным':
						oid = int(user_info['mode'].replace('in_order_', ''))
						db.drop_order(oid)
						bot.send_message(uid, 'Заказ помечен как выполненный и был удалён!', reply_markup=get_admin_menu_key())
						db.update_user_mode(uid, 'start')

					elif text == 'Отказать':
						oid = int(user_info['mode'].replace('in_order_', ''))
						order = db.get_order()[0]

						bot.send_message(int(order['description'].split()[-1]), f'Отказано в заказе!\n\n<<<{order["description"]}>>>\n\nВозможно, сейчас его нет на складе, попробуйте позже.')
						bot.send_message(uid, 'Уведомление отправлено пользователю!', reply_markup=get_admin_menu_key())
						db.drop_order(oid)
						db.update_user_mode(uid, 'start')

			elif user_info['mode'] == 'choice_delete_product':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text.isdigit():
						db.delete_product_by_id(int(text))
						bot.send_message(uid, 'Товар удалён!', reply_markup=get_admin_menu_key())
						db.update_user_mode(uid, 'start')
					else:
						bot.send_message(uid, 'Код товара должен быть числом!')

			elif user_info['mode'] == 'input_new_product_name':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
					db.clear_temp()
				else:
					db.add_temp('new_product_title', text)
					bot.send_message(uid, 'Отлично, теперь введите описание продукта')
					db.update_user_mode(uid, 'input_new_product_desc')

			elif user_info['mode'] == 'input_new_product_desc':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
					db.clear_temp()
				else:
					db.add_temp('new_product_desc', text)
					bot.send_message(uid, 'Отлично, теперь введите стоимость продукта')
					db.update_user_mode(uid, 'input_new_product_price')

			elif user_info['mode'] == 'input_new_product_price':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
					db.clear_temp()
				else:
					if text.isdigit():
						db.add_temp('new_product_price', int(text))
						bot.send_message(uid, 'Отлично, теперь пришлите мне фото продукта')
						db.update_user_mode(uid, 'input_new_product_photo')
					else:
						bot.send_message(uid, 'Неверное значение!')

			elif user_info['mode'] == 'input_new_product_photo':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_admin_menu_key())
					db.update_user_mode(uid, 'start')
					db.clear_temp()
				else:
					""" Эта часть описана в обработчике в верхней части кода """
					pass

		else:
			if user_info['mode'] == 'init_phone':
				db.update_user_phone(uid, text)
				bot.send_message(uid, 'Отлично, теперь введи свой email')
				db.update_user_mode(uid, 'init_email')

			elif user_info['mode'] == 'init_email':
				db.update_user_email(uid, text)
				bot.send_message(uid, 'Супер!\nТеперь ты можешь собрать корзину и заказать товары!', reply_markup=get_menu_key())
				db.update_user_mode(uid, 'start')

			elif user_info['mode'] == 'start':
				if text == 'Посмотреть товары':
					names = db.get_all_products_names()

					text = 'Вот наш ассортимент:\n\n'
					for product in names:
						text = f'{text}{product["title"]}\nКод продукта: <{product["id"]}>\n\n'

					bot.send_message(uid, text)
					bot.send_message(uid, 'Выберите товар для детального просмотра\nНужно ввести код товара', reply_markup=get_back_key())
					db.update_user_mode(uid, 'choice_product')

				elif text == 'Корзина':
					ans = "Вот ваша корзина:\n"
					basket = db.get_user_basket(uid)

					for pid in basket:
						p_inf = db.get_product_by_id(pid)
						ans = f'{ans}\n{p_inf["title"]}\n(Код товара: {p_inf["id"]})\n'

					if len(basket) == 0:
						ans = 'Ваша корзина пуста!'
						bot.send_message(uid, ans, reply_markup=get_menu_key())
					else:
						bot.send_message(uid, ans, reply_markup=get_basket_key())
						db.update_user_mode(uid, 'in_trash')

			elif user_info['mode'] == 'in_trash':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text == 'Отправить заявку':
						ans = "Новая заявка:\n"
						basket = db.get_user_basket(uid)

						for pid in basket:
							p_inf = db.get_product_by_id(pid)
							ans = f'{ans}\n{p_inf["title"]}\n(Код товара: {p_inf["id"]})\n'

						ans = f'{ans}\n\nДанные покупателя:\nНомер телефона: {user_info["phone"]}\nEmail: {user_info["email"]}\nTelegram ID: {user_info["id"]}'
						db.add_order(ans)
						db.clear_user_trash(uid)
						bot.send_message(uid, 'Ваш заказ оформлен!\nОжидайте связи с менеджером!', reply_markup=get_menu_key())
						db.update_user_mode(uid, 'start')

					elif text == 'Удалить товар из корзины':
						bot.send_message(uid, 'Введите код товара, который хотите удалить из корзины', reply_markup=get_back_key())
						db.update_user_mode(uid, 'delete_product_from_trash')

			elif user_info['mode'] == 'delete_product_from_trash':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text.isdigit():

						db.delete_product_from_trash(uid, int(text))
						bot.send_message(uid, f'Товар с кодом {text} удалён из вашей корзины!', reply_markup=get_menu_key())
						db.update_user_mode(uid, 'start')

					else:
						bot.send_message(uid, 'Код продукта должен быть числом!', reply_markup=get_back_key())

			elif user_info['mode'] == 'choice_product':
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text.isdigit():
						prod_info = db.get_product_by_id(int(text))
						desc = f'Название: {prod_info["title"]}\nОписание: {prod_info["description"]}\nЦена: {prod_info["price"]}'

						with open(f'photos/{prod_info["photo_path"]}', 'rb') as photo:
							bot.send_photo(uid, photo, desc, reply_markup=get_product_menu())
						db.update_user_mode(uid, f'selected_product_{prod_info["id"]}')
					else:
						bot.send_message(uid, 'Код продукта должен быть числом!', reply_markup=get_back_key())

			elif user_info['mode'].startswith('selected_product_'):
				if text == 'Назад':
					bot.send_message(uid, 'Выберите действие', reply_markup=get_menu_key())
					db.update_user_mode(uid, 'start')
				else:
					if text == 'Добавить товар в корзину':
						prod_id = int(user_info['mode'].replace('selected_product_', ''))
						db.add_ticket(uid, prod_id)
						p_info = db.get_product_by_id(prod_id)
						bot.send_message(uid, f'Товар "' + p_info["title"] + '" успешно добавлен в вашу корзину!', reply_markup=get_menu_key())
						db.update_user_mode(uid, 'start')


if __name__ == '__main__':
	bot.infinity_polling()
