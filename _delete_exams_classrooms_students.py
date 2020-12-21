# python manage.py shell < _delete_exams_classrooms_students.py

from student.models import Student
Student.objects.all().delete()

from exam.models import ClassroomExam, StudentExamQuestion, StudentExam, VariationExam, Exam
StudentExamQuestion.objects.all().delete()
StudentExam.objects.all().delete()
ClassroomExam.objects.all().delete()
VariationExam.objects.all().delete()
Exam.objects.all().delete()

from course.models import Classroom
Classroom.objects.all().delete()

