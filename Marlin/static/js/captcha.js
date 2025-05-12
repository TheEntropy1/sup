/**
 * Marlin - Premium Imageboard
 * Captcha Handling
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all captcha elements on the page
    initAllCaptchas();
});

/**
 * Initialize all captcha elements on the page
 */
function initAllCaptchas() {
    const captchaContainers = document.querySelectorAll('.captcha-container');
    
    captchaContainers.forEach(container => {
        initCaptcha(container);
    });
}

/**
 * Initialize a single captcha container
 */
function initCaptcha(container) {
    const refreshButton = container.querySelector('.captcha-refresh');
    const tokenInput = container.querySelector('input[name="captcha_token"]');
    const captchaImage = container.querySelector('.captcha-image');
    
    if (refreshButton && tokenInput && captchaImage) {
        // Load initial captcha
        loadNewCaptcha(tokenInput, captchaImage);
        
        // Add refresh handler
        refreshButton.addEventListener('click', function(e) {
            e.preventDefault();
            loadNewCaptcha(tokenInput, captchaImage);
        });
    }
}

/**
 * Load a new captcha from the server
 */
function loadNewCaptcha(tokenInput, captchaImage) {
    // Show loading indicator
    captchaImage.style.opacity = '0.5';
    
    fetch('/captcha/generate')
        .then(response => {
            if (!response.ok) {
                throw new Error('Captcha generation failed');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update the captcha image and token
                tokenInput.value = data.token;
                captchaImage.src = 'data:image/png;base64,' + data.image;
                captchaImage.style.opacity = '1';
            } else {
                console.error('Failed to generate captcha:', data.error);
                showCaptchaError(captchaImage);
            }
        })
        .catch(error => {
            console.error('Error loading captcha:', error);
            showCaptchaError(captchaImage);
        });
}

/**
 * Display an error when captcha fails to load
 */
function showCaptchaError(captchaImage) {
    captchaImage.src = '';
    captchaImage.style.backgroundColor = '#ffebee';
    captchaImage.style.display = 'flex';
    captchaImage.style.justifyContent = 'center';
    captchaImage.style.alignItems = 'center';
    captchaImage.style.color = '#d32f2f';
    captchaImage.style.opacity = '1';
    captchaImage.textContent = 'Failed to load captcha. Click refresh to try again.';
}

/**
 * Validate captcha input before form submission
 */
function validateCaptcha(form) {
    const captchaSolution = form.querySelector('input[name="captcha_solution"]');
    
    if (!captchaSolution || !captchaSolution.value.trim()) {
        // Show error message
        const errorMsg = document.createElement('div');
        errorMsg.classList.add('captcha-error');
        errorMsg.textContent = 'Please enter the captcha text';
        errorMsg.style.color = '#d32f2f';
        errorMsg.style.fontSize = '0.9rem';
        errorMsg.style.marginTop = '0.5rem';
        
        captchaSolution.parentNode.appendChild(errorMsg);
        captchaSolution.focus();
        
        // Remove error after 3 seconds
        setTimeout(() => {
            if (errorMsg.parentNode) {
                errorMsg.parentNode.removeChild(errorMsg);
            }
        }, 3000);
        
        return false;
    }
    
    return true;
}
