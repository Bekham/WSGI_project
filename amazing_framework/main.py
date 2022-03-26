
class PageNotFound404:
    def __call__(self, request):
        return '404 WHAT', '404 PAGE Not Found'


class AmazingFramework:

    """Класс Framework - основа фреймворка"""

    def __init__(self, routes, fronts):
        self.routes = routes
        self.fronts = fronts

    def __call__(self, environ, start_response):
        # получаем адрес, по которому выполнен переход
        path = environ['PATH_INFO']
        # добавление закрывающего слеша
        if not path.endswith('/'):
            path = f'{path}/'

        # находим нужный контроллер
        # отработка паттерна page controller

        if path in self.routes:
            view = self.routes[path]
        else:
            view = PageNotFound404()
        request = {}
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        print(body)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

