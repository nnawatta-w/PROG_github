from student import Student
from course import Course

s = Student("001", "Indy", "Example")
c = Course("05696111", "Foundation of Programming")

c.enroll(s)
c.enroll(s)

c.display()
s.display()