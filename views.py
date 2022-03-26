from amazing_framework.templator import render


class Index:
    def __call__(self, request):
        return '200 OK', render('index.html', minutes=request.get('minutes', None))


class Contacts:
    def __call__(self, request):
        return '200 OK', 'contacts'

class About:
    def __call__(self, request):
        return '200 OK', 'about'

class Remember:
    def __call__(self, request):
        remember_text = '<head>' \
                        '<meta charset="utf-8">' \
                        '</head>' \
                        '<body>Напоминание установлено!</body>'
        return '200 OK', remember_text

