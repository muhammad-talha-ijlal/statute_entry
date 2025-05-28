/**
 * Form validation functionality for Legal Text Structuring App
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize form validation
    initFormValidation();
});

/**
 * Initialize form validation for all forms
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Get all required fields
            const requiredFields = form.querySelectorAll('[required]');
            let formValid = true;
            
            // Check each required field
            requiredFields.forEach(field => {
                // Clear previous error styling
                field.classList.remove('error');
                
                // Remove any existing error message
                const existingError = field.parentNode.querySelector('.field-error');
                if (existingError) {
                    existingError.remove();
                }
                
                // Check if field is empty
                if (!field.value.trim()) {
                    formValid = false;
                    
                    // Add error styling
                    field.classList.add('error');
                    
                    // Create error message
                    const errorMessage = document.createElement('div');
                    errorMessage.className = 'field-error';
                    errorMessage.textContent = 'This field is required';
                    errorMessage.style.color = '#e74c3c';
                    errorMessage.style.fontSize = '0.9rem';
                    errorMessage.style.marginTop = '0.3rem';
                    
                    // Insert error message after the field
                    field.parentNode.insertBefore(errorMessage, field.nextSibling);
                }
            });
            
            // Prevent form submission if validation fails
            if (!formValid) {
                e.preventDefault();
                
                // Scroll to first error
                const firstError = form.querySelector('.error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstError.focus();
                }
            }
        });
    });
    
    // Add input event listeners to remove error styling when field is filled
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('input', function() {
            if (this.value.trim()) {
                this.classList.remove('error');
                
                // Remove error message if it exists
                const errorMessage = this.parentNode.querySelector('.field-error');
                if (errorMessage) {
                    errorMessage.remove();
                }
            }
        });
    });
}

/**
 * Validate a specific form
 * @param {HTMLFormElement} form - The form to validate
 * @returns {boolean} - Whether the form is valid
 */
function validateForm(form) {
    // Get all required fields
    const requiredFields = form.querySelectorAll('[required]');
    let formValid = true;
    
    // Check each required field
    requiredFields.forEach(field => {
        // Check if field is empty
        if (!field.value.trim()) {
            formValid = false;
            
            // Add error styling
            field.classList.add('error');
            
            // Create error message if it doesn't exist
            if (!field.parentNode.querySelector('.field-error')) {
                const errorMessage = document.createElement('div');
                errorMessage.className = 'field-error';
                errorMessage.textContent = 'This field is required';
                errorMessage.style.color = '#e74c3c';
                errorMessage.style.fontSize = '0.9rem';
                errorMessage.style.marginTop = '0.3rem';
                
                // Insert error message after the field
                field.parentNode.insertBefore(errorMessage, field.nextSibling);
            }
        }
    });
    
    // Return validation result
    return formValid;
}

/**
 * Validate form fields on the fly as user types
 * @param {string} formId - ID of the form to validate
 */
function validateOnType(formId) {
    const form = document.getElementById(formId);
    
    if (form) {
        // Add input event listeners to all form fields
        form.querySelectorAll('input, textarea, select').forEach(field => {
            field.addEventListener('blur', function() {
                // Check if field is required and empty
                if (field.hasAttribute('required') && !field.value.trim()) {
                    // Add error styling
                    field.classList.add('error');
                    
                    // Create error message if it doesn't exist
                    if (!field.parentNode.querySelector('.field-error')) {
                        const errorMessage = document.createElement('div');
                        errorMessage.className = 'field-error';
                        errorMessage.textContent = 'This field is required';
                        errorMessage.style.color = '#e74c3c';
                        errorMessage.style.fontSize = '0.9rem';
                        errorMessage.style.marginTop = '0.3rem';
                        
                        // Insert error message after the field
                        field.parentNode.insertBefore(errorMessage, field.nextSibling);
                    }
                } else {
                    // Remove error styling
                    field.classList.remove('error');
                    
                    // Remove error message if it exists
                    const errorMessage = field.parentNode.querySelector('.field-error');
                    if (errorMessage) {
                        errorMessage.remove();
                    }
                }
            });
        });
    }
}