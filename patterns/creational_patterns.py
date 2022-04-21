

from patterns.behavioral_patterns import Subject, EmailNotifier, SmsNotifier, ConsoleWriter
import copy
import quopri

# абстрактный пользователь



class User:
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
        self.admins = []
        self.guests = []
        self.goods = []
        self.categories = []

    @staticmethod
    def create_user(type_, name, goods):
        new_user = UserFactory.create(type_, name, goods)
        if len(goods):
            for good in goods:
                good.add_user_to_notify(user=new_user)
        return new_user

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
                    self.goods[i].notify({'price': {'old':old_good.cost,
                                                    'new':update_good['price']}})
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
        new_admin = self.create_user('admin', name='admin', goods=[new_good])
        self.admins.append(new_admin)
        new_guest = self.create_user('guest', name='user', goods=[])
        self.guests.append(new_guest)

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




