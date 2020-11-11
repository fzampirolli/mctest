from setuptools import setup

setup(
    name='mctest',
    version='5.1',
    packages=['exam', 'exam.migrations', 'topic', 'topic.migrations', 'course', 'course.migrations', 'mctest',
              'account', 'account.migrations', 'student', 'student.migrations'],
    url='vision.ufabc.edu.br',
    license='LGPL',
    author='fz',
    author_email='fzampirolli@ufabc.edu.br',
    description='Generator and Corrector Exams'
)
