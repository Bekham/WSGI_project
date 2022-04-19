from amazing_framework.site_requests import GetRequests, PostRequests
import quopri

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
        # Получаем все данные запроса
        method = environ['REQUEST_METHOD']
        request['method'] = method
        if method == 'POST':
            data = PostRequests().get_request_params(environ)
            request['data'] = data
            print(f'Нам пришёл post-запрос: {AmazingFramework.decode_value(data)}')
            request['verify'] = True
        if method == 'GET':
            request_params = GetRequests().get_request_params(environ)
            request['request_params'] = request_params
            print(f'Нам пришли GET-параметры: {request_params}')
        # наполняем словарь request элементами
        # этот словарь получат все контроллеры
        # отработка паттерна front controller
        for front in self.fronts:
            front(request)
        # запуск контроллера с передачей объекта request
        code, body = view(request)
        start_response(code, [('Content-Type', 'text/html')])
        return [body.encode('utf-8')]

    @staticmethod
    def decode_value(data):
        new_data = {}
        for k, v in data.items():
            val = bytes(v.replace('%', '=').replace("+", " "), 'UTF-8')
            val_decode_str = quopri.decodestring(val).decode('UTF-8')
            new_data[k] = val_decode_str
        return new_data

class DebugApplication(AmazingFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = AmazingFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        print('DEBUG MODE')
        print(env)
        return self.application(env, start_response)


# Новый вид WSGI-application.
# Второй — фейковый (на все запросы пользователя отвечает:
# 200 OK, Hello from Fake).
class FakeApplication(AmazingFramework):

    def __init__(self, routes_obj, fronts_obj):
        self.application = AmazingFramework(routes_obj, fronts_obj)
        super().__init__(routes_obj, fronts_obj)

    def __call__(self, env, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'Hello from Fake']