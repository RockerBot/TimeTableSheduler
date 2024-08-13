from states import CollapsedState, SuperState, Teacher, Subject, Section, Table_T, GroupID_T, Group_T
from colorama import Fore

def print_tt(tt, dims, elective_slots, blocked_slots, ndx=None):
    n_sections, n_days_per_week, n_slots_per_day = dims
    padding = 23#74#23#10  # len(''.join(subjects.keys()))+len(str(MAX_ENTROPY))+3-3
    if ndx is not None:
        print(ndx)
    for section_i in range(n_sections):
        print('\rSECTION', section_i + 1, Section.at(section_i).subjects)
        for day_j in range(n_days_per_week):
            print(
                "\r",
                # "-"*230,"\n"
                "day", day_j, end=':  ')
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
                if slot_k==8:#slot_k%3==2:
                    print(end='\n        ')
    print(end='\r')

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
        for grpID, count in sorted(sec_cls.items(), key=lambda x:x[0][1]):
            print(f'{groupings[grpID]}: {count}', end=', ')
        print()

def print_tt_faculty(tt, dims, faculty:list[Teacher]):
    n_sections, n_days_per_week, n_slots_per_day = dims
    faculty_padding = 16
    for fac in faculty:
        print(fac.name, fac.id)
        for row in fac.availability:
            print('|'.join(map(
                lambda x:x.center(faculty_padding)
                .replace('0'.center(faculty_padding), ' '.center(faculty_padding))
                .replace('1'.center(faculty_padding),('X'*(faculty_padding-2)).center(faculty_padding)), map(str,row)
            )))
    

def print_to_csv(tt, dims, elective_slots, blocked_slots, faculty:list[Teacher]):
    n_sections, n_days_per_week, n_slots_per_day = dims
    day_of_week = ['Monday','Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    with open('timetable_student.csv', 'w') as file:
        for sec_i in range(n_sections):
            file.write(f"SECTION {sec_i+1}\n")
            for day_j in range(n_days_per_week):
                file.write(f"{day_of_week[day_j]},")
                file.write(', '.join(map(lambda x:str(x).replace(',',''), tt[sec_i][day_j])))
                file.write("\n")

    with open('timetable_faculty.csv', 'w') as file:
        for fac in faculty:
            file.write(f"{fac.name} {fac.id}\n")
            for row in fac.availability:
                file.write(', '.join(map(lambda x:str(x).replace(',','_'),row)))
                file.write('\n')


def score_faculty(blocked_slots, elective_slots, dims, elec_faculty:list[set[Teacher]], teachers:list[Teacher], sections:list[Section]):
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
    
    for i in range(n_days_per_week):
        for j in range(1, n_slots_per_day-1):
            for k,elec in enumerate(elective_slots):
                if elec[i][j-1]: # ie elective before current index
                    for fac in elec_faculty[k]:
                        fac.availability[i][j] = 1
                if elec[i][j+1]: # ie elective after current index
                    for fac in elec_faculty[k]:
                        fac.availability[i][j] = 1
                    

    
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

def setup(dims, blocked_slots, elective_slots, elec_faculty, teachers:list[Teacher], sections, subjects, groupings:dict[GroupID_T, Group_T]) -> Table_T:
    score_faculty(blocked_slots, elective_slots, dims, elec_faculty, teachers, sections)
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
    

# def input_file(file_name):
#     with open(file_name, 'r') as file:
#         n_days_per_week = int(file.readline().split('=')[-1])
#         n_slots_per_day = int(file.readline().split('=')[-1])
#         n_semesters     = int(file.readline().split('=')[-1])
#         n_subjects      = int(file.readline().split('=')[-1])
#         n_faculty       = int(file.readline().split('=')[-1])
#         n_electives     = int(file.readline().split('=')[-1])
        
#         n_sections      = (*map(int,file.readline().split('=')[-1].split(',')),) #tuple(int,int,...) tuple of no of sections per semester

#         # subjects
#         subjects_dict = {}
#         for _ in range(n_subjects):
#             subj_name, subj_info= map(str.strip, file.readline().strip().split('='))
#             subjects_dict[subj_name] = [*map(int, subj_info.split(','))]
        
#         #electives
#         electives = []
#         elective_slots = []
#         for i in range(n_electives):
#             n_subjs = [*map(int,file.readline().split('=')[-1].strip().split(','))]
#             electives.append((
#                 [file.readline().strip() for _ in range(n_subjs[0])],
#                 n_subjs[1:]
#             ))
#             elective_slots.append(
#                 [ [*map(int,file.readline().strip())] for _ in range(n_days_per_week)]
#             )
        
#         #faculty
#         faculty_dict = {}
#         for _ in range(n_faculty):
#             faculty, subjs = map(str.strip, file.readline().split('='))
#             faculty_dict[faculty] =[*map(str.strip, subjs.split(','))]
        
#         # blocked_slolts and semester subjects
#         semester_subjects_list = []
#         blocked_slots = []
#         for i in range(n_semesters):
#             subjs = file.readline().split('=')[-1]
#             semester_subjects_list.append(
#                 [*map(str.strip, subjs.split(','))]
#             )
#             blocked_slots.append( [ 
#                 [*map(int,file.readline().strip())]
#                 for _ in range(n_days_per_week)
#             ] )

#         #faculty availability
#         faculty_availability_dict = {}
#         for _ in range(n_faculty):
#             faculty, availability = map(str.strip, file.readline().split('='))
#             faculty_availability_dict[faculty] = [
#                 [*map(int, day.strip())]
#                 for day in availability.split(',')
#             ]


#     #TODO blocked_slots --> blocked_slots[sem]
#     #TODO n_sections --> n_sections[sem]

#     #TODO new --> semester_subjects_list, n_semesters, faculty_availability_dict
#     print(f"""
#         {n_days_per_week=}
#         {n_slots_per_day=}
#         {n_semesters=}
#         {n_subjects=}
#         {n_faculty=}
#         {n_electives=}
#         {n_sections=}

#         {subjects_dict=}
#         {electives=}
#     """)
#     print("ElectiveSlots")
#     for elec_slots in elective_slots:
#         print('-'*n_slots_per_day)
#         for row in elec_slots:
#             print(''.join(map(str,row)))
#     print("faculty dictionary")
#     for k,v in faculty_dict.items():
#         print(k,v)
#     print("Semester subjects")
#     for i,subjs in enumerate(semester_subjects_list):
#         print(f"Semester{i+1}",subjs)
#     print("Blocked slots")
#     for i in range(n_semesters):
#         for row in blocked_slots[i]:
#             print(''.join(map(str,row)))
#     print("Teacher Availability")
#     for k,v in faculty_availability_dict.items():
#         print(k,v)
    
#     return (
#         n_days_per_week, 
#         n_slots_per_day, 
#         n_semesters,
#         n_sections, #n_sections[0]
#         n_subjects, 
#         n_faculty, 
#         n_electives, 
#         subjects_dict, 
#         electives,
#         elective_slots, 
#         faculty_dict, 
#         semester_subjects_list,
#         blocked_slots, #blocked_slots[0]
#         faculty_availability_dict
#     )

# if __name__ == '__main__':
#     input_file('config2.txt')