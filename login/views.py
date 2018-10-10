import hashlib
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.http import Http404
from captcha.models import CaptchaStore
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
#from django.views.generic import DetailView
from . import models
from . import forms
from .models import ContensInfo


def hash_code(s, salt='mysite'):
    """ Hash encryption algorithm. """
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()


class Index(ListView):

    model = ContensInfo
    template_name = 'login/index.html'
    context_object_name = 'all_content'

    def get(self, request, *args, **kwargs):

        if not request.session.get('is_login', None):
            return redirect('/login/login1')

        self.object_list = self.get_queryset()
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now_author = self.request.session.get('user_name')
        try:
            context['title'] = ContensInfo.objects.filter(author=now_author)
        except:
            pass
        return context


class Login(View):

    form_class = forms.UserForm

    def get(self, request):
        if request.session.get('is_login', None):
            return redirect(reverse('login:index'))
        login_form = self.form_class()
        #return render(request, reverse('login:login1'), locals())
        return render(request, 'login/login.html', locals())

    def post(self, request):
        if request.session.get('is_login', None):
            return redirect('/login/index')
        login_form = self.form_class(request.POST)
        message = '请检查填写内容！'
        if login_form.is_valid():
            #print(login_form.cleaned_data['captcha'])
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '该用户未通过邮件确认'
                    return render(request, 'login/login.html', locals())
                if user.password == hash_code(password):
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/login/index/')
                else:
                        message = '密码错误'
            except Exception as e:
                message = '用户不存在'
        return render(request, 'login/login.html', locals())


class Register(View):

    form_class = forms.RegisterForm

    def judge(self, request):
        if request.session.get('is_login', None):
            return redirect('/login/index')

    def send_email(self, email, code):
        """ Send email """
        from django.core.mail import EmailMultiAlternatives

        subject = '来自www.realbio.cn的注册确认邮件'

        text_content = ('感谢注册如果你,看到这条消息，说明你的邮箱服务器不提'
                        '供HTML链接功能，请联系管理员！')

        html_content = ('<p>感谢注  册<a href="http://{}/login/confirm/?code={}" '
                        'target=blank>www.realbio.cn</a>，'
                        '</p><p>请点击站点链接完成注册确认！</p>'
                        '<p>此链接有效期为{}天！</p>')\
            .format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)

        msg = EmailMultiAlternatives(subject, text_content,
                                     settings.EMAIL_HOST_USER, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def make_confirm_string(self, user):
        """ Get confirmation code """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        code = hash_code(user.name, now)
        models.ConfirmString.objects.create(code=code, user=user, )
        return code

    def get(self, request):
        self.judge(request)
        register_form = self.form_class()
        return render(request, 'login/register.html', locals())

    def post(self, request):
        register_form = self.form_class(request.POST)
        message = '请检查填写内容！'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            sex = register_form.cleaned_data['sex']
            email = register_form.cleaned_data['email']
            if password1 != password2:
                message = '两次填写的密码不一致'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:
                    message = '用户名已存在，请重新选择'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:
                    message = '该邮箱已被注册，请重新填写新邮箱'
                    return render(request, 'login/register.html', locals())
                new_user = models.User()
                new_user.name = username.strip()
                new_user.password = hash_code(password1)
                new_user.sex = sex
                new_user.email = email
                new_user.save()
                code = self.make_confirm_string(new_user)
                self.send_email(email, code)
                message = '请前往注册邮箱，进行邮件确认'
                # 跳转到等待邮件确认界面
                return render(request, 'login/confirm.html', locals())
        return render(request, 'login/register.html', locals())


class Logout(View):

    def get(self, request):
        request.session.flush()
        return redirect('/login/login1/')


class UserConfirm(View):

    def get(self, request):
        """ Email confirmtion """
        code = request.GET.get('code', None)
        message = ''
        try:
            confirm = models.ConfirmString.objects.get(code=code)
        except:
            message = '等待确认'
            return redirect('/login/login1/')    # 待完善
        c_time = confirm.c_time
        now = datetime.datetime.now()
        last_time = c_time + datetime.timedelta(settings.CONFIRM_DAYS)
        last_time = last_time.strftime('%Y-%m-%d %H:%M:%S')
        last_time = datetime.datetime.strptime(last_time, "%Y-%m-%d %H:%M:%S")
        if now > last_time:
            confirm.user.delete()
            message = '您的邮件已经过期！请重新注册!'
            return render(request, 'login/register.html', locals())
        else:
            confirm.user.has_confirmed = True
            confirm.user.save()
            confirm.delete()
            message = '感谢确认，请使用账户登录！'
            return redirect('/login/login1/')


"""
class AjaxVal(View):

    def get(request):
        """
#Ajax dynamically identifies the verification code.
"""
        if request.is_ajax():
            str = request.GET['response']    #注意大小写转换
            cs = CaptchaStore.objects.filter(response=str.lower(),
                                             hashkey=request.GET['hash_key'])
            if cs:
                json_data = {'status': 1}
            else:
                json_data = {'status': 0}
            return JsonResponse(json_data)
        else:
            json_data = {'status': 0}
            return JsonResponse(json_data)
"""


def ajax_val(request):
    """ Ajax dynamically identifies the verification code. """
    if request.is_ajax():
        str = request.GET['response']  # 注意大小写转换
        cs = CaptchaStore.objects.filter(response=str.lower(),
                                         hashkey=request.GET['hash_key'])
        if cs:
            json_data = {'status': 1}
        else:
            json_data = {'status': 0}
        return JsonResponse(json_data)
    else:
        json_data = {'status': 0}
        return JsonResponse(json_data)

class EditPage(View):

    def get(self, request, article_id):
        if not request.session.get('is_login', None):
            return redirect('/login/login1')
        page_form = forms.EditPage()
        if str(article_id) == '0':
            return render(request, 'login/edit_page.html', {'page_form': page_form})
        article = ContensInfo.objects.get(pk=article_id)
        data = {'title': article.title, 'content': article.content}
        page_form = forms.EditPage(data)
        return render(request, 'login/edit_page.html', locals())


class Content(View):

    def get(self, request, content_id):
        if not request.session.get('is_login', None):
            return redirect('/login/login1')
        message = "欢迎阅读"
        try:
            content = ContensInfo.objects.get(pk=content_id)
            return render(request, 'login/content.html', {'article': content})
        except:
            message = "查阅异常，请重试"
        return render(request, 'login/index.html', locals())


class EditAction(View):

    def post(self, request):
        article_id = request.POST.get('article_id', '0')
        page_form = forms.EditPage(request.POST)
        if page_form.is_valid():
            title = page_form.cleaned_data['title']
            content = page_form.cleaned_data['content']
            author_name = request.session.get('user_name')
            if str(article_id) == '0':
                #新建文章
                u = models.User.objects.get(name=author_name)     #异常捕获
                ContensInfo.objects.create(title=title, content=content, author=u)
                article = ContensInfo.objects.filter(author=u.id)
                return redirect('/login/index')
                #return render(request, 'login/index.html', {'all_content':
                # article})
            #修改文章
            article = ContensInfo.objects.get(pk=article_id)
            article.title = title
            article.content = content
            article.save()
        return redirect('/login/index')


class Delete(View):

    def get(self, request, article_id):
        if not request.session.get('is_login', None):
            return redirect('/login/login1')
        ContensInfo.objects.filter(pk=article_id).delete()
        return redirect('/login/index')
