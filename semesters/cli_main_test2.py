import time

from states2 import Teacher, Subject, Section, Table_T
from helpfull2 import print_to_csv, print_tt, print_tt_stats, print_tt_faculty, setup, input_file
import states2 as states
import WFC2 as WFC


def init_subjects(subjects_dict:dict) -> list[Subject]:
    subjects: list[Subject] = []
    for subj_name, subj_info in subjects_dict.items():
        subjs = Subject.create(
            subj_name, 
            subj_info[0], 
            min_blk_sz=subj_info[1]
        )
        subjects_dict[subj_name] = subjs
        subjects.extend(subjs)
    return subjects

def init_faculty(dims, faculty_dict:dict, subjects_dict:dict[str,list[Subject]], elec_faculty, faculty_availability_dict) -> list[Teacher]:
    n_sections, n_days_per_week, n_slots_per_day = dims

    teachers = []
    for faculty_name, faculty_info in faculty_dict.items():
        if len(faculty_info) == 0:
            for i in range(len(elec_faculty)):
                elec_faculty[i] -= {faculty_name}
            continue
        
        fac = Teacher(faculty_name)

        # replaces faculty name in the set with the faculty object
        for i in range(len(elec_faculty)):
            if faculty_name in elec_faculty[i]:
                elec_faculty[i] |= {fac}
                elec_faculty[i] -= {faculty_name}

        for subj_nm in faculty_info:
            fac.addSubjects(set(subjects_dict[subj_nm]))

        fac.setAvailability(
            faculty_availability_dict[faculty_name]
        )
        teachers.append(fac)
    return teachers

def init_section(dims5, subjects_dict, semester_subjects_list):
    n_sections, n_days_per_week, n_slots_per_day, n_semesters, n_sections_per_semester = dims5
    sections: list[Section] = []
    print(subjects_dict, "-"*25)
    for sem_i in range(n_semesters):
        subjs = []
        for subj_nm in semester_subjects_list[sem_i]:
            subjs.extend(subjects_dict[subj_nm])
        for _ in range(n_sections_per_semester[sem_i]):
            section = Section()
            section.addSubjects(subjs)
            section.setAvailability(
                [[0] * n_slots_per_day 
                for _ in range(n_days_per_week)]
            )
            sections.append(section)
    return sections


def main_loop(table, dims5, elective_slots, blocked_slots, semester_electives_list, faculty, subjects, callback):
    dims = dims5[0], dims5[1], dims5[2]
    collapseable_slot = (0,0,0)
    iteration_count = 0
    while True:
        try:
            collapseable_slot = WFC.iterate(table, dims, subjects, callback)
        except AssertionError as e:
            print(e)
            print_tt(table, dims5, elective_slots, blocked_slots, semester_electives_list)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            print_to_csv(table, dims, elective_slots, blocked_slots, faculty)
            raise e
        if collapseable_slot is None:
            print("The Wave Function has Collapsed")
            print_tt(table, dims5, elective_slots, blocked_slots, semester_electives_list)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            print_to_csv(table, dims, elective_slots, blocked_slots, faculty)
            break
        # print_tt(table, dims5, elective_slots, blocked_slots, semester_electives_list, collapseable_slot)
        # print(end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
        print(collapseable_slot, table[collapseable_slot[0]][collapseable_slot[1]][collapseable_slot[2]])
        # time.sleep(0.1)
        # input("next?: ")


def main(
        n_days_per_week, n_slots_per_day, n_semesters, n_sections_per_semester, #n_sections[0]
        n_subjects, n_faculty, #? not required
        n_electives, 
        subjects_dict, 
        electives, elective_slots, 
        faculty_dict:dict, 
        semester_subjects_list, semester_electives_list,
        blocked_slots, #blocked_slots[0]
        faculty_availability_dict,
        callback
    ):
    n_sections = sum(n_sections_per_semester)
    dims = n_sections, n_days_per_week, n_slots_per_day
    dims5 = *dims, n_semesters, n_sections_per_semester
    print("main")

    elec_faculty = []
    for i in range(n_electives):
        elec_name = f'e{i+1}'
        subjects_dict[elec_name] = list(electives[i][1])
        elecs = set(electives[i][0])
        elec_fac = set()
        for fac_nm in faculty_dict.keys():
            fac_subjs = set(faculty_dict[fac_nm])
            if len(elecs&fac_subjs):
                faculty_dict[fac_nm] = list(
                    (fac_subjs - elecs) #| {elec_name}
                )
                elec_fac.add(fac_nm) 
        elec_faculty.append(elec_fac)
        
    print(faculty_dict)
    # subjects and teachers initialization
    subjects: list[Subject] = init_subjects(subjects_dict)
    teachers: list[Teacher] = init_faculty(dims, faculty_dict, subjects_dict, elec_faculty, faculty_availability_dict)
    sections: list[Section] = init_section(dims5, subjects_dict, semester_subjects_list)
    print(subjects)
    print(teachers)
    print(sections)
    
    table: Table_T = setup(dims5,
        blocked_slots, elective_slots, elec_faculty,
        semester_electives_list, semester_subjects_list,
        teachers, sections, subjects,
        states.groupings
    )
    for i in range(n_days_per_week):
        for j in range(n_slots_per_day):
            for k_sem in range(n_semesters):
                for e_ndx in semester_electives_list[k_sem]:
                    if elective_slots[e_ndx][i][j]:
                        blocked_slots[k_sem][i][j] = 1
                        break

    WFC.init(table, dims, n_semesters, n_sections_per_semester, blocked_slots, teachers, subjects, callback)
    
    print(states.groupings)
    for cls,val in states.groupings.items():
        print(f'{chr(65+cls[0])}{cls[1]}: {val}', end=', ')
    print()

    for teacher in teachers:
        print(teacher.availability, teacher.name)
    print(table[0][0][0].classes)
    print()
    print_tt(table, dims5, elective_slots, blocked_slots, semester_electives_list)
    print("="*100)

    main_loop(table, dims5, elective_slots, blocked_slots, semester_electives_list, teachers, subjects, callback)


if __name__ == '__main__':
    import os

    # file_name = './semesters/config2.txt'
    file_name = 'config2.txt'
    # file_name = 'config_test.txt'
    assert file_name in os.listdir(), f"file not present {os.listdir()}"
    main(*input_file(file_name), lambda x:None)
