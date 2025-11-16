// Carousel functionality
document.addEventListener("DOMContentLoaded", () => {
  const slides = document.querySelectorAll(".carousel-slide");
  const prev = document.getElementById("prev");
  const next = document.getElementById("next");
  const dotsContainer = document.getElementById("carousel-dots");
  let current = 0;
  let interval;

  // Create dots
  slides.forEach((_, i) => {
    const dot = document.createElement("button");
    dot.addEventListener("click", () => goToSlide(i));
    dotsContainer.appendChild(dot);
  });

  const dots = dotsContainer.querySelectorAll("button");

  function updateSlides() {
    slides.forEach((s, i) => s.classList.toggle("active", i === current));
    dots.forEach((d, i) => d.classList.toggle("active", i === current));

    // Restart text animations
    const content = slides[current].querySelector(".slide-content");
    if (content) {
      content.querySelectorAll(".animate-up, .fade-in").forEach(el => {
        el.style.animation = "none";
        void el.offsetWidth; // Force reflow
        el.style.animation = "";
      });
    }
  }

  function goToSlide(index) {
    current = index;
    updateSlides();
    resetInterval();
  }

  function nextSlide() {
    current = (current + 1) % slides.length;
    updateSlides();
  }

  function prevSlide() {
    current = (current - 1 + slides.length) % slides.length;
    updateSlides();
  }

  function startInterval() {
    interval = setInterval(nextSlide, 6000);
  }

  function resetInterval() {
    clearInterval(interval);
    startInterval();
  }

  prev?.addEventListener("click", prevSlide);
  next?.addEventListener("click", nextSlide);

  // Touch/swipe support for mobile
  let touchStartX = 0;
  let touchEndX = 0;
  let isSwiping = false;

  const carousel = document.querySelector('.hero-carousel');
  if (carousel) {
    carousel.addEventListener('touchstart', (e) => {
      touchStartX = e.touches[0].clientX;
      isSwiping = true;
    }, { passive: true });

    carousel.addEventListener('touchmove', (e) => {
      if (!isSwiping) return;
      e.preventDefault();
    }, { passive: false });

    carousel.addEventListener('touchend', (e) => {
      if (!isSwiping) return;
      touchEndX = e.changedTouches[0].clientX;
      handleSwipe();
      isSwiping = false;
    }, { passive: true });

    // Pause auto-rotation on hover/touch
    carousel.addEventListener('mouseenter', () => {
      clearInterval(interval);
    });

    carousel.addEventListener('mouseleave', () => {
      startInterval();
    });

    carousel.addEventListener('touchstart', () => {
      clearInterval(interval);
    });

    carousel.addEventListener('touchend', () => {
      setTimeout(startInterval, 3000); // Resume after 3 seconds
    });
  }

  function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartX - touchEndX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
      if (swipeDistance > 0) {
        // Swiped left - next slide
        nextSlide();
      } else {
        // Swiped right - previous slide
        prevSlide();
      }
      resetInterval();
    }
  }

  updateSlides();
  startInterval();
});

// Add smooth scroll behavior for any anchor links
document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
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
});
