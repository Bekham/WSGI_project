from patterns.behavioral_patterns import ListView, CreateView, TemplateView, EmailNotifier, SmsNotifier, BaseSerializer
from patterns.creational_patterns import Engine, Logger
from patterns.structural_patterns import AppRoute, Debug

site = Engine()
logger = Logger('main')
site.create_test_data()
email_notifier = EmailNotifier()
sms_notifier = SmsNotifier()
routes = {}


@AppRoute(routes=routes, url='/')
class IndexView(TemplateView, object):
    title = 'Главная'
    template_name = 'index.html'

    def add_context_data(self, **kwargs):
        self.context['minutes'] = self.request.get('minutes', None)


@AppRoute(routes=routes, url='/Contact.html/')
class ContactsView(TemplateView):
    title = 'Контакты'


@AppRoute(routes=routes, url='/About.html/')
class AboutView(TemplateView):
    title = 'О нас'


@AppRoute(routes=routes, url='/Remember.html/')
class RememberView(TemplateView):
    title = 'Напомнить мне'
    template_name = 'remember.html'

    def add_context_data(self, **kwargs):
        self.context['verify'] = self.request.get('verify', None)


@AppRoute(routes=routes, url='/Admin/CategoryList.html/')
class CategoryListView(ListView):
    title = 'Список категорий'
    template_name = 'category_list.html'

    def get_queryset(self, data):
        self.queryset = data

    def __call__(self, *args, **kwargs):
        logger.log('Список категорий')
        self.get_queryset(site.categories)
        if not len(self.queryset):
            self.context['empty_list'] = 'Категории еще не созданы'
        return super().__call__(self, **kwargs)



@AppRoute(routes=routes, url='/Admin/CategoryCreate.html/')
class CategoryCreateView(CreateView):
    title = 'Создание категории'
    template_name = 'create_category-1.html'

    def create_obj(self, data):
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

    def add_context_data(self, **kwargs):
        self.context['categories'] = site.categories


@AppRoute(routes=routes, url='/Admin/edit-category/')
class CategoryEditView(CreateView):
    title = 'Редактирование категории'
    template_name = 'edit_category-1.html'

    def create_obj(self, data):
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

    def process_get_params(self, data):
        category = site.find_category_by_id(int(data['id']))
        self.context['category'] = category
        self.context['categories'] = site.categories



@AppRoute(routes=routes, url='/Admin/copy-category/')
class CategoryCopyView(TemplateView):
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
                new_category.id = len(site.categories) + 1
                new_category.goods = []
                site.categories.append(new_category)
        self.context['objects_list'] = site.categories
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/delete-category/')
class CategoryDeleteView(TemplateView):
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
class GoodsListView(ListView):

    title = 'Список товаров'
    template_name = 'goods_list.html'

    def get_queryset(self, data):
        self.queryset = data

    def __call__(self, *args, **kwargs):
        logger.log('Список категорий')
        self.get_queryset(site.goods)
        if not len(self.queryset):
            self.context['empty_list'] = 'Товары еще не созданы'
        return super().__call__(self, **kwargs)

@AppRoute(routes=routes, url='/Admin/GoodsCreate.html/')
class GoodsCreateView(CreateView):
    title = 'Создание товара'
    template_name = 'create_goods-1.html'

    def create_obj(self, data):
        if data['category']:
            category_id = data['category']
            good = site.create_good(name=site.decode_value(data['good_name']),
                                    description=site.decode_value(data['good_desc']),
                                    discount=int(data['good_discount']),
                                    cost=float(data['good_price']),
                                    category=site.find_category_by_id(int(category_id))
                                    )
            good.observers.append(email_notifier)
            good.observers.append(sms_notifier)
            site.goods.append(good)

    def add_context_data(self, **kwargs):
        self.context['categories'] = site.categories


@AppRoute(routes=routes, url='/Admin/copy-good/')
class GoodsCopyView(TemplateView):
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
                new_good.id = len(site.goods) + 1
                for i in range(len(site.categories)):
                    if site.categories[i].id == new_good.category.id:
                        site.categories[i].goods.append(new_good)
                site.goods.append(new_good)
        self.context['objects_list'] = site.goods
        return super().__call__(self)


@AppRoute(routes=routes, url='/Admin/delete-good/')
class GoodsDeleteView(TemplateView):
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
class GoodsEditView(CreateView):
    title = 'Редактирование товара'
    template_name = 'edit_good-1.html'
    old_good = None

    def create_obj(self, data):
        if data['good_name']:
            update_good = {
                'id': self.context['good'].id,
                'name': site.decode_value(data['good_name']),
                'desc': site.decode_value(data['good_desc']),
                'price': data['good_price'],
                'discount': data['good_discount'],
                'category': data['category']
            }
            site.update_good(update_good=update_good, old_good=self.old_good)

    def process_get_params(self, data):
        good = site.find_good_by_id(int(data['id']))
        self.old_good = good
        self.context['categories'] = site.categories
        self.context['good'] = good

@AppRoute(routes=routes, url='/Admin/UsersList.html/')
class UsersListView(ListView):
    title = 'Список пользователей'
    template_name = 'users_list.html'

    def get_queryset(self, data):
        if data and data not in self.queryset:
            self.queryset.append(data)

    def __call__(self, *args, **kwargs):
        logger.log('Список пользователей')
        self.get_queryset(site.admins)
        self.get_queryset(site.guests)
        if not len(self.queryset):
            self.context['empty_list'] = 'Пользователи еще не созданы'
        return super().__call__(self, **kwargs)

    @AppRoute(routes=routes, url='/Admin/UsersCreate.html/')
    class CategoryCreateView(CreateView):
        title = 'Добавление пользователя'
        template_name = 'create_user-1.html'

        def create_obj(self, data):
            if data['user_name'] and not site.find_user_by_name(data['user_name']):
                goods = []
                if data['good_sub']:
                    goods_id = data['good_sub'].split('_')
                    for good_id in goods_id:
                        if good_id != '---':
                            goods.append(site.find_good_by_id(int(good_id)))

                if int(data['admin']):
                    new_user = site.create_user(type_='admin',
                                                name=site.decode_value(data['user_name']),
                                                goods=goods)
                    site.admins.append(new_user)
                else:
                    new_user = site.create_user(type_='guest',
                                                name=site.decode_value(data['user_name']),
                                                goods=goods)
                    site.guests.append(new_user)

        def add_context_data(self, **kwargs):
            self.context['goods'] = site.goods


@AppRoute(routes=routes, url='/Admin/edit-user/')
class CategoryEditView(CreateView):
    title = 'Редактирование пользователя'
    template_name = 'edit_user-1.html'
    old_profile = None

    def create_obj(self, data):
        if data['user_name']:
            goods = []
            if len(data['good_sub'].split('_')):
                goods_id = data['good_sub'].split('_')
                if '0' not in goods_id:
                    goods = goods_id
            else:
                goods = site.find_user_by_name((data['name'])).goods
            update_user = {
                'name': data['user_name'],
                'good_sub': goods,
                'admin': data['admin']
            }
            site.update_user(update_user=update_user, old_profile=self.old_profile)

    def process_get_params(self, data):
        user = site.find_user_by_name((data['name']))
        self.old_profile = user
        self.context['user'] = user
        self.context['goods'] = site.goods

    @AppRoute(routes=routes, url='/api/')
    class GoodsApi:
        @Debug()
        def __call__(self, request):
            return '200 OK', BaseSerializer(site.goods).save()