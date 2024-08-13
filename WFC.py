from typing import Callable

from states import SuperState, CollapsedState, Teacher, Subject, Section, Table_T, GroupID_T, Index_T
import states
import constraints
import numpy as np
import random

def calculate_state_entropy(modified_states: set[tuple[Index_T, SuperState]], callback):
    for ndx, state in modified_states:
        state.calc_entropy()
    callback(modified_states)


def get_min_cls(state: SuperState, ndx) -> GroupID_T:
    sec, day, slot = ndx
    min_cls = None
    min_entropy = np.inf
    for cls in state.classes:
        if (cls_entropy := states.get_entropy(cls, slot)) < min_entropy:
            min_entropy = cls_entropy
            min_cls = cls
    assert min_cls is not None, f"{ndx=} {state=} {state.classes=} {state.entropy=}"
    return min_cls


def get_collapsable_state(table:Table_T, dims) -> tuple[int,int,int]:
    n_sections, n_days_per_week, n_slots_per_day = dims
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


def propagate_constraints(table, dims, ndx, subjects, callback):
    modified_states: set[tuple[Index_T, SuperState]] = set()
    constraints.hard_constraints(table, dims, ndx, subjects, modified_states)
    constraints.soft_constraints(table, dims, ndx, subjects, modified_states)
    calculate_state_entropy(modified_states, callback)


def collapse_state(table, dims, ndx, min_cls, subjects, callback: Callable):
    sec, day, slot = ndx
    table[sec][day][slot] = CollapsedState(min_cls)
    callback({(ndx, table[sec][day][slot]),})
    if min_cls == (0,0):
        return
    facultyID, subjectID = min_cls
    sec_subj = Section.at(sec).subjects
    for subjID in states.block_subjects[subjectID]:
        sec_subj[subjID] = sec_subj.get(subjID, 0) + 1
    Teacher.at(facultyID).availability[day][slot] = (sec, Subject.at(subjectID))


def iterate(table, dims, subjects, callback):
    ndx = get_collapsable_state(table, dims)
    if ndx is None:
        return None
    sec, day, slot = ndx
    min_cls = get_min_cls(table[sec][day][slot], ndx)
    collapse_state(table, dims, ndx, min_cls, subjects, callback)

    if min_cls != (0,0):
        propagate_constraints(table, dims, ndx, subjects, callback)
    return ndx

def init(table, dims, blocked_slots, teachers, subjects, callback):
    states.block_grpIDs = set()
    for subj in states.only_block_subjects:
        states.block_grpIDs |= subj.groupIDs
    
    modified_states:set[tuple[Index_T, SuperState]] = set()
    constraints.pre_constraints(table, dims, blocked_slots, teachers, subjects, modified_states)
    calculate_state_entropy(modified_states, callback)


def reset():
    states.reset()
    constraints.reset()