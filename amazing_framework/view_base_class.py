
from jinja2 import Environment, FileSystemLoader
from settings import TEMPLATE, STATIC_URL


class ViewBaseClass:
    title = None
    folder = TEMPLATE
    template_name = None
    static = STATIC_URL

    def __init__(self):
        self.context = {}

    def __call__(self, request=None, *args, **kwargs):
        self.request = request
        self.get_context_data(**kwargs)
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
        for key, item in kwargs:
            self.context[key] = item
        self.context['title'] = self.title
        self.context['static'] = self.static
        return self.context

    def render(self):
        # file_path = os.path.join(self.template_name, self.title)
        # kwargs['static'] = static_url
        # Открываем шаблон по имени
        env = Environment()
        env.loader = FileSystemLoader(self.folder)
        template = env.get_template(self.template_name)
        return template.render(self.context)
