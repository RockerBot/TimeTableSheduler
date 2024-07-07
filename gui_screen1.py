from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen

from gui_helpfull import add_colour, add_widgets


def add_to_list(input_elem, layout_list):
    if value := input_elem.text.strip():  # Ensure the value is not empty
        list_entry = ListEntry(value, spacing=10, size_hint_y=None, height=dp(30))
        layout_list.add_widget(list_entry)
        input_elem.text = ''  # Clear the input field


class ListEntry(BoxLayout):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.label = Label(text=text, size_hint=(0.8, 1))
        self.button = Button(text="—", size_hint=(None,None), size=(dp(50),dp(30)))

        self.button.bind(on_release=self.remove_element)

        self.add_widget(self.label)
        self.add_widget(self.button)
        add_colour(self, (1,0,0,1))

    def remove_element(self, instance):
        self.parent.remove_widget(self)

    def get_text(self):
        return self.label.text


class InputScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.pass_data = None
        self.layout_hz = BoxLayout(orientation='horizontal')
        self.layout_input = StackLayout(padding=10, spacing=30)
        self.layout_subjects = BoxLayout(orientation='vertical', spacing=10)
        self.layout_teachers = BoxLayout(orientation='vertical', spacing=10)
        self.layout_teacher_input = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint_y=None, height=dp(50))
        self.layout_subject_input = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint_y=None, height=dp(50))
        self.layout_teacher_list = BoxLayout(orientation='vertical', size_hint_y=None)
        self.layout_subject_list = BoxLayout(orientation='vertical', size_hint_y=None)

        default_input_args = {
            'input_filter': 'int',
            'size_hint_y': None,
            'height': dp(50)
        }
        self.input_sec = TextInput(hint_text='Enter number of sections', **default_input_args)
        self.input_day = TextInput(hint_text='Enter number of days', **default_input_args)
        self.input_slot = TextInput(hint_text='Enter number of slots', **default_input_args)
        self.input_elective = TextInput(hint_text='Enter number of electives', **default_input_args)
        self.input_teacher = TextInput(hint_text='Enter Teacher Name', size_hint=(0.65, 1))
        self.input_subject = TextInput(hint_text='Enter Subject Name', size_hint=(0.65, 1))

        self.scroll_view_teachers = ScrollView(size_hint=(1, 1))
        self.scroll_view_subjects = ScrollView(size_hint=(1, 1))

        self.button_add_teacher = Button(text='+', size_hint=(None, 1), width=dp(50))
        self.button_add_subject = Button(text='+', size_hint=(None, 1), width=dp(50))
        self.button_continue = Button(text='Continue', size_hint_y=None, height=dp(50))

        self.button_add_subject.bind(on_press=lambda x: add_to_list(self.input_subject, self.layout_subject_list))
        self.button_add_teacher.bind(on_press=lambda x: add_to_list(self.input_teacher, self.layout_teacher_list))
        self.button_continue.bind(on_press=self.goto_next_screen)

        self.layout_subject_list.bind(minimum_height=self.layout_subject_list.setter('height'))
        self.layout_teacher_list.bind(minimum_height=self.layout_teacher_list.setter('height'))

        # input layout
        add_widgets(
            self.input_sec,
            self.input_day,
            self.input_slot,
            self.input_elective,
            self.button_continue,
            to=self.layout_input
        )

        # subjects layout
        add_widgets(
            self.input_subject,
            self.button_add_subject,
            to=self.layout_subject_input
        )
        self.scroll_view_subjects.add_widget(self.layout_subject_list)
        add_widgets(
            self.layout_subject_input,
            self.scroll_view_subjects,
            to=self.layout_subjects
        )

        # teachers layout
        add_widgets(
            self.input_teacher,
            self.button_add_teacher,
            to=self.layout_teacher_input
        )
        self.scroll_view_teachers.add_widget(self.layout_teacher_list)
        add_widgets(
            self.layout_teacher_input,
            self.scroll_view_teachers,
            to=self.layout_teachers
        )

        # main horizontal layout
        add_widgets(
            self.layout_input,
            self.layout_subjects,
            self.layout_teachers,
            to=self.layout_hz
        )

        # add_colour(self.layout_input, (1, 1, 0, 1))
        # add_colour(self.layout_subjects, (1, 0, 1, 1))
        # add_colour(self.layout_teachers, (1, 1, 1, 1))
        # add_colour(self.scroll_view_subjects, (0, 1, 1, 1))

        self.add_widget(self.layout_hz)

    def goto_next_screen(self, instance):
        subject_list = self.layout_subject_list.children
        teacher_list = self.layout_teacher_list.children
        if len(subject_list) == 0 or len(teacher_list) == 0:
            return

        n_sections = self.input_sec.text.strip() or 10
        n_days = self.input_day.text.strip() or 5
        n_slots = self.input_slot.text.strip() or 9
        n_electives = self.input_elective.text.strip() or 2
        n_sections, n_days, n_slots, n_electives = int(n_sections), int(n_days), int(n_slots), int(n_electives)
        subjects = [child.get_text() for child in subject_list]
        teachers = [child.get_text() for child in teacher_list]
        print(n_sections, n_days, n_slots, n_electives, subjects, teachers)
        self.pass_data(n_sections, n_days, n_slots, n_electives, subjects, teachers)
        self.manager.current = 'table'
