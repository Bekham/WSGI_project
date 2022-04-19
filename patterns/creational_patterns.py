from jinja2 import Environment, FileSystemLoader

from patterns.structural_patterns import Debug
from settings import TEMPLATE, STATIC_URL
import copy
import quopri

# абстрактный пользователь
class User:
    pass


# гость
class Guest(User):
    pass


# админ
class Admin(User):
    pass


# порождающий паттерн Абстрактная фабрика - фабрика пользователей
class UserFactory:
    types = {
        'guest': Guest,
        'admin': Admin
    }

    # порождающий паттерн Фабричный метод
    @classmethod
    def create(cls, type_):
        return cls.types[type_]()


# порождающий паттерн Прототип - Курс
class GoodsPrototype:
    # прототип курсов обучения
    def clone(self):
        return copy.deepcopy(self)

class Goods(GoodsPrototype):
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

    def __call__(self, *args, **kwargs):
        if not self.category.visible:
            self.visible = False

    def clone(self):
        Category.auto_id += 1
        return super().clone()


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
    def create_user(type_):
        return UserFactory.create(type_)

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

    def update_category(self, update_category):
        for i in range(len(self.categories)):
            if self.categories[i].id == update_category['id']:
                self.categories[i].name = update_category['name']
                self.categories[i].description = update_category['desc']
                self.categories[i].category = update_category['parent_category']


    def delete_category(self, delete_category):
        del_num = None
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

    def update_good(self, update_good):
        for i in range(len(self.goods)):
            if self.goods[i].id == update_good['id']:
                self.goods[i].name = update_good['name']
                self.goods[i].description = update_good['desc']
                self.goods[i].cost = update_good['price']
                self.goods[i].discount = update_good['discount']
                self.goods[i].category = self.find_category_by_id(int(update_good['category']))

    def delete_good(self, delete_good):
        del_num = None
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
        self.goods.append(new_good)

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

    def __init__(self, name):
        self.name = name

    @staticmethod
    def log(text):
        print('log--->', text)


class ViewBaseClass:
    title = None
    folder = TEMPLATE
    template_name = None
    static = STATIC_URL

    def __init__(self):
        self.context = {}

    @Debug()
    def __call__(self, request=None, *args, **kwargs):
        self.request = request
        self.get_context_data(**kwargs)
        self.add_context_data(**kwargs)
        if self.title and self.template_name:
            return '200 OK', self.render()
        elif self.title:
            html_text = '<head>' \
                            '<meta charset="utf-8">' \
                            '</head>' \
                            f'<body>{self.title}</body>'
            return '200 OK', html_text
        else:
            return '404 WHAT', '404 PAGE Not Found'

    def get_context_data(self, **kwargs):

        self.context['title'] = self.title
        self.context['static'] = self.static
        if kwargs:
            for key, item in kwargs:
                self.context[key] = item
        return self.context

    def add_context_data(self, **kwargs):
        pass

    def render(self):
        # file_path = os.path.join(self.template_name, self.title)
        # kwargs['static'] = static_url
        # Открываем шаблон по имени
        env = Environment()
        env.loader = FileSystemLoader(self.folder)
        template = env.get_template(self.template_name)
        return template.render(self.context)
