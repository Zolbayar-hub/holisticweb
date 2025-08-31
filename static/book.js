// Book.js - Modern Booking Interface JavaScript

class BookingApp {
    constructor() {
        this.currentStep = 1;
        this.selectedService = null;
        this.selectedDate = null;
        this.selectedTime = null;
        this.services = [];
        this.availableSlots = [];
        
        this.init();
    }

    init() {
        this.loadServices();
        this.setupEventListeners();
        this.initCalendar();
    }

    // Load services from the backend
    async loadServices() {
        try {
            const response = await fetch('/booking/services');
            if (response.ok) {
                this.services = await response.json();
                
                // Add icons for services if not provided by backend
                this.services.forEach(service => {
                    if (!service.icon) {
                        switch (service.name.toLowerCase()) {
                            case 'yoga session':
                            case 'yoga':
                                service.icon = 'fas fa-meditation';
                                break;
                            case 'guided meditation':
                            case 'meditation':
                                service.icon = 'fas fa-lotus';
                                break;
                            case 'reiki healing':
                            case 'reiki':
                                service.icon = 'fas fa-hands';
                                break;
                            case 'holistic massage':
                            case 'massage':
                                service.icon = 'fas fa-spa';
                                break;
                            default:
                                service.icon = 'fas fa-heart';
                        }
                    }
                });
            } else {
                // Fallback to static data if API fails
                this.services = [
                    {
                        id: 1,
                        name: "Yoga Session",
                        description: "Relaxing yoga session to restore balance and flexibility",
                        duration: 60,
                        price: 75,
                        icon: "fas fa-meditation"
                    },
                    {
                        id: 2,
                        name: "Guided Meditation",
                        description: "Deep meditation practice for mental clarity and peace",
                        duration: 45,
                        price: 50,
                        icon: "fas fa-lotus"
                    },
                    {
                        id: 3,
                        name: "Reiki Healing",
                        description: "Energy healing session for physical and emotional wellness",
                        duration: 60,
                        price: 90,
                        icon: "fas fa-hands"
                    },
                    {
                        id: 4,
                        name: "Holistic Massage",
                        description: "Therapeutic massage combining multiple healing techniques",
                        duration: 90,
                        price: 120,
                        icon: "fas fa-spa"
                    }
                ];
            }
            
            this.renderServices();
        } catch (error) {
            console.error('Error loading services:', error);
            // Use fallback data
            this.services = [
                {
                    id: 1,
                    name: "Yoga Session",
                    description: "Relaxing yoga session to restore balance and flexibility",
                    duration: 60,
                    price: 75,
                    icon: "fas fa-meditation"
                },
                {
                    id: 2,
                    name: "Guided Meditation",
                    description: "Deep meditation practice for mental clarity and peace",
                    duration: 45,
                    price: 50,
                    icon: "fas fa-lotus"
                },
                {
                    id: 3,
                    name: "Reiki Healing",
                    description: "Energy healing session for physical and emotional wellness",
                    duration: 60,
                    price: 90,
                    icon: "fas fa-hands"
                },
                {
                    id: 4,
                    name: "Holistic Massage",
                    description: "Therapeutic massage combining multiple healing techniques",
                    duration: 90,
                    price: 120,
                    icon: "fas fa-spa"
                }
            ];
            this.renderServices();
        }
    }

    renderServices() {
        const servicesGrid = document.getElementById('services-grid');
        servicesGrid.innerHTML = '';

        this.services.forEach(service => {
            const serviceCard = document.createElement('div');
            serviceCard.className = 'service-card';
            serviceCard.setAttribute('data-service-id', service.id);
            
            serviceCard.innerHTML = `
                <div class="service-icon">
                    <i class="${service.icon}"></i>
                </div>
                <div class="service-name">${service.name}</div>
                <div class="service-description">${service.description}</div>
                <div class="service-details">
                    <span class="service-duration">
                        <i class="fas fa-clock"></i> ${service.duration} min
                    </span>
                    <span class="service-price">$${service.price}</span>
                </div>
            `;
            
            serviceCard.addEventListener('click', () => this.selectService(service));
            servicesGrid.appendChild(serviceCard);
        });
    }

    selectService(service) {
        // Remove previous selection
        document.querySelectorAll('.service-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Add selection to clicked card
        document.querySelector(`[data-service-id="${service.id}"]`).classList.add('selected');
        
        this.selectedService = service;
        document.getElementById('next-to-datetime').disabled = false;
    }

    initCalendar() {
        const calendar = document.getElementById('calendar');
        const currentDate = new Date();
        
        this.renderCalendar(currentDate);
    }

    renderCalendar(date) {
        const calendar = document.getElementById('calendar');
        const year = date.getFullYear();
        const month = date.getMonth();
        
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const firstDayOfWeek = firstDay.getDay();
        const daysInMonth = lastDay.getDate();
        
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        calendar.innerHTML = `
            <div class="calendar-header">
                <button class="calendar-nav" id="prev-month">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <div class="calendar-month">${monthNames[month]} ${year}</div>
                <button class="calendar-nav" id="next-month">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            <div class="calendar-grid">
                <div class="calendar-day-header">Sun</div>
                <div class="calendar-day-header">Mon</div>
                <div class="calendar-day-header">Tue</div>
                <div class="calendar-day-header">Wed</div>
                <div class="calendar-day-header">Thu</div>
                <div class="calendar-day-header">Fri</div>
                <div class="calendar-day-header">Sat</div>
            </div>
        `;
        
        const calendarGrid = calendar.querySelector('.calendar-grid');
        
        // Add empty cells for days before the first day of the month
        for (let i = 0; i < firstDayOfWeek; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day disabled';
            calendarGrid.appendChild(emptyDay);
        }
        
        // Add days of the month
        const today = new Date();
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;
            
            const currentDay = new Date(year, month, day);
            
            // Disable past dates
            if (currentDay < today.setHours(0, 0, 0, 0)) {
                dayElement.classList.add('disabled');
            } else {
                // Check if it's today
                if (currentDay.toDateString() === new Date().toDateString()) {
                    dayElement.classList.add('today');
                }
                
                dayElement.addEventListener('click', () => this.selectDate(currentDay));
            }
            
            calendarGrid.appendChild(dayElement);
        }
        
        // Add navigation event listeners
        document.getElementById('prev-month').addEventListener('click', () => {
            const prevMonth = new Date(year, month - 1, 1);
            this.renderCalendar(prevMonth);
        });
        
        document.getElementById('next-month').addEventListener('click', () => {
            const nextMonth = new Date(year, month + 1, 1);
            this.renderCalendar(nextMonth);
        });
    }

    selectDate(date) {
        // Remove previous selection
        document.querySelectorAll('.calendar-day').forEach(day => {
            day.classList.remove('selected');
        });
        
        // Add selection to clicked day
        event.target.classList.add('selected');
        
        this.selectedDate = date;
        this.updateSelectedDateDisplay();
        this.loadAvailableSlots(date);
    }

    updateSelectedDateDisplay() {
        const display = document.getElementById('selected-date-display');
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        display.textContent = this.selectedDate.toLocaleDateString('en-US', options);
    }

    async loadAvailableSlots(date) {
        try {
            // Generate available time slots (9 AM to 6 PM, 30-minute intervals)
            const slots = [];
            const startHour = 9;
            const endHour = 18;
            
            for (let hour = startHour; hour < endHour; hour++) {
                for (let minutes of [0, 30]) {
                    if (hour === endHour - 1 && minutes === 30) break; // Don't go past 6 PM
                    
                    const time = new Date(date);
                    time.setHours(hour, minutes, 0, 0);
                    
                    // Check if slot is available (simulate with random availability)
                    const isAvailable = Math.random() > 0.3; // 70% chance of being available
                    
                    slots.push({
                        time: time,
                        available: isAvailable,
                        timeString: this.formatTime(time)
                    });
                }
            }
            
            this.availableSlots = slots;
            this.renderTimeSlots();
        } catch (error) {
            console.error('Error loading available slots:', error);
            this.showError('Failed to load available time slots.');
        }
    }

    renderTimeSlots() {
        const timeSlotsContainer = document.getElementById('time-slots');
        timeSlotsContainer.innerHTML = '';

        this.availableSlots.forEach((slot, index) => {
            const slotElement = document.createElement('div');
            slotElement.className = 'time-slot';
            slotElement.textContent = slot.timeString;
            
            if (slot.available) {
                slotElement.addEventListener('click', () => this.selectTimeSlot(slot, slotElement));
            } else {
                slotElement.classList.add('unavailable');
            }
            
            timeSlotsContainer.appendChild(slotElement);
        });
    }

    selectTimeSlot(slot, element) {
        // Remove previous selection
        document.querySelectorAll('.time-slot').forEach(ts => {
            ts.classList.remove('selected');
        });
        
        // Add selection to clicked slot
        element.classList.add('selected');
        
        this.selectedTime = slot;
        document.getElementById('next-to-details').disabled = false;
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }

    setupEventListeners() {
        // Step navigation
        document.getElementById('next-to-datetime').addEventListener('click', () => {
            this.goToStep(2);
        });
        
        document.getElementById('back-to-service').addEventListener('click', () => {
            this.goToStep(1);
        });
        
        document.getElementById('next-to-details').addEventListener('click', () => {
            this.goToStep(3);
        });
        
        document.getElementById('back-to-datetime').addEventListener('click', () => {
            this.goToStep(2);
        });
        
        document.getElementById('next-to-summary').addEventListener('click', () => {
            if (this.validateContactForm()) {
                this.goToStep(4);
                this.renderBookingSummary();
            }
        });
        
        document.getElementById('back-to-details').addEventListener('click', () => {
            this.goToStep(3);
        });
        
        document.getElementById('confirm-booking').addEventListener('click', () => {
            this.submitBooking();
        });

        // Form validation
        const form = document.getElementById('contact-form');
        form.addEventListener('input', this.updateFormValidation.bind(this));

        // Modal close
        document.querySelector('.close').addEventListener('click', this.closeModal);
        window.addEventListener('click', (event) => {
            const modal = document.getElementById('error-modal');
            if (event.target === modal) {
                this.closeModal();
            }
        });
    }

    goToStep(stepNumber) {
        // Hide current step
        document.querySelectorAll('.booking-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show target step
        document.getElementById(`step-${stepNumber}`).classList.add('active');
        
        // Update progress bar
        document.querySelectorAll('.progress-step').forEach((step, index) => {
            if (index + 1 <= stepNumber) {
                step.classList.add('active');
            } else {
                step.classList.remove('active');
            }
        });
        
        this.currentStep = stepNumber;
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    validateContactForm() {
        const name = document.getElementById('user-name').value.trim();
        const email = document.getElementById('user-email').value.trim();
        
        if (!name) {
            this.showError('Please enter your full name.');
            return false;
        }
        
        if (!email || !this.isValidEmail(email)) {
            this.showError('Please enter a valid email address.');
            return false;
        }
        
        return true;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    updateFormValidation() {
        const name = document.getElementById('user-name').value.trim();
        const email = document.getElementById('user-email').value.trim();
        
        const isValid = name && email && this.isValidEmail(email);
        document.getElementById('next-to-summary').disabled = !isValid;
    }

    renderBookingSummary() {
        const summary = document.getElementById('booking-summary');
        const name = document.getElementById('user-name').value;
        const email = document.getElementById('user-email').value;
        const phone = document.getElementById('user-phone').value;
        const requests = document.getElementById('special-requests').value;
        
        const endTime = new Date(this.selectedTime.time);
        endTime.setMinutes(endTime.getMinutes() + this.selectedService.duration);
        
        summary.innerHTML = `
            <div class="summary-item">
                <span class="summary-label">Service:</span>
                <span class="summary-value">${this.selectedService.name}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Date:</span>
                <span class="summary-value">${this.selectedDate.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                })}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Time:</span>
                <span class="summary-value">${this.formatTime(this.selectedTime.time)} - ${this.formatTime(endTime)}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Duration:</span>
                <span class="summary-value">${this.selectedService.duration} minutes</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Name:</span>
                <span class="summary-value">${name}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Email:</span>
                <span class="summary-value">${email}</span>
            </div>
            ${phone ? `
                <div class="summary-item">
                    <span class="summary-label">Phone:</span>
                    <span class="summary-value">${phone}</span>
                </div>
            ` : ''}
            ${requests ? `
                <div class="summary-item">
                    <span class="summary-label">Special Requests:</span>
                    <span class="summary-value">${requests}</span>
                </div>
            ` : ''}
            <div class="summary-item">
                <span class="summary-label">Total Price:</span>
                <span class="summary-value">$${this.selectedService.price}</span>
            </div>
        `;
    }

    async submitBooking() {
        this.showLoading(true);
        
        try {
            const bookingData = {
                user_name: document.getElementById('user-name').value,
                email: document.getElementById('user-email').value,
                start_time: this.selectedTime.time.toISOString(),
                end_time: new Date(this.selectedTime.time.getTime() + this.selectedService.duration * 60000).toISOString(),
                service_id: this.selectedService.id,
                phone: document.getElementById('user-phone').value || null,
                special_requests: document.getElementById('special-requests').value || null
            };
            
            const response = await fetch('/booking/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(bookingData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.showSuccess();
            } else {
                const error = await response.json();
                throw new Error(error.error || 'Failed to create booking');
            }
        } catch (error) {
            console.error('Error submitting booking:', error);
            this.showError('Failed to submit booking. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    showSuccess() {
        // Hide all steps
        document.querySelectorAll('.booking-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show success step
        document.getElementById('step-success').style.display = 'block';
        
        // Update confirmation details
        const confirmationDetails = document.getElementById('confirmation-details');
        const endTime = new Date(this.selectedTime.time);
        endTime.setMinutes(endTime.getMinutes() + this.selectedService.duration);
        
        confirmationDetails.innerHTML = `
            <div class="booking-details">
                <h4><i class="fas fa-info-circle"></i> Booking Details</h4>
                <p><strong>Service:</strong> ${this.selectedService.name}</p>
                <p><strong>Date:</strong> ${this.selectedDate.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                })}</p>
                <p><strong>Time:</strong> ${this.formatTime(this.selectedTime.time)} - ${this.formatTime(endTime)}</p>
                <p><strong>Location:</strong> Our Holistic Wellness Center</p>
            </div>
        `;
        
        // Hide progress bar
        document.querySelector('.progress-bar').style.display = 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    showError(message) {
        const modal = document.getElementById('error-modal');
        const errorMessage = document.getElementById('error-message');
        errorMessage.textContent = message;
        modal.style.display = 'block';
    }

    closeModal() {
        document.getElementById('error-modal').style.display = 'none';
    }
}

// Initialize the booking app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new BookingApp();
});

// Global function for modal close
function closeModal() {
    document.getElementById('error-modal').style.display = 'none';
}
