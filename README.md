# CP Learn Buddy

CP Learn Buddy is an educational web application designed specifically for children with cerebral palsy. The application provides an accessible, engaging, and adaptive learning experience tailored to the unique needs of these children.

## Features

- **AI-Generated Educational Content**: Creates custom lessons on any topic using AI
- **Emotion Detection System**: Uses webcam to detect emotions and adapt content accordingly
- **Accessibility Features**: Text-to-speech, speech recognition, and customizable interface
- **Interactive Quizzes**: Engaging quizzes with immediate feedback
- **Progress Tracking**: Monitor learning progress and achievements
- **Reward System**: Motivational rewards for completing lessons and quizzes
- **Adaptive Learning**: Content adjusts based on the child's emotional state and needs

## Technology Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Integration**: Google Gemini AI for content generation
- **Emotion Detection**: face-api.js for real-time emotion recognition
- **Accessibility**: Web Speech API, custom UI controls

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/cp_learn_buddy.git
cd cp_learn_buddy
```

2. Create and activate a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Apply migrations:
```
python manage.py migrate
```

5. Create a superuser:
```
python manage.py createsuperuser
```

6. Run the development server:
```
python manage.py runserver
```

## Usage

1. Access the application at http://localhost:8000/
2. Log in with your credentials
3. Browse categories or create a new lesson
4. Enable emotion detection for adaptive learning
5. Track progress in the user dashboard

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Google Gemini AI for content generation
- face-api.js for emotion detection
- Django community for the robust framework
- Bootstrap for responsive design components
