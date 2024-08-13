from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView

from gui_helpfull import add_widgets, add_colour

default_btn_args = {
    'size_hint': (None, 1),
    'width': dp(70)
}


def update_text_size(instance, value):
    instance.text_size = instance.size


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


class IndexButton(Button):
    def __init__(self, val, **kwargs):
        super().__init__(**kwargs)
        self.index = val


class SellectState(Popup):
    def __init__(self, select_callback, teach_dict, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Select a Faculty member'
        self.size_hint = (0.9, 0.9)
        self.teach_dict = teach_dict
        self.select_callback = select_callback
        self.teach = ''

        self.layout = BoxLayout(orientation='vertical')
        self.layout_list = BoxLayout(orientation='vertical')

        self.scroll_view = ScrollView(size_hint=(1, 1))

        cancel_button = Button(text='Cancel', size_hint_y=None, height=50)

        cancel_button.bind(on_press=self.dismiss)
        for teach in teach_dict.keys():
            btn = Button(text=teach)
            btn.bind(on_press=self.select_teacher)
            self.layout_list.add_widget(btn)
        self.scroll_view.add_widget(self.layout_list)
        self.layout.add_widget(self.scroll_view)
        self.layout.add_widget(cancel_button)
        self.add_widget(self.layout)

    def select_teacher(self, instance):
        self.teach = instance.text
        self.layout_list.clear_widgets()
        for subj in self.teach_dict[instance.text]:
            btn = Button(text=subj)
            btn.bind(on_press=self.select_subject)
            self.layout_list.add_widget(btn)

    def select_subject(self, instance):
        self.select_callback(f"{self.teach}, {instance.text}")
        self.dismiss()


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
        self.run_algo = None
        self.modified_states = []
        self.sections = []
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.layout_nav = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        self.layout_sections = BoxLayout(orientation='vertical', size_hint_y=None)
        self.layout_options = BoxLayout(orientation='horizontal', spacing=10)

        self.button_back = Button(text='Back', **default_btn_args)
        self.button_continue = Button(text='Continue', disabled=True, **default_btn_args)
        self.button_generate = Button(text='Generate', **default_btn_args)

        self.scroll_view_sections = CustomScrollView(size_hint=(1, 1))

        self.layout_sections.bind(minimum_height=self.layout_sections.setter('height'))
        self.button_back.bind(on_press=self.goto_prev_screen)
        self.button_continue.bind(on_press=self.goto_next_screen)
        self.button_generate.bind(on_press=self.run_wfc)

        self.layout_options.add_widget(self.button_generate)

        add_widgets(
            self.button_back,
            self.layout_options,
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

    def set_data(self, n_sections, n_days, n_slots, n_electives, subject_list, teacher_dict, callback):
        self.layout_sections.clear_widgets()
        self.n_sections = n_sections
        self.n_days = n_days
        self.n_slots = n_slots
        self.n_electives = n_electives
        self.subject_list = subject_list
        self.teacher_dict = teacher_dict
        self.run_algo = callback
        self.modified_states = []

        self.scroll_view_sections.set_scrl_wdth(0.5/n_sections)

        self.sections = []
        for i in range(n_sections):
            grid = GridLayout(cols=self.n_slots, size_hint=(1, None), height=dp(95*self.n_days + 20))
            for col in range(self.n_days):
                for row in range(self.n_slots):
                    btn = IndexButton(
                        (i, col, row), text='',
                        size_hint_y=None, height=dp(95), padding=5,
                        halign='center', valign='middle'
                    )
                    btn.text_size = btn.size
                    btn.bind(size=update_text_size)
                    btn.bind(on_press=self.select_state)
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

    def run_wfc(self, instance):
        print("running wfc")
        self.run_algo(self)

    def set_states(self, modified_states):
        print("---------------------------------")
        for ndx, st in modified_states:
            self.set_wfc_state(ndx, str(st))

    def set_wfc_state(self, ndx, text):
        sec, day, slot = ndx
        self.sections[sec].children[-(day*self.n_slots + slot) - 1].text = text

    def select_state(self, instance):
        SellectState(lambda x:self.set_text(instance,x), self.teacher_dict).open()

    def set_text(self, instance, text):
        instance.text = text
        self.modified_states.append((instance.index, text))