import pymysql


class Base:
	def __init__(self):
		self.con = pymysql.connect(
			host='localhost',
			user='root',
			password='Ltkmnf-02',
			database='electro_bot',
			cursorclass=pymysql.cursors.DictCursor
		)

	def init_tables(self):
		tables = (
			'users(id int primary key, mode varchar(50), phone varchar(50), email varchar(100))',
			'products(id int primary key auto_increment, title varchar(70), description varchar(300), photo_path varchar(255), price int)',
			'baskets(u_id int not null, product_id int not null, FOREIGN KEY (u_id) REFERENCES users(id), FOREIGN KEY (product_id) REFERENCES products(id))',
			'temp_table(name varchar(100), val text)',
			'orders(id int primary key auto_increment, description text)'
		)
		with self.con.cursor() as cur:
			for table in tables:
				cur.execute(f"create table if not exists {table};")

		self.con.commit()

	def delete_product_from_trash(self, uid, pid):
		with self.con.cursor() as cur:
			cur.execute(f'delete from baskets where u_id={uid} and product_id={pid};')
		self.con.commit()

	def add_new_user(self, u_id):
		with self.con.cursor() as cur:
			cur.execute(f'insert into users(id, mode) values({u_id}, "start");')
		self.con.commit()

	def get_user_info(self, u_id):
		with self.con.cursor() as cur:
			cur.execute(f'select * from users where id = {u_id};')
			ans = cur.fetchall()
			if ans:
				return ans[0]
			return None

	def update_user_mode(self, u_id, mode):
		with self.con.cursor() as cur:
			cur.execute(f'update users set mode="{mode}" where id={u_id};')
		self.con.commit()

	def update_user_phone(self, u_id, phone):
		with self.con.cursor() as cur:
			cur.execute(f'update users set phone="{phone}" where id={u_id};')
		self.con.commit()

	def update_user_email(self, u_id, email):
		with self.con.cursor() as cur:
			cur.execute(f'update users set email="{email}" where id={u_id};')
		self.con.commit()

	def add_product(self):
		with self.con.cursor() as cur:
			cur.execute('select * from temp_table;')
			data = cur.fetchall()

			params = ('new_product_title', 'new_product_photo_path', 'new_product_price', 'new_product_desc')
			datas = [(x['name'], x['val']) for x in data]
			for param in params:
				if not param in [x[0] for x in datas]:
					return False

			title = [x[1] for x in datas if x[0] == 'new_product_title'][0]
			photo_path = [x[1] for x in datas if x[0] == 'new_product_photo_path'][0]
			price = [x[1] for x in datas if x[0] == 'new_product_price'][0]
			desc = [x[1] for x in datas if x[0] == 'new_product_desc'][0]

			cur.execute(
				f'insert into products(title, description, photo_path, price) values("{title}", "{desc}", "{photo_path}", {price});'
			)
			self.clear_temp()
			return True

	def delete_product_by_id(self, pid):
		with self.con.cursor() as cur:
			cur.execute(f'delete FROM products where id={pid};')
		self.con.commit()

	def get_product_by_id(self, pid):
		with self.con.cursor() as cur:
			cur.execute(f'SELECT * FROM products where id={pid};')
			ans = cur.fetchall()
			if ans:
				return ans[0]
			else:
				return None

	def get_new_product(self):
		with self.con.cursor() as cur:
			cur.execute(f'SELECT id FROM products ORDER BY ID DESC LIMIT 1;')
			return cur.fetchall()

	def add_ticket(self, uid, pid):
		with self.con.cursor() as cur:
			cur.execute(f'insert into baskets(u_id, product_id) values({uid}, {pid});')
		self.con.commit()

	def add_temp(self, name, value):
		with self.con.cursor() as cur:
			cur.execute(f'INSERT INTO temp_table (name, val) VALUES("{name}", "{value}") ON DUPLICATE KEY UPDATE name="{name}", val="{value}";')
		self.con.commit()

	def clear_temp(self):
		with self.con.cursor() as cur:
			cur.execute(f'delete from temp_table;')
		self.con.commit()

	def get_all_products_names(self):
		with self.con.cursor() as cur:
			cur.execute(f'select id, title from products;')
			return cur.fetchall()

	def get_user_basket(self, uid):
		with self.con.cursor() as cur:
			cur.execute(f'select product_id from baskets where u_id={uid};')
			return [x['product_id'] for x in cur.fetchall()]

	def add_order(self, desc):
		with self.con.cursor() as cur:
			cur.execute(f'insert into orders(description) values("{desc}");')
		self.con.commit()

	def get_order(self):
		with self.con.cursor() as cur:
			cur.execute('select * from orders limit 1;')
			return cur.fetchall()

	def drop_order(self, oid):
		with self.con.cursor() as cur:
			cur.execute(f'delete from orders where id={oid};')

	def clear_user_trash(self, uid):
		with self.con.cursor() as cur:
			cur.execute(f'delete from baskets where u_id={uid};')
		self.con.commit()


if __name__ == '__main__':
	base = Base()
	base.init_tables()
