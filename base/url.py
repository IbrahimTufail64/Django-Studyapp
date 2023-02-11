from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login_register/', views.LoginPage, name='login_page'),
    path('logout/', views.logoutUser, name='logout'),
    path('room/<str:pk>/', views.room, name='room'),
    path('profile/<str:pk>/', views.userProfile, name='user-profile'),
    path('form/', views.form, name='create-form'),
    path('update/<str:pk>/', views.update, name='update'),
    path('delete-form/<str:pk>/', views.deleteForm, name='delete-form'),
    path('delete-message/<str:pk>/', views.deleteMessage, name='delete-message'),
    path('edit-user/<str:pk>/', views.updateUser, name='update-user'),
    path('register/', views.registerPage, name='register')
]
