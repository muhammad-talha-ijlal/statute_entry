/**
 * Main JavaScript functionality for Legal Text Structuring App
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all forms to prevent duplicate submissions
    initFormSubmitHandlers();
    
    // Initialize save buttons
    initSaveButtons();
    
    // Initialize any progress indicators
    updateProgressIndicators();
});

/**
 * Prevent multiple form submissions
 */
function initFormSubmitHandlers() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Disable all submit buttons on this form
            const submitButtons = form.querySelectorAll('button[type="submit"]');
            submitButtons.forEach(button => {
                // Store original text
                button.dataset.originalText = button.innerHTML;
                button.disabled = true;
                button.innerHTML = 'Processing...';
            });
            
            // Re-enable after a short delay if the form doesn't submit for some reason
            setTimeout(() => {
                submitButtons.forEach(button => {
                    if (button.disabled) {
                        button.disabled = false;
                        button.innerHTML = button.dataset.originalText || 'Submit';
                    }
                });
            }, 5000);
        });
    });
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = message;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Position it
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '200px';
    notification.style.maxWidth = '400px';
    
    // Remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
    
    // Add transition
    notification.style.transition = 'opacity 0.5s ease';
}