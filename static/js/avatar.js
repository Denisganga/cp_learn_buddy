/**
 * Avatar functionality for CP Learn Buddy
 */

class AvatarBuddy {
    constructor() {
        this.avatarWidget = null;
        this.avatarBubble = null;
        this.avatarImage = null;
        this.avatarMenu = null;
        this.avatarControls = null;
        this.isSpeaking = false;
        this.messageQueue = [];
        this.isInitialized = false;
        this.colorScheme = 'blue';
        this.lastInteraction = Date.now();
        this.idleMessages = [
            "How's your learning going?",
            "Need any help?",
            "Ready to learn something new?",
            "You're doing great today!",
            "Remember to take breaks!",
            "Learning is fun with you!"
        ];
    }
    
    /**
     * Initialize the avatar widget
     */
    init() {
        if (this.isInitialized) return;
        
        // Create avatar widget
        this.createAvatarWidget();
        
        // Add event listeners
        this.addEventListeners();
        
        // Show initial greeting after a delay
        setTimeout(() => {
            this.speak('greeting');
        }, 2000);
        
        // Set up idle messages
        this.setupIdleMessages();
        
        this.isInitialized = true;
    }
    
    /**
     * Create the avatar widget HTML
     */
    createAvatarWidget() {
        // Create widget container
        this.avatarWidget = document.createElement('div');
        this.avatarWidget.className = 'avatar-widget avatar-' + this.colorScheme;
        
        // Create speech bubble
        this.avatarBubble = document.createElement('div');
        this.avatarBubble.className = 'avatar-bubble';
        this.avatarBubble.style.display = 'none';
        this.avatarWidget.appendChild(this.avatarBubble);
        
        // Create avatar menu
        this.avatarMenu = document.createElement('div');
        this.avatarMenu.className = 'avatar-menu';
        
        // Add menu items
        const menuItems = [
            { icon: 'fa-comment', text: 'Say Hello', action: 'greeting' },
            { icon: 'fa-thumbs-up', text: 'Encourage Me', action: 'encouragement' },
            { icon: 'fa-star', text: 'Celebrate', action: 'celebration' },
            { icon: 'fa-cog', text: 'Customize', action: 'customize' }
        ];
        
        menuItems.forEach(item => {
            const menuItem = document.createElement('div');
            menuItem.className = 'avatar-menu-item';
            menuItem.innerHTML = `<i class="fas ${item.icon}"></i> ${item.text}`;
            menuItem.dataset.action = item.action;
            this.avatarMenu.appendChild(menuItem);
        });
        
        this.avatarWidget.appendChild(this.avatarMenu);
        
        // Create avatar image container
        const avatarImageContainer = document.createElement('div');
        avatarImageContainer.className = 'avatar-image-container';
        
        // Create avatar image
        this.avatarImage = document.createElement('img');
        this.avatarImage.className = 'avatar-image';
        this.avatarImage.alt = 'Your Avatar';
        avatarImageContainer.appendChild(this.avatarImage);
        
        // Create avatar controls
        this.avatarControls = document.createElement('div');
        this.avatarControls.className = 'avatar-controls';
        this.avatarControls.innerHTML = '<i class="fas fa-ellipsis-v"></i>';
        avatarImageContainer.appendChild(this.avatarControls);
        
        this.avatarWidget.appendChild(avatarImageContainer);
        
        // Add to document
        document.body.appendChild(this.avatarWidget);
        
        // Fetch avatar data
        this.fetchAvatarData();
    }
    
    /**
     * Add event listeners to avatar elements
     */
    addEventListeners() {
        // Avatar image click - say hello
        this.avatarWidget.querySelector('.avatar-image-container').addEventListener('click', () => {
            this.speak('greeting');
            this.lastInteraction = Date.now();
        });
        
        // Avatar controls click - toggle menu
        this.avatarControls.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMenu();
            this.lastInteraction = Date.now();
        });
        
        // Menu item clicks
        this.avatarMenu.addEventListener('click', (e) => {
            const menuItem = e.target.closest('.avatar-menu-item');
            if (menuItem) {
                const action = menuItem.dataset.action;
                
                if (action === 'customize') {
                    window.location.href = '/avatar/select/';
                } else {
                    this.speak(action);
                }
                
                this.toggleMenu(false);
                this.lastInteraction = Date.now();
            }
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (this.avatarMenu.classList.contains('show') && !this.avatarWidget.contains(e.target)) {
                this.toggleMenu(false);
            }
        });
    }
    
    /**
     * Toggle the avatar menu
     */
    toggleMenu(show = null) {
        if (show === null) {
            this.avatarMenu.classList.toggle('show');
        } else if (show) {
            this.avatarMenu.classList.add('show');
        } else {
            this.avatarMenu.classList.remove('show');
        }
    }
    
    /**
     * Fetch avatar data from the server
     */
    fetchAvatarData() {
        // Make a request to get the avatar data
        fetch('/avatar/speak/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                speech_type: 'greeting',
                context: 'init'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update avatar image
                this.avatarImage.src = data.avatar_image;
                this.avatarImage.alt = data.avatar_name;
                
                // Set color scheme if provided
                if (data.color_scheme) {
                    this.setColorScheme(data.color_scheme);
                }
            } else {
                console.error('Error fetching avatar data:', data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching avatar data:', error);
        });
    }
    
    /**
     * Make the avatar speak
     */
    speak(speechType, context = '') {
        // Add to message queue
        this.messageQueue.push({ speechType, context });
        
        // Process queue if not already speaking
        if (!this.isSpeaking) {
            this.processMessageQueue();
        }
    }
    
    /**
     * Process the message queue
     */
    processMessageQueue() {
        if (this.messageQueue.length === 0) {
            this.isSpeaking = false;
            return;
        }
        
        this.isSpeaking = true;
        const { speechType, context } = this.messageQueue.shift();
        
        // Make a request to get the speech
        fetch('/avatar/speak/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify({
                speech_type: speechType,
                context: context
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show the message
                this.showMessage(data.message);
                
                // Speak the message
                speakText(data.message);
                
                // Add animation to avatar
                this.animateAvatar(speechType);
                
                // Process next message after a delay
                setTimeout(() => {
                    this.processMessageQueue();
                }, 1000 + (data.message.length * 50)); // Delay based on message length
            } else {
                console.error('Error getting avatar speech:', data.error);
                this.isSpeaking = false;
            }
        })
        .catch(error => {
            console.error('Error getting avatar speech:', error);
            this.isSpeaking = false;
        });
    }
    
    /**
     * Show a message in the avatar bubble
     */
    showMessage(message) {
        // Set message text
        this.avatarBubble.textContent = message;
        
        // Show bubble
        this.avatarBubble.style.display = 'block';
        
        // Add show class after a small delay (for animation)
        setTimeout(() => {
            this.avatarBubble.classList.add('show');
        }, 10);
        
        // Hide bubble after a delay
        const hideDelay = 3000 + (message.length * 50); // Longer delay for longer messages
        setTimeout(() => {
            this.avatarBubble.classList.remove('show');
            
            // Hide bubble after animation completes
            setTimeout(() => {
                this.avatarBubble.style.display = 'none';
            }, 300);
        }, hideDelay);
    }
    
    /**
     * Animate the avatar based on speech type
     */
    animateAvatar(speechType) {
        const avatarImage = this.avatarWidget.querySelector('.avatar-image-container');
        
        // Remove any existing animation classes
        avatarImage.classList.remove('avatar-bounce', 'avatar-pulse', 'avatar-wave');
        
        // Add appropriate animation class
        switch (speechType) {
            case 'greeting':
                avatarImage.classList.add('avatar-wave');
                break;
            case 'encouragement':
                avatarImage.classList.add('avatar-pulse');
                break;
            case 'celebration':
                avatarImage.classList.add('avatar-bounce');
                break;
            default:
                avatarImage.classList.add('avatar-pulse');
        }
    }
    
    /**
     * Set the avatar color scheme
     */
    setColorScheme(colorScheme) {
        // Remove existing color class
        this.avatarWidget.classList.remove('avatar-blue', 'avatar-green', 'avatar-purple', 'avatar-orange', 'avatar-pink');
        
        // Add new color class
        this.avatarWidget.classList.add('avatar-' + colorScheme);
        this.colorScheme = colorScheme;
    }
    
    /**
     * Set up idle messages
     */
    setupIdleMessages() {
        // Check for idle time every 30 seconds
        setInterval(() => {
            const idleTime = Date.now() - this.lastInteraction;
            
            // If idle for more than 5 minutes and not currently speaking
            if (idleTime > 5 * 60 * 1000 && !this.isSpeaking && Math.random() < 0.3) {
                // Show a random idle message
                const message = this.idleMessages[Math.floor(Math.random() * this.idleMessages.length)];
                this.showMessage(message);
                speakText(message);
                this.animateAvatar('greeting');
            }
        }, 30000);
    }
    
    /**
     * Get CSRF token from cookies
     */
    getCsrfToken() {
        const name = 'csrftoken';
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
}

// Initialize avatar when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is logged in (avatar widget should only show for logged in users)
    const isLoggedIn = document.body.classList.contains('logged-in');
    
    if (isLoggedIn) {
        window.avatarBuddy = new AvatarBuddy();
        window.avatarBuddy.init();
    }
});
