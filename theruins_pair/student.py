class Student:
    def __init__(self, id, firstname, lastname):
        self.id = id
        self.first_name = firstname
        self.last_name = lastname
        self.courses = []

    def __str__(self):
        return f"({self.id}, {self.first_name} {self.last_name})"

    def display(self):
        courses = sorted(self.courses, key=lambda course: course.id)

        if not courses:
            return

        print("+----------+----------------------------+")
        print("| Cour. ID | Name                       |")
        print("+----------+----------------------------+")

        for course in courses:
            title = course.title

            if len(title) > 28:
                title = title[:25] + "..."

            print(f"| {course.id:<8} | {title:<28} |")

        print("+----------+----------------------------+")