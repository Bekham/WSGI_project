from amazing_framework.main import AmazingFramework
from urls import routes, fronts
from wsgiref.simple_server import make_server
from whitenoise import WhiteNoise
from settings import STATIC_URL, HOST, PORT

app = AmazingFramework(routes, fronts)
app = WhiteNoise(app)
app.add_files(f'./{STATIC_URL}', prefix=f'{STATIC_URL}')

with make_server(HOST, PORT, app) as httpd:
    print("Запуск на порту 8000...")
    print(f'{HOST}:{PORT}')
    httpd.serve_forever()
