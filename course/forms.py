from django import forms


class UpdateClassroomForm(forms.Form):
    # students = forms.ModelMultipleChoiceField(
    #    queryset=Classroom.objects.all(),
    #    help_text = _("Choose the classrooms"),
    #    label=_("Classrooms"))
    #def __init__(self, *args, **kwargs):
    #   super(UpdateClassroomForm, self).__init__(*args, **kwargs)
    pass

    def __init__(self, *args, **kwargs):
        super(UpdateClassroomForm, self).__init__(*args, **kwargs)
        try:
            # user = kwargs['initial']['question_who_created']
            # self.fields['topic'].queryset = Question.objects.filter(topic__course__discipline_profs=user)
            # self.fields['classrooms'].queryset = Classroom.objects.filter(discipline__discipline_profs=user)
            pass

        except:
            pass
