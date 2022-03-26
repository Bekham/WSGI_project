from amazing_framework.main import AmazingFramework
from urls import routes, fronts
from wsgiref.simple_server import make_server
from whitenoise import WhiteNoise
from settings import static_url

app = AmazingFramework(routes, fronts)
app = WhiteNoise(app)
app.add_files(f'./{static_url}', prefix=f'{static_url}')

with make_server('', 8000, app) as httpd:
    print("Запуск на порту 8000...")
    httpd.serve_forever()
