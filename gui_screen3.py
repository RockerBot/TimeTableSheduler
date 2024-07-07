from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

from gui_helpfull import add_widgets, add_colour


class CustomScrollView(ScrollView):
    def on_scroll_start(self, touch, check_children=True):
        if self.collide_point(*touch.pos):
            if self.do_scroll_x and touch.button == 'scrolldown':
                self.scroll_x += 0.1
                self.scroll_x = max(min(1, self.scroll_x), 0)
            elif self.do_scroll_x and touch.button == 'scrollup':
                self.scroll_x -= 0.1
                self.scroll_x = max(min(1, self.scroll_x), 0)
        return super().on_scroll_start(touch, check_children)


class ListEntry(BoxLayout):
    def __init__(self, text, subjects, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.label = Label(text=text, size_hint=(0.2, 1))
        self.scroll_view = CustomScrollView(size_hint=(0.8, 1))
        self.layout_subj = BoxLayout(orientation='horizontal', spacing=10, size_hint_x=None)

        for subj in subjects:
            btn = ToggleButton(text=subj, size_hint_x=None, width=dp(70))
            # btn.bind(minimum_width=btn.setter('width'))
            self.layout_subj.add_widget(btn)

        self.layout_subj.bind(minimum_width=self.layout_subj.setter('width'))

        self.scroll_view.add_widget(self.layout_subj)
        add_widgets(
            self.label,
            self.scroll_view,
            to=self
        )
        add_colour(self, (1, 0, 0, 1))
        add_colour(self.scroll_view, (1, 1, 0, 1))

    def get_text(self):
        return self.label.text

    def get_subjects(self):
        return [btn.text for btn in self.layout_subj.children if btn.state == 'down']


class TeacherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pass_data = None
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.layout_teachers = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.layout_nav = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40))

        self.scroll_view_teachers = ScrollView(size_hint=(1, 1))

        self.button_back = Button(text='Back', size_hint=(None, 1), width=dp(70))
        self.button_continue = Button(text='Continue', size_hint=(None, 1), width=dp(70), pos_hint={'right':1})

        self.layout_teachers.bind(minimum_height=self.layout_teachers.setter('height'))
        self.button_back.bind(on_press=self.goto_prev_screen)
        self.button_continue.bind(on_press=self.goto_next_screen)

        add_widgets(
            self.button_back,
            Widget(size_hint=(1, 1)),
            self.button_continue,
            to=self.layout_nav
        )

        self.scroll_view_teachers.add_widget(self.layout_teachers)
        add_widgets(
            self.layout_nav,
            self.scroll_view_teachers,
            to=self.layout
        )
        self.add_widget(self.layout)

    def set_data(self, subjects, teachers, n_electives):
        subjs = [*subjects]
        for i in range(n_electives):
            subjs.append(f'elective{i+1}')

        self.layout_teachers.clear_widgets()
        for teacher in teachers:
            list_entry = ListEntry(teacher, subjs, spacing=10, size_hint_y=None, height=dp(30))
            self.layout_teachers.add_widget(list_entry)

    def goto_prev_screen(self, instance):
        self.manager.current = 'table'

    def goto_next_screen(self, instance):
        teachers = {}
        for i, child in enumerate(self.layout_teachers.children):
            if i == 0:
                continue
            teachers[child.get_text()] = child.get_subjects()
        print(teachers)
        self.pass_data(teachers)
        self.manager.current = 'wfc'

