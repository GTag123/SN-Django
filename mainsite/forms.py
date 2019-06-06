## -*- coding: utf-8 -*-
from django import forms
from .models import Account, Group, Post, Tag
# from django.core.exceptions import ValidationError
# from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import AuthenticationForm

class UserCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Ник'
        self.fields['email'].label = 'Почта'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].required = True
        self.fields['first_name'].required = True # required тут добавляет проверку в <form>_clean,
        self.fields['last_name'].required = True  # а в виджетах не проверяется пустота!!!!(можно пробелы проставить!)

    password1 = forms.CharField(widget=forms.PasswordInput(attrs=
        {'class': 'form-control', 'placeholder': 'Введите пароль'}), min_length=5, label=u'Ваш пароль')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=
        {'class': 'form-control', 'placeholder': 'Повторите пароль'}), min_length=5, label=u'Повторите пароль')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите ник'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите фамилию'}),
        }
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email должен быть уникальным!')
        return email.lower()

    def clean_password2(self):
        if self.cleaned_data.get("password1") != self.cleaned_data.get("password2"):
            raise forms.ValidationError('Пароли не совпадают')
        return self.cleaned_data.get("password2")

    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        user.save()
        return user

class UserEditForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Ваш новый пароль'
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    field_order = ['username', 'email', 'old_password', 'password1', 'password2', 'first_name', 'last_name']
    old_password = forms.CharField(widget=forms.PasswordInput(attrs=
        {'class': 'form-control', 'placeholder': 'Введите старый пароль'}), label=u'Ваш старый пароль', required=False)

    def clean_email(self):
        user = self.instance
        email = self.cleaned_data.get("email").lower()
        try:
            exists_email = User.objects.get(email__iexact=email)
        except:
            return email
        if exists_email != user:
            raise forms.ValidationError('Email должен быть уникальным!')
        return email
    
    def is_valid(self):
        valid = super().is_valid()
        if not valid:
            return valid
        user = self.instance

        validate_passwords = False
        if self.cleaned_data.get('old_password') or self.cleaned_data.get('password1'):
            validate_passwords = True
            if not user.check_password(self.cleaned_data['old_password']):
                self.errors['old_password'] = ['Введите правильный старый пароль!'] # _errors
                valid = False

        if validate_passwords and valid:
            #   old password is correct
            if not self.cleaned_data.get('password1'):
                self.errors['password1'] = ['Пароль не может быть пустым!']
                valid = False

        if validate_passwords and valid:
            #   new password is not empty
            if self.cleaned_data.get('password1') != self.cleaned_data.get('password2'):
                self.errors['password2'] = ['Пароли не одинаковые!']
                valid = False
        return valid

class UserMoreInfoForm(forms.ModelForm): # form for Account model(it depends on the User)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['views'].label = 'Политические взгляды'
        self.fields['age'].label = 'Возраст'
    class Meta:
        model = Account
        fields = ('age', 'views', 'photo')
        widgets = {
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Возраст', 'max': 150}),
            'views': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваши взгляды', 'rows': 2}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age:
            try:
                int(self.cleaned_data.get("age"))
            except:
                raise forms.ValidationError('Возраст должен быть числом!')
            if age > 150:
                raise forms.ValidationError('Возраст не может быть больше 150!))')
        return age
    
    def save(self, *args, **kwargs): # <-- это тупо, можно во вьюхах сделать test = form.save(commit=False), а потом
        userinfo = super().save(commit=False) # test.user = blablabla и затем test.save()
        userinfo.user = kwargs['user']
        userinfo.save()
        return userinfo

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': True})
        self.fields['password'].label = 'Пароль'
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': True})

class GroupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
    class Meta:
        model = Group
        fields = ('name', 'slug','description', 'photo')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название группы'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL группы'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug and (slug.lower() == 'create' or slug.lower() == 'list'):
            raise forms.ValidationError("Ссылка не может быть 'create', 'list' или 'delete!")
        return slug

class PostForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите тэги через запятую'}),
    label=u'Тэги', required=False, help_text='(Введите через запятую)')

    class Meta:
        model = Post
        fields = ('title', 'body')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Содержание', 'rows': 10}),
        }
    def save(self, *args, **kwargs): # FIXME: на спец символы не создаётся слаг и выдаётся ошибка уникальности
        post = super().save(commit=False)
        post.author = kwargs.get('author')
        post.group = kwargs.get('group')
        post.save()
        tags = list(map(lambda tag: tag.strip(), self.cleaned_data['tags'].split(',')))
        print('tags:', tags)
        for tag in tags:
            if tag:
                try:
                    post.tags.add(Tag.objects.get(title__iexact=tag))
                except Tag.DoesNotExist:
                    post.tags.create(title=tag)
        return post