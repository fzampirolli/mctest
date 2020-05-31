from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import validate_email
from django.http import Http404

from course.models import Institute
from .models import User


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        u = self.cleaned_data["email"]
        flag_email = False
        code_inst = ""
        for i in Institute.objects.all():
            if i.institute_url.find(u[u.find("@") + 1:]) >= 0:
                flag_email = True
                code_inst = i.institute_code
                break
        user.email = u
        user.username = u[0:u.find("@")]  # code_inst + "." +
        if commit and flag_email:
            user.save()
            # g = Group.objects.get(name='professor')
            # user.groups.add(g)
        else:
            # messages.error(self, "account: Make sure email is intitutional: "+u)
            # return render(self, 'exam/exam_errors.html', {})
            # raise forms.ValidationError("Make sure email is intitutional: "+u)
            # raise Http404(forms)
            # raise  forms.ValidationError(_('Invalid value'), code='invalid')
            raise Http404("Make sure email is intitutional: " + u)

        return user

    def validate(self, value):
        """Check if value consists only of valid emails."""
        # Use the parent's handling of required fields, etc.

        super().validate(value)
        for email in value:
            validate_email(email)
