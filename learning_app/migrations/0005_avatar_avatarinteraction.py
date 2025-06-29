# Generated by Django 5.2.3 on 2025-06-21 14:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning_app', '0004_activityplan_planactivity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Avatar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('avatar_type', models.CharField(choices=[('animal', 'Animal'), ('robot', 'Robot'), ('fantasy', 'Fantasy Character'), ('cartoon', 'Cartoon Character')], max_length=20)),
                ('character', models.CharField(max_length=50)),
                ('voice_type', models.CharField(choices=[('friendly', 'Friendly'), ('cheerful', 'Cheerful'), ('calm', 'Calm'), ('encouraging', 'Encouraging')], default='friendly', max_length=20)),
                ('color_scheme', models.CharField(default='blue', max_length=20)),
                ('custom_greeting', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='avatar', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AvatarInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('greeting', 'Greeting'), ('encouragement', 'Encouragement'), ('celebration', 'Celebration'), ('tip', 'Learning Tip'), ('feedback', 'Feedback')], max_length=20)),
                ('message', models.TextField()),
                ('context', models.CharField(blank=True, max_length=100, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='avatar_interactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
