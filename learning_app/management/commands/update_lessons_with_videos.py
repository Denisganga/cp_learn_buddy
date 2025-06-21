from django.core.management.base import BaseCommand
from learning_app.models import Lesson
from learning_app.views import fetch_cartoon_video

class Command(BaseCommand):
    help = 'Updates existing lessons with relevant cartoon videos'

    def handle(self, *args, **options):
        # Get all lessons without videos
        lessons_without_videos = Lesson.objects.filter(video_url__isnull=True) | Lesson.objects.filter(video_url='')
        
        self.stdout.write(self.style.SUCCESS(f'Found {lessons_without_videos.count()} lessons without videos'))
        
        # Update each lesson with a video
        for lesson in lessons_without_videos:
            # Get the topic from either the category name or the lesson title
            topic = lesson.category.name
            
            # Find a relevant video
            video_data = fetch_cartoon_video(topic)
            
            if video_data:
                lesson.video_url = video_data["url"]
                lesson.video_title = video_data["title"]
                lesson.video_description = video_data["description"]
                lesson.save()
                
                self.stdout.write(self.style.SUCCESS(f'Added video to lesson: {lesson.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Could not find a video for lesson: {lesson.title}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully updated lessons with videos'))
