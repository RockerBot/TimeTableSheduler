from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from gui_helpfull import add_widgets, add_colour


class CustomScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scrll_wdth = 0.1

    def on_scroll_start(self, touch, check_children=True):
        if self.collide_point(*touch.pos):
            if self.do_scroll_y and touch.button == 'scrolldown':
                self.scroll_y += self.scrll_wdth
                self.scroll_y = max(min(1, self.scroll_y), 0)
            elif self.do_scroll_y and touch.button == 'scrollup':
                self.scroll_y -= self.scrll_wdth
                self.scroll_y = max(min(1, self.scroll_y), 0)
        return super().on_scroll_start(touch, check_children)

    def set_scrl_wdth(self, wdth):
        self.scrll_wdth = wdth


class WFCScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.n_sections = None
        self.n_days = None
        self.n_slots = None
        self.n_electives = None
        self.subject_list = None
        self.teacher_dict = None

        self.pass_data = None
        self.sections = []
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.layout_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.layout_sections = BoxLayout(orientation='vertical', size_hint_y=None)

        self.button_back = Button(text='Back', size_hint=(None, 1), width=dp(70))
        self.button_continue = Button(text='Continue', size_hint=(None, 1), width=dp(70), pos_hint={'right': 1})

        self.scroll_view_sections = CustomScrollView(size_hint=(1, 1))

        self.layout_sections.bind(minimum_height=self.layout_sections.setter('height'))
        self.button_back.bind(on_press=self.goto_prev_screen)
        self.button_continue.bind(on_press=self.goto_next_screen)

        add_widgets(
            self.button_back,
            Widget(size_hint=(1, 1)),
            self.button_continue,
            to=self.layout_nav
        )
        self.scroll_view_sections.add_widget(self.layout_sections)
        add_widgets(
            self.layout_nav,
            self.scroll_view_sections,
            to=self.layout
        )
        self.add_widget(self.layout)
        # add_colour(self.scroll_view_sections, (1,0,0,1))

    def set_data(self, n_sections, n_days, n_slots, n_electives, subject_list, teacher_dict):
        self.layout_sections.clear_widgets()
        self.n_sections = n_sections
        self.n_days = n_days
        self.n_slots = n_slots
        self.n_electives = n_electives
        self.subject_list = subject_list
        self.teacher_dict = teacher_dict

        self.scroll_view_sections.set_scrl_wdth(0.5/n_sections)

        self.sections = []
        for i in range(n_sections):
            grid = GridLayout(cols=self.n_slots, size_hint=(1, None), height=dp(95*self.n_days + 20))
            for row in range(self.n_slots):
                for col in range(self.n_days):
                    btn = Button(text=f'R{row + 1}C{col + 1}', size_hint_y=None, height=dp(95))
                    grid.add_widget(btn)
            self.sections.append(grid)

            lbl = Label(text=f'section {i+1}', font_size='20sp', size_hint_y=None, height=dp(30))

            self.layout_sections.add_widget(lbl)
            self.layout_sections.add_widget(grid)

    def goto_prev_screen(self, instance):
        self.manager.current = 'teacher'

    def goto_next_screen(self, instance):
        return
        self.manager.current = 'output'

    def set_wfc_state(self, ndx, text):
        sec, day, slot = ndx
        self.sections[sec].children[-(day*self.n_slots + slot) - 1].text = text