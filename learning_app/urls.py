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
    path('lesson/<int:lesson_id>/find-video/', views.find_video_for_lesson, name='find_video_for_lesson'),
    path('workout/', views.workout_recommendation, name='workout_recommendation'),
    path('workout/update-emotion/<int:exercise_id>/', views.update_exercise_emotion, name='update_exercise_emotion'),
    
    # Planning routes
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.create_plan, name='create_plan'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:plan_id>/add-activity/', views.add_activity, name='add_activity'),
    path('plans/activity/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    path('plans/activity/<int:activity_id>/complete/', views.mark_activity_complete, name='mark_activity_complete'),
    path('plans/<int:plan_id>/delete/', views.delete_plan, name='delete_plan'),
    
    # Avatar routes
    path('avatar/select/', views.avatar_selection, name='avatar_selection'),
    path('avatar/<int:avatar_id>/customize/', views.avatar_customize, name='avatar_customize'),
    path('avatar/speak/', views.avatar_speak, name='avatar_speak'),
]
