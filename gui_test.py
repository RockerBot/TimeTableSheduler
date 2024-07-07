import threading

from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from gui_screen1 import InputScreen
from gui_screen2 import TableScreen
from gui_screen3 import TeacherScreen
from gui_screen4 import WFCScreen

# from states import Teacher, Subject, Section, Table_T
# from helpfull import print_tt, print_tt_stats, print_tt_faculty, setup
# import states
# import WFC

n_sections, n_days, n_slots, n_electives = 1, 1, 1, 1
subject_list = []
teacher_list = []
elective_slots = []
blocked_slots = []
teacher_dict = {}


def lloopp():
    while True:
        print("\r_-_", end='')


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        input_screen = InputScreen(name='input')
        table_screen = TableScreen(name='table')
        teacher_screen = TeacherScreen(name='teacher')
        wfc_screen = WFCScreen(name='wfc')

        def pass_data_input(sec, day, slot, elec, subjects, teachers):
            global n_sections, n_days, n_slots, n_electives, subject_list, teacher_list
            n_sections, n_days, n_slots, n_electives = sec, day, slot, elec
            subject_list = subjects
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
            wfc_screen.set_data(n_sections, n_days, n_slots, n_electives, subject_list, teacher_dict)

        input_screen.pass_data = pass_data_input
        table_screen.pass_data = pass_data_table
        teacher_screen.pass_data = pass_data_teacher

        sm.add_widget(input_screen)
        sm.add_widget(table_screen)
        sm.add_widget(teacher_screen)
        sm.add_widget(wfc_screen)

        return sm


if __name__ == '__main__':
    MyApp().run()
    print("sssssssssssssssssssssssssssssssss")



# def init_subjects(subjects_dict: dict) -> list[Subject]:
#     subjects: list[Subject] = []
#     for subj_name, subj_info in subjects_dict.items():
#         subjs = Subject.create(
#             subj_name,
#             subj_info[0],
#             min_blk_sz=subj_info[1]
#         )
#         subjects_dict[subj_name] = subjs
#         subjects.extend(subjs)
#     return subjects
#
#
# def init_faculty(dims, faculty_dict: dict, subjects_dict: dict[str, list[Subject]], elec_faculty) -> tuple[
#     list[Teacher], list[set[Teacher]]]:
#     n_sections, n_days_per_week, n_slots_per_day = dims
#
#     teachers = []
#     for faculty_name, faculty_info in faculty_dict.items():
#         if len(faculty_info) == 0:
#             for i in range(len(elec_faculty)):
#                 elec_faculty[i] -= {faculty_name}
#             continue
#
#         fac = Teacher(faculty_name)
#
#         # replaces faculty name in the set with the faculty object
#         for i in range(len(elec_faculty)):
#             if faculty_name in elec_faculty[i]:
#                 elec_faculty[i] |= {fac}
#                 elec_faculty[i] -= {faculty_name}
#
#         for subj_nm in faculty_info:
#             fac.addSubjects(set(subjects_dict[subj_nm]))
#
#         fac.setAvailability(
#             [[0] * n_slots_per_day
#              for _ in range(n_days_per_week)]
#         )
#         teachers.append(fac)
#     return teachers
#
#
# def init_section(dims, subjects):
#     n_sections, n_days_per_week, n_slots_per_day = dims
#     sections: list[Section] = []
#     for _ in range(n_sections):
#         section = Section()
#         section.addSubjects(subjects)
#         section.setAvailability(
#             [[0] * n_slots_per_day
#              for _ in range(n_days_per_week)]
#         )
#         sections.append(section)
#     return sections
#
#
# def main_loop(table, dims, elective_slots, blocked_slots, faculty, subjects):
#     collapseable_slot = (0, 0, 0)
#     iteration_count = 0
#     while True:
#         try:
#             collapseable_slot = WFC.iterate(table, dims, subjects)
#         except AssertionError as e:
#             print(e)
#             print_tt(table, dims, elective_slots, blocked_slots)
#             print_tt_stats(table, dims, states.groupings, states.block_subjects)
#             print_tt_faculty(table, dims, faculty)
#             raise e
#         if collapseable_slot is None:
#             print("The Wave Function has Collapsed")
#             print_tt(table, dims, elective_slots, blocked_slots)
#             print_tt_stats(table, dims, states.groupings, states.block_subjects)
#             print_tt_faculty(table, dims, faculty)
#             break
#         # print_tt(table, dims, elective_slots, blocked_slots, collapseable_slot)
#         # print(end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
#         print(collapseable_slot, table[collapseable_slot[0]][collapseable_slot[1]][collapseable_slot[2]])
#         # input("next?: ")
#
#
#
#
#
# def main():
#     (n_sections, n_days_per_week, n_slots_per_day,
#      n_subjects, n_faculty,  # ? not required
#      n_electives,
#      subjects_dict,
#      electives, elective_slots,
#      faculty_dict,
#      blocked_slots
#      ) = input_file()
#     dims = n_sections, n_days_per_week, n_slots_per_day
#
#     elec_faculty = []
#     for i in range(n_electives[0]):
#         elec_name = f'e{i + 1}'
#         subjects_dict[elec_name] = list(n_electives[1:])
#         elecs = set(electives[i])
#         elec_fac = set()
#         for fac_nm in faculty_dict.keys():
#             fac_subjs = set(faculty_dict[fac_nm])
#             if len(elecs & fac_subjs):
#                 faculty_dict[fac_nm] = list(
#                     (fac_subjs - elecs)  # | {elec_name}
#                 )
#                 elec_fac.add(fac_nm)
#         elec_faculty.append(elec_fac)
#
#     print(faculty_dict)
#     # subjects and teachers initialization
#     subjects: list[Subject] = init_subjects(subjects_dict)
#     teachers: list[Teacher] = init_faculty(dims, faculty_dict, subjects_dict, elec_faculty)
#     sections: list[Section] = init_section(dims, subjects)
#     print(subjects)
#     print(teachers)
#     print(sections)
#
#     table: Table_T = setup(
#         dims,
#         blocked_slots, elective_slots, elec_faculty,
#         teachers, sections, subjects,
#         states.groupings
#     )
#     for i in range(n_days_per_week):
#         for j in range(n_slots_per_day):
#             for elec in elective_slots:
#                 if elec[i][j]:
#                     blocked_slots[i][j] = 1
#                     break
#
#     WFC.init(table, dims, blocked_slots, teachers, subjects)
#
#     print(states.groupings)
#     for cls, val in states.groupings.items():
#         print(f'{chr(65 + cls[0])}{cls[1]}: {val}', end=', ')
#     print()
#
#     for teacher in teachers:
#         print(teacher.availability, teacher.name)
#     print(table[0][0][0].classes)
#     print()
#     print_tt(table, dims, elective_slots, blocked_slots)
#     print("=" * 100)
#
#     main_loop(table, dims, elective_slots, blocked_slots, teachers, subjects)
#
#
# if __name__ == '__main__':
#     # input_file()
#     main()
