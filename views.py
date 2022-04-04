from amazing_framework.view_base_class import ViewBaseClass


class IndexView(ViewBaseClass):
    title = 'Главная'
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        super(IndexView, self).get_context_data(**kwargs)
        self.context['minutes'] = self.request.get('minutes', None)


class ContactsView(ViewBaseClass):
    title = 'Контакты'


class AboutView(ViewBaseClass):
    title = 'О нас'


class RememberView(ViewBaseClass):
    title = 'Напомнить мне'
    template_name = 'remember.html'

    def get_context_data(self, **kwargs):
        super(RememberView, self).get_context_data(**kwargs)
        self.context['verify'] = self.request.get('verify', None)
