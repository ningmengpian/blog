from django.urls import re_path
from . import views

app_name = 'login'
urlpatterns = [
    re_path(r'^index/$', views.Index.as_view(), name='index'),
    re_path(r'^login1/$', views.Login.as_view(), name='login1'),
    re_path(r'^register/$', views.Register.as_view(), name='register'),
    re_path(r'^logout/$', views.Logout.as_view(), name='logout'),
    re_path(r'^confirm/$', views.UserConfirm.as_view(), name='confirm'),
    #re_path(r'^ajax_val/$', views.AjaxVal.as_view(), name='ajax_val'),
    re_path(r'^ajax_val/$', views.ajax_val, name='ajax_val'),
    re_path(r'^edit_page/(?P<article_id>[0-9]+)$', views.EditPage.as_view(),
            name='edit_page'),
    re_path(r'^edit_page/$', views.EditAction.as_view(), name='edit_action'),
    re_path(r'^content/(?P<content_id>[0-9]+)$', views.Content.as_view(),
            name='content'),
    re_path(r'^delete/(?P<article_id>[0-9]+)$', views.Delete.as_view(),
            name='delete')
    ]