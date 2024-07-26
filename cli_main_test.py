import time

from states import Teacher, Subject, Section, Table_T
from helpfull import print_to_csv, print_tt, print_tt_stats, print_tt_faculty, setup
import states
import WFC


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

def init_faculty(dims, faculty_dict:dict, subjects_dict:dict[str,list[Subject]], elec_faculty) -> list[Teacher]:
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
            [[0] * n_slots_per_day 
            for _ in range(n_days_per_week)]
        )
        teachers.append(fac)
    return teachers

def init_section(dims, subjects):
    n_sections, n_days_per_week, n_slots_per_day = dims
    sections: list[Section] = []
    for _ in range(n_sections):
        section = Section()
        section.addSubjects(subjects)
        section.setAvailability(
            [[0] * n_slots_per_day 
             for _ in range(n_days_per_week)]
        )
        sections.append(section)
    return sections


def main_loop(table, dims, elective_slots, blocked_slots, faculty, subjects, callback):
    collapseable_slot = (0,0,0)
    iteration_count = 0
    while True:
        try:
            collapseable_slot = WFC.iterate(table, dims, subjects, callback)
        except AssertionError as e:
            print(e)
            print_tt(table, dims, elective_slots, blocked_slots)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            print_to_csv(table, dims, elective_slots, blocked_slots, faculty)
            raise e
        if collapseable_slot is None:
            print("The Wave Function has Collapsed")
            print_tt(table, dims, elective_slots, blocked_slots)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            print_to_csv(table, dims, elective_slots, blocked_slots, faculty)
            break
        print_tt(table, dims, elective_slots, blocked_slots, collapseable_slot)
        print(end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
        print(collapseable_slot, table[collapseable_slot[0]][collapseable_slot[1]][collapseable_slot[2]])
        # time.sleep(0.1)
        # input("next?: ")


def input_file(file_name):
    with open(file_name, 'r') as file:
        n_sections      = int(file.readline().split('=')[-1])
        n_days_per_week = int(file.readline().split('=')[-1])
        n_slots_per_day = int(file.readline().split('=')[-1])
        n_subjects      = int(file.readline().split('=')[-1])
        n_faculty       = int(file.readline().split('=')[-1])

        n_electives     = (*map(int,file.readline().split('=')[-1].split(',')),)
        
        subjects_dict = {}
        for _ in range(n_subjects):
            subj_name, subj_info= map(str.strip, file.readline().strip().split('='))
            subjects_dict[subj_name] = [*map(int, subj_info.split(','))]
        
        electives = []
        elective_slots = []
        for i in range(n_electives[0]):
            n_subjs = int(file.readline().split('=')[-1])
            electives.append(
                [file.readline().strip() for _ in range(n_subjs)]
            )
            elective_slots.append(
                [ [*map(int,file.readline().strip())] for _ in range(n_days_per_week)]
            )
        
        faculty_dict = {}
        for i in range(n_faculty):
            faculty, subjs = map(str.strip, file.readline().split('='))
            faculty_dict[faculty] =[*map(str.strip, subjs.split(','))]
        
        blocked_slots = [ [*map(int,file.readline().strip())] for _ in range(n_days_per_week)]

    print(f"""
        {n_sections=}
        {n_days_per_week=}
        {n_slots_per_day=}
        {n_subjects=}
        {n_faculty=}
        {n_electives=}

        {subjects_dict=}
        {electives=}
    """)
    for elec_slots in elective_slots:
        print('-'*n_slots_per_day)
        for row in elec_slots:
            print(''.join(map(str,row)))
    for k,v in faculty_dict.items():
        print(k,v)    
    for row in blocked_slots:
        print(''.join(map(str,row)))
    
    return (
        n_sections, 
        n_days_per_week, 
        n_slots_per_day, 
        n_subjects, 
        n_faculty, 
        n_electives, 
        subjects_dict, 
        electives,
        elective_slots, 
        faculty_dict, 
        blocked_slots
    )


def main(n_sections, n_days_per_week, n_slots_per_day, 
        n_subjects, n_faculty, #? not required
        n_electives, 
        subjects_dict, 
        electives, elective_slots, 
        faculty_dict, 
        blocked_slots,
        callback
    ):
    dims = n_sections, n_days_per_week, n_slots_per_day
    print("main")
    elec_faculty = []
    for i in range(n_electives[0]):
        elec_name = f'e{i+1}'
        subjects_dict[elec_name] = list(n_electives[1:])
        elecs = set(electives[i])
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
    teachers: list[Teacher] = init_faculty(dims, faculty_dict, subjects_dict, elec_faculty)
    sections: list[Section] = init_section(dims, subjects)
    print(subjects)
    print(teachers)
    print(sections)
    
    table: Table_T = setup(
        dims,
        blocked_slots, elective_slots, elec_faculty,
        teachers, sections, subjects,
        states.groupings
    )
    for i in range(n_days_per_week):
        for j in range(n_slots_per_day):
            for elec in elective_slots:
                if elec[i][j]:
                    blocked_slots[i][j] = 1
                    break

    WFC.init(table, dims, blocked_slots, teachers, subjects, callback)
    
    print(states.groupings)
    for cls,val in states.groupings.items():
        print(f'{chr(65+cls[0])}{cls[1]}: {val}', end=', ')
    print()

    for teacher in teachers:
        print(teacher.availability, teacher.name)
    print(table[0][0][0].classes)
    print()
    print_tt(table, dims, elective_slots, blocked_slots)
    print("="*100)

    main_loop(table, dims, elective_slots, blocked_slots, teachers, subjects, callback)


if __name__ == '__main__':
    import os

    # file_name = 'config1.txt'
    file_name = 'config_test.txt'
    assert file_name in os.listdir(), "file not present"
    main(*input_file(file_name), lambda x:None)
