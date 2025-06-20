from django.contrib import admin
from .models import Category, Lesson, Quiz, Question, Answer, UserProgress, Reward, UserReward

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ('text', 'quiz')
    search_fields = ('text',)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3

class QuizAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ('title', 'lesson')
    search_fields = ('title',)

class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 1

class LessonAdmin(admin.ModelAdmin):
    inlines = [QuizInline]
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('name', 'description')
    search_fields = ('name',)

class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'score', 'last_activity')
    list_filter = ('completed', 'last_activity')
    search_fields = ('user__username', 'lesson__title')

class UserRewardAdmin(admin.ModelAdmin):
    list_display = ('user', 'reward', 'earned_at')
    list_filter = ('earned_at',)
    search_fields = ('user__username', 'reward__name')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(UserProgress, UserProgressAdmin)
admin.site.register(Reward)
admin.site.register(UserReward, UserRewardAdmin)
