from states import Teacher, Subject, Section, Table_T
from helpfull import print_tt, print_tt_stats, setup
import states
import WFC


def init_subjects(dims):
    subjects: list[Subject] = []
    subjects.extend(Subject.create('A', 6))
    subjects.extend(Subject.create('B', 6))
    subjects.extend(Subject.create('C', 6))
    subjects.extend(Subject.create('a', 2, min_blk_sz=2))
    subjects.extend(Subject.create('b', 2, min_blk_sz=2))
    return subjects

def init_faculty(dims, subjects):
    n_sections, n_days_per_week, n_slots_per_day = dims
    t1 = Teacher()
    t1.addSubjects({subjects[0], subjects[3],subjects[4]})
    t1.setAvailability(
        [[0] * n_slots_per_day 
         for _ in range(n_days_per_week)]
    )

    t2 = Teacher()
    t2.addSubjects({subjects[1], subjects[5], subjects[6]})
    t2.setAvailability(
        [[0] * n_slots_per_day 
         for _ in range(n_days_per_week)]
    )

    t3 = Teacher()
    t3.addSubjects({subjects[2],})
    t3.setAvailability(
        [[0] * n_slots_per_day 
         for _ in range(n_days_per_week)]
    )
    # for i in range(n_days_per_week):
    #     t3.availability[i][0] = 1

    teachers: list[Teacher] = [t1, t2, t3]
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


def main_loop(table, dims, subjects):
    collapseable_slot = (0,0,0)
    iteration_count = 0
    while True:
        collapseable_slot = WFC.iterate(table, dims, subjects)
        if collapseable_slot is None:
            print("The Wave Function has Collapsed")
            print_tt(table, dims)
            print_tt_stats(table, dims, states.groupings, states.block_subjects)
            break
        print_tt(table, dims, collapseable_slot)
        print(end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
        input("next?: ")

def main(n_sections = 3, n_days_per_week = 5, n_slots_per_day = 9):
    dims = n_sections, n_days_per_week, n_slots_per_day

    blocked_slots = [
        [0,0,0, 1,1,1, 0,0,0],
        [0,0,0, 1,1,1, 0,0,0],
        [1,1,1, 0,0,0, 1,1,1],
        [1,1,1, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
    ]

    # subjects and teachers initialization
    subjects: list[Subject] = init_subjects(dims)
    teachers: list[Teacher] = init_faculty(dims, subjects)
    sections: list[Section] = init_section(dims, subjects)
    print(subjects)
    print(teachers)
    print(sections)

    table: Table_T = setup(blocked_slots, dims, teachers, sections, subjects, states.groupings)

    WFC.init(table, dims, blocked_slots, teachers, subjects)

    print(states.groupings)    
    for teacher in teachers:
        print(teacher.availability)
    print(table[0][0][0].classes)
    print()
    print_tt(table, dims)
    print("="*100)

    main_loop(table, dims, subjects)



if __name__ == '__main__':
    # print(Subject.create("A",6,2,2))
    main()