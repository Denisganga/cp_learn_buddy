from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Lesson(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='lessons')
    description = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='lesson_images/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="URL to an animated video related to the lesson")
    video_title = models.CharField(max_length=200, blank=True, null=True)
    video_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    
    def __str__(self):
        return self.text[:50]

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'lesson')
        
    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='reward_images/')
    
    def __str__(self):
        return self.name

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"
class Exercise(models.Model):
    EMOTION_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('surprised', 'Surprised'),
        ('fearful', 'Fearful'),
        ('disgusted', 'Disgusted'),
        ('neutral', 'Neutral'),
        ('tired', 'Tired'),
        ('frustrated', 'Frustrated'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('challenging', 'Challenging'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)
    suitable_emotions = models.CharField(max_length=100, help_text="Comma-separated emotions this exercise is good for")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='easy')
    duration_minutes = models.IntegerField(default=5)
    benefits = models.TextField(help_text="Benefits of this exercise for children with cerebral palsy")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_emotions_list(self):
        return [emotion.strip() for emotion in self.suitable_emotions.split(',')]

class UserExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    emotion_at_start = models.CharField(max_length=50, blank=True, null=True)
    emotion_at_end = models.CharField(max_length=50, blank=True, null=True)
    date_completed = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title}"
class ActivityPlan(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    ACTIVITY_TYPES = [
        ('lesson', 'Learning Lesson'),
        ('exercise', 'Physical Exercise'),
        ('break', 'Rest Break'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_plans')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Plan: {self.title}"
    
    def get_activities_by_day(self):
        """Returns activities organized by day of week"""
        activities_by_day = {}
        for day in dict(self.DAYS_OF_WEEK).keys():
            activities_by_day[day] = self.activities.filter(day_of_week=day).order_by('time_slot')
        return activities_by_day

class PlanActivity(models.Model):
    TIME_SLOTS = [
        ('morning', 'Morning (8am-12pm)'),
        ('afternoon', 'Afternoon (12pm-4pm)'),
        ('evening', 'Evening (4pm-8pm)'),
    ]
    
    plan = models.ForeignKey(ActivityPlan, on_delete=models.CASCADE, related_name='activities')
    day_of_week = models.CharField(max_length=10, choices=ActivityPlan.DAYS_OF_WEEK)
    time_slot = models.CharField(max_length=10, choices=TIME_SLOTS)
    activity_type = models.CharField(max_length=10, choices=ActivityPlan.ACTIVITY_TYPES)
    duration_minutes = models.IntegerField(default=30)
    
    # References to specific activities (only one should be set based on activity_type)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    
    # For custom activities or breaks
    title = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('plan', 'day_of_week', 'time_slot')
        ordering = ['day_of_week', 'time_slot']
    
    def __str__(self):
        activity_name = self.get_activity_name()
        return f"{self.get_day_of_week_display()} {self.get_time_slot_display()}: {activity_name}"
    
    def get_activity_name(self):
        """Returns the name of the activity based on its type"""
        if self.activity_type == 'lesson' and self.lesson:
            return f"Lesson: {self.lesson.title}"
        elif self.activity_type == 'exercise' and self.exercise:
            return f"Exercise: {self.exercise.title}"
        elif self.title:
            return self.title
        else:
            return f"{self.get_activity_type_display()}"
    
    def get_activity_url(self):
        """Returns the URL to view the activity"""
        if self.activity_type == 'lesson' and self.lesson:
            return reverse('learning_app:lesson_detail', args=[self.lesson.id])
        elif self.activity_type == 'exercise' and self.exercise:
            # Assuming we pass the emotion parameter to get a consistent exercise
            return f"{reverse('learning_app:workout_recommendation')}?emotion=neutral"
        else:
            return None
class Avatar(models.Model):
    AVATAR_TYPES = [
        ('animal', 'Animal'),
        ('robot', 'Robot'),
        ('fantasy', 'Fantasy Character'),
        ('cartoon', 'Cartoon Character'),
    ]
    
    VOICE_TYPES = [
        ('friendly', 'Friendly'),
        ('cheerful', 'Cheerful'),
        ('calm', 'Calm'),
        ('encouraging', 'Encouraging'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar')
    name = models.CharField(max_length=50)
    avatar_type = models.CharField(max_length=20, choices=AVATAR_TYPES)
    character = models.CharField(max_length=50)  # e.g., "lion", "robot-blue", "wizard"
    voice_type = models.CharField(max_length=20, choices=VOICE_TYPES, default='friendly')
    color_scheme = models.CharField(max_length=20, default='blue')
    custom_greeting = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Avatar: {self.name}"
    
    def get_avatar_image_url(self):
        """Returns the URL for the avatar image"""
        return f"/static/images/avatars/{self.avatar_type}/{self.character}.png"
    
    def get_greeting(self):
        """Returns the avatar's greeting message"""
        if self.custom_greeting:
            return self.custom_greeting
        
        greetings = {
            'friendly': f"Hi there! I'm {self.name}, your learning buddy!",
            'cheerful': f"Hello! I'm {self.name}! Let's have fun learning together!",
            'calm': f"Welcome. I'm {self.name}, and I'm here to help you learn.",
            'encouraging': f"Hey there! I'm {self.name}! You're going to do great today!"
        }
        
        return greetings.get(self.voice_type, greetings['friendly'])
    
    def get_encouragement(self):
        """Returns a random encouragement message"""
        encouragements = [
            "You're doing great! Keep it up!",
            "Wow! You're making amazing progress!",
            "I believe in you! You can do it!",
            "That's the way! You're learning so much!",
            "Fantastic job! You're so smart!",
            "Keep going! You're on the right track!",
            "I'm so proud of you!",
            "You're a superstar learner!"
        ]
        
        import random
        return random.choice(encouragements)
    
    def get_celebration(self):
        """Returns a random celebration message"""
        celebrations = [
            "Hooray! You did it!",
            "Amazing job! You're awesome!",
            "Woohoo! That's fantastic!",
            "Congratulations! You're a champion!",
            "Yay! You've earned a big high-five!",
            "Incredible work! You should be so proud!",
            "That's a win! You're crushing it!",
            "Spectacular! You're a learning superstar!"
        ]
        
        import random
        return random.choice(celebrations)

class AvatarInteraction(models.Model):
    INTERACTION_TYPES = [
        ('greeting', 'Greeting'),
        ('encouragement', 'Encouragement'),
        ('celebration', 'Celebration'),
        ('tip', 'Learning Tip'),
        ('feedback', 'Feedback'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avatar_interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    message = models.TextField()
    context = models.CharField(max_length=100, blank=True, null=True)  # e.g., "lesson_complete", "quiz_start"
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Avatar {self.interaction_type} at {self.timestamp}"
