from django.urls import path
from . import views

app_name = 'learning_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:lesson_id>/quiz/', views.quiz, name='quiz'),
    path('generate-lesson/', views.generate_lesson, name='generate_lesson'),
    path('progress/', views.progress, name='progress'),
    path('rewards/', views.rewards, name='rewards'),
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),
    path('register/', views.register, name='register'),
]
