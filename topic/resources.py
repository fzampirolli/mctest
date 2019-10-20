from import_export import resources

from .models import Question


class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
