/**
 * Marlin - Premium Imageboard
 * Thread Handling
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize thread-specific features
    initThreadPage();
});

/**
 * Initialize thread page functionality
 */
function initThreadPage() {
    // Format post content
    formatPostContent();
    
    // Initialize post reference highlighting
    initPostReferences();
    
    // Set up post reply functionality
    initReplyButtons();
    
    // Initialize image expanding
    initImageExpanding();
    
    // Check if thread is locked
    checkThreadLocked();
}

/**
 * Format post content (greentext, links, etc.)
 */
function formatPostContent() {
    const postContents = document.querySelectorAll('.post-text');
    
    postContents.forEach(content => {
        let html = content.innerHTML;
        
        // Format greentext (lines starting with >)
        html = html.replace(
            /^(&gt;)([^&gt;].*)$/gm, 
            '<span class="greentext">$1$2</span>'
        );
        
        // Format post references (>>12345)
        html = html.replace(
            /&gt;&gt;(\d+)/g, 
            '<a href="#post-$1" class="post-ref" data-post-id="$1">&gt;&gt;$1</a>'
        );
        
        // Format URLs
        html = html.replace(
            /(https?:\/\/[^\s<]+[^<.,:;"')\]\s])/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        content.innerHTML = html;
    });
}

/**
 * Initialize post reference functionality
 */
function initPostReferences() {
    const postRefs = document.querySelectorAll('.post-ref');
    
    postRefs.forEach(ref => {
        // Highlight referenced post when hovering over reference
        ref.addEventListener('mouseenter', function() {
            const postId = this.getAttribute('data-post-id');
            const targetPost = document.getElementById('post-' + postId);
            
            if (targetPost) {
                targetPost.classList.add('post-highlighted');
                
                // Create and show preview
                showPostPreview(this, targetPost);
            }
        });
        
        // Remove highlight when mouse leaves
        ref.addEventListener('mouseleave', function() {
            const postId = this.getAttribute('data-post-id');
            const targetPost = document.getElementById('post-' + postId);
            
            if (targetPost) {
                targetPost.classList.remove('post-highlighted');
            }
            
            // Remove preview
            if (this.preview) {
                document.body.removeChild(this.preview);
                this.preview = null;
            }
        });
        
        // Scroll to post when clicked
        ref.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.getAttribute('data-post-id');
            const targetPost = document.getElementById('post-' + postId);
            
            if (targetPost) {
                targetPost.scrollIntoView({ behavior: 'smooth' });
                
                // Briefly highlight the post
                targetPost.classList.add('post-highlighted');
                setTimeout(() => {
                    targetPost.classList.remove('post-highlighted');
                }, 2000);
            }
        });
    });
}

/**
 * Show a preview of a referenced post
 */
function showPostPreview(referenceElement, targetPost) {
    // Create preview element
    const preview = document.createElement('div');
    preview.classList.add('post-preview');
    
    // Copy content from target post
    const postContent = targetPost.querySelector('.post-content').cloneNode(true);
    
    // Simplify preview by removing certain elements
    const actionsToRemove = postContent.querySelectorAll('.post-actions');
    actionsToRemove.forEach(el => el.remove());
    
    // Add content to preview
    preview.appendChild(postContent);
    
    // Style the preview
    preview.style.position = 'absolute';
    preview.style.zIndex = '1000';
    preview.style.backgroundColor = 'var(--background-secondary)';
    preview.style.border = '1px solid var(--border)';
    preview.style.borderRadius = '4px';
    preview.style.padding = '0.75rem';
    preview.style.maxWidth = '400px';
    preview.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
    
    // Position the preview
    const refRect = referenceElement.getBoundingClientRect();
    
    // Check if preview should appear above or below the reference
    const spaceBelow = window.innerHeight - refRect.bottom;
    
    if (spaceBelow < 200) {
        // Position above
        preview.style.bottom = (window.innerHeight - refRect.top + 5) + 'px';
    } else {
        // Position below
        preview.style.top = (refRect.bottom + window.scrollY + 5) + 'px';
    }
    
    // Horizontal positioning
    preview.style.left = refRect.left + 'px';
    
    // Adjust if off-screen
    requestAnimationFrame(() => {
        const previewRect = preview.getBoundingClientRect();
        
        if (previewRect.right > window.innerWidth) {
            const newLeft = window.innerWidth - previewRect.width - 10;
            preview.style.left = (newLeft > 0 ? newLeft : 0) + 'px';
        }
    });
    
    // Add to DOM and store reference
    document.body.appendChild(preview);
    referenceElement.preview = preview;
}

/**
 * Initialize reply buttons for quoting posts
 */
function initReplyButtons() {
    const replyButtons = document.querySelectorAll('.reply-button');
    
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            quotePost(postId);
        });
    });
}

/**
 * Quote a post in the reply form
 */
function quotePost(postId) {
    const replyForm = document.querySelector('.reply-form');
    const replyTextarea = document.querySelector('textarea[name="content"]');
    
    if (replyForm && replyTextarea) {
        // Add the post reference to the textarea
        replyTextarea.value += `>>${postId}\n`;
        
        // Focus the textarea
        replyTextarea.focus();
        
        // Scroll to the reply form
        replyForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

/**
 * Initialize image expanding functionality
 */
function initImageExpanding() {
    const postImages = document.querySelectorAll('.post-image');
    
    postImages.forEach(image => {
        image.addEventListener('click', function(e) {
            e.preventDefault();
            
            const fullSizeUrl = this.getAttribute('data-full-url') || this.src;
            openImageModal(fullSizeUrl);
        });
    });
}

/**
 * Open modal with full-size image
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
    
    // Create close button
    const closeButton = document.createElement('div');
    closeButton.textContent = '×';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '20px';
    closeButton.style.right = '30px';
    closeButton.style.fontSize = '30px';
    closeButton.style.color = 'white';
    closeButton.style.cursor = 'pointer';
    
    // Create image element
    const image = document.createElement('img');
    image.src = imageUrl;
    image.style.maxWidth = '90%';
    image.style.maxHeight = '90%';
    image.style.objectFit = 'contain';
    
    // Add close functionality
    closeButton.addEventListener('click', function() {
        document.body.removeChild(modal);
    });
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            document.body.removeChild(modal);
        }
    });
    
    // Add to DOM
    modal.appendChild(closeButton);
    modal.appendChild(image);
    document.body.appendChild(modal);
}

/**
 * Check if thread is locked and disable reply form if needed
 */
function checkThreadLocked() {
    const threadContainer = document.querySelector('.thread-container');
    const replyForm = document.querySelector('.reply-form');
    
    if (threadContainer && replyForm) {
        const isLocked = threadContainer.getAttribute('data-locked') === 'true';
        
        if (isLocked) {
            // Disable form elements
            const formElements = replyForm.querySelectorAll('input, textarea, button');
            formElements.forEach(el => {
                el.disabled = true;
            });
            
            // Add locked message
            const lockedMessage = document.createElement('div');
            lockedMessage.classList.add('locked-message');
            lockedMessage.textContent = 'This thread is locked. You cannot reply.';
            lockedMessage.style.backgroundColor = '#ffebee';
            lockedMessage.style.padding = '0.75rem';
            lockedMessage.style.borderRadius = '4px';
            lockedMessage.style.marginBottom = '1rem';
            lockedMessage.style.textAlign = 'center';
            
            replyForm.prepend(lockedMessage);
        }
    }
}
