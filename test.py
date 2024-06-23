import random

# Define sections, subjects, and days
sections = ['A', 'B', 'C']
subjects = ['Math', 'Science', 'English', 'Social Studies', 'Art']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

# Initialize an empty timetable
timetable = {section: {day: [] for day in days} for section in sections}

# Function to check if a subject can be added to a specific day
def can_add_subject(day_schedule, subject):
    return day_schedule.count(subject) < 2

# Function to generate a timetable for a section
def generate_timetable():
    section_timetable = {day: [] for day in days}
    
    for subject in subjects:
        slots = 0
        while slots < 6:
            day = random.choice(days)
            if can_add_subject(section_timetable[day], subject):
                section_timetable[day].append(subject)
                slots += 1
    
    return section_timetable

# Generate timetable for each section
for section in sections:
    timetable[section] = generate_timetable()

# Print the timetable
for section, schedule in timetable.items():
    print(f"\nTimetable for Section {section}:")
    for day, subjects in schedule.items():
        print(f"{day}: {subjects}")