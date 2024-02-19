# python manage.py shell < _delete_question_statistics.py

from exam.models import StudentExamQuestion, StudentExam
StudentExamQuestion.objects.all().delete()
StudentExam.objects.all().delete()

from topic.models import Question
Question.objects.update(
    question_correction_count=0,
    question_correct_count=0,
    question_IRT_a_discrimination=0,
    question_IRT_b_ability=-5,
    question_IRT_c_guessing=0
)
