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
    
    // Initialize services carousel
    new ServicesCarousel();
    
    // Initialize about image carousel
    new AboutImageCarousel();
    
    // Initialize testimonials carousel
    new TestimonialsCarousel();
});

// Contact form handling
document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! We will get back to you soon.');
    this.reset();
});

// Services Carousel Functionality
class ServicesCarousel {
    constructor() {
        this.grid = document.getElementById('services-grid');
        this.prevBtn = document.getElementById('carousel-prev');
        this.nextBtn = document.getElementById('carousel-next');
        this.cards = this.grid ? this.grid.querySelectorAll('.service-card') : [];
        this.currentIndex = 0;
        this.cardsToShow = window.innerWidth <= 768 ? 1 : 3; // Show 1 on mobile, 3 on desktop
        
        if (this.grid && this.cards.length > 0) {
            this.init();
        }
    }
    
    init() {
        // Only show carousel if there are more cards than the display limit
        if (this.cards.length <= this.cardsToShow) {
            this.hideCarouselButtons();
            return;
        }
        
        this.setupEventListeners();
        this.updateCarousel();
        this.updateButtons();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const newCardsToShow = window.innerWidth <= 768 ? 1 : 3;
            if (newCardsToShow !== this.cardsToShow) {
                this.cardsToShow = newCardsToShow;
                this.currentIndex = 0; // Reset to beginning
                this.updateCarousel();
                this.updateButtons();
                
                // Show/hide buttons based on card count
                if (this.cards.length <= this.cardsToShow) {
                    this.hideCarouselButtons();
                } else {
                    this.showCarouselButtons();
                }
            }
        });
    }
    
    setupEventListeners() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prev());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.next());
        }
    }
    
    prev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateCarousel();
            this.updateButtons();
        }
    }
    
    next() {
        const maxIndex = this.cards.length - this.cardsToShow;
        if (this.currentIndex < maxIndex) {
            this.currentIndex++;
            this.updateCarousel();
            this.updateButtons();
        }
    }
    
    updateCarousel() {
        if (!this.grid) return;
        
        const cardWidth = this.cards[0].offsetWidth;
        const gap = 32; // 2rem in pixels
        const translateX = -(this.currentIndex * (cardWidth + gap));
        
        this.grid.style.transform = `translateX(${translateX}px)`;
    }
    
    updateButtons() {
        if (!this.prevBtn || !this.nextBtn) return;
        
        const maxIndex = this.cards.length - this.cardsToShow;
        
        this.prevBtn.disabled = this.currentIndex === 0;
        this.nextBtn.disabled = this.currentIndex >= maxIndex;
    }
    
    hideCarouselButtons() {
        if (this.prevBtn) this.prevBtn.style.display = 'none';
        if (this.nextBtn) this.nextBtn.style.display = 'none';
    }
    
    showCarouselButtons() {
        if (this.prevBtn) this.prevBtn.style.display = 'block';
        if (this.nextBtn) this.nextBtn.style.display = 'block';
    }
}

// About Image Carousel Functionality
class AboutImageCarousel {
    constructor() {
        this.carousel = document.querySelector('.about-carousel');
        this.slides = document.querySelectorAll('.about-slide');
        this.prevBtn = document.getElementById('about-prev');
        this.nextBtn = document.getElementById('about-next');
        this.dots = document.querySelectorAll('.about-carousel-dots .about-dot');
        this.currentSlide = 0;
        this.autoSlideInterval = null;
        
        if (this.carousel && this.slides.length > 0) {
            this.init();
        }
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoSlide();
        
        // Pause auto-slide on hover
        this.carousel.addEventListener('mouseenter', () => this.pauseAutoSlide());
        this.carousel.addEventListener('mouseleave', () => this.startAutoSlide());
    }
    
    setupEventListeners() {
        // Navigation buttons
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                this.pauseAutoSlide();
                this.prevSlide();
                this.startAutoSlide();
            });
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                this.pauseAutoSlide();
                this.nextSlide();
                this.startAutoSlide();
            });
        }
        
        // Dot indicators
        this.dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.pauseAutoSlide();
                this.goToSlide(index);
                this.startAutoSlide();
            });
        });
        
        // Touch/swipe support for mobile
        let startX = 0;
        let endX = 0;
        
        this.carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        this.carousel.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            this.handleSwipe(startX, endX);
        });
    }
    
    handleSwipe(startX, endX) {
        const difference = startX - endX;
        const threshold = 50; // Minimum swipe distance
        
        if (Math.abs(difference) > threshold) {
            this.pauseAutoSlide();
            if (difference > 0) {
                // Swipe left - next slide
                this.nextSlide();
            } else {
                // Swipe right - previous slide
                this.prevSlide();
            }
            this.startAutoSlide();
        }
    }
    
    goToSlide(index) {
        // Remove active class from current slide and dot
        this.slides[this.currentSlide].classList.remove('active');
        this.dots[this.currentSlide].classList.remove('active');
        
        // Update current slide index
        this.currentSlide = index;
        
        // Add active class to new slide and dot
        this.slides[this.currentSlide].classList.add('active');
        this.dots[this.currentSlide].classList.add('active');
    }
    
    nextSlide() {
        const nextIndex = (this.currentSlide + 1) % this.slides.length;
        this.goToSlide(nextIndex);
    }
    
    prevSlide() {
        const prevIndex = (this.currentSlide - 1 + this.slides.length) % this.slides.length;
        this.goToSlide(prevIndex);
    }
    
    startAutoSlide() {
        this.autoSlideInterval = setInterval(() => {
            this.nextSlide();
        }, 4000); // Change slide every 4 seconds
    }
    
    pauseAutoSlide() {
        if (this.autoSlideInterval) {
            clearInterval(this.autoSlideInterval);
            this.autoSlideInterval = null;
        }
    }
}

// Testimonials Carousel Functionality
class TestimonialsCarousel {
    constructor() {
        this.grid = document.getElementById('testimonials-grid');
        this.prevBtn = document.getElementById('testimonial-prev');
        this.nextBtn = document.getElementById('testimonial-next');
        this.cards = this.grid ? this.grid.querySelectorAll('.testimonial-card') : [];
        this.currentIndex = 0;
        this.cardsToShow = window.innerWidth <= 768 ? 1 : window.innerWidth <= 1024 ? 2 : 3;
        
        if (this.grid && this.cards.length > 0) {
            this.init();
        }
    }
    
    init() {
        // Only show carousel if there are more cards than the display limit
        if (this.cards.length <= this.cardsToShow) {
            this.hideCarouselButtons();
            return;
        }
        
        this.setupEventListeners();
        this.updateCarousel();
        this.updateButtons();
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const newCardsToShow = window.innerWidth <= 768 ? 1 : window.innerWidth <= 1024 ? 2 : 3;
            if (newCardsToShow !== this.cardsToShow) {
                this.cardsToShow = newCardsToShow;
                this.currentIndex = 0; // Reset to beginning
                this.updateCarousel();
                this.updateButtons();
                
                // Show/hide buttons based on card count
                if (this.cards.length <= this.cardsToShow) {
                    this.hideCarouselButtons();
                } else {
                    this.showCarouselButtons();
                }
            }
        });
    }
    
    setupEventListeners() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prev());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.next());
        }
    }
    
    prev() {
        if (this.currentIndex > 0) {
            this.currentIndex--;
            this.updateCarousel();
            this.updateButtons();
        }
    }
    
    next() {
        const maxIndex = this.cards.length - this.cardsToShow;
        if (this.currentIndex < maxIndex) {
            this.currentIndex++;
            this.updateCarousel();
            this.updateButtons();
        }
    }
    
    updateCarousel() {
        if (!this.grid) return;
        
        const cardWidth = this.cards[0].offsetWidth;
        const gap = 32; // 2rem in pixels
        const translateX = -(this.currentIndex * (cardWidth + gap));
        
        this.grid.style.transform = `translateX(${translateX}px)`;
    }
    
    updateButtons() {
        if (!this.prevBtn || !this.nextBtn) return;
        
        const maxIndex = this.cards.length - this.cardsToShow;
        
        this.prevBtn.disabled = this.currentIndex === 0;
        this.nextBtn.disabled = this.currentIndex >= maxIndex;
    }
    
    hideCarouselButtons() {
        if (this.prevBtn) this.prevBtn.style.display = 'none';
        if (this.nextBtn) this.nextBtn.style.display = 'none';
    }
    
    showCarouselButtons() {
        if (this.prevBtn) this.prevBtn.style.display = 'block';
        if (this.nextBtn) this.nextBtn.style.display = 'block';
    }
}
