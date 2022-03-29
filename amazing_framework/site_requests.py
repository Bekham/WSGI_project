
class GetRequests:

    @staticmethod
    def parse_input_data(data: str):
        result = {}
        if data:
            # делим параметры через &
            params = data.split('&')
            for item in params:
                # делим ключ и значение через =
                k, v = item.split('=')
                result[k] = v
        return result

    @staticmethod
    def get_request_params(environ):
        # получаем параметры запроса
        query_string = environ['QUERY_STRING']
        # превращаем параметры в словарь
        request_params = GetRequests.parse_input_data(query_string)
        return request_params


# post requests
class PostRequests:

    @staticmethod
    def parse_input_data(data: str):
        result = {}
        if data:
            # делим параметры через &
            params = data.split('&')
            for item in params:
                # делим ключ и значение через =
                k, v = item.split('=')
                result[k] = v
        return result

    @staticmethod
    def get_wsgi_input_data(env) -> bytes:
        # получаем длину тела
        content_length_data = env.get('CONTENT_LENGTH')
        print(f'ддлина - {type(content_length_data)}') # ддлина - <class 'str'>
        # приводим к int
        content_length = int(content_length_data) if content_length_data else 0
        print(content_length)
        # считываем данные, если они есть
        # print(f"-{type(env['wsgi.input'])}") -> <class '_io.BufferedReader'>
        # запускаем режим чтения
        # Посмотрите в консоле браузера что грузиться дольше всего - найдете причину!
        data = env['wsgi.input'].read(content_length) if content_length > 0 else b''
        return data

    def parse_wsgi_input_data(self, data: bytes) -> dict:
        result = {}
        if data:
            # декодируем данные
            data_str = data.decode(encoding='utf-8')
            print(f'строка после декод - {data_str}')
            # собираем их в словарь
            result = self.parse_input_data(data_str)
        return result

    def get_request_params(self, environ):
        # получаем данные
        data = self.get_wsgi_input_data(environ)
        # превращаем данные в словарь
        data = self.parse_wsgi_input_data(data)
        return data

# 'method': 'POST', 'data':
# {'name': '%D0%9F%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8C',
# 'email': 'cdi9%40yandex.ru', 'location': 'ny'}}