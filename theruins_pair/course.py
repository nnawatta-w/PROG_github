class Course:
    def __init__(self, id, title):
        self.id = id
        self.title = title
        self.students = []

    def enroll(self, student):
        if student not in self.students:
            self.students.append(student)

        if self not in student.courses:
            student.courses.append(self)

    def remove(self, student):
        if student in self.students:
            self.students.remove(student)

            if self in student.courses:
                student.courses.remove(self)

    def display(self):
        print(self.students)