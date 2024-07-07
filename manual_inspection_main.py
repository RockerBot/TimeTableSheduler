from states import Teacher, Subject, Section, Table_T
from helpfull import print_tt, print_tt_stats, print_tt_faculty, setup
import states
import WFC
from cli_main_test import init_faculty, init_subjects, init_section, input_file

def iterate(table, dims, subjects):    
    ndx = eval(input("Enter collapsable state: "))
    if ndx is None:
        return None
    
    sec, day, slot = ndx
    min_cls = WFC.get_min_cls(table[sec][day][slot], slot)
    WFC.collapse_state(table, dims, ndx, min_cls, subjects)

    if min_cls != (0,0):
        WFC.propagate_constraints(table, dims, ndx, subjects)
    return ndx



def main_loop(table, dims, elective_slots, blocked_slots, faculty, subjects):
    collapseable_slot = (0,0,0)
    iteration_count = 0
    while True:
        try:
            collapseable_slot = iterate(table, dims, subjects)
        except AssertionError as e:
            print(e)
            print_tt(table, dims, elective_slots, blocked_slots)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            raise e
        if collapseable_slot is None:
            print("The Wave Function has Collapsed")
            print_tt(table, dims, elective_slots, blocked_slots)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            print_tt_faculty(table, dims, faculty)
            break
        print_tt(table, dims, elective_slots, blocked_slots, collapseable_slot)
        print(end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
        print(collapseable_slot, table[collapseable_slot[0]][collapseable_slot[1]][collapseable_slot[2]])


def main():    
    (n_sections, n_days_per_week, n_slots_per_day, 
        n_subjects, n_faculty, #? not required
        n_electives, 
        subjects_dict, 
        electives, elective_slots, 
        faculty_dict, 
        blocked_slots
    ) = input_file()
    dims = n_sections, n_days_per_week, n_slots_per_day

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

    WFC.init(table, dims, blocked_slots, teachers, subjects)
    
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

    main_loop(table, dims, elective_slots, blocked_slots, teachers, subjects)


if __name__ == '__main__':
    # input_file()
    main()
