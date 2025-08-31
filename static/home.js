// Hamburger menu functionality
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
const mobileAuthBtn = document.getElementById('mobile-auth-btn');
const desktopAuthBtn = document.getElementById('desktop-auth-btn');

hamburger.addEventListener('click', (e) => {
    e.stopPropagation();
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

// Close mobile menu when clicking outside
document.addEventListener('click', (e) => {
    if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
    }
});

// Prevent mobile menu from closing when clicking inside it
mobileMenu.addEventListener('click', (e) => {
    e.stopPropagation();
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

// Override auth.js initialization to use our auth buttons
function initializeAuthButtons() {
    updateAuthButtons().catch(error => {
        console.error('Failed to update auth buttons:', error);
        // Buttons already have default state
    });
}

async function updateAuthButtons() {
    try {
        const status = await checkAuthStatus();
        
        // Update both mobile and desktop auth buttons
        const authButtons = [mobileAuthBtn, desktopAuthBtn].filter(btn => btn);
        
        authButtons.forEach(btn => {
            if (status.logged_in) {
                btn.textContent = 'Logout';
                btn.classList.add('logout-btn');
                btn.onclick = async () => {
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
                btn.textContent = 'Login';
                btn.classList.remove('logout-btn');
                btn.onclick = showLoginModal;
            }
        });
    } catch (error) {
        console.error('Error checking auth status:', error);
        const authButtons = [mobileAuthBtn, desktopAuthBtn].filter(btn => btn);
        authButtons.forEach(btn => {
            btn.textContent = 'Login';
            btn.classList.remove('logout-btn');
            btn.onclick = showLoginModal;
        });
    }
}

// Initialize auth buttons when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for auth.js to load
    setTimeout(initializeAuthButtons, 100);
});

// Contact form handling
document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! We will get back to you soon.');
    this.reset();
});
