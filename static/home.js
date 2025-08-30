// Hamburger menu functionality
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
const mobileAuthBtn = document.getElementById('mobile-auth-btn');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    mobileMenu.classList.toggle('active');
});

// Close mobile menu when clicking on links
document.querySelectorAll('.mobile-menu a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
    });
});

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Override auth.js initialization to use our mobile button
function initializeMobileAuthButton() {
    updateMobileAuthButton().catch(error => {
        console.error('Failed to update mobile auth button:', error);
        // Button already has default state
    });
}

async function updateMobileAuthButton() {
    try {
        const status = await checkAuthStatus();
        if (status.logged_in) {
            mobileAuthBtn.textContent = 'Logout';
            mobileAuthBtn.classList.add('logout-btn');
            mobileAuthBtn.onclick = async () => {
                try {
                    const res = await logout();
                    if (res.message) {
                        location.reload();
                    }
                } catch (error) {
                    console.error('Logout error:', error);
                }
            };
        } else {
            mobileAuthBtn.textContent = 'Login';
            mobileAuthBtn.classList.remove('logout-btn');
            mobileAuthBtn.onclick = showLoginModal;
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
        mobileAuthBtn.textContent = 'Login';
        mobileAuthBtn.classList.remove('logout-btn');
        mobileAuthBtn.onclick = showLoginModal;
    }
}

// Initialize mobile auth button when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for auth.js to load
    setTimeout(initializeMobileAuthButton, 100);
});

// Contact form handling
document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! We will get back to you soon.');
    this.reset();
});
