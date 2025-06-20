// Emotion Detection System for CP Learn Buddy
// This script uses face-api.js to detect emotions from webcam feed

let isEmotionDetectionActive = false;
let videoEl;
let canvas;
let emotionData = {
    happy: 0,
    sad: 0,
    angry: 0,
    fearful: 0,
    disgusted: 0,
    surprised: 0,
    neutral: 0
};

let emotionHistory = [];
const HISTORY_LENGTH = 10; // Number of emotion readings to keep
let adaptationInterval;
let currentEmotion = 'neutral';
let emotionConfidence = 0;

// Initialize the emotion detection system
async function initEmotionDetection() {
    try {
        // Load the required face-api.js models
        await faceapi.nets.tinyFaceDetector.loadFromUri('/static/models');
        await faceapi.nets.faceExpressionNet.loadFromUri('/static/models');
        
        console.log('Face detection models loaded successfully');
        
        // Create video and canvas elements
        videoEl = document.createElement('video');
        videoEl.id = 'emotion-detection-video';
        videoEl.width = 320;
        videoEl.height = 240;
        videoEl.style.display = 'none'; // Hide the video element
        document.body.appendChild(videoEl);
        
        // Create canvas for visualization (optional - can be shown in debug mode)
        canvas = document.createElement('canvas');
        canvas.id = 'emotion-detection-canvas';
        canvas.width = 320;
        canvas.height = 240;
        canvas.style.display = 'none'; // Hide by default
        document.body.appendChild(canvas);
        
        // Add emotion indicator
        const emotionIndicator = document.createElement('div');
        emotionIndicator.id = 'emotion-indicator';
        emotionIndicator.className = 'emotion-indicator';
        emotionIndicator.innerHTML = '<span id="emotion-icon">😐</span>';
        document.body.appendChild(emotionIndicator);
        
        // Add toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'toggle-emotion-detection';
        toggleButton.className = 'btn btn-sm btn-primary rounded-circle position-fixed';
        toggleButton.style.bottom = '80px';
        toggleButton.style.right = '20px';
        toggleButton.style.zIndex = '1000';
        toggleButton.innerHTML = '<i class="fas fa-smile"></i>';
        toggleButton.title = 'Toggle Emotion Detection';
        toggleButton.onclick = toggleEmotionDetection;
        document.body.appendChild(toggleButton);
        
        console.log('Emotion detection UI elements created');
        
        // Create debug panel (hidden by default)
        createDebugPanel();
        
        return true;
    } catch (error) {
        console.error('Error initializing emotion detection:', error);
        return false;
    }
}

// Start the webcam and emotion detection
async function startEmotionDetection() {
    try {
        // Access the webcam
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: 320, 
                height: 240,
                facingMode: 'user' 
            } 
        });
        
        videoEl.srcObject = stream;
        await videoEl.play();
        
        // Start detection loop
        detectEmotions();
        
        // Start adaptation interval
        adaptationInterval = setInterval(adaptToEmotions, 5000);
        
        isEmotionDetectionActive = true;
        updateEmotionIndicator('neutral', 0);
        
        // Show success message
        showNotification('Emotion detection started!', 'success');
        
        return true;
    } catch (error) {
        console.error('Error starting emotion detection:', error);
        showNotification('Could not access webcam. Please check permissions.', 'error');
        return false;
    }
}

// Stop emotion detection
function stopEmotionDetection() {
    if (videoEl && videoEl.srcObject) {
        const tracks = videoEl.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        videoEl.srcObject = null;
    }
    
    if (adaptationInterval) {
        clearInterval(adaptationInterval);
    }
    
    isEmotionDetectionActive = false;
    updateEmotionIndicator('neutral', 0);
    
    // Show notification
    showNotification('Emotion detection stopped', 'info');
}

// Toggle emotion detection on/off
function toggleEmotionDetection() {
    if (isEmotionDetectionActive) {
        stopEmotionDetection();
        document.getElementById('toggle-emotion-detection').classList.remove('btn-danger');
        document.getElementById('toggle-emotion-detection').classList.add('btn-primary');
    } else {
        startEmotionDetection();
        document.getElementById('toggle-emotion-detection').classList.remove('btn-primary');
        document.getElementById('toggle-emotion-detection').classList.add('btn-danger');
    }
}

// Detect emotions from video feed
async function detectEmotions() {
    if (!isEmotionDetectionActive) return;
    
    try {
        // Detect faces and expressions
        const detections = await faceapi.detectAllFaces(
            videoEl, 
            new faceapi.TinyFaceDetectorOptions()
        ).withFaceExpressions();
        
        // Process detected emotions
        if (detections && detections.length > 0) {
            const expressions = detections[0].expressions;
            
            // Update emotion data
            emotionData = {
                happy: expressions.happy,
                sad: expressions.sad,
                angry: expressions.angry,
                fearful: expressions.fearful,
                disgusted: expressions.disgusted,
                surprised: expressions.surprised,
                neutral: expressions.neutral
            };
            
            // Add to history
            emotionHistory.push({...emotionData, timestamp: Date.now()});
            if (emotionHistory.length > HISTORY_LENGTH) {
                emotionHistory.shift();
            }
            
            // Determine dominant emotion
            let maxEmotion = 'neutral';
            let maxValue = 0;
            
            for (const [emotion, value] of Object.entries(emotionData)) {
                if (value > maxValue) {
                    maxValue = value;
                    maxEmotion = emotion;
                }
            }
            
            // Update current emotion if confidence is high enough
            if (maxValue > 0.5) {
                currentEmotion = maxEmotion;
                emotionConfidence = maxValue;
                updateEmotionIndicator(currentEmotion, emotionConfidence);
            }
            
            // Update debug panel if visible
            updateDebugPanel();
            
            // Optional: Draw face detection results on canvas for debugging
            if (canvas.style.display !== 'none') {
                const displaySize = { width: videoEl.width, height: videoEl.height };
                faceapi.matchDimensions(canvas, displaySize);
                
                const resizedDetections = faceapi.resizeResults(detections, displaySize);
                
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Draw face detection box
                faceapi.draw.drawDetections(canvas, resizedDetections);
                
                // Draw face expressions
                faceapi.draw.drawFaceExpressions(canvas, resizedDetections);
            }
        }
    } catch (error) {
        console.error('Error in emotion detection:', error);
    }
    
    // Continue detection loop
    if (isEmotionDetectionActive) {
        requestAnimationFrame(detectEmotions);
    }
}

// Update the emotion indicator
function updateEmotionIndicator(emotion, confidence) {
    const indicator = document.getElementById('emotion-indicator');
    const icon = document.getElementById('emotion-icon');
    
    if (!indicator || !icon) return;
    
    // Remove all emotion classes
    indicator.classList.remove('emotion-happy', 'emotion-sad', 'emotion-angry', 
                             'emotion-fearful', 'emotion-disgusted', 
                             'emotion-surprised', 'emotion-neutral');
    
    // Add the current emotion class
    indicator.classList.add(`emotion-${emotion}`);
    
    // Update the emoji based on emotion
    let emoji = '😐'; // neutral default
    
    switch(emotion) {
        case 'happy':
            emoji = '😊';
            break;
        case 'sad':
            emoji = '😢';
            break;
        case 'angry':
            emoji = '😠';
            break;
        case 'fearful':
            emoji = '😨';
            break;
        case 'disgusted':
            emoji = '🤢';
            break;
        case 'surprised':
            emoji = '😲';
            break;
        case 'neutral':
        default:
            emoji = '😐';
    }
    
    icon.textContent = emoji;
    
    // Show/hide based on confidence
    if (confidence > 0.5) {
        indicator.style.opacity = '1';
    } else {
        indicator.style.opacity = '0.5';
    }
}

// Adapt the lesson based on detected emotions
function adaptToEmotions() {
    if (emotionHistory.length === 0) return;
    
    // Calculate average emotions over time
    const avgEmotions = {
        happy: 0,
        sad: 0,
        angry: 0,
        fearful: 0,
        disgusted: 0,
        surprised: 0,
        neutral: 0
    };
    
    emotionHistory.forEach(entry => {
        for (const emotion in avgEmotions) {
            avgEmotions[emotion] += entry[emotion];
        }
    });
    
    for (const emotion in avgEmotions) {
        avgEmotions[emotion] /= emotionHistory.length;
    }
    
    // Determine if adaptation is needed
    if (avgEmotions.confused > 0.4 || avgEmotions.sad > 0.4 || avgEmotions.angry > 0.4) {
        // Child might be struggling - simplify content
        simplifyContent();
    } else if (avgEmotions.happy > 0.5) {
        // Child is engaged and happy - provide positive reinforcement
        providePositiveReinforcement();
    } else if (avgEmotions.neutral > 0.7) {
        // Child might be bored - make content more engaging
        makeContentMoreEngaging();
    }
}

// Simplify content for confused or frustrated children
function simplifyContent() {
    // Find complex paragraphs and simplify them
    const contentElements = document.querySelectorAll('.lesson-formatted-content p, .lesson-formatted-content li');
    
    contentElements.forEach(el => {
        // If paragraph is long, add a highlight class
        if (el.textContent.length > 100) {
            el.classList.add('simplified-content');
            
            // Add a "Listen" button for longer paragraphs
            if (!el.querySelector('.listen-btn')) {
                const listenBtn = document.createElement('button');
                listenBtn.className = 'btn btn-sm btn-info listen-btn ms-2';
                listenBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
                listenBtn.onclick = (e) => {
                    e.stopPropagation();
                    speakText(el.textContent);
                };
                el.appendChild(listenBtn);
            }
        }
    });
    
    // Show a supportive message
    showAdaptiveMessage("Let's take it step by step. You're doing great!", 'info');
}

// Provide positive reinforcement for happy children
function providePositiveReinforcement() {
    // Show celebration animation
    showCelebration();
    
    // Show encouraging message
    showAdaptiveMessage("Amazing job! You're doing fantastic!", 'success');
}

// Make content more engaging for potentially bored children
function makeContentMoreEngaging() {
    // Add interactive elements or animations
    const contentContainer = document.querySelector('.lesson-content');
    
    if (contentContainer) {
        // Add a subtle animation to draw attention
        contentContainer.classList.add('pulse-animation');
        
        setTimeout(() => {
            contentContainer.classList.remove('pulse-animation');
        }, 2000);
    }
    
    // Show an engaging question
    showAdaptiveMessage("What do you think about this? Can you tell me more?", 'primary');
}

// Show adaptive messages based on emotions
function showAdaptiveMessage(message, type) {
    const messageContainer = document.getElementById('adaptive-message-container');
    
    if (!messageContainer) {
        // Create container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'adaptive-message-container';
        container.className = 'position-fixed bottom-0 start-50 translate-middle-x mb-4';
        container.style.zIndex = '1000';
        document.body.appendChild(container);
    }
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `alert alert-${type} alert-dismissible fade show`;
    messageEl.innerHTML = `
        <strong><i class="fas fa-robot me-2"></i>Buddy says:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add to container
    document.getElementById('adaptive-message-container').appendChild(messageEl);
    
    // Remove after 5 seconds
    setTimeout(() => {
        messageEl.classList.remove('show');
        setTimeout(() => messageEl.remove(), 500);
    }, 5000);
    
    // Also speak the message
    speakText(message);
}

// Show celebration animation for positive reinforcement
function showCelebration() {
    // Create celebration container if it doesn't exist
    if (!document.getElementById('celebration-container')) {
        const celebrationContainer = document.createElement('div');
        celebrationContainer.id = 'celebration-container';
        celebrationContainer.className = 'position-fixed top-0 start-0 w-100 h-100 pointer-events-none';
        celebrationContainer.style.zIndex = '1000';
        document.body.appendChild(celebrationContainer);
    }
    
    // Add celebration emojis
    const emojis = ['🎉', '⭐', '👏', '🌟', '🎊'];
    const container = document.getElementById('celebration-container');
    
    for (let i = 0; i < 20; i++) {
        const emoji = document.createElement('div');
        emoji.className = 'celebration-emoji';
        emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
        emoji.style.left = `${Math.random() * 100}%`;
        emoji.style.animationDuration = `${1 + Math.random() * 2}s`;
        emoji.style.animationDelay = `${Math.random() * 0.5}s`;
        container.appendChild(emoji);
        
        // Remove after animation
        setTimeout(() => emoji.remove(), 3000);
    }
}

// Create debug panel for developers
function createDebugPanel() {
    const debugPanel = document.createElement('div');
    debugPanel.id = 'emotion-debug-panel';
    debugPanel.className = 'card position-fixed';
    debugPanel.style.bottom = '20px';
    debugPanel.style.left = '20px';
    debugPanel.style.zIndex = '1000';
    debugPanel.style.width = '300px';
    debugPanel.style.display = 'none';
    
    debugPanel.innerHTML = `
        <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
            <span>Emotion Detection Debug</span>
            <button class="btn btn-sm btn-outline-light" onclick="toggleDebugPanel()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="card-body">
            <div class="mb-3">
                <label class="form-label">Current Emotion: <span id="debug-current-emotion">neutral</span></label>
                <div class="progress">
                    <div id="debug-emotion-confidence" class="progress-bar" role="progressbar" style="width: 0%"></div>
                </div>
            </div>
            <div id="debug-emotion-bars">
                <!-- Emotion bars will be added here -->
            </div>
            <div class="form-check form-switch mt-3">
                <input class="form-check-input" type="checkbox" id="debug-show-canvas">
                <label class="form-check-label" for="debug-show-canvas">Show Camera Feed</label>
            </div>
        </div>
    `;
    
    document.body.appendChild(debugPanel);
    
    // Add emotion bars
    const emotionBarsContainer = document.getElementById('debug-emotion-bars');
    
    for (const emotion of ['happy', 'sad', 'angry', 'fearful', 'disgusted', 'surprised', 'neutral']) {
        const barContainer = document.createElement('div');
        barContainer.className = 'mb-2';
        barContainer.innerHTML = `
            <div class="d-flex justify-content-between">
                <small>${emotion}</small>
                <small id="debug-value-${emotion}">0%</small>
            </div>
            <div class="progress" style="height: 8px;">
                <div id="debug-bar-${emotion}" class="progress-bar bg-${getEmotionColor(emotion)}" 
                     role="progressbar" style="width: 0%"></div>
            </div>
        `;
        emotionBarsContainer.appendChild(barContainer);
    }
    
    // Add event listener for canvas toggle
    document.getElementById('debug-show-canvas').addEventListener('change', function() {
        canvas.style.display = this.checked ? 'block' : 'none';
    });
}

// Update debug panel with current emotion data
function updateDebugPanel() {
    const debugPanel = document.getElementById('emotion-debug-panel');
    if (!debugPanel || debugPanel.style.display === 'none') return;
    
    // Update current emotion
    document.getElementById('debug-current-emotion').textContent = currentEmotion;
    
    // Update confidence bar
    const confidenceBar = document.getElementById('debug-emotion-confidence');
    confidenceBar.style.width = `${emotionConfidence * 100}%`;
    confidenceBar.className = `progress-bar bg-${getEmotionColor(currentEmotion)}`;
    
    // Update individual emotion bars
    for (const [emotion, value] of Object.entries(emotionData)) {
        const bar = document.getElementById(`debug-bar-${emotion}`);
        const valueEl = document.getElementById(`debug-value-${emotion}`);
        
        if (bar && valueEl) {
            bar.style.width = `${value * 100}%`;
            valueEl.textContent = `${Math.round(value * 100)}%`;
        }
    }
}

// Toggle debug panel visibility
window.toggleDebugPanel = function() {
    const debugPanel = document.getElementById('emotion-debug-panel');
    if (debugPanel) {
        debugPanel.style.display = debugPanel.style.display === 'none' ? 'block' : 'none';
    }
}

// Get color class for emotion
function getEmotionColor(emotion) {
    switch(emotion) {
        case 'happy': return 'success';
        case 'sad': return 'info';
        case 'angry': return 'danger';
        case 'fearful': return 'warning';
        case 'disgusted': return 'dark';
        case 'surprised': return 'primary';
        case 'neutral': 
        default: return 'secondary';
    }
}

// Show notification
function showNotification(message, type) {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'position-fixed top-0 end-0 p-3';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `toast align-items-center text-white bg-${type} border-0`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    notification.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    document.getElementById('notification-container').appendChild(notification);
    
    // Show notification
    const toast = new bootstrap.Toast(notification);
    toast.show();
    
    // Remove after it's hidden
    notification.addEventListener('hidden.bs.toast', function() {
        notification.remove();
    });
}

// Add keyboard shortcut for debug panel
document.addEventListener('keydown', function(e) {
    // Ctrl+Shift+D to toggle debug panel
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        toggleDebugPanel();
    }
});

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for emotion detection
    const style = document.createElement('style');
    style.textContent = `
        #emotion-indicator {
            position: fixed;
            bottom: 20px;
            right: 80px;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #fff;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            transition: all 0.3s ease;
            opacity: 0.5;
        }
        
        #emotion-icon {
            font-size: 24px;
        }
        
        .emotion-happy { background-color: #d4edda !important; }
        .emotion-sad { background-color: #d1ecf1 !important; }
        .emotion-angry { background-color: #f8d7da !important; }
        .emotion-fearful { background-color: #fff3cd !important; }
        .emotion-disgusted { background-color: #d3d3d4 !important; }
        .emotion-surprised { background-color: #cce5ff !important; }
        
        .simplified-content {
            background-color: #fffacd;
            border-left: 3px solid #ffc107;
            padding-left: 10px !important;
        }
        
        .pulse-animation {
            animation: pulse 2s;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .celebration-emoji {
            position: absolute;
            font-size: 30px;
            animation: fall linear forwards;
            opacity: 1;
        }
        
        @keyframes fall {
            0% { transform: translateY(-50px); opacity: 1; }
            80% { opacity: 1; }
            100% { transform: translateY(100vh); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    
    // Initialize emotion detection
    initEmotionDetection().then(success => {
        if (success) {
            console.log('Emotion detection system ready');
            
            // Add debug panel toggle button
            const debugBtn = document.createElement('button');
            debugBtn.id = 'toggle-debug-panel';
            debugBtn.className = 'btn btn-sm btn-secondary rounded-circle position-fixed';
            debugBtn.style.bottom = '80px';
            debugBtn.style.left = '20px';
            debugBtn.style.zIndex = '1000';
            debugBtn.innerHTML = '<i class="fas fa-bug"></i>';
            debugBtn.title = 'Toggle Debug Panel';
            debugBtn.onclick = toggleDebugPanel;
            document.body.appendChild(debugBtn);
        }
    });
});
