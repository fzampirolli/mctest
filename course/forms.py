from django import forms

from account.models import User
from .models import Classroom
from .models import Discipline


class ClassroomCreateForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = [
            'discipline',
            'classroom_profs',
            'classroom_code',
            'classroom_room',
            'classroom_days',
            'classroom_type',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ClassroomCreateForm, self).__init__(*args, **kwargs)

        profs = []
        for d in Discipline.objects.filter(discipline_profs=user):
            for p in d.discipline_profs.all():
                profs.append(p.pk)
            for p in d.discipline_coords.all():
                profs.append(p.pk)
        try:
            d1 = Discipline.objects.filter(discipline_profs=user)
            d2 = Discipline.objects.filter(discipline_coords=user)
            self.fields['discipline'].queryset = (d1 | d2).distinct()
            self.fields['classroom_profs'].queryset = User.objects.filter(pk__in=profs).order_by("email")
        except:
            pass


class ClassroomUpdateForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = [
            'discipline',
            'students',
            'classroom_profs',
            'classroom_code',
            'classroom_room',
            'classroom_days',
            'classroom_type',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ClassroomUpdateForm, self).__init__(*args, **kwargs)

        profs = []
        for d in Discipline.objects.filter(discipline_profs=user):
            for p in d.discipline_profs.all():
                profs.append(p.pk)
            for p in d.discipline_coords.all():
                profs.append(p.pk)
        try:
            d1 = Discipline.objects.filter(discipline_profs=user)
            d2 = Discipline.objects.filter(discipline_coords=user)
            self.fields['discipline'].queryset = (d1 | d2).distinct()
            self.fields['classroom_profs'].queryset = User.objects.filter(pk__in=profs).order_by("email")
        except:
            pass