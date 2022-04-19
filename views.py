from patterns.creational_patterns import ViewBaseClass, Engine, Logger
from patterns.structural_patterns import AppRoute, Debug

site = Engine()
logger = Logger('main')
site.create_test_data()

routes = {}


@AppRoute(routes=routes, url='/')
class IndexView(ViewBaseClass, object):
    title = 'Главная'
    template_name = 'index.html'

    def add_context_data(self, **kwargs):
        self.context['minutes'] = self.request.get('minutes', None)


@AppRoute(routes=routes, url='/Contact.html/')
class ContactsView(ViewBaseClass):
    title = 'Контакты'


@AppRoute(routes=routes, url='/About.html/')
class AboutView(ViewBaseClass):
    title = 'О нас'


@AppRoute(routes=routes, url='/Remember.html/')
class RememberView(ViewBaseClass):
    title = 'Напомнить мне'
    template_name = 'remember.html'

    def add_context_data(self, **kwargs):
        self.context['verify'] = self.request.get('verify', None)


@AppRoute(routes=routes, url='/Admin/CategoryList.html/')
class CategoryListView(ViewBaseClass):
    title = 'Список категорий'
    template_name = 'category_list.html'

    def __call__(self, *args, **kwargs):
        logger.log('Список категорий')
        try:
            all_categories = site.categories
            self.context['objects_list'] = all_categories
            if not len(self.context['objects_list']):
                self.context['empty_list'] = 'Категории еще не созданы'
            return super().__call__(self)
        except KeyError:
            return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/CategoryCreate.html/')
class CategoryCreateView(ViewBaseClass):
    title = 'Создание категории'
    template_name = 'create_category-1.html'

    def __call__(self, request=None, *args, **kwargs):
        self.context['verify'] = request.get('verify', None)
        if request['method'] == 'POST':
            # self.context['verify'] = request.get('verify', None)
            # метод пост
            data = request['data']

            if data['category_name'] and not site.find_category_by_name(data['category_name']):
                category_id = data['category']
                if category_id != '0':
                    parent_category = site.find_category_by_id(int(category_id))
                else:
                    parent_category = None
                new_category = site.create_category(name=site.decode_value(data['category_name']),
                                                    description=site.decode_value(data['category_desc']),
                                                    category=parent_category)
                site.categories.append(new_category)
        return super().__call__(self)

    def add_context_data(self, **kwargs):
        self.context['categories'] = site.categories


@AppRoute(routes=routes, url='/Admin/edit-category/')
class CategoryEditView(ViewBaseClass):
    title = 'Редактирование категории'
    template_name = 'edit_category-1.html'

    def __call__(self, request=None, *args, **kwargs):
        # self.context['verify'] = request.get('verify', None)
        if request['method'] == 'GET':
            data = request['request_params']
            category = site.find_category_by_id(int(data['id']))
            self.context['category'] = category
            self.context['categories'] = site.categories
        if request['method'] == 'POST':
            self.context['verify'] = request.get('verify', None)
            # метод пост
            data = request['data']
            if data['category_name']:
                if data['parent_category'] == '0':
                    parent_category = None
                else:
                    parent_category = site.find_category_by_id(int(data['parent_category']))
                update_category = {
                    'id': self.context['category'].id,
                    'name': data['category_name'],
                    'desc': site.decode_value(data['category_desc']),
                    'parent_category': parent_category
                }
                site.update_category(update_category)
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/copy-category/')
class CategoryCopyView(ViewBaseClass):
    title = 'Список категорий'
    template_name = 'category_list.html'

    def __call__(self, request=None, *args, **kwargs):
        if request['method'] == 'GET':
            data = request['request_params']
            old_category = site.find_category_by_id(int(data['id']))
            if old_category:
                new_name = f"copy_{old_category.name}"
                new_category = old_category.clone()
                new_category.name = new_name
                new_category.id = len(site.categories)
                new_category.goods = []
                site.categories.append(new_category)
        self.context['objects_list'] = site.categories
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/delete-category/')
class CategoryDeleteView(ViewBaseClass):
    title = 'Список категорий'
    template_name = 'category_list.html'

    def __call__(self, request=None, *args, **kwargs):

        if request['method'] == 'GET':
            data = request['request_params']
            del_category = site.find_category_by_id(int(data['id']))
            if del_category:
                site.delete_category(del_category)
        self.context['objects_list'] = site.categories
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/GoodsList.html/')
class GoodsListView(ViewBaseClass):
    title = 'Список товаров'
    template_name = 'goods_list.html'

    def __call__(self, *args, **kwargs):
        logger.log('Список товаров')
        try:
            all_goods = site.goods
            self.context['objects_list'] = all_goods
            if not len(self.context['objects_list']):
                self.context['empty_list'] = 'Товары еще не добавлены'
            return super().__call__(self)
        except KeyError:
            return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/GoodsCreate.html/')
class GoodsCreateView(ViewBaseClass):
    title = 'Создание товара'
    template_name = 'create_goods-1.html'

    def __call__(self, request=None, *args, **kwargs):
        if request['method'] == 'POST':
            self.context['verify'] = request.get('verify', None)
            # метод пост
            data = request['data']
            if data['category']:
                category_id = data['category']
                good = site.create_good(name=site.decode_value(data['good_name']),
                                        description=site.decode_value(data['good_desc']),
                                        discount=int(data['good_discount']),
                                        cost=float(data['good_price']),
                                        category=site.find_category_by_id(int(category_id))
                                        )
                site.goods.append(good)
        return super().__call__(self)

    def add_context_data(self, **kwargs):
        self.context['categories'] = site.categories


@AppRoute(routes=routes, url='/Admin/copy-good/')
class GoodsCopyView(ViewBaseClass):
    title = 'Список товаров'
    template_name = 'goods_list.html'

    def __call__(self, request=None, *args, **kwargs):
        if request['method'] == 'GET':
            data = request['request_params']
            old_good = site.find_good_by_id(int(data['id']))
            if old_good:
                new_name = f"copy_{old_good.name}"
                new_good = old_good.clone()
                new_good.name = new_name
                new_good.id = len(site.goods)
                for i in range(len(site.categories)):
                    if site.categories[i].id == new_good.category.id:
                        site.categories[i].goods.append(new_good)
                site.goods.append(new_good)
        self.context['objects_list'] = site.goods
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/delete-good/')
class GoodsDeleteView(ViewBaseClass):
    title = 'Список товаров'
    template_name = 'goods_list.html'

    def __call__(self, request=None, *args, **kwargs):
        if request['method'] == 'GET':
            data = request['request_params']
            del_good = site.find_good_by_id(int(data['id']))
            if del_good:
                site.delete_good(del_good)
        self.context['objects_list'] = site.goods
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/edit-good/')
class GoodsEditView(ViewBaseClass):
    title = 'Редактирование товара'
    template_name = 'edit_good-1.html'

    def __call__(self, request=None, *args, **kwargs):
        if request['method'] == 'GET':
            data = request['request_params']
            good = site.find_good_by_id(int(data['id']))
            self.context['categories'] = site.categories
            self.context['good'] = good
        if request['method'] == 'POST':
            self.context['verify'] = request.get('verify', None)
            # метод пост
            data = request['data']
            if data['good_name']:
                update_good = {
                    'id': self.context['good'].id,
                    'name': site.decode_value(data['good_name']),
                    'desc': site.decode_value(data['good_desc']),
                    'price': data['good_price'],
                    'discount': data['good_discount'],
                    'category': data['category']
                }
                site.update_good(update_good)
        return super().__call__(self)
