from states import CollapsedState, SuperState, Teacher, Subject, Section, Table_T, GroupID_T, SubjectID_T, FacultyID_T, Index_T
import states

to_be_propagated:list[tuple[
    tuple[int,int,int],
    tuple[FacultyID_T,SubjectID_T]
]] = []
#TODO Add constraint, if a teacher is assigned to a class, remove that many availability slots, ie always check when assigning a teacher if they have enough availability for another subject

def remove_invalids(state: 'SuperState', invalidIDs: set[GroupID_T], ndx, modified_states: set[tuple[Index_T, SuperState]]):
    # only_block_subjects
    global to_be_propagated
    blk_states = state.classes&invalidIDs&states.block_grpIDs
    # to_be_propagated.extend((ndx, x[1]) for x in blk_states)
    to_be_propagated.extend((ndx, x) for x in blk_states)
    state.classes -= invalidIDs
    modified_states.add((ndx, state))


def remove_invalid_blocks(table: Table_T, dims, modified_states: set[tuple[Index_T, SuperState]]):
    # return
    n_sections, n_days_per_week, n_slots_per_day = dims
    visited:set[GroupID_T] = set()
    while len(to_be_propagated):
        state_info = to_be_propagated.pop(0)
        if state_info in visited:
            continue
        visited.add(state_info)
        """
        The state has been handled
        u need to handle the nbr states
            then add the nbrs to the to_be_propagated stack
        if there was nothing to 'handle', dont add to stack
        """
        ndx, cls = state_info
        # subjID = cls
        facID, subjID = cls
        sec, day, slot = ndx
        subj = Subject.at(subjID) # 6
        blk_subjs = states.block_subjects[subjID]

        blk_ofst = subj.blk_index # 2
        slot_base = slot - blk_ofst # slot-2 | slot-0
        for i in range(0, blk_ofst): # states in block with a lower blk index
            slot_i = slot_base + i
            if n_slots_per_day > slot_i >= 0:                
                state = table[sec][day][slot_i]
                if not isinstance(state, SuperState):
                    continue
                nbr_subjID = blk_subjs[i]
                # invalidIDs = Subject.at(nbr_subjID).groupIDs
                invalidIDs = {(facID, nbr_subjID)}
                if len(state.classes&invalidIDs) == 0:
                    continue
                # to_be_propagated.append(( (sec,day,slot_i), nbr_subjID ))
                to_be_propagated.append(( (sec,day,slot_i), (facID,nbr_subjID) ))
                state.classes -= invalidIDs
                modified_states.add(((sec, day, slot_i), state))
        
        for i in range(blk_ofst+1, subj.min_blk_sz): # states in block with a higher blk index
            slot_i = slot_base + i
            if n_slots_per_day > slot_i >= 0:
                state = table[sec][day][slot_i]
                if not isinstance(state, SuperState):
                    continue
                nbr_subjID = blk_subjs[i]
                # invalidIDs = Subject.at(nbr_subjID).groupIDs
                invalidIDs = {(facID, nbr_subjID)}
                if len(state.classes&invalidIDs) == 0:
                    continue
                # to_be_propagated.append(( (sec,day,slot_i), nbr_subjID ))
                to_be_propagated.append(( (sec,day,slot_i), (facID,nbr_subjID) ))
                state.classes -= invalidIDs
                modified_states.add(((sec, day, slot_i), state))


        


def teachers_unavailable(table: Table_T, dims, blocked_slots, teachers:list[Teacher], modified_states):
    """removes states where the faculty is not available"""
    n_sections, n_days_per_week, n_slots_per_day = dims
    for day_i in range(n_days_per_week):
        for slot_j in range(n_slots_per_day):
            if blocked_slots[day_i][slot_j]:
                continue
            invalidIDs = set()
            for faculty in teachers:
                val = faculty.availability[day_i][slot_j]
                if not val:
                    continue
                invalidIDs |= faculty.groupIDs
            if len(invalidIDs) == 0: continue
            for sec_k in range(n_sections):
                state = table[sec_k][day_i][slot_j]
                if not isinstance(state, SuperState):
                    continue
                remove_invalids(state, invalidIDs, (sec_k,day_i,slot_j), modified_states)

def impossible_blocks(table: Table_T, dims, blocked_slots, modified_states):
    """
    removes block states if the entire block can not be placed at that location
    due to 'blocked_slots' and slot index = 0 or -1
    """
    n_sections, n_days_per_week, n_slots_per_day = dims
    
    for slot_k in range(n_slots_per_day):
        invalidIDs_1 = set()
        for subj in states.only_block_subjects:
            if 0 <= (slot_k - subj.blk_index) <= n_slots_per_day-subj.min_blk_sz:
                continue
            invalidIDs_1 |= subj.groupIDs # blksubjs at the end and begining slots
        for day_j in range(n_days_per_week):
            if blocked_slots[day_j][slot_k]:
                continue
            invalidIDs_2 = set()|invalidIDs_1
            for subj in states.only_block_subjects:
                min_slot = max(0,slot_k - subj.blk_index)
                max_slot = min(n_slots_per_day, slot_k + subj.min_blk_sz - subj.blk_index)
                if any(blocked_slots[day_j][min_slot: max_slot]):
                    invalidIDs_2 |= subj.groupIDs
            for section_i in range(n_sections):
                state = table[section_i][day_j][slot_k]
                if not isinstance(state, SuperState):
                    continue
                remove_invalids(state, invalidIDs_2, (section_i,day_j,slot_k), modified_states)



def first_slot_diff_subj(table: Table_T, dims, ndx, collapsed_state: CollapsedState, modified_states):
    """Every day must start with a different subject"""
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    if slot > 0: return
    invalidIDs = {collapsed_state.cls}
    for d in range(n_days_per_week):
        state = table[sec][d][slot]
        if not isinstance(state, SuperState):
            continue
        remove_invalids(state, invalidIDs, (sec,d,slot), modified_states)

def one_teacher_per_subject_per_section(table: Table_T, dims, ndx, collapsed_state: CollapsedState, modified_states):
    """For a particular subject for a particular section, only one teacher
        ie two teachers can not teach the same subject for the same section
    """
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    facultyID, subjectID = collapsed_state.cls
    invalidIDs = set()
    for subjID in states.block_subjects[subjectID]:
        invalidIDs |= Subject.at(subjID).groupIDs - {(facultyID, subjID)}
    # invalidIDs = Subject.at(subjectID).groupIDs - {collapsed_state.cls}
    if not len(invalidIDs):
        return
    for d in range(n_days_per_week):
        for p in range(n_slots_per_day):
            state = table[sec][d][p]
            if not isinstance(state, SuperState):
                continue
            remove_invalids(state, invalidIDs, (sec,d,p), modified_states)

def at_one_place_at_one_time(table: Table_T, dims, ndx, collapsed_state: CollapsedState, modified_states):
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
        remove_invalids(state, invalidIDs, (s,day,slot), modified_states)

def max_subject_slots_per_week(table: Table_T, dims, ndx:tuple[int,int,int], collapsed_state:CollapsedState, modified_states):
    "each subject is allowed a certain number of slots per week"
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    subjectID = collapsed_state.cls[1]
    subject = Subject.at(subjectID)
    invalidIDs = subject.groupIDs
    if Section.at(sec).subjects[subjectID] == subject.total_slots_per_week:
        for d in range(n_days_per_week):
            for p in range(n_slots_per_day):
                state = table[sec][d][p]
                if not isinstance(state, SuperState):
                    continue
                # is a SuperState
                remove_invalids(state, invalidIDs, (sec,d,p), modified_states)

def min_block_slots(table: Table_T, dims, ndx, collapsed_state: CollapsedState, subjects:list[Subject], modified_states):
    "subjects requiring group slots ie consecutive slots"
    n_sections, n_days_per_week, n_slots_per_day = dims
    sec, day, slot = ndx
    facultyID, subjectID = collapsed_state.cls
    subject = Subject.at(subjectID)
    slot_base = slot-subject.blk_index
    blk_subj_list = states.block_subjects[subjectID]
    if subject.min_blk_sz>1: # it is a block subject
        # only valid state for block subject
        for i in range(subject.min_blk_sz):
            slot_i = slot_base + i
            state = table[sec][day][slot_i]
            if not isinstance(state, SuperState):
                continue
            invalidIDs = state.classes - {(facultyID,blk_subj_list[i])}
            remove_invalids(state, invalidIDs, (sec,day,slot_i), modified_states)
    
    # assuming slot_base as a wall, therefore update block states
    visited = set()
    for blk_subj in states.only_block_subjects:
        if blk_subj.id in visited: continue
        blk_subj_list = states.block_subjects[blk_subj.id]
        visited |= set(blk_subj_list)

        invalidIDs1 = set()
        invalidIDs2 = set()
        blk_end = blk_subj.min_blk_sz - 1
        for i in range(blk_end):
            slot_i = slot_base                        - blk_end + i # indexes before the collapsed state    [123][23][3][X]
            slot_j = slot_base + subject.min_blk_sz-1 + blk_end - i # indexes after the collapsed state                 [X][1][12][123]
            if n_slots_per_day > slot_i >= 0:
                state = table[sec][day][slot_i]
                if isinstance(state, SuperState):
                    invalidIDs1 |= Subject.at(blk_subj_list[i]).groupIDs
                    remove_invalids(state, invalidIDs1, (sec,day,slot_i), modified_states)
            if n_slots_per_day > slot_j >= 0:
                state = table[sec][day][slot_j]
                if isinstance(state, SuperState):
                    invalidIDs2 |= Subject.at(blk_subj_list[-i-1]).groupIDs
                    remove_invalids(state, invalidIDs2, (sec,day,slot_j), modified_states)



def hard_constraints(table: Table_T, dims, ndx, subjects, modified_states):
    global to_be_propagated
    sec, day, slot = ndx
    collapsed_state = table[sec][day][slot]
    assert isinstance(collapsed_state, CollapsedState)
    to_be_propagated = []
    # first_slot_diff_subj(table, dims, ndx, collapsed_state, modified_states)
    one_teacher_per_subject_per_section(table, dims, ndx, collapsed_state, modified_states)
    at_one_place_at_one_time(table, dims, ndx, collapsed_state, modified_states)
    max_subject_slots_per_week(table, dims, ndx, collapsed_state, modified_states)
    min_block_slots(table, dims, ndx, collapsed_state, subjects, modified_states)
    remove_invalid_blocks(table,dims, modified_states)

def soft_constraints(table: Table_T, dims, ndx, subjects, modified_states):
    sec, day, slot = ndx
    collapsed_state = table[sec][day][slot]
    assert isinstance(collapsed_state, CollapsedState)
    first_slot_diff_subj(table, dims, ndx, collapsed_state, modified_states)

def pre_constraints(table: Table_T, dims, blocked_slots, teachers:list[Teacher], subjects:list[Subject], modified_states):
    global to_be_propagated
    to_be_propagated = []
    teachers_unavailable(table, dims, blocked_slots, teachers, modified_states)
    impossible_blocks(table, dims, blocked_slots, modified_states)
    remove_invalid_blocks(table,dims, modified_states)

    