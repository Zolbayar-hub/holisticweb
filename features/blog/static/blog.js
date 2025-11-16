// Professional Blog JavaScript - Human-Centered Interactions

document.addEventListener('DOMContentLoaded', function() {
    console.log('Blog feature loaded successfully');
    
    // Initialize all blog functionality
    initSearch();
    initSocialSharing();
    initNewsletter();
    initReadingProgress();
    initSmoothScrolling();
    initImageLazyLoading();
});

// Enhanced Search Functionality
function initSearch() {
    const searchForms = document.querySelectorAll('.search-form, .search-form-large, .newsletter-form');
    
    searchForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const input = form.querySelector('input[type="text"], input[type="email"]');
            const query = input.value.trim();
            
            if (form.classList.contains('newsletter-form')) {
                e.preventDefault();
                handleNewsletterSignup(query);
                return;
            }
            
            if (!query) {
                e.preventDefault();
                showNotification('Please enter a search term', 'warning');
                input.focus();
            }
        });
    });
    
    // Search suggestions (simple implementation)
    const searchInputs = document.querySelectorAll('.search-input, .search-input-large');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', debounce(function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // Could implement live search suggestions here
                console.log('Searching for:', query);
            }
        }, 300));
    });
}

// Social Sharing Functions
function initSocialSharing() {
    // Add click handlers to social share buttons
    const shareButtons = document.querySelectorAll('.share-btn');
    shareButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const platform = this.classList[1]; // twitter, facebook, etc.
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            
            switch(platform) {
                case 'twitter':
                    shareOnTwitter(url, title);
                    break;
                case 'facebook':
                    shareOnFacebook(url);
                    break;
                case 'linkedin':
                    shareOnLinkedIn(url, title);
                    break;
                case 'copy':
                    copyToClipboard();
                    break;
            }
        });
    });
}

function shareOnTwitter(url = null, title = null) {
    const shareUrl = url || encodeURIComponent(window.location.href);
    const shareTitle = title || encodeURIComponent(document.title);
    const twitterUrl = `https://twitter.com/intent/tweet?url=${shareUrl}&text=${shareTitle}`;
    
    window.open(twitterUrl, 'twitter-share', 'width=600,height=400');
    trackSocialShare('twitter');
}

function shareOnFacebook(url = null) {
    const shareUrl = url || encodeURIComponent(window.location.href);
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${shareUrl}`;
    
    window.open(facebookUrl, 'facebook-share', 'width=600,height=400');
    trackSocialShare('facebook');
}

function shareOnLinkedIn(url = null, title = null) {
    const shareUrl = url || encodeURIComponent(window.location.href);
    const shareTitle = title || encodeURIComponent(document.title);
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${shareUrl}&title=${shareTitle}`;
    
    window.open(linkedinUrl, 'linkedin-share', 'width=600,height=400');
    trackSocialShare('linkedin');
}

function copyToClipboard() {
    const url = window.location.href;
    
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            showNotification('Link copied to clipboard!', 'success');
            trackSocialShare('copy');
        }).catch(() => {
            fallbackCopyToClipboard(url);
        });
    } else {
        fallbackCopyToClipboard(url);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showNotification('Link copied to clipboard!', 'success');
        trackSocialShare('copy');
    } catch (err) {
        showNotification('Unable to copy link', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Newsletter Signup
function initNewsletter() {
    const newsletterForms = document.querySelectorAll('.newsletter-form');
    
    newsletterForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = form.querySelector('input[type="email"]').value;
            handleNewsletterSignup(email);
        });
    });
}

function handleNewsletterSignup(email) {
    if (!validateEmail(email)) {
        showNotification('Please enter a valid email address', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = event.target.querySelector('button');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Subscribing...';
    submitBtn.disabled = true;
    
    // Simulate API call (replace with actual implementation)
    setTimeout(() => {
        // Reset button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        // Show success message
        showNotification('Thank you for subscribing! Welcome to our community.', 'success');
        
        // Clear form
        event.target.querySelector('input[type="email"]').value = '';
        
        // Track signup
        trackNewsletterSignup(email);
    }, 1500);
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Reading Progress Indicator (for blog posts)
function initReadingProgress() {
    if (!document.querySelector('.post-page')) return;
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'reading-progress';
    progressBar.innerHTML = '<div class="reading-progress-fill"></div>';
    document.body.appendChild(progressBar);
    
    // Add CSS for progress bar
    const progressStyles = `
        .reading-progress {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: rgba(139, 94, 60, 0.1);
            z-index: 1000;
        }
        .reading-progress-fill {
            height: 100%;
            background: #8B5E3C;
            width: 0%;
            transition: width 0.3s ease;
        }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = progressStyles;
    document.head.appendChild(styleSheet);
    
    // Update progress on scroll
    const articleContent = document.querySelector('.article-content');
    if (articleContent) {
        window.addEventListener('scroll', throttle(updateReadingProgress, 10));
    }
}

function updateReadingProgress() {
    const articleContent = document.querySelector('.article-content');
    if (!articleContent) return;
    
    const articleRect = articleContent.getBoundingClientRect();
    const articleHeight = articleContent.offsetHeight;
    const viewportHeight = window.innerHeight;
    
    let progress = 0;
    
    if (articleRect.top < 0) {
        progress = Math.abs(articleRect.top) / (articleHeight - viewportHeight);
        progress = Math.min(progress, 1);
    }
    
    const progressFill = document.querySelector('.reading-progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progress * 100}%`;
    }
}

// Smooth Scrolling for Anchor Links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Lazy Loading for Images
function initImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Notification System
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create new notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    const notificationStyles = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 300px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .notification-success { background: #27ae60; }
        .notification-error { background: #e74c3c; }
        .notification-warning { background: #f39c12; }
        .notification-info { background: #3498db; }
        .notification.show { transform: translateX(0); }
    `;
    
    if (!document.querySelector('#notification-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'notification-styles';
        styleSheet.textContent = notificationStyles;
        document.head.appendChild(styleSheet);
    }
    
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto-hide notification
    setTimeout(() => {
        notification.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Analytics and Tracking Functions
function trackSocialShare(platform) {
    console.log(`Shared on ${platform}:`, window.location.href);
    
    // Google Analytics 4 example
    if (typeof gtag !== 'undefined') {
        gtag('event', 'share', {
            method: platform,
            content_type: 'article',
            item_id: window.location.pathname
        });
    }
}

function trackNewsletterSignup(email) {
    console.log('Newsletter signup:', email);
    
    // Google Analytics 4 example
    if (typeof gtag !== 'undefined') {
        gtag('event', 'sign_up', {
            method: 'newsletter'
        });
    }
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Keyboard Navigation Enhancement
document.addEventListener('keydown', function(e) {
    // ESC key to close modals or return to blog index
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.active');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    // Search shortcut (Ctrl/Cmd + K)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input, .search-input-large');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Performance Monitoring
if ('performance' in window) {
    window.addEventListener('load', function() {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }, 0);
    });
}

// Export functions for external use
window.blogUtils = {
    shareOnTwitter,
    shareOnFacebook,
    shareOnLinkedIn,
    copyToClipboard,
    showNotification
};
