import threading
import time

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from gui_screen1 import InputScreen
from gui_screen2 import TableScreen
from gui_screen3 import TeacherScreen
from gui_screen4 import WFCScreen

import cli_main_test

n_sections, n_days, n_slots, n_electives = 1, 1, 1, 1
subject_list = []
teacher_list = []
elective_slots = []
blocked_slots = []
subject_dict = {}
teacher_dict = {}
elective_nms = []
# gui_obj = None

# def start_algo(self):
#     global gui_obj
#     gui_obj = None


def run_algo(self):
    # while gui_obj is None:
    #     time.sleep(1)
    if len(elective_nms):
        for i in range(n_electives):
            elective_nms[i].append(f'elective{i+1}')
    else:
        for i in range(n_electives):
            elective_nms.append([f'elective{i+1}'])

    print(
        (n_sections, n_days, n_slots),
        (len(subject_list), len(teacher_list)),
        (n_electives, 6, 3),
        subject_dict,
        [elective_nms[i] for i in range(n_electives)]
    )
    print(elective_slots)
    print(teacher_dict)
    print(blocked_slots)
    # input("???")

    thrd = threading.Thread(target=cli_main_test.main, args=(
        n_sections, n_days, n_slots,
        len(subject_list), len(teacher_list),
        (n_electives, 6, 3),
        subject_dict,
        [elective_nms[i] for i in range(n_electives)],
        elective_slots,
        teacher_dict,
        blocked_slots,
        self.set_states
    ))
    thrd.start()
    pass


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        input_screen = InputScreen(cli_main_test.input_file, name='input')
        table_screen = TableScreen(name='table')
        teacher_screen = TeacherScreen(name='teacher')
        wfc_screen = WFCScreen(name='wfc')

        def pass_data_input(sec, day, slot, elec, subjects, subject_d, teachers):
            global n_sections, n_days, n_slots, n_electives, subject_list, subject_dict, teacher_list
            n_sections, n_days, n_slots, n_electives = sec, day, slot, elec
            subject_list = subjects
            subject_dict = subject_d
            teacher_list = teachers
            table_screen.set_data(n_sections, n_days, n_slots, n_electives, subject_list, teacher_list)

        def pass_data_table(electives, blocked):
            global elective_slots, blocked_slots
            elective_slots = electives
            blocked_slots = blocked
            teacher_screen.set_data(subject_list, teacher_list, n_electives)

        def pass_data_teacher(teachers):
            global teacher_dict
            teacher_dict = teachers
            wfc_screen.set_data(n_sections, n_days, n_slots, n_electives, subject_list, teacher_dict, run_algo)

        def pass_all_data(sec, day, slot, n_subject, n_faculty, elec,
                          subject_d, electives, slots_elective, teacher_d,  slots_blocked):
            global n_sections, n_days, n_slots, n_electives, \
                subject_list, subject_dict, \
                teacher_list, teacher_dict, \
                elective_slots, blocked_slots, elective_nms
            elective_nms = electives
            pass_data_input(sec, day, slot, elec[0], [*subject_d.keys()], subject_d, [*teacher_dict.keys()])
            pass_data_table(slots_elective, slots_blocked)
            pass_data_teacher(teacher_d)

        input_screen.pass_data = pass_data_input
        table_screen.pass_data = pass_data_table
        teacher_screen.pass_data = pass_data_teacher

        input_screen.pass_all_data = pass_all_data

        sm.add_widget(input_screen)
        sm.add_widget(table_screen)
        sm.add_widget(teacher_screen)
        sm.add_widget(wfc_screen)

        return sm


if __name__ == '__main__':
    # threading.Thread(target=run_algo).start()

    MyApp().run()
    print("Program Finished Execution")
