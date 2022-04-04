from datetime import datetime
from views import IndexView, ContactsView, AboutView, RememberView


# data controller
def data_front(request):
    d1 = datetime.now()
    d2 = datetime.strptime('2022-04-25 23:00:00', '%Y-%m-%d %H:%M:%S')
    minutes = (d2 - d1).total_seconds() / 3600
    request['minutes'] = f'{int(minutes)}h'


fronts = [data_front]

routes = {
    '/': IndexView(),
    '/Contact.html/': ContactsView(),
    '/About.html/': AboutView(),
    '/Remember.html/': RememberView(),
}
