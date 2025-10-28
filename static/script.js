// JavaScript for Stock Management System

// Initialize tooltips if using any
document.addEventListener('DOMContentLoaded', function() {
    // Any initialization code can go here
    
    // Example: Add confirmation for delete actions
    const deleteButtons = document.querySelectorAll('form[action*="delete_product"] button');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this product? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.mb-4.p-4.rounded-md');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
});