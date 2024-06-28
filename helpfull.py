from states import CollapsedState, SuperState, Teacher, Subject, Section, Table_T, GroupID_T, Group_T
from colorama import Fore

def print_tt(tt, dims, elective_slots, blocked_slots, ndx=None):
    n_sections, n_days_per_week, n_slots_per_day = dims
    padding = 74#23#10  # len(''.join(subjects.keys()))+len(str(MAX_ENTROPY))+3-3
    if ndx is not None:
        print(ndx)
    for section_i in range(n_sections):
        print('\rSECTION', section_i + 1)
        for day_j in range(n_days_per_week):
            print("\r","-"*250,"\nday", day_j, end=':  ')
            for slot_k in range(n_slots_per_day):
                state = tt[section_i][day_j][slot_k]
                clr = ('\033[39m', '\033[92m')[isinstance(state, CollapsedState)]
                if blocked_slots[day_j][slot_k]:
                    for i,elec in enumerate(elective_slots):
                        if elec[day_j][slot_k]:
                            print(f"{clr}{(f'elec{i+1}'.center(padding))}\033[39m", end=' ')
                            break
                    else:
                        print(f"{clr}{'XXX'.center(padding)}\033[39m", end=' ')
                elif (section_i,day_j,slot_k) == ndx:
                    print(f"{Fore.RED}{state:-{padding}}\033[39m", end=' ')
                else:
                    print(f"{clr}{state:-{padding}}\033[39m", end=' ')
                if slot_k%3==2:
                    print("\n        ",end='')

def print_tt_stats(tt, dims, groupings, block_subjects):
    n_sections, n_days_per_week, n_slots_per_day = dims
    for section_i in range(n_sections):
        sec_cls = {}
        for day_j in range(n_days_per_week):
            for slot_k in range(n_slots_per_day):
                state = tt[section_i][day_j][slot_k]
                if not isinstance(state, CollapsedState):
                    continue
                facultyID, subjID = state.cls
                grpID = facultyID, 0 if subjID == 0 else block_subjects[subjID][0]
                sec_cls[grpID] = sec_cls.get(grpID, 0) + 1
        for grpID,count in sec_cls.items():
            print(f'{groupings[grpID]}: {count}', end=', ')
        print()


def score_faculty(blocked_slots, elective_slots, dims, teachers:list[Teacher], sections:list[Section]):
    n_sections, n_days_per_week, n_slots_per_day = dims

    for i in range(n_days_per_week):
        for j in range(n_slots_per_day):
            for elec in elective_slots:
                if elec[i][j]: break
            else: 
                if not blocked_slots[i][j]:
                    continue
            for teacher in teachers:
                teacher.availability[i][j] = 1
            for section in sections:
                section.availability[i][j] = 1
    
    for teacher in teachers:
        teacher.score = (
            (n_days_per_week * n_slots_per_day)
            - sum(sum(row) for row in teacher.availability)
        ) / sum(subj.total_slots_per_week for subj in teacher.subjects)
    
def create_groupings(teachers:list[Teacher], groupings):
    for teacher in teachers:
        if not len(teacher.subjects): continue
        for subj in teacher.subjects:
            key = (teacher.id, subj.id)
            groupings[key] = (teacher, subj)
            teacher.groupIDs |= {key}
            subj.groupIDs |= {key}
    groupings[(0,0)] = 0

def setup(dims, blocked_slots, elective_slots, teachers:list[Teacher], sections, subjects, groupings:dict[GroupID_T, Group_T]) -> Table_T:
    score_faculty(blocked_slots, elective_slots, dims, teachers, sections)
    create_groupings(teachers, groupings)
    n_sections, n_days_per_week, n_slots_per_day = dims
    table: Table_T = [
        [
            [
                CollapsedState((0,0))
                if blocked_slots[day_j][slot_k]
                else SuperState(
                    set(groupings.keys()),
                    multiplier= 1 if slot_k>0 else 0.5,
                    pos=slot_k
                ) 
            for slot_k in range(n_slots_per_day)]
        for day_j in range(n_days_per_week)]
    for section_i in range(n_sections)]
    
    for j in range(n_days_per_week):
        for k in range(n_slots_per_day):
            for elec in elective_slots:
                if not elec[j][k]: continue
                for i in range(n_sections):
                    table[i][j][k] = CollapsedState((0,0))#TODO collapsed states with elective subj

    return table
    