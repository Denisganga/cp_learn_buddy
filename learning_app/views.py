from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.core.files.base import ContentFile
from .models import Category, Lesson, Quiz, Question, Answer, UserProgress, Reward, UserReward
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
