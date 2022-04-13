from datetime import datetime
from views import IndexView, ContactsView, AboutView, RememberView, CategoryListView, CategoryCreateView, GoodsListView, \
    GoodsCreateView, CategoryEditView, CategoryCopyView, CategoryDeleteView, GoodsCopyView, GoodsDeleteView, \
    GoodsEditView


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
    '/Admin/CategoryList.html/': CategoryListView(),
    '/Admin/CategoryCreate.html/': CategoryCreateView(),
    '/Admin/GoodsList.html/': GoodsListView(),
    '/Admin/GoodsCreate.html/': GoodsCreateView(),
    '/Admin/edit-category/': CategoryEditView(),
    '/Admin/copy-category/': CategoryCopyView(),
    '/Admin/delete-category/': CategoryDeleteView(),
    '/Admin/edit-good/': GoodsEditView(),
    '/Admin/copy-good/': GoodsCopyView(),
    '/Admin/delete-good/': GoodsDeleteView(),
}
