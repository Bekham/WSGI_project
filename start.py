from amazing_framework.main import AmazingFramework, DebugApplication, FakeApplication
from urls import fronts
from wsgiref.simple_server import make_server
from whitenoise import WhiteNoise
from settings import STATIC_URL, HOST, PORT, MODE
from views import routes

modes = {
    'REALISE': AmazingFramework,
    'DEBUG': DebugApplication,
    'FAKE': FakeApplication
}


app = modes[MODE](routes, fronts)
app = WhiteNoise(app)
app.add_files(f'./{STATIC_URL}', prefix=f'{STATIC_URL}')

with make_server(HOST, PORT, app) as httpd:
    print(f"Запуск на порту {PORT}...")
    print(f'{HOST}:{PORT}')
    httpd.serve_forever()
