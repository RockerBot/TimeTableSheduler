import numpy as np

SubjectID_T = int
FacultyID_T = int
Group_T = tuple['Teacher', 'Subject']
GroupID_T = tuple[FacultyID_T,SubjectID_T]
Table_T = list[list[list['SuperState']]]
Index_T = tuple[int,int,int]

ENTROPY_MAX = 1_000_000_000_000
groupings: dict[GroupID_T, Group_T] = {}

block_subjects:dict[SubjectID_T,list[SubjectID_T]] = {} #dict [subjectID] -> list of subjectIDs corresponding to the same subject, 
# EX: 1->[1],2->[2,3],3->[2,3] because 2 and 3 are the same block subject
only_block_subjects: list['Subject'] = [] #set of only block Subjects
block_grpIDs:set[GroupID_T] = set() #set of groupIDs for only block subjects

def get_entropy(cls: GroupID_T, pos=-1):
    global groupings
    if cls == (0,0):
        return ENTROPY_MAX
    faculty, subject = groupings[cls]
    score = faculty.score * subject.score
    if pos == 0 and len(block_subjects[cls[1]])>1:
        return score * 20
    return score

class Subject:
    ID = 1 # subject's ID starts from 1, 0 is reserved
    subject_list: list['Subject'] = []

    @staticmethod
    def create(name, total_slots_per_week ,min_blk_sz = 1, max_blk_sz = 2):
        subjs = []
        subjIDs = []
        for i in range(min_blk_sz):
            subject = Subject(
                name,
                total_slots_per_week,
                min_blk_sz,
                max_blk_sz,
                i
            )
            subjs.append(subject)
            subjIDs.append(subject.id)
            if min_blk_sz > 1:
                only_block_subjects.append(subject)
        for id in subjIDs:
            block_subjects[id] = subjIDs
        return subjs



    def __init__(self, name, total_slots_per_week ,min_blk_sz = 1, max_blk_sz = 2, blk_index=1):
        self.id = Subject.ID
        Subject.ID += 1
        Subject.subject_list.append(self)
        self.name = name
        self.total_slots_per_week = total_slots_per_week
        self.score = total_slots_per_week / min_blk_sz
        self.blk_index = blk_index
        self.min_blk_sz = min_blk_sz
        self.max_blk_sz = max_blk_sz
        self.groupIDs: set[GroupID_T] = set()
    
    def __hash__(self) -> int:
        return hash(f'Subject{self.id}')
    
    def __repr__(self):
        if self.min_blk_sz > 1:
            return f'{self.name}{self.blk_index}'#[{self.min_blk_sz}-{self.max_blk_sz}]'
        return self.name
    
    @classmethod
    def at(cls, index) -> 'Subject':
        return cls.subject_list[index-1]


class Teacher:
    ID = 1 # teacher's ID starts from 1, 0 is reserved
    teacher_list: list['Teacher'] = []

    def __init__(self, name='BLANK'):
        self.id = Teacher.ID
        Teacher.ID += 1
        Teacher.teacher_list.append(self)
        self.name = name
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
        return f'{chr(65+self.id)}'#[{self.subjects}]'

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

    def __init__(self, classes: set[GroupID_T], multiplier=1, pos=-1) -> None:
        self.classes: set[GroupID_T] = classes
        super().__init__()
        self.id = SuperState.ID
        SuperState.ID += 1
        self.pos = pos
        self.multiplier = multiplier
        self.calc_entropy()

    def calc_entropy(self) -> None:
        if self.pos == 0:
            entropy = sum(
                get_entropy(cls, pos=0) / 
                (20 if cls[1] and len(block_subjects[cls[1]])>1 else 1)
                for cls in self.classes
            )
        else:
            entropy = sum(
                get_entropy(cls, pos=self.pos)
                for cls in self.classes
            )
        self.entropy = entropy * self.multiplier

    def __hash__(self):
        return hash(f'SState{self.id}')
        return hash('SState''_'.join(self.classes))

    def __repr__(self):
        # return str(self.ID)        
        # return '_'.join(
        return ' '.join(
            f'{chr(65+cls[0])}{cls[1]}' for cls in sorted(self.classes)
        ) #+ f"_[{self.entropy}]"