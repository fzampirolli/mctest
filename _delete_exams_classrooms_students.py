# python3 manage.py shell < _delete_exams_classrooms_students.py

from student.models import Student
from topic.models import Question, Topic

Student.objects.all().delete()

from exam.models import ClassroomExam, StudentExamQuestion, StudentExam, VariationExam, Exam
StudentExamQuestion.objects.all().delete()
StudentExam.objects.all().delete()
ClassroomExam.objects.all().delete()
VariationExam.objects.all().delete()
Exam.objects.all().delete()


#Question.objects.all().delete()

from course.models import Classroom, Discipline
Classroom.objects.all().delete()

