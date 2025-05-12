/**
 * Marlin - Premium Imageboard
 * Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle mobile navigation
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        const isClickInsideNav = navMenu && navMenu.contains(event.target);
        const isClickOnHamburger = hamburger && hamburger.contains(event.target);
        
        if (navMenu && navMenu.classList.contains('show') && !isClickInsideNav && !isClickOnHamburger) {
            navMenu.classList.remove('show');
        }
    });
    
    // Handle image clicks to show full-size
    const postImages = document.querySelectorAll('.post-image');
    
    postImages.forEach(image => {
        image.addEventListener('click', function() {
            const imageUrl = this.getAttribute('src');
            if (imageUrl) {
                openImageModal(imageUrl);
            }
        });
    });
    
    // Setup captcha handling for forms
    initializeCaptcha();
    
    // Initialize post reference hover
    initializePostReferences();
    
    // Handle spoiler tags
    const spoilerTags = document.querySelectorAll('.spoiler');
    
    spoilerTags.forEach(tag => {
        tag.addEventListener('click', function() {
            this.classList.toggle('revealed');
        });
    });
});

/**
 * Opens a modal to display the full-size image
 */
function openImageModal(imageUrl) {
    // Create modal container
    const modal = document.createElement('div');
    modal.classList.add('image-modal');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.9)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '9999';
    
    // Create image element
    const image = document.createElement('img');
    image.src = imageUrl;
    image.style.maxWidth = '90%';
    image.style.maxHeight = '90%';
    image.style.objectFit = 'contain';
    
    // Add close functionality
    modal.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    // Prevent image click from closing modal
    image.addEventListener('click', function(event) {
        event.stopPropagation();
    });
    
    // Add to DOM
    modal.appendChild(image);
    document.body.appendChild(modal);
}

/**
 * Initialize captcha functionality
 */
function initializeCaptcha() {
    // Find all captcha containers
    const captchaContainers = document.querySelectorAll('.captcha-container');
    
    captchaContainers.forEach(container => {
        const refreshButton = container.querySelector('.captcha-refresh');
        const tokenInput = container.querySelector('input[name="captcha_token"]');
        const captchaImage = container.querySelector('.captcha-image');
        
        if (refreshButton && tokenInput && captchaImage) {
            // Initial captcha load
            getCaptcha(tokenInput, captchaImage);
            
            // Refresh captcha when button is clicked
            refreshButton.addEventListener('click', function() {
                getCaptcha(tokenInput, captchaImage);
            });
        }
    });
}

/**
 * Get a new captcha from the server
 */
function getCaptcha(tokenInput, captchaImage) {
    fetch('/captcha/generate')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                tokenInput.value = data.token;
                captchaImage.src = 'data:image/png;base64,' + data.image;
            } else {
                console.error('Failed to load captcha:', data.error);
            }
        })
        .catch(error => {
            console.error('Error loading captcha:', error);
        });
}

/**
 * Initialize post reference hover functionality
 */
function initializePostReferences() {
    // Find all post reference links
    const postRefs = document.querySelectorAll('.post-ref');
    
    postRefs.forEach(ref => {
        ref.addEventListener('mouseenter', function() {
            const postId = this.getAttribute('data-post-id');
            if (postId) {
                const refPost = document.getElementById('post-' + postId);
                if (refPost) {
                    // Create hover preview
                    const preview = document.createElement('div');
                    preview.classList.add('post-preview');
                    preview.innerHTML = refPost.innerHTML;
                    preview.style.position = 'absolute';
                    preview.style.zIndex = '1000';
                    preview.style.backgroundColor = 'var(--background-secondary)';
                    preview.style.border = '1px solid var(--border)';
                    preview.style.borderRadius = '4px';
                    preview.style.padding = '1rem';
                    preview.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                    preview.style.maxWidth = '400px';
                    
                    // Calculate position
                    const rect = this.getBoundingClientRect();
                    preview.style.left = rect.left + 'px';
                    preview.style.top = (rect.bottom + window.scrollY + 5) + 'px';
                    
                    // Add to DOM
                    this.preview = preview;
                    document.body.appendChild(preview);
                }
            }
        });
        
        ref.addEventListener('mouseleave', function() {
            if (this.preview && this.preview.parentNode) {
                document.body.removeChild(this.preview);
                this.preview = null;
            }
        });
    });
}

/**
 * Handle upvoting posts and threads
 */
function upvote(type, id, boardSlug, threadId) {
    // Redirect to login if not authenticated
    const isAuthenticated = document.body.getAttribute('data-authenticated') === 'true';
    
    if (!isAuthenticated) {
        window.location.href = '/login?next=/' + boardSlug + '/thread/' + threadId;
        return;
    }
    
    let url;
    if (type === 'thread') {
        url = '/' + boardSlug + '/thread/' + id + '/upvote';
    } else {
        url = '/' + boardSlug + '/thread/' + threadId + '/post/' + id + '/upvote';
    }
    
    // Submit upvote form
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = url;
    document.body.appendChild(form);
    form.submit();
}

/**
 * Format greentext in post content
 */
function formatContent() {
    const postContents = document.querySelectorAll('.post-text');
    
    postContents.forEach(content => {
        // Format greentext
        const html = content.innerHTML;
        const formattedHtml = html.replace(
            /^(&gt;.+)$/gm, 
            '<span class="greentext">$1</span>'
        );
        
        if (html !== formattedHtml) {
            content.innerHTML = formattedHtml;
        }
    });
}

/**
 * Handle post quoting
 */
function quotePost(postId) {
    const replyTextarea = document.querySelector('textarea[name="content"]');
    if (replyTextarea) {
        replyTextarea.value += '>>' + postId + '\n';
        replyTextarea.focus();
        
        // Scroll to reply form
        const replyForm = document.querySelector('.reply-form');
        if (replyForm) {
            replyForm.scrollIntoView({ behavior: 'smooth' });
        }
    }
}
