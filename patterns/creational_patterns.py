import sqlite3
from patterns.architectural_system_pattern_unit_of_work import DomainObject, UnitOfWork
from patterns.behavioral_patterns import Subject, EmailNotifier, SmsNotifier, ConsoleWriter
import copy
import quopri


# абстрактный пользователь


class User(DomainObject):
    def __init__(self, name):
        self.name = name


# гость
class Guest(User):
    def __init__(self, name, goods):
        self.admin = False
        self.goods = goods
        super().__init__(name)


# админ
class Admin(User):
    def __init__(self, name, goods):
        self.admin = True
        self.goods = goods
        super().__init__(name)


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'guest': Guest,
        'admin': Admin
    }

    @classmethod
    def types_from_admin(cls, name, goods, admin):
        if admin:
            return cls.types['admin'](name, goods)
        else:
            return cls.types['guest'](name, goods)

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_, name, goods):
        return cls.types[type_](name, goods)


# порождающий паттерн Прототип - Курс
class GoodsPrototype:
    # прототип курсов обучения
    def clone(self):
        return copy.deepcopy(self)


class Goods(GoodsPrototype, Subject):
    auto_id = 1

    def __init__(self, name, description, image, discount, cost, visible, category):
        self.id = Goods.auto_id
        Goods.auto_id += 1
        self.name = name
        self.description = description
        self.image = image
        self.discount = discount
        self.cost = cost
        self.visible = visible
        self.category = category
        self.category.goods.append(self)
        self.notify_users = []
        super().__init__()

    def __call__(self, *args, **kwargs):
        if not self.category.visible:
            self.visible = False

    def clone(self):
        Category.auto_id += 1
        return super().clone()

    def add_user_to_notify(self, user):
        self.notify_users.append(user)

    def del_user_to_notify(self, user):
        del_num = None
        for i in range(len(self.notify_users)):
            if self.notify_users[i].name == user.name:
                del_num = i
        try:
            self.notify_users.pop(del_num)
        except Exception as e:
            print('Не удалось отключить напомнинания')


class Category(GoodsPrototype):
    # реестр
    auto_id = 1

    def __init__(self, name, description, visible, category):
        self.id = Category.auto_id
        Category.auto_id += 1
        self.name = name
        self.description = description
        self.visible = visible
        self.category = category
        self.goods = []

    def goods_count(self):
        result = len(self.goods)
        if self.category:
            result += self.category.goods_count()
        return result

    def clone(self):
        Category.auto_id += 1
        return super().clone()


class Engine:
    def __init__(self):
        UnitOfWork.new_current()
        UnitOfWork.get_current().set_mapper_registry(MapperRegistry)
        self.admins = []
        self.guests = []
        self.goods = []
        self.categories = []
        self.create_test_data()
        self.load_data_from_db()

    def load_data_from_db(self):
        all_users = MapperRegistry().get_current_mapper('guest').all(self)
        for item in all_users:
            if item.admin:
                self.admins.append(item)
            else:
                self.guests.append(item)
        print('Data base loaded')

    @staticmethod
    def create_user(type_, name, goods):
        new_user = UserFactory.create(type_, name, goods)
        if len(goods):
            for good in goods:
                good.add_user_to_notify(user=new_user)
        new_user.mark_new()
        UnitOfWork.get_current().commit()
        return new_user

    def delete_user(self, delete_user):
        if not delete_user.admin:
            del_num = None
            for i in range(len(self.guests)):
                if self.guests[i].name == delete_user.name:
                    del_num = i
            self.guests.pop(del_num)
            for good in delete_user.goods:
                good.del_user_to_notify(delete_user)
            MapperRegistry().get_current_mapper('guest').delete(delete_user)

    @staticmethod
    def create_category(name, description='', visible=True, category=None):
        return Category(name, description, visible, category)

    def find_category_by_id(self, id):
        for item in self.categories:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет категории с id = {id}')

    def find_category_by_name(self, name):
        for item in self.categories:
            if item.name == name:
                return True
        return False

    def find_user_by_name(self, name):
        for item in self.admins:
            if item.name == name:
                return item
        for item in self.guests:
            if item.name == name:
                return item
        return False

    def update_category(self, update_category):
        for i in range(len(self.categories)):
            if self.categories[i].id == update_category['id']:
                self.categories[i].name = update_category['name']
                self.categories[i].description = update_category['desc']
                self.categories[i].category = update_category['parent_category']

    def update_user(self, update_user, old_profile):
        goods_list = []
        if len(update_user['good_sub']):
            for item in update_user['good_sub']:
                goods_list.append(self.find_good_by_id(int(item)))
        user_num = 0
        if not old_profile.admin:
            for i in range(len(self.guests)):
                if old_profile.name == self.guests[i].name:
                    user_num = i
            self.guests.pop(user_num)
        else:
            for i in range(len(self.admins)):
                if old_profile.name == self.admins[i].name:
                    user_num = i
            self.admins.pop(user_num)
        if update_user['admin']:
            new = self.create_user(type_='admin',
                                   name=self.decode_value(update_user['name']),
                                   goods=goods_list)
            self.admins.append(new)
        else:
            new = self.create_user(type_='guest',
                                   name=self.decode_value(update_user['name']),
                                   goods=goods_list)
            self.guests.append(new)

    def delete_category(self, delete_category):
        # del_num = None
        for i in range(len(self.categories)):
            if self.categories[i].id == delete_category.id:
                self.categories[i].visible = False
                # del_num = i
        # self.categories.pop(del_num)

    @staticmethod
    def create_good(name,
                    description='',
                    image=None,
                    discount=0,
                    visible=True,
                    cost=0,
                    category=None):
        return Goods(name, description, image, discount, cost, visible, category)

    def get_good(self, name):
        for item in self.goods:
            if item.name == name:
                return item
        return None

    def find_good_by_id(self, id):
        for item in self.goods:
            print('item', item.id)
            if item.id == id:
                return item
        raise Exception(f'Нет товара с id = {id}')

    def update_good(self, update_good, old_good):
        for i in range(len(self.goods)):
            if self.goods[i].id == update_good['id']:
                if update_good['price'] != old_good.cost:
                    self.goods[i].notify({'price': {'old': old_good.cost,
                                                    'new': update_good['price']}})
                elif update_good['discount'] != old_good.discount:
                    self.goods[i].notify({'discount': {'old': old_good.discount,
                                                       'new': update_good['discount']}})
                self.goods[i].name = update_good['name']
                self.goods[i].description = update_good['desc']
                self.goods[i].cost = update_good['price']
                self.goods[i].discount = update_good['discount']
                self.goods[i].category = self.find_category_by_id(int(update_good['category']))

    def delete_good(self, delete_good):
        # del_num = None
        for i in range(len(self.goods)):
            if self.goods[i].id == delete_good.id:
                self.goods[i].visible = False
        #         del_num = i
        # self.goods.pop(del_num)

    @staticmethod
    def decode_value(val):
        val_b = bytes(val.replace('%', '=').replace("+", " "), 'UTF-8')
        val_decode_str = quopri.decodestring(val_b)
        return val_decode_str.decode('UTF-8')

    def get_guest(self, name) -> Guest:
        for item in self.guests:
            if item.name == name:
                return item

    def create_test_data(self):
        new_category = self.create_category(name='Test',
                                            description='тест',
                                            visible=True,
                                            category=None)
        self.categories.append(new_category)
        new_good = self.create_good(name='Good_Test',
                                    description='описание товара',
                                    image=None,
                                    discount=10,
                                    visible=True,
                                    cost=1234,
                                    category=self.categories[0]
                                    )
        new_good.observers.append(EmailNotifier())
        new_good.observers.append(SmsNotifier())
        self.goods.append(new_good)
        new_good2 = self.create_good(name='Good_Test2',
                                    description='описание товара',
                                    image=None,
                                    discount=10,
                                    visible=True,
                                    cost=12345,
                                    category=self.categories[0]
                                    )
        new_good2.observers.append(EmailNotifier())
        new_good2.observers.append(SmsNotifier())
        self.goods.append(new_good2)
        # new_admin = self.create_user('admin', name='admin', goods=[new_good])
        # self.admins.append(new_admin)
        # new_guest = self.create_user('guest', name='user', goods=[])
        # self.guests.append(new_guest)

    def create_goods_list_by_id(self, good_sub):
        goods_list = []
        if good_sub:
            good_id = good_sub.split('_')
            for id in good_id:
                goods_list.append(self.find_good_by_id(int(id)))
        return goods_list


# порождающий паттерн Синглтон
class SingletonByName(type):

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = {}

    def __call__(cls, *args, **kwargs):
        if args:
            name = args[0]
        if kwargs:
            name = kwargs['name']

        if name in cls.__instance:
            return cls.__instance[name]
        else:
            cls.__instance[name] = super().__call__(*args, **kwargs)
            return cls.__instance[name]


class Logger(metaclass=SingletonByName):

    def __init__(self, name, writer=ConsoleWriter()):
        self.name = name
        self.writer = writer

    def log(self, text):
        text = f'log---> {text}'
        self.writer.write(text)


# поведенческий паттерн - Шаблонный метод


class UserMapper:

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'users'
        self.start()


    def start(self):
        table = f"CREATE TABLE IF NOT EXISTS {self.tablename}(" \
                f"id INTEGER PRIMARY KEY," \
                f"name TEXT UNIQUE," \
                f"good_sub TEXT," \
                f"admin BOOL)"
        self.cursor.execute(table)
        self.connection.commit()

    def all(self, engine_obj):
        statement = f'SELECT * from {self.tablename}'
        self.cursor.execute(statement)
        result = []
        for item in self.cursor.fetchall():
            id, name, good_sub, admin = item
            goods_list = engine_obj.create_goods_list_by_id(good_sub)
            user = UserFactory.types_from_admin(name=name, goods=goods_list, admin=admin)
            user.id = id
            result.append(user)
        return result

    def find_by_id(self, id, engine_obj):
        statement = f"SELECT id, name, good_sub, admin FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (id,))
        result = self.cursor.fetchone()

        if result:
            id, name, good_sub, admin = result
            goods_list = engine_obj.create_goods_list_by_id(good_sub)
            user = UserFactory.types_from_admin(name=name, goods=goods_list, admin=admin)
            user.id = id
            return user
        else:
            raise RecordNotFoundException(f'record with id={id} not found')

    def insert(self, obj):
        goods_id_str = ''
        for item in obj.goods:
            if len(goods_id_str):
                goods_id_str = f'{goods_id_str}_{item.id}'
            else:
                goods_id_str = f'{item.id}'
        try:
            statement = f"INSERT INTO {self.tablename} (name, good_sub, admin) VALUES (?, ?, ?)"
            self.cursor.execute(statement, (obj.name, goods_id_str, obj.admin))
            try:
                self.connection.commit()
            except Exception as e:
                raise DbCommitException(e.args)
        except sqlite3.IntegrityError:
            print('Отмена записи нового пользователя в БД. Пользователь с таким именем уже существует.')

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, good_sub=?, admin=? WHERE id=?"
        # Где взять obj.id? Добавить в DomainModel? Или добавить когда берем объект из базы
        self.cursor.execute(statement, (obj.name, obj.goods, obj.admin, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbUpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE name=?"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DbDeleteException(e.args)


connection = sqlite3.connect('patterns.sqlite')


# архитектурный системный паттерн - Data Mapper
class MapperRegistry:
    mappers = {
        'guest': UserMapper,
        'admin': UserMapper,
        # 'category': CategoryMapper
    }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, User):
            return UserMapper(connection)
        if isinstance(obj, Admin):
            return UserMapper(connection)
        # if isinstance(obj, Category):
        # return CategoryMapper(connection)

    @staticmethod
    def get_current_mapper(name):
        return MapperRegistry.mappers[name](connection)


class DbCommitException(Exception):
    def __init__(self, message):
        super().__init__(f'Db commit error: {message}')


class DbUpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Db update error: {message}')


class DbDeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Db delete error: {message}')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Record not found: {message}')
