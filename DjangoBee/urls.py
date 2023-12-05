"""
URL configuration for DjangoBee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_user, name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('signup/', views.signup, name='signup'),
    path('login_required_message/', views.login_required_message, name='login_required_message'),
    path('overview/', login_required(views.overview), name='overview'),
    path('hives_place/<int:hives_place_id>/', login_required(views.hives_place), name='hives_place'),
    path('add_hives_place/', login_required(views.add_hives_place), name='add_hives_place'),
    path('add_hive/<str:hives_place_id>', login_required(views.add_hive), name='add_hive'),
    path('visits/<str:hive_id>/', login_required(views.visits), name='visits'),
    path('add_visit/<str:hive_id>/', login_required(views.add_visit), name='add_visit'),
    path('mothers/<str:mother_id>/', login_required(views.mothers), name='mothers'),
    path('add_mother/<str:hive_id>/', login_required(views.add_mother), name='add_mother'),
    path('erase_mother/<str:mother_id>/', login_required(views.erase_mother), name='erase_mother'),
    path('remove_hives_place/<str:hives_place_id>/', login_required(views.remove_hives_place), name='remove_hives_place'),
    path('remove_hive/<str:hive_id>/', login_required(views.remove_hive), name='remove_hive'),
    path('move_hive/<str:old_hives_place>/', login_required(views.move_hive), name='move_hive')

]
