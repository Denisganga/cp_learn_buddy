// Custom JavaScript for CP Learn Buddy

// Text-to-Speech functionality
function speakText(text) {
    fetch("/text-to-speech/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: "text=" + encodeURIComponent(text)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const audio = new Audio(data.audio_url);
            audio.play();
        }
    });
}

// Speech Recognition
let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        document.getElementById('speech-result').textContent = transcript;
        
        // You can add logic here to check answers
        checkAnswer(transcript);
    };
    
    recognition.onend = function() {
        document.getElementById('listening-indicator').style.display = 'none';
    };
}

function startListening() {
    if (recognition) {
        recognition.start();
        document.getElementById('listening-indicator').style.display = 'block';
    }
}

// Background music toggle
document.addEventListener('DOMContentLoaded', function() {
    const musicBtn = document.getElementById('toggleMusic');
    const music = document.getElementById('backgroundMusic');
    let musicPlaying = false;

    if (musicBtn && music) {
        musicBtn.addEventListener('click', function() {
            if (musicPlaying) {
                music.pause();
                musicBtn.innerHTML = '<i class="fas fa-music"></i>';
            } else {
                music.play();
                musicBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }
            musicPlaying = !musicPlaying;
        });
    }

    // Accessibility toggles
    const contrastBtn = document.getElementById('toggleContrast');
    if (contrastBtn) {
        contrastBtn.addEventListener('click', function() {
            document.body.classList.toggle('high-contrast-mode');
        });
    }

    const textSizeBtn = document.getElementById('toggleTextSize');
    if (textSizeBtn) {
        textSizeBtn.addEventListener('click', function() {
            document.body.classList.toggle('large-text');
        });
    }

    // Quiz options selection
    document.querySelectorAll('.quiz-option').forEach(option => {
        option.addEventListener('click', function() {
            const name = this.getAttribute('data-name');
            document.querySelectorAll(`.quiz-option[data-name="${name}"]`).forEach(opt => {
                opt.classList.remove('selected');
            });
            this.classList.add('selected');
            
            // Set the hidden input value
            document.querySelector(`input[name="${name}"]`).value = this.getAttribute('data-value');
        });
    });
});

// Function to check spoken answers
function checkAnswer(transcript) {
    // This is a simple example - you would customize this based on the current question
    const correctAnswers = {
        "what color is the sky": "blue",
        "what animal says moo": "cow",
        "how many fingers do you have": "five"
    };
    
    let feedback = "I didn't understand. Try again!";
    let foundMatch = false;
    
    for (const question in correctAnswers) {
        if (document.querySelector('.current-question') && 
            document.querySelector('.current-question').textContent.toLowerCase().includes(question)) {
            if (transcript.toLowerCase().includes(correctAnswers[question])) {
                feedback = "Well done! That's correct!";
                document.getElementById('emoji-feedback').innerHTML = '😃';
                foundMatch = true;
            }
            break;
        }
    }
    
    if (!foundMatch && document.getElementById('emoji-feedback')) {
        document.getElementById('emoji-feedback').innerHTML = '🤔';
    }
    
    speakText(feedback);
    
    if (document.getElementById('feedback-text')) {
        document.getElementById('feedback-text').textContent = feedback;
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Record audio for speech recognition
let mediaRecorder;
let audioChunks = [];

function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                audioChunks = [];
                
                const formData = new FormData();
                formData.append("audio", audioBlob);
                
                fetch("/speech-to-text/", {
                    method: "POST",
                    body: formData,
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken")
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('speech-result').textContent = data.text;
                        checkAnswer(data.text);
                    }
                });
            });

            setTimeout(() => {
                mediaRecorder.stop();
            }, 5000);
        });
}
