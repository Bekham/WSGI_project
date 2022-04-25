import jsonpickle
from jinja2 import Environment, FileSystemLoader


# поведенческий паттерн - наблюдатель
# Курс
from patterns.structural_patterns import Debug
from settings import TEMPLATE, STATIC_URL


class Observer:

    def update(self, subject, changed):
        pass


class Subject:

    def __init__(self):
        self.observers = []

    def notify(self, changed):
        for item in self.observers:
            item.update(self, changed)


class SmsNotifier(Observer):

    def update(self, subject, changed):
        if 'price' in changed.keys():
            old = changed['price']['old']
            new = changed['price']['new']
            print('SMS->', f'Изменение цены товара {subject.name}: {old}руб -> {new}руб')
        elif 'discount' in changed.keys():
            old = changed['discount']['old']
            new = changed['discount']['new']
            print('SMS->', f'Изменение скидки на товар {subject.name}: {old}% -> {new}%')


class EmailNotifier(Observer):

    def update(self, subject, changed):
        if 'price' in changed.keys():
            old = changed['price']['old']
            new = changed['price']['new']
            print('EMAIL->', f'Изменение цены товара {subject.name}: {old}руб -> {new}руб')
        elif 'discount' in changed.keys():
            old = changed['discount']['old']
            new = changed['discount']['new']
            print('EMAIL->', f'Изменение скидки на товар {subject.name}: {old}% -> {new}%')


class BaseSerializer:

    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return jsonpickle.dumps(self.obj)

    @staticmethod
    def load(data):
        return jsonpickle.loads(data)

# поведенческий паттерн - Шаблонный метод
class TemplateView:
    title = 'template.html'
    folder = TEMPLATE
    template_name = None
    static = STATIC_URL

    def __init__(self):
        self.context = {}

    def get_context_data(self, **kwargs):
        self.context['title'] = self.title
        self.context['static'] = self.static
        if kwargs:
            for key, item in kwargs:
                self.context[key] = item

    def add_context_data(self, **kwargs):
        pass

    def render(self):
        env = Environment()
        env.loader = FileSystemLoader(self.folder)
        template = env.get_template(self.template_name)
        return template.render(self.context)

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


class ListView(TemplateView):
    queryset = []
    template_name = 'list.html'
    context_object_name = 'objects_list'

    def get_queryset(self, data):
        pass
        # print(self.queryset)

    def get_context_object_name(self):
        return self.context_object_name

    def get_context_data(self, **kwargs):
        # queryset = self.get_queryset()
        context_object_name = self.get_context_object_name()
        self.context[context_object_name] = self.queryset
        return super().get_context_data(**kwargs)

class CreateView(TemplateView):
    template_name = 'create.html'

    def create_obj(self, data):
        pass

    def process_get_params(self, data):
        pass

    def __call__(self, request=None, *args, **kwargs):
        self.context['verify'] = request.get('verify', None)
        if request['method'] == 'GET':
            data = request['request_params']
            self.process_get_params(data)
        if request['method'] == 'POST':
            # метод пост
            data = request['data']
            self.create_obj(data)
        return super().__call__(self)





# поведенческий паттерн - Стратегия
class ConsoleWriter:

    def write(self, text):
        print(text)


class FileWriter:

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text):
        with open(self.file_name, 'a', encoding='utf-8') as f:
            f.write(f'{text}\n')

