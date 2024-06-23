'''
inputs
- faculty, semester, section
- LAB, elective, special topic blocks

'''

'''
- faculty can be at one place at one time
- faculty has n first classes for n subjects
- max 4 sessions for a faculty per day
- atleast 1 session break between 2 theory blocks

- max 2 theory per day


- max 2 consecutive sessions per subject
- faculty can have max 2lab, or max 1 theory on the same day as their special topic

- Wed afternoon no class
'''

import random
import numpy as np
import typing

Group_T = typing.Tuple['Teacher', 'Subject']
GroupID_T = typing.Tuple[int,int]
Table_T = list[list[list['SuperState']]]

ENTROPY_MAX = 1_000_000_000

def print_tt(tt, n_sections, n_days_per_week, n_slots_per_day):
    padding = 20#10  # len(''.join(subjects.keys()))+len(str(MAX_ENTROPY))+3-3
    for section_i in range(n_sections):
        print('SECTION', section_i + 1)
        for day_j in range(n_days_per_week):
            print("day", day_j, end=':  ')
            for slot_k in range(n_slots_per_day):
                state = tt[section_i][day_j][slot_k]
                clr = ('\033[39m', '\033[92m')[isinstance(state, CollapsedState)]
                print(f"{clr}{state:-{padding}}\033[39m", end=' ')
            print()

def print_tt_stats(tt, n_sections, n_days_per_week, n_slots_per_day):
    for section_i in range(n_sections):
        sec_cls = {}
        for day_j in range(n_days_per_week):
            for slot_k in range(n_slots_per_day):
                state = tt[section_i][day_j][slot_k]
                if not isinstance(state, CollapsedState):
                    continue
                sec_cls[state.cls] = sec_cls.get(state.cls, 0) + 1
        print(sec_cls)


def get_entropy(cls: GroupID_T):
    global groupings
    if cls == (0,0):
        return ENTROPY_MAX
    
    grouping = groupings[cls]
    return grouping[0].score * grouping[1].score


class Subject:
    ID = 1 # subject's ID starts from 1, 0 is reserved
    subject_list: list['Subject'] = []

    def __init__(self, name, total_slots_per_week ,min_blk_sz = 1, max_blk_sz = 2):
        self.id = Subject.ID
        Subject.ID += 1
        Subject.subject_list.append(self)
        self.name = name
        self.total_slots_per_week = total_slots_per_week
        self.score = total_slots_per_week / min_blk_sz
        self.min_blk_sz = min_blk_sz
        self.max_blk_sz = max_blk_sz
        self.groupIDs: set[GroupID_T] = set()
    
    def __hash__(self) -> int:
        return hash(f'Subject{self.id}')
    
    def __repr__(self):
        return f'{self.name}'#[{self.min_blk_sz}-{self.max_blk_sz}]'
    
    @classmethod
    def at(cls, index) -> 'Subject':
        return cls.subject_list[index-1]


class Teacher:
    ID = 1 # teacher's ID starts from 1, 0 is reserved
    teacher_list: list['Teacher'] = []

    def __init__(self):
        self.id = Teacher.ID
        Teacher.ID += 1
        Teacher.teacher_list.append(self)
        self.availability = None
        self.score = None
        self.subjects: set[Subject] = set()
        self.groupIDs: set[GroupID_T] = set()
            
    def setAvailability(self, availability):
        self.availability = availability

    def addSubjects(self, subjects: set[Subject]):
        self.subjects |= subjects

    def __hash__(self) -> int:
        return hash(f'Teacher{self.id}')
    
    def __repr__(self):
        return f'T{self.id}'#[{self.subjects}]'

    @classmethod
    def at(cls, index) -> 'Teacher':
        return cls.teacher_list[index-1]

class Section:
    ID = 1
    section_list: list['Section'] = []

    def __init__(self) -> None:
        self.id = Section.ID
        Section.ID += 1
        Section.section_list.append(self)

        self.availability = None
        self.subjects: dict[int,int] = {}
    
    def setAvailability(self, availability):
        self.availability = availability

    def addSubjects(self, subjects: list[Subject]):
        for subject in subjects:
            self.subjects[subject.id] = 0

    @classmethod
    def at(cls, index) -> 'Section':
        return cls.section_list[index]


class State:
    def __init__(self, ) -> None:
        self.entropy = np.inf

    def __repr__(self):
        return f'State[{self.entropy}]'

    def __format__(self, format_spec):
        out: str = repr(self)
        if format_spec[0] in '_-':
            return out.center(int(format_spec[1:]))
        return f'{out:{format_spec}}'


class CollapsedState(State):
    def __init__(self, cls: GroupID_T, /):
        self.cls: GroupID_T = cls
        super().__init__()
        self.entropy = get_entropy(cls)

    def __hash__(self):
        return hash(f'CState[{self.cls}]')

    def __repr__(self):
        # return str(self.ID)
        return f"{groupings[self.cls]}"  # f"{self.cls}=[{self.entropy}]"


class SuperState(State):
    ID = 0

    def __init__(self, classes: set[GroupID_T], multiplier=1) -> None:
        self.classes: set[GroupID_T] = classes
        super().__init__()
        self.ID = SuperState.ID
        SuperState.ID += 1
        self.multiplier = multiplier
        self.calc_entropy()

    def calc_entropy(self) -> None:
        self.entropy = sum(get_entropy(cls) for cls in self.classes) * self.multiplier

    def __hash__(self):
        return hash('SState''_'.join(self.classes))

    def __repr__(self):
        # return str(self.ID)        
        return '_'.join(
            f'{cls[0]}{cls[1]}' for cls in self.classes
        ) #+ f"_[{self.entropy}]"


def get_min_cls(state: SuperState) -> GroupID_T:
    min_cls = None
    min_entropy = np.inf
    for cls in state.classes:
        if (cls_entropy := get_entropy(cls)) < min_entropy:
            min_entropy = cls_entropy
            min_cls = cls
    return min_cls


def get_collapsable_state(table:Table_T, n_sections, n_days_per_week, n_slots_per_day) -> tuple[int,int,int]:
    min_entropy = np.inf
    for sec_i in range(n_sections):
        for day_j in range(n_days_per_week):
            for slot_k in range(n_slots_per_day):
                if not isinstance(table[sec_i][day_j][slot_k], SuperState):
                    continue
                if table[sec_i][day_j][slot_k].entropy <= min_entropy:
                    min_entropy = table[sec_i][day_j][slot_k].entropy
    
    candidate_states = []
    for sec_i in range(n_sections):
        for day_j in range(n_days_per_week):
            for slot_k in range(n_slots_per_day):
                if not isinstance(table[sec_i][day_j][slot_k], SuperState):
                    continue
                if table[sec_i][day_j][slot_k].entropy == min_entropy:
                    candidate_states.append(
                        (sec_i,day_j,slot_k)
                    )
    
    if len(candidate_states) == 0:
        return None
    
    return random.choice(candidate_states)


def first_slot_diff_subj(table, dims, ndx, collapsed_state:CollapsedState):
    """Every day must start with a different subject"""
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    if slot > 0: return
    invalidIDs = {collapsed_state.cls}
    for d in range(n_days_per_week):
        state = table[sec][d][slot]
        if not isinstance(state, SuperState):
            continue
        state.classes-= invalidIDs
        state.calc_entropy()

def one_teacher_per_subject_per_section(table: Table_T, dims, ndx, collapsed_state: CollapsedState):
    """For a particular subject for a particular section, only one teacher
        ie two teachers can not teach the same subject for the same section
    """
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    subjectID = collapsed_state.cls[1]
    invalidIDs = Subject.at(subjectID).groupIDs - {collapsed_state.cls}
    for d in range(n_days_per_week):
        for p in range(n_slots_per_day):
            state = table[sec][d][p]
            if not isinstance(state, SuperState):
                continue
            state.classes-= invalidIDs
            state.calc_entropy()

def at_one_place_at_one_time(table: Table_T, dims, ndx, collapsed_state: CollapsedState):
    """faculty can not teach two different sections at the same time slot"""
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    facultyID = collapsed_state.cls[0]
    invalidIDs = Teacher.at(facultyID).groupIDs
    for s in range(n_sections):
        state = table[s][day][slot]
        if not isinstance(state, SuperState):
            continue
        # is a SuperState
        state.classes -= invalidIDs
        state.calc_entropy()

def max_subject_slots_per_week(table, dims, ndx:tuple[int,int,int], collapsed_state:CollapsedState):
    "each subject is allowed a certain number of slots per week"
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    subjectID = collapsed_state.cls[1]
    subject = Subject.at(subjectID)
    invalidIDs = subject.groupIDs
    if Section.at(sec).subjects[subjectID] == subject.total_slots_per_week:
        for d in range(n_days_per_week):
            for p in range(n_slots_per_day):
                state = state = table[sec][d][p]
                if not isinstance(state, SuperState):
                    continue
                # is a SuperState
                state.classes -= invalidIDs
                state.calc_entropy()

def min_block_slots(table, dims, ndx, collapsed_state: CollapsedState):
    "subjects requiring group slots ie consecutive slots"
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    subjectID = collapsed_state.cls[1]
    subject = Subject.at(subjectID)
    if slot > 0:
        slot - 1
    # for p in range(n_slots_per_day)

def hard_constraints(table: Table_T, dims, ndx):
    sec, day, slot = ndx
    collapsed_state = table[sec][day][slot]
    assert isinstance(collapsed_state, CollapsedState)

    one_teacher_per_subject_per_section(table, dims, ndx, collapsed_state)
    at_one_place_at_one_time(table, dims, ndx, collapsed_state)
    max_subject_slots_per_week(table, dims, ndx, collapsed_state)
    # min_block_slots(table, dims, ndx, collapsed_state)

def soft_constraints(table: Table_T, dims, ndx):
    sec, day, slot = ndx
    collapsed_state = table[sec][day][slot]
    assert isinstance(collapsed_state, CollapsedState)
    first_slot_diff_subj(table, dims, ndx, collapsed_state)

def propagate_constraints(table, dims, ndx):
    hard_constraints(table, dims, ndx)
    soft_constraints(table, dims, ndx)

def iterate(table, n_sections, n_days_per_week, n_slots_per_day):
    sec, day, slot = get_collapsable_state(table, n_sections, n_days_per_week, n_slots_per_day)
    min_cls = get_min_cls(table[sec][day][slot])
    # collapse_state
    sec_subj = Section.at(sec).subjects
    sec_subj[min_cls[1]] = sec_subj.get(min_cls[1],0) + 1
    table[sec][day][slot] = CollapsedState(min_cls)


    if min_cls != (0,0):
        propagate_constraints(table, (n_sections, n_days_per_week, n_slots_per_day), (sec, day, slot))

def init_subjects(n_sections, n_days_per_week, n_slots_per_day):
    s1 = Subject('A', 6)
    s2 = Subject('B', 6)
    s3 = Subject('C', 6)
    s4 = Subject('a', 2, min_blk_sz=2)
    s5 = Subject('b', 2, min_blk_sz=2)

    subjects: list[Subject] = [s1,s2,s3,s4,s5]
    return subjects

def init_faculty(n_sections, n_days_per_week, n_slots_per_day, subjects):
    t1 = Teacher()
    t1.addSubjects({subjects[0], subjects[3]})
    t1.setAvailability(
        [[0] * n_slots_per_day 
         for _ in range(n_days_per_week)]
    )

    t2 = Teacher()
    t2.addSubjects({subjects[1], subjects[4]})
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

    teachers: list[Teacher] = [t1, t2, t3]
    return teachers

def init_section(n_sections, n_days_per_week, n_slots_per_day, subjects):
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

def main():
    global groupings
    n_sections = 3
    n_days_per_week = 5
    n_slots_per_day = 9

    blocked_slots = [
        [0,0,0, 1,1,1, 0,0,0],
        [0,0,0, 1,1,1, 0,0,0],
        [1,1,1, 0,0,0, 1,1,1],
        [1,1,1, 0,0,0, 0,0,0],
        [0,0,0, 0,0,0, 0,0,0],
    ]
    
    # subjects and teachers initialization
    subjects: list[Subject] = init_subjects(n_sections, n_days_per_week, n_slots_per_day)
    teachers: list[Teacher] = init_faculty(n_sections, n_days_per_week, n_slots_per_day, subjects)
    sections: list[Section] = init_section(n_sections, n_days_per_week, n_slots_per_day, subjects)
    print(subjects)
    print(teachers)
    print(sections)

    for i in range(len(blocked_slots)):
        for j in range(len(blocked_slots[0])):
            if not blocked_slots[i][j]: continue
            for teacher in teachers:
                teacher.availability[i][j] = 1
            for section in sections:
                section.availability[i][j] = 1
    
    for teacher in teachers:
        teacher.score = (
            (n_days_per_week * n_slots_per_day)
            - sum(sum(row) for row in teacher.availability)
        ) / sum(subj.total_slots_per_week for subj in teacher.subjects)


    for teacher in teachers:
        if not len(teacher.subjects): continue
        for subj in teacher.subjects:
            key = (teacher.id, subj.id)
            groupings[key] = (teacher, subj)
            teacher.groupIDs |= {key}
            subj.groupIDs |= {key}
    print(groupings)
    
    for teacher in teachers:
        print(teacher.availability)

    groupings[(0,0)] = 0
    table: Table_T = [
        [
            [
                CollapsedState((0,0))
                if blocked_slots[day_j][slot_k]
                else SuperState(set(groupings.keys()),multiplier= 1 if slot_k>0 else 0.5 ) 
                for slot_k in range(n_slots_per_day)
            ]
            for day_j in range(n_days_per_week)
        ]
        for section_i in range(n_sections)
    ]

    print(table[0][0][0].classes)
    print()
    print_tt(table, n_sections, n_days_per_week, n_slots_per_day)
    print()

    #TODO pick min entropy as starting state
    #TODO handle first slot 
    collapseable_slot = (0,0,0)

    iteration_count = 0
    while True:
        iterate(table, n_sections, n_days_per_week, n_slots_per_day)
        print_tt(table, n_sections, n_days_per_week, n_slots_per_day)
        print(collapseable_slot, end=f"\n{'*' * 100}{(iteration_count:=iteration_count+1)}\n")
        input("next?: ")


if __name__ == '__main__':
    groupings: dict[GroupID_T, Group_T] = {}
    main()



"""
Calculating score

LOWER SCORE (less options), more likely to be chosen first

Subject ----------------------------------

    total_slots_per_week / min_blk_sz

    EX:
    2 slots per week, min block size = 2
    2/2 => 1

    EX:
    6 slots per week, min block size = 1
    6/1 => 6

Teacher ----------------------------------

    (total available slots / sum(subject hours) for each subject taught) / available slots

    EX:
    9 slots, subjects: [2,2]
    9/(2+2) => 2.25 /9

    EX:
    4 slots, subjects: [2]
    4/2 => 2 /9


------------------------------------------

Teacher * Subject

"""
