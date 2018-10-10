from django import forms
from captcha.fields import CaptchaField


class UserForm(forms.Form):
    username = forms.CharField(label='登录名', max_length=128,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='密码', max_length=128,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码',)


class RegisterForm(forms.Form):
    gender = (
        ('male', '男'),
        ('female', '女'),
        )
    username = forms.CharField(label='用户名', max_length=128,
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label='密码', max_length=128,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='确认密码', max_length=128,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label='性别', choices=gender)
    email = forms.EmailField(label='邮箱地址', widget=forms.EmailInput(attrs={'class': 'form-control'}))
    captcha1 = CaptchaField(label='验证码',)


class EditPage(forms.Form):
    title = forms.CharField(label='文章标题', max_length=200,
                            widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label='内容', max_length=1000,
                              widget=forms.TextInput(attrs={'class': 'form-control'}))