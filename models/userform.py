from django import forms
from django.contrib.auth.models import User
from django.urls import reverse
from django.shortcuts import render, redirect
from datetime import datetime
from clientmanagement import userfunctions

class UserForm(forms.ModelForm):
    error_messages = {
        'password_complex1': "Passsword must be at least 7 characters long ",
        'password_complex2': "Password must consist of characters from at least two groups: digits, lower case letters, upper case letters, characters: !@#$%^&;*~`_+=,.<;>;/",
        'password_mismatch': "The two password fields didn't match.",
        'email_not_valid': "Please, enter a valid email.",
        'email_already_in_use': "This email is already in use.",
    }
    password1 = forms.CharField(label="Password",
        widget=forms.PasswordInput(render_value = True))
    password2 = forms.CharField(label="Password confirmation",
        widget=forms.PasswordInput(render_value = True))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required=True
        self.fields['last_name'].required=True
        self.fields['username'].required=True
        self.fields['username'].help_text=""
        self.fields['email'].required=True
        self.fields['password1'].required=True
        self.fields['password2'].required=True
        instance = getattr(self, 'instance', None)
        if instance and instance.id:
            self.fields['username'].widget.attrs['readonly'] = True
            self.fields['password1'].initial ="*********"
            self.fields['password2'].initial ="*********"

    def clean_email(self):
        result = userfunctions.checkEmailExistsForm(self.cleaned_data.get("email"), curuserid=self.instance.id)
        if result == 2 or result == 3:
            raise forms.ValidationError(self.error_messages['email_not_valid'], code='email_not_valid')
        if result == 1:
            raise forms.ValidationError(self.error_messages['email_already_in_use'], code='email_already_in_use')
        return self.cleaned_data.get("email")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean_password1(self):
        passwordcom, message = userfunctions.checkPasswordComplexity(self.cleaned_data.get("password1"))
        if not passwordcom:
            raise forms.ValidationError([
                forms.ValidationError(self.error_messages['password_complex1'], code='password_complex1'),
                forms.ValidationError(self.error_messages['password_complex2'], code='password_complex2')
            ]
            )
        self.clean_password2()
        return self.cleaned_data.get("password1")


    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        if ('password1' in self.changed_data):
            user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def userFormParse(request):
    data={}
    data['PAGE_TITLE'] = 'Change User: CMS infotek'
    if (request.method == 'POST') and ('action' in request.POST):
        if (request.POST['action']=='add'):
            form = UserForm(request.POST)
            if form.is_valid():
                model = form.save(commit=False)
                model.save()
                return redirect(reverse('usermanagement'))
            else:
                data['action']='add'
                data['PAGE_TITLE'] = 'New User: CMS infotek'
                data['minititle'] = 'Add User'
                data['submbutton'] = 'Add user'
        elif (request.POST['action']=='change'):
            if('targetid' in request.POST):
                try:
                    curuser=User.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('usermanagement'))
                form = UserForm(instance=curuser)
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change User "'+curuser.get_full_name()+'"'
                data['submbutton'] = 'Change user'
                data['deletebutton'] = 'Delete ' +curuser.get_full_name()
            else:
                return redirect(reverse('usermanagement'))
        elif (request.POST['action']=='changed'):
            if('targetid' in request.POST):
                try:
                    curuser=User.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('usermanagement'))
                form = UserForm(request.POST, instance=curuser)
                if form.is_valid():
                    model = form.save(commit=False)
                    model.save()
                    return redirect(reverse('usermanagement'))
                data['action'] = 'changed'
                data['targetid'] = request.POST['targetid']
                data['minititle'] = 'Change User "'+curuser.get_full_name()+'"'
                data['submbutton'] = 'Change user'
                data['deletebutton'] = 'Delete ' +curuser.get_full_name()
            else:
                return redirect(reverse('usermanagement'))
        elif (request.POST['action']=='delete'):
            if('targetid' in request.POST):
                try:
                    curuser=User.objects.get(id=request.POST['targetid'])
                except Exception:
                    return redirect(reverse('usermanagement'))
                curuser.delete()
                return redirect(reverse('usermanagement'))
            else:
                return redirect(reverse('usermanagement'))
        else:
            return redirect(reverse('usermanagement'))
    else:
        form = UserForm()
        data['action']='add'
        data['PAGE_TITLE'] = 'New User: CMS infotek'
        data['minititle'] = 'Add User'
        data['submbutton'] = 'Add user'
    data['form'] = form
    data['built'] = datetime.now().strftime("%H:%M:%S") 
    data['backurl'] = reverse('usermanagement')
    return render(request, 'forms/unimodelform.html', data, content_type='text/html')
