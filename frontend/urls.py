from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
	url(r'^$', views.LoginView.as_view(), name='login'),
	url(r'^login_user/$', views.login_user, name='login_user'),
	url(r'^recipe/$', views.recipe, name='recipe'),
	url(r'^logout_user/$', views.logout_user, name='logout_user'),
	url(r'^end/$', views.end, name='end'),
]