from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from django.utils import timezone
from .models import Category, Lesson, Quiz, Question, Answer, UserProgress, Reward, UserReward, Exercise, UserExercise, ActivityPlan, PlanActivity, Avatar, AvatarInteraction
import google.generativeai as genai
import json
import os
import base64
import requests
import urllib.parse
import markdown
import re
from gtts import gTTS
import speech_recognition as sr
import tempfile
import uuid
import random

def fetch_image_from_unsplash(query):
    """Fetch an image from Unsplash based on the query"""
    try:
        # Using the Unsplash Source API which doesn't require authentication
        # This is a simple way to get images for educational purposes
        url = f"https://source.unsplash.com/800x600/?{urllib.parse.quote(query)}"
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
        return None

def fetch_cartoon_video(topic):
    """
    Find a relevant cartoon video for the given topic from YouTube.
    This function returns an embedded YouTube video URL based on the topic.
    """
    # Expanded list of educational cartoon videos by topic
    educational_videos = {
        # Numbers and counting
        "numbers": [
            "https://www.youtube.com/embed/bGetqbqDVaA",  # Count to 100
            "https://www.youtube.com/embed/e0dJWfQHF8Y",  # Count to 20
            "https://www.youtube.com/embed/D0Ajq682yrA",  # Count to 10
            "https://www.youtube.com/embed/DR-cfDsHCGA",  # Number songs
        ],
        # Alphabet and letters
        "alphabet": [
            "https://www.youtube.com/embed/hq3yfQnllfQ",  # ABC Song
            "https://www.youtube.com/embed/36IBDpTRVNE",  # Phonics Song
            "https://www.youtube.com/embed/cR-Qr1V8e_w",  # Letter Sounds
            "https://www.youtube.com/embed/Nw_6ZaV3KpE",  # ABC Phonics
        ],
        # Colors
        "colors": [
            "https://www.youtube.com/embed/xz5rA5wKoTQ",  # Colors for Children
            "https://www.youtube.com/embed/ybt2jhCQ3lA",  # Rainbow Colors
            "https://www.youtube.com/embed/jYAWf8Y91hA",  # Color Mixing
            "https://www.youtube.com/embed/tkpfg-1FJLU",  # Colors Song
        ],
        # Shapes
        "shapes": [
            "https://www.youtube.com/embed/dsR0h50BiFQ",  # Shapes Cartoon
            "https://www.youtube.com/embed/OEbRDtCAFdU",  # 3D Shapes
            "https://www.youtube.com/embed/AnoNb2OMQ6s",  # Shape Songs
            "https://www.youtube.com/embed/zUfqgdtttVQ",  # Shapes for Kids
        ],
        # Animals
        "animals": [
            "https://www.youtube.com/embed/CA6Mofzh7jo",  # Animal Cartoon
            "https://www.youtube.com/embed/wCfWmlnJl-A",  # Farm Animals
            "https://www.youtube.com/embed/p5qwOxlvyhk",  # Wild Animals
            "https://www.youtube.com/embed/25_u1GzruQM",  # Animal Sounds
        ],
        # Space and planets
        "planets": [
            "https://www.youtube.com/embed/libKVRa01L8",  # Solar System
            "https://www.youtube.com/embed/mQrlgH97v94",  # The Planets
            "https://www.youtube.com/embed/Qd6nLM2QlWw",  # Space for Kids
            "https://www.youtube.com/embed/F2prtmPEjOc",  # Outer Space
        ],
        # Weather
        "weather": [
            "https://www.youtube.com/embed/RmSKsyJ15yg",  # Weather Cartoon
            "https://www.youtube.com/embed/tfAB4BXSHOA",  # Weather Types
            "https://www.youtube.com/embed/XcW9Ct000yY",  # Seasons
            "https://www.youtube.com/embed/ksGiLaIx39c",  # Weather for Kids
        ],
        # Human body
        "body": [
            "https://www.youtube.com/embed/BjUkL7lELDI",  # Human Body
            "https://www.youtube.com/embed/zKSqg-l_JjI",  # Body Parts
            "https://www.youtube.com/embed/SUt8q0EKbms",  # Human Body Systems
            "https://www.youtube.com/embed/AXQZwmv5MQo",  # My Body
        ],
        # Food
        "food": [
            "https://www.youtube.com/embed/RE5tvaveVak",  # Healthy Foods
            "https://www.youtube.com/embed/mVE9pYdwX-I",  # Food Groups
            "https://www.youtube.com/embed/L9ymkJK2QCU",  # Fruits and Vegetables
            "https://www.youtube.com/embed/fE8lezHs19s",  # Nutrition
        ],
        # Transportation
        "transportation": [
            "https://www.youtube.com/embed/Ut-HbauKzDw",  # Transportation Vehicles
            "https://www.youtube.com/embed/biX7NNxw_w8",  # Cars and Trucks
            "https://www.youtube.com/embed/Spc9I5Xk3dc",  # Trains
            "https://www.youtube.com/embed/gUdnsvvhnzQ",  # Vehicles
        ],
        # Emotions
        "emotions": [
            "https://www.youtube.com/embed/akTRWJZMks0",  # Feelings and Emotions
            "https://www.youtube.com/embed/dOkyKyVFnSs",  # Emotions Song
            "https://www.youtube.com/embed/ZHS7vCdBeus",  # Feelings
            "https://www.youtube.com/embed/l4WNrvVjiTw",  # Emotions for Kids
        ],
        # Science
        "science": [
            "https://www.youtube.com/embed/K0QmXRmKkmk",  # Science Experiments
            "https://www.youtube.com/embed/6qZH5p3ZTSs",  # States of Matter
            "https://www.youtube.com/embed/AqchPrhezxQ",  # Water Cycle
            "https://www.youtube.com/embed/3yrikH2QEFA",  # Simple Machines
        ],
        # Math
        "math": [
            "https://www.youtube.com/embed/bGetqbqDVaA",  # Counting
            "https://www.youtube.com/embed/uedvwH6Ay18",  # Addition
            "https://www.youtube.com/embed/GJBtMLdLOlc",  # Subtraction
            "https://www.youtube.com/embed/FJ5qLWP3Fqo",  # Basic Math
        ],
        # Music
        "music": [
            "https://www.youtube.com/embed/XqZsoesa55w",  # Baby Shark
            "https://www.youtube.com/embed/yCjJyiqpAuU",  # Musical Instruments
            "https://www.youtube.com/embed/NwT5oX_mqS0",  # Nursery Rhymes
            "https://www.youtube.com/embed/JV-D_K4dxcQ",  # Children's Songs
        ],
        # Default videos for general education
        "default": [
            "https://www.youtube.com/embed/hq3yfQnllfQ",  # ABC Song
            "https://www.youtube.com/embed/bGetqbqDVaA",  # Counting
            "https://www.youtube.com/embed/xz5rA5wKoTQ",  # Colors
            "https://www.youtube.com/embed/CA6Mofzh7jo",  # Animals
            "https://www.youtube.com/embed/dsR0h50BiFQ",  # Shapes
        ]
    }
    
    # Convert topic to lowercase for matching
    topic_lower = topic.lower()
    
    # Check for keyword matches in the topic
    for category, videos in educational_videos.items():
        if category in topic_lower or any(word in topic_lower for word in category.split()):
            # Return a random video from the matching category
            import random
            video_url = random.choice(videos)
            
            # Create video metadata
            video_title = f"{topic.title()} Cartoon for Kids"
            video_description = f"Watch this fun cartoon about {topic.lower()} and learn while having fun!"
            
            return {
                "url": video_url,
                "title": video_title,
                "description": video_description
            }
    
    # If no specific match, return a default educational video
    import random
    video_url = random.choice(educational_videos["default"])
    
    return {
        "url": video_url,
        "title": f"Educational Cartoon for {topic.title()}",
        "description": f"Watch this fun educational cartoon to learn more about {topic.lower()}!"
    }

def fetch_image_from_pexels(query):
    """Fetch an image from Pexels based on the query"""
    try:
        # Using a placeholder image with the query text
        # In a production app, you would use the Pexels API with an API key
        url = f"https://via.placeholder.com/800x600?text={urllib.parse.quote(query)}"
        response = requests.get(url, stream=True)
        
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
        return None

def format_lesson_content(content):
    """
    Format the lesson content by converting markdown to HTML and adding
    additional formatting for better readability and interactivity.
    """
    if not content:
        return ""
    
    # First, ensure we have proper markdown formatting
    # Replace any plain text patterns with markdown equivalents
    
    # Add line breaks to ensure proper paragraph separation
    content = content.replace('\n', '\n\n')
    
    # Format section titles that don't have markdown headings
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Convert section titles to proper markdown headings
        if re.match(r'^[A-Z][\w\s]{2,30}:$', line.strip()):
            formatted_lines.append(f"## {line.strip()}")
        # Convert questions to styled format
        elif '?' in line and len(line) < 100:
            formatted_lines.append(f"### 🤔 {line.strip()}")
        # Add emoji to "Let's" or "Now" beginnings to make them stand out
        elif line.strip().startswith("Let's") or line.strip().startswith("Now"):
            formatted_lines.append(f"### 🌟 {line.strip()}")
        # Add emphasis to important points
        elif "important" in line.lower() or "remember" in line.lower():
            formatted_lines.append(f"**🔑 {line.strip()}**")
        else:
            formatted_lines.append(line)
    
    md_content = '\n'.join(formatted_lines)
    
    # Convert markdown to HTML with extensions for tables, code blocks, etc.
    html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    
    # Add Bootstrap styling and interactive elements
    
    # Style headings
    html_content = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="display-4 text-primary fw-bold mb-4">\1</h1>', html_content)
    html_content = re.sub(r'<h2>(.*?)</h2>', r'<h2 class="h3 text-primary fw-bold mt-5 mb-4 border-bottom pb-2">\1</h2>', html_content)
    html_content = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="h4 text-success fw-bold mt-4 mb-3">\1</h3>', html_content)
    
    # Style paragraphs
    html_content = re.sub(r'<p>(.*?)</p>', r'<p class="fs-5 mb-4">\1</p>', html_content)
    
    # Style lists
    html_content = re.sub(r'<ul>', r'<ul class="fs-5 mb-4 styled-list">', html_content)
    html_content = re.sub(r'<ol>', r'<ol class="fs-5 mb-4 styled-list">', html_content)
    html_content = re.sub(r'<li>(.*?)</li>', r'<li class="mb-2">\1</li>', html_content)
    
    # Add interactive elements to questions
    html_content = re.sub(
        r'<p class="fs-5 mb-4">(.*?\?)</p>',
        r'<div class="interactive-question alert alert-info p-4 mb-4 rounded-3 shadow-sm border-start border-info border-5">'
        r'<p class="fs-5 mb-2">\1</p>'
        r'<button class="btn btn-info btn-sm mt-2" onclick="speakText(\'\1\')">'
        r'<i class="fas fa-volume-up me-2"></i>Listen</button></div>',
        html_content
    )
    
    # Add special styling to paragraphs with bold text
    html_content = re.sub(
        r'<p class="fs-5 mb-4"><strong>(.*?)</strong></p>',
        r'<p class="fs-5 mb-4 alert alert-warning p-3 rounded-3 border-start border-warning border-5"><strong>\1</strong></p>',
        html_content
    )
    
    # Add click-to-speak to all elements
    html_content = re.sub(
        r'<p class="fs-5 mb-4">(.*?)</p>',
        r'<p class="fs-5 mb-4 clickable-paragraph" onclick="speakText(this.textContent)">\1</p>',
        html_content
    )
    
    html_content = re.sub(
        r'<h([1-6])(.*?)>(.*?)</h\1>',
        r'<h\1\2 class="clickable-heading" onclick="speakText(this.textContent)">\3</h\1>',
        html_content
    )
    
    html_content = re.sub(
        r'<li class="mb-2">(.*?)</li>',
        r'<li class="mb-2 clickable-item" onclick="speakText(this.textContent)">\1</li>',
        html_content
    )
    
    # Wrap the content in a styled container
    html_content = f'''
    <div class="lesson-formatted-content p-4 bg-light rounded-3 shadow-sm">
        {html_content}
        <div class="mt-5 p-3 bg-primary bg-opacity-10 rounded-3 border border-primary">
            <h3 class="h5 text-primary">What did you learn?</h3>
            <p class="fs-5">Think about what you learned in this lesson. Can you remember the main points?</p>
            <button class="btn btn-primary" onclick="speakText('What did you learn in this lesson? Can you remember the main points?')">
                <i class="fas fa-volume-up me-2"></i>Listen
            </button>
        </div>
    </div>
    '''
    
    return html_content

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'learning_app/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('learning_app:home')

def home(request):
    categories = Category.objects.all()[:6]
    return render(request, 'learning_app/home.html', {'categories': categories})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'learning_app/category_list.html', {'categories': categories})

def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    lessons = category.lessons.all()
    return render(request, 'learning_app/category_detail.html', {
        'category': category,
        'lessons': lessons
    })

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    return render(request, 'learning_app/lesson_detail.html', {'lesson': lesson})

def quiz(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    quiz = lesson.quizzes.first()
    
    if request.method == 'POST':
        score = 0
        total = 0
        for question in quiz.questions.all():
            total += 1
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id and question.answers.get(id=answer_id).is_correct:
                score += 1
        
        # Update user progress
        if request.user.is_authenticated:
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )
            progress.score = score
            progress.completed = True
            progress.save()
            
            # Check if user deserves a reward
            if score == total:
                reward, created = Reward.objects.get_or_create(
                    name="Perfect Score",
                    defaults={
                        'description': "You got a perfect score on a quiz!"
                    }
                )
                
                # If this is a new reward, fetch an image for it
                if created:
                    reward_image = fetch_image_from_unsplash("trophy award gold star")
                    if reward_image:
                        image_filename = f"reward_{uuid.uuid4()}.jpg"
                        reward.image.save(image_filename, ContentFile(reward_image), save=True)
                
                UserReward.objects.get_or_create(user=request.user, reward=reward)
        
        return render(request, 'learning_app/quiz_results.html', {
            'lesson': lesson,
            'score': score,
            'total': total
        })
    
    return render(request, 'learning_app/quiz.html', {
        'lesson': lesson,
        'quiz': quiz
    })

@login_required
def generate_lesson(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        age_group = request.POST.get('age_group')
        difficulty = request.POST.get('difficulty')
        
        # Generate lesson content using Gemini
        prompt = f"""
        Create an educational lesson for children with cerebral palsy about {topic}.
        Age group: {age_group}
        Difficulty level: {difficulty}
        
        The lesson should include:
        1. A title
        2. A brief introduction
        3. Main content with simple, clear explanations, organized into sections
        4. 3 quiz questions with multiple choice answers (4 options each)
        5. A prompt for an image that would help illustrate this topic (be specific)
        
        Format the response as JSON with the following structure:
        {{
            "title": "Lesson title",
            "introduction": "Brief introduction",
            "content": "Main lesson content with proper structure. Use markdown formatting: ## for section headings, ** for important text, * for bullet points. Include at least 3 sections with clear headings. Add questions throughout the content to engage the reader. Use short paragraphs with line breaks between them.",
            "image_prompt": "Detailed description for generating an image",
            "quiz": [
                {{
                    "question": "Question 1",
                    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                    "correct_answer": 0
                }},
                ...
            ]
        }}
        
        Make sure the content is:
        - Very simple to understand (appropriate for {age_group})
        - Uses short sentences and paragraphs
        - Has colorful descriptions and engaging language
        - Is encouraging and positive
        - Includes interactive elements like "Can you point to...?" or "What do you see?"
        - Has clear section headings that end with colons
        - Includes important points marked with ** for emphasis
        - Has at least one numbered list or bullet points
        - Includes at least 2-3 questions throughout the content
        
        IMPORTANT: Your response must be valid JSON only, with no additional text before or after the JSON.
        """
        
        try:
            # Configure the Gemini API
            genai.configure(api_key="AIzaSyCyOTCnErddha6q1njBGrQ-rhzybinKDUs")
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Debug the response
            print("Raw response:", response.text)
            
            # Try to extract JSON from the response
            # Sometimes the model might include markdown code blocks or other text
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response.text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # If no code block, try to find JSON directly
                json_str = response.text.strip()
            
            # Parse the JSON
            lesson_data = json.loads(json_str)
            
            # Create a default lesson structure if any required fields are missing
            if 'title' not in lesson_data:
                lesson_data['title'] = f"Lesson about {topic}"
            
            if 'introduction' not in lesson_data:
                lesson_data['introduction'] = f"Let's learn about {topic}!"
                
            if 'content' not in lesson_data:
                lesson_data['content'] = f"This is a lesson about {topic}."
                
            if 'image_prompt' not in lesson_data:
                lesson_data['image_prompt'] = f"A colorful, simple illustration of {topic} for children."
                
            if 'quiz' not in lesson_data or not lesson_data['quiz']:
                lesson_data['quiz'] = [
                    {
                        "question": f"What are we learning about today?",
                        "options": [f"{topic}", "Animals", "Colors", "Numbers"],
                        "correct_answer": 0
                    }
                ]
            
            # Create category if it doesn't exist
            category, created = Category.objects.get_or_create(
                name=topic.title(),
                defaults={'description': f"Lessons about {topic}"}
            )
            
            # If this is a new category, fetch an image for it
            if created:
                category_image = fetch_image_from_unsplash(topic)
                if category_image:
                    image_filename = f"category_{uuid.uuid4()}.jpg"
                    category.image.save(image_filename, ContentFile(category_image), save=True)
            
            # Create the lesson
            lesson = Lesson.objects.create(
                title=lesson_data['title'],
                category=category,
                description=lesson_data['introduction'],
                content=format_lesson_content(lesson_data['content'])
            )
            
            # Fetch and save an image for the lesson
            image_query = lesson_data.get('image_prompt', topic)
            image_content = fetch_image_from_unsplash(image_query)
            if image_content:
                image_filename = f"{uuid.uuid4()}.jpg"
                lesson.image.save(image_filename, ContentFile(image_content), save=True)
            
            # Find and add a relevant cartoon video
            video_data = fetch_cartoon_video(topic)
            if video_data:
                lesson.video_url = video_data["url"]
                lesson.video_title = video_data["title"]
                lesson.video_description = video_data["description"]
                lesson.save()
            
            # Create quiz
            quiz = Quiz.objects.create(
                lesson=lesson,
                title=f"Quiz: {lesson_data['title']}"
            )
            
            # Create questions and answers
            for q_data in lesson_data['quiz']:
                question = Question.objects.create(
                    quiz=quiz,
                    text=q_data['question']
                )
                
                # Fetch and save an image for the question
                # Extract keywords from the question for better image search
                question_keywords = q_data['question'].split()[:3]  # First 3 words
                question_query = ' '.join(question_keywords) + ' ' + topic
                question_image = fetch_image_from_unsplash(question_query)
                if question_image:
                    image_filename = f"question_{uuid.uuid4()}.jpg"
                    question.image.save(image_filename, ContentFile(question_image), save=True)
                
                for i, option in enumerate(q_data.get('options', [])):
                    Answer.objects.create(
                        question=question,
                        text=option,
                        is_correct=(i == q_data.get('correct_answer', 0))
                    )
            
            return redirect('learning_app:lesson_detail', lesson_id=lesson.id)
            
        except Exception as e:
            import traceback
            print("Error generating lesson:", str(e))
            print(traceback.format_exc())
            return render(request, 'learning_app/generate_lesson.html', {
                'error': str(e),
                'topic': topic,
                'age_group': age_group,
                'difficulty': difficulty
            })
    
    return render(request, 'learning_app/generate_lesson.html')

@login_required
def progress(request):
    user_progress = UserProgress.objects.filter(user=request.user).order_by('-last_activity')
    return render(request, 'learning_app/progress.html', {'progress': user_progress})

@login_required
def rewards(request):
    user_rewards = UserReward.objects.filter(user=request.user).order_by('-earned_at')
    return render(request, 'learning_app/rewards.html', {'rewards': user_rewards})

@csrf_exempt
def text_to_speech(request):
    if request.method == 'POST':
        text = request.POST.get('text', '')
        
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.close()
            
            # Generate speech with a child-like voice
            tts = gTTS(text=text, lang='en', tld='com', slow=False)
            tts.save(temp_file.name)
            
            # Create media directory if it doesn't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tts'), exist_ok=True)
            
            # Create a unique filename
            filename = f"tts_{uuid.uuid4()}.mp3"
            filepath = os.path.join(settings.MEDIA_ROOT, 'tts', filename)
            
            # Move the temporary file to the media directory
            os.rename(temp_file.name, filepath)
            
            return JsonResponse({
                'success': True,
                'audio_url': f"{settings.MEDIA_URL}tts/{filename}"
            })
        except Exception as e:
            print("Error in text-to-speech:", str(e))
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def speech_to_text(request):
    if request.method == 'POST':
        try:
            audio_data = request.FILES.get('audio')
            
            if not audio_data:
                return JsonResponse({'success': False, 'error': 'No audio data provided'})
            
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_file.close()
            
            # Save the audio data to the temporary file
            with open(temp_file.name, 'wb') as f:
                for chunk in audio_data.chunks():
                    f.write(chunk)
            
            # Use speech recognition to convert speech to text
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_file.name) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio)
            
            # Clean up the temporary file
            os.unlink(temp_file.name)
            
            return JsonResponse({'success': True, 'text': text})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
def find_video_for_lesson(request, lesson_id):
    """
    AJAX endpoint to find a video for a lesson
    """
    if request.method == 'POST':
        try:
            lesson = get_object_or_404(Lesson, id=lesson_id)
            
            # Get the topic from either the category name or the lesson title
            topic = lesson.category.name
            
            # Find a relevant video
            video_data = fetch_cartoon_video(topic)
            
            if video_data:
                lesson.video_url = video_data["url"]
                lesson.video_title = video_data["title"]
                lesson.video_description = video_data["description"]
                lesson.save()
                
                return JsonResponse({
                    'success': True,
                    'video_url': lesson.video_url,
                    'video_title': lesson.video_title,
                    'video_description': lesson.video_description
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Could not find a video for this lesson'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
def fetch_exercise_video(emotion, difficulty='easy'):
    """
    Find appropriate exercise videos based on the detected emotion and difficulty level.
    This function returns YouTube video URLs for exercises suitable for children with cerebral palsy.
    """
    # Dictionary mapping emotions to appropriate exercise types
    emotion_exercise_map = {
        'happy': ['fun', 'energetic', 'dance', 'playful'],
        'sad': ['gentle', 'calming', 'mood-lifting', 'mindful'],
        'angry': ['calming', 'relaxation', 'breathing', 'stretching'],
        'surprised': ['focus', 'balance', 'coordination', 'mindful'],
        'fearful': ['gentle', 'reassuring', 'simple', 'guided'],
        'disgusted': ['distraction', 'fun', 'engaging', 'playful'],
        'neutral': ['balanced', 'variety', 'general', 'mixed'],
        'tired': ['energizing', 'gentle', 'awakening', 'short'],
        'frustrated': ['releasing', 'simple', 'achievable', 'confidence-building']
    }
    
    # Dictionary of exercise videos organized by emotion and difficulty
    exercise_videos = {
        # Happy exercises
        'happy': {
            'easy': [
                {
                    'url': 'https://www.youtube.com/embed/JoF_d5sgGgc',
                    'title': 'Fun Dance Exercises for Kids',
                    'description': 'Enjoy these simple dance moves that will make you smile!'
                },
                {
                    'url': 'https://www.youtube.com/embed/388Q44ReOWE',
                    'title': 'Happy Movement Games',
                    'description': 'Simple and fun movement games to keep the joy flowing.'
                }
            ],
            'medium': [
                {
                    'url': 'https://www.youtube.com/embed/fpD9Mvjznf4',
                    'title': 'Dance Along Workout',
                    'description': 'Follow along with this upbeat dance routine for kids.'
                }
            ],
            'challenging': [
                {
                    'url': 'https://www.youtube.com/embed/ymigWt5TOV8',
                    'title': 'Energetic Movement Challenge',
                    'description': 'A more challenging but fun dance workout for kids.'
                }
            ]
        },
        
        # Sad exercises
        'sad': {
            'easy': [
                {
                    'url': 'https://www.youtube.com/embed/cyvuaL_2avY',
                    'title': 'Gentle Mood-Lifting Stretches',
                    'description': 'Simple stretches to help lift your mood and make you feel better.'
                },
                {
                    'url': 'https://www.youtube.com/embed/Bk_qU7l-fcU',
                    'title': 'Calming Movement for Kids',
                    'description': 'Gentle movements to help when you\'re feeling down.'
                }
            ],
            'medium': [
                {
                    'url': 'https://www.youtube.com/embed/8rp5bpFIUpg',
                    'title': 'Yoga for Better Mood',
                    'description': 'Kid-friendly yoga poses to help improve your mood.'
                }
            ],
            'challenging': [
                {
                    'url': 'https://www.youtube.com/embed/40SZl84Lr7A',
                    'title': 'Expressive Movement Therapy',
                    'description': 'Express your feelings through movement and feel better.'
                }
            ]
        },
        
        # Angry exercises
        'angry': {
            'easy': [
                {
                    'url': 'https://www.youtube.com/embed/DSgOW879jjA',
                    'title': 'Calming Breathing Exercises',
                    'description': 'Simple breathing techniques to help manage anger.'
                },
                {
                    'url': 'https://www.youtube.com/embed/YFdZXwE6fRE',
                    'title': 'Gentle Stretches for Calm',
                    'description': 'Easy stretches to release tension when feeling angry.'
                }
            ],
            'medium': [
                {
                    'url': 'https://www.youtube.com/embed/bRkILioT_NA',
                    'title': 'Relaxation Movement Sequence',
                    'description': 'A sequence of movements to help release anger and find calm.'
                }
            ],
            'challenging': [
                {
                    'url': 'https://www.youtube.com/embed/aJzj_b7G7i8',
                    'title': 'Anger Release Exercise Routine',
                    'description': 'A more intensive routine to help channel and release anger safely.'
                }
            ]
        },
        
        # Neutral exercises - good for any emotion
        'neutral': {
            'easy': [
                {
                    'url': 'https://www.youtube.com/embed/2n7FOBFMvXg',
                    'title': 'Basic Stretches for Kids',
                    'description': 'Simple stretching exercises suitable for children with cerebral palsy.'
                },
                {
                    'url': 'https://www.youtube.com/embed/nRNBzGM2JE4',
                    'title': 'Seated Exercises for Kids',
                    'description': 'Gentle exercises that can be done while seated.'
                }
            ],
            'medium': [
                {
                    'url': 'https://www.youtube.com/embed/ybPwuaGoa9E',
                    'title': 'Balance and Coordination Exercises',
                    'description': 'Fun exercises to improve balance and coordination.'
                }
            ],
            'challenging': [
                {
                    'url': 'https://www.youtube.com/embed/wK99lII1oFM',
                    'title': 'Strength Building for Kids',
                    'description': 'Exercises to build strength adapted for different abilities.'
                }
            ]
        },
        
        # Default exercises if emotion is not recognized
        'default': {
            'easy': [
                {
                    'url': 'https://www.youtube.com/embed/2n7FOBFMvXg',
                    'title': 'Basic Stretches for Kids',
                    'description': 'Simple stretching exercises suitable for children with cerebral palsy.'
                }
            ],
            'medium': [
                {
                    'url': 'https://www.youtube.com/embed/ybPwuaGoa9E',
                    'title': 'Balance and Coordination Exercises',
                    'description': 'Fun exercises to improve balance and coordination.'
                }
            ],
            'challenging': [
                {
                    'url': 'https://www.youtube.com/embed/wK99lII1oFM',
                    'title': 'Strength Building for Kids',
                    'description': 'Exercises to build strength adapted for different abilities.'
                }
            ]
        }
    }
    
    # Map other emotions to the main categories
    emotion_mapping = {
        'surprised': 'neutral',
        'fearful': 'sad',
        'disgusted': 'angry',
        'tired': 'sad',
        'frustrated': 'angry'
    }
    
    # Normalize the emotion
    emotion = emotion.lower()
    if emotion in emotion_mapping:
        emotion = emotion_mapping[emotion]
    
    if emotion not in exercise_videos:
        emotion = 'default'
    
    # Ensure difficulty is valid
    if difficulty not in ['easy', 'medium', 'challenging']:
        difficulty = 'easy'
    
    # Get videos for the emotion and difficulty
    videos = exercise_videos.get(emotion, {}).get(difficulty, [])
    
    # If no videos found for the specific difficulty, fall back to easy
    if not videos:
        videos = exercise_videos.get(emotion, {}).get('easy', [])
    
    # If still no videos, use default
    if not videos:
        videos = exercise_videos['default']['easy']
    
    # Return a random video from the available options
    import random
    return random.choice(videos)

def workout_recommendation(request):
    """
    View to recommend exercises based on detected emotion
    """
    # Default emotion if none detected
    current_emotion = 'neutral'
    
    # Get emotion from request if available
    if request.method == 'POST':
        current_emotion = request.POST.get('emotion', current_emotion)
    
    # Get user's preferred difficulty level (could be stored in user profile)
    difficulty = 'easy'  # Default to easy
    
    # Find appropriate exercise video
    exercise_video = fetch_exercise_video(current_emotion, difficulty)
    
    # Check if this exercise already exists in our database
    exercise, created = Exercise.objects.get_or_create(
        video_url=exercise_video['url'],
        defaults={
            'title': exercise_video['title'],
            'description': exercise_video['description'],
            'suitable_emotions': current_emotion,
            'difficulty': difficulty,
            'benefits': 'This exercise helps improve mobility, coordination, and mood for children with cerebral palsy.'
        }
    )
    
    # Initialize user_exercise and previous_exercises
    user_exercise = None
    previous_exercises = []
    
    # If user is authenticated, record the exercise and get history
    if request.user.is_authenticated:
        # Record that this exercise was recommended to the user
        user_exercise, created = UserExercise.objects.get_or_create(
            user=request.user,
            exercise=exercise,
            defaults={
                'emotion_at_start': current_emotion
            }
        )
        
        # Get previous exercises for this user
        previous_exercises = UserExercise.objects.filter(
            user=request.user
        ).order_by('-date_completed')[:5]
    
    context = {
        'exercise': exercise,
        'current_emotion': current_emotion,
        'previous_exercises': previous_exercises,
        'emotion_description': get_emotion_description(current_emotion),
        'user_exercise': user_exercise
    }
    
    return render(request, 'learning_app/workout.html', context)

def get_emotion_description(emotion):
    """
    Returns a child-friendly description of the emotion and what exercises might help
    """
    descriptions = {
        'happy': "You're feeling happy! Let's channel that positive energy into fun movements!",
        'sad': "You seem a bit sad. These gentle exercises can help lift your mood.",
        'angry': "You might be feeling frustrated. These calming movements can help you feel better.",
        'surprised': "You look surprised! Let's focus that energy with some fun coordination exercises.",
        'fearful': "You might be feeling a little scared. These gentle exercises can help you feel safe and calm.",
        'disgusted': "Let's try some fun movements to shift your focus to something enjoyable!",
        'neutral': "Let's do some exercises that are good for your body and mind!",
        'tired': "You seem a bit tired. These gentle energizing movements might help you feel more awake.",
        'frustrated': "You might be feeling frustrated. These exercises can help you feel more in control."
    }
    
    return descriptions.get(emotion.lower(), descriptions['neutral'])

@csrf_exempt
def update_exercise_emotion(request, exercise_id):
    """
    AJAX endpoint to update the emotion after completing an exercise
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            emotion = data.get('emotion', 'neutral')
            
            user_exercise = get_object_or_404(UserExercise, id=exercise_id, user=request.user)
            user_exercise.emotion_at_end = emotion
            user_exercise.completed = True
            user_exercise.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Emotion updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
@login_required
def plan_list(request):
    """
    View to list all activity plans for the user
    """
    plans = ActivityPlan.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'plans': plans,
    }
    
    return render(request, 'learning_app/plan_list.html', context)

@login_required
def plan_detail(request, plan_id):
    """
    View to show details of a specific plan
    """
    plan = get_object_or_404(ActivityPlan, id=plan_id, user=request.user)
    activities_by_day = plan.get_activities_by_day()
    
    # Get all available lessons and exercises for the form
    lessons = Lesson.objects.all()
    exercises = Exercise.objects.all()
    
    context = {
        'plan': plan,
        'activities_by_day': activities_by_day,
        'days_of_week': ActivityPlan.DAYS_OF_WEEK,
        'time_slots': PlanActivity.TIME_SLOTS,
        'activity_types': ActivityPlan.ACTIVITY_TYPES,
        'lessons': lessons,
        'exercises': exercises,
    }
    
    return render(request, 'learning_app/plan_detail.html', context)

@login_required
def create_plan(request):
    """
    View to create a new activity plan
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        if title:
            plan = ActivityPlan.objects.create(
                user=request.user,
                title=title,
                description=description
            )
            
            messages.success(request, 'Your plan has been created!')
            return redirect('learning_app:plan_detail', plan_id=plan.id)
        else:
            messages.error(request, 'Please provide a title for your plan.')
    
    return render(request, 'learning_app/create_plan.html')

@login_required
def add_activity(request, plan_id):
    """
    View to add an activity to a plan
    """
    plan = get_object_or_404(ActivityPlan, id=plan_id, user=request.user)
    
    if request.method == 'POST':
        day_of_week = request.POST.get('day_of_week')
        time_slot = request.POST.get('time_slot')
        activity_type = request.POST.get('activity_type')
        duration_minutes = request.POST.get('duration_minutes', 30)
        
        # Check if an activity already exists in this time slot
        existing_activity = PlanActivity.objects.filter(
            plan=plan,
            day_of_week=day_of_week,
            time_slot=time_slot
        ).first()
        
        if existing_activity:
            messages.error(request, 'There is already an activity scheduled for this time slot.')
            return redirect('learning_app:plan_detail', plan_id=plan.id)
        
        # Create the activity
        activity = PlanActivity(
            plan=plan,
            day_of_week=day_of_week,
            time_slot=time_slot,
            activity_type=activity_type,
            duration_minutes=duration_minutes
        )
        
        # Set the specific activity based on type
        if activity_type == 'lesson':
            lesson_id = request.POST.get('lesson_id')
            if lesson_id:
                activity.lesson = get_object_or_404(Lesson, id=lesson_id)
        elif activity_type == 'exercise':
            exercise_id = request.POST.get('exercise_id')
            if exercise_id:
                activity.exercise = get_object_or_404(Exercise, id=exercise_id)
        
        # Set title and notes for custom activities
        activity.title = request.POST.get('title', '')
        activity.notes = request.POST.get('notes', '')
        
        activity.save()
        
        messages.success(request, 'Activity added to your plan!')
        return redirect('learning_app:plan_detail', plan_id=plan.id)
    
    # If not POST, redirect to plan detail
    return redirect('learning_app:plan_detail', plan_id=plan.id)

@login_required
def delete_activity(request, activity_id):
    """
    View to delete an activity from a plan
    """
    activity = get_object_or_404(PlanActivity, id=activity_id)
    
    # Check if the user owns this activity's plan
    if activity.plan.user != request.user:
        messages.error(request, 'You do not have permission to delete this activity.')
        return redirect('learning_app:plan_list')
    
    plan_id = activity.plan.id
    activity.delete()
    
    messages.success(request, 'Activity removed from your plan.')
    return redirect('learning_app:plan_detail', plan_id=plan_id)

@login_required
def mark_activity_complete(request, activity_id):
    """
    View to mark an activity as complete
    """
    activity = get_object_or_404(PlanActivity, id=activity_id)
    
    # Check if the user owns this activity's plan
    if activity.plan.user != request.user:
        messages.error(request, 'You do not have permission to update this activity.')
        return redirect('learning_app:plan_list')
    
    activity.completed = True
    activity.completion_date = timezone.now()
    activity.save()
    
    messages.success(request, 'Activity marked as complete!')
    return redirect('learning_app:plan_detail', plan_id=activity.plan.id)

@login_required
def delete_plan(request, plan_id):
    """
    View to delete an entire plan
    """
    plan = get_object_or_404(ActivityPlan, id=plan_id, user=request.user)
    
    if request.method == 'POST':
        plan.delete()
        messages.success(request, 'Your plan has been deleted.')
        return redirect('learning_app:plan_list')
    
    return render(request, 'learning_app/delete_plan.html', {'plan': plan})
@login_required
def avatar_selection(request):
    """
    View to select or create an avatar
    """
    # Check if user already has an avatar
    try:
        avatar = Avatar.objects.get(user=request.user)
        return redirect('learning_app:avatar_customize', avatar_id=avatar.id)
    except Avatar.DoesNotExist:
        pass
    
    # Define available avatars by type
    available_avatars = {
        'animal': ['lion', 'elephant', 'giraffe', 'monkey', 'panda', 'penguin', 'fox', 'owl'],
        'robot': ['robot-blue', 'robot-green', 'robot-red', 'robot-yellow', 'robot-purple'],
        'fantasy': ['wizard', 'fairy', 'dragon', 'unicorn', 'knight', 'princess'],
        'cartoon': ['superhero', 'astronaut', 'pirate', 'scientist', 'athlete', 'artist']
    }
    
    if request.method == 'POST':
        avatar_type = request.POST.get('avatar_type')
        character = request.POST.get('character')
        name = request.POST.get('name')
        voice_type = request.POST.get('voice_type')
        color_scheme = request.POST.get('color_scheme', 'blue')
        
        if avatar_type and character and name and voice_type:
            # Create the avatar
            avatar = Avatar.objects.create(
                user=request.user,
                name=name,
                avatar_type=avatar_type,
                character=character,
                voice_type=voice_type,
                color_scheme=color_scheme
            )
            
            messages.success(request, f"Meet {name}, your new learning buddy!")
            return redirect('learning_app:avatar_customize', avatar_id=avatar.id)
        else:
            messages.error(request, "Please fill out all required fields.")
    
    context = {
        'available_avatars': available_avatars,
        'avatar_types': Avatar.AVATAR_TYPES,
        'voice_types': Avatar.VOICE_TYPES,
    }
    
    return render(request, 'learning_app/avatar_selection.html', context)

@login_required
def avatar_customize(request, avatar_id):
    """
    View to customize an existing avatar
    """
    avatar = get_object_or_404(Avatar, id=avatar_id)
    
    # Ensure the avatar belongs to the current user
    if avatar.user != request.user:
        messages.error(request, "You don't have permission to customize this avatar.")
        return redirect('learning_app:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        voice_type = request.POST.get('voice_type')
        color_scheme = request.POST.get('color_scheme')
        custom_greeting = request.POST.get('custom_greeting')
        
        if name and voice_type:
            # Update the avatar
            avatar.name = name
            avatar.voice_type = voice_type
            avatar.color_scheme = color_scheme
            avatar.custom_greeting = custom_greeting
            avatar.save()
            
            messages.success(request, f"{name} has been updated!")
            return redirect('learning_app:home')
        else:
            messages.error(request, "Please fill out all required fields.")
    
    context = {
        'avatar': avatar,
        'voice_types': Avatar.VOICE_TYPES,
    }
    
    return render(request, 'learning_app/avatar_customize.html', context)

@csrf_exempt
def avatar_speak(request):
    """
    AJAX endpoint to get avatar speech
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            speech_type = data.get('speech_type', 'greeting')
            context = data.get('context', '')
            
            # Get the user's avatar
            try:
                avatar = Avatar.objects.get(user=request.user)
            except Avatar.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'No avatar found for this user'
                })
            
            # Get the appropriate message based on speech type
            if speech_type == 'greeting':
                message = avatar.get_greeting()
            elif speech_type == 'encouragement':
                message = avatar.get_encouragement()
            elif speech_type == 'celebration':
                message = avatar.get_celebration()
            else:
                message = avatar.get_greeting()
            
            # Record the interaction
            AvatarInteraction.objects.create(
                user=request.user,
                interaction_type=speech_type,
                message=message,
                context=context
            )
            
            # Return the message
            return JsonResponse({
                'success': True,
                'message': message,
                'avatar_name': avatar.name,
                'avatar_image': avatar.get_avatar_image_url()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    })
