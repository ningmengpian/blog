from django.db import models


class User(models.Model):
    gender = (
        ('male', '男'),
        ('female', '女'),
         )

    name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='女')
    create_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-create_time"]
        verbose_name = "用户"
        verbose_name_plural = "用户"


class ConfirmString(models.Model):
    code = models.CharField(max_length=256,)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name + ":   " + self.code

    class Meta:

        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


class ContensInfo(models.Model):
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    title = models.CharField(max_length=100, default='Title')
    content = models.CharField(max_length=1000, null=True)
    create_content_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + ":   " + self.author

    class Meta:
        ordering = ["-create_content_time"]
        verbose_name = "文章列表"
