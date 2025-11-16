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
            // Get language from URL parameter or default to 'ENG'
            const urlParams = new URLSearchParams(window.location.search);
            const language = urlParams.get('lang') || 'ENG';
            
            const response = await fetch(`/booking/services?lang=${language}`);
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
            // Fetch available slots from the backend API
            const formattedDate = date.toISOString().split('T')[0]; // YYYY-MM-DD format
            const serviceId = this.selectedService ? this.selectedService.id : '';
            
            const response = await fetch(`/booking/available-slots?date=${formattedDate}&service_id=${serviceId}`);
            
            if (response.ok) {
                const slots = await response.json();
                this.availableSlots = slots;
            } else {
                // Fallback to generating slots locally if API fails
                const slots = [];
                const startHour = 9;
                const endHour = 18;
                
                for (let hour = startHour; hour < endHour; hour++) {
                    for (let minutes of [0, 30]) {
                        if (hour === endHour - 1 && minutes === 30) break; // Don't go past 6 PM
                        
                        const time = new Date(date);
                        time.setHours(hour, minutes, 0, 0);
                        
                        slots.push({
                            time: time.toISOString(),
                            available: true,
                            isFullyBooked: false,
                            bookingCount: 0,
                            timeString: this.formatTime(time)
                        });
                    }
                }
                
                this.availableSlots = slots;
            }
            
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
            
            // Parse the time if it's a string
            const slotTime = typeof slot.time === 'string' ? new Date(slot.time) : slot.time;
            
            // Show "Fully Booked" indicator if slot has 10+ bookings
            if (slot.isFullyBooked) {
                slotElement.innerHTML = `
                    <div class="time-slot-time">${slot.timeString}</div>
                    <div class="time-slot-status fully-booked">Fully Booked (${slot.bookingCount})</div>
                `;
                slotElement.classList.add('fully-booked-slot');
            } else {
                slotElement.innerHTML = `
                    <div class="time-slot-time">${slot.timeString}</div>
                    ${slot.bookingCount > 0 ? `<div class="time-slot-status">(${slot.bookingCount} booked)</div>` : ''}
                `;
            }
            
            // Always clickable - even "Fully Booked" slots can be selected
            slotElement.addEventListener('click', () => this.selectTimeSlot({
                time: slotTime,
                timeString: slot.timeString,
                isFullyBooked: slot.isFullyBooked,
                bookingCount: slot.bookingCount
            }, slotElement));

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
        const numPeople = parseInt(document.getElementById('num-people').value) || 1;
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
                <span class="summary-label">Number of People:</span>
                <span class="summary-value">${numPeople} ${numPeople === 1 ? 'person' : 'people'}</span>
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
            // Get number of people with better validation
            const numPeopleElement = document.getElementById('num-people');
            let numPeople = 1; // Default value
            
            if (numPeopleElement && numPeopleElement.value) {
                numPeople = parseInt(numPeopleElement.value);
                if (isNaN(numPeople) || numPeople < 1) {
                    numPeople = 1;
                } else if (numPeople > 10) {
                    numPeople = 10;
                }
            }
            
            console.log('Number of people selected:', numPeople);
            
            // Validate required fields
            const userName = document.getElementById('user-name').value.trim();
            const userEmail = document.getElementById('user-email').value.trim();
            
            if (!userName) {
                throw new Error('Please enter your full name.');
            }
            
            if (!userEmail || !userEmail.includes('@')) {
                throw new Error('Please enter a valid email address.');
            }
            
            if (!this.selectedService || !this.selectedTime) {
                throw new Error('Please select a service and time slot.');
            }
            
            console.log('Submitting booking with data:', {
                user_name: userName,
                email: userEmail,
                phone: document.getElementById('user-phone').value || null,
                num_people: numPeople,
                service_id: this.selectedService.id,
                start_time: this.selectedTime.time.toISOString(),
                end_time: new Date(this.selectedTime.time.getTime() + this.selectedService.duration * 60000).toISOString()
            });
            
            const bookingData = {
                user_name: userName,
                email: userEmail,
                start_time: this.selectedTime.time.toISOString(),
                end_time: new Date(this.selectedTime.time.getTime() + this.selectedService.duration * 60000).toISOString(),
                service_id: this.selectedService.id,
                phone: document.getElementById('user-phone').value || null,
                num_people: numPeople,
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
                
                // Show special message if the slot was fully booked
                if (result.isFullyBooked) {
                    this.showFullyBookedSuccess(result);
                } else {
                    this.showSuccess();
                }
            } else {
                let errorMessage = 'Failed to create booking';
                try {
                    const error = await response.json();
                    errorMessage = error.error || error.message || errorMessage;
                    console.error('Server error response:', error);
                } catch (parseError) {
                    console.error('Failed to parse error response:', parseError);
                    errorMessage = `Server error (${response.status}): ${response.statusText}`;
                }
                console.error('Final error message:', errorMessage);
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error('Error submitting booking:', error);
            console.error('Error details:', error.message);
            console.error('Error type:', typeof error);
            console.error('Error string representation:', String(error));
            
            // Better error message handling
            let errorMessage = 'Failed to submit booking. Please try again.';
            if (error && error.message) {
                errorMessage = error.message;
            } else if (typeof error === 'string') {
                errorMessage = error;
            }
            
            this.showError(errorMessage);
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

    showFullyBookedSuccess(result) {
        // Hide all steps
        document.querySelectorAll('.booking-step').forEach(step => {
            step.classList.remove('active');
        });
        
        // Show success step
        document.getElementById('step-success').style.display = 'block';
        
        // Update confirmation details with "Fully Booked" notice
        const confirmationDetails = document.getElementById('confirmation-details');
        const endTime = new Date(this.selectedTime.time);
        endTime.setMinutes(endTime.getMinutes() + this.selectedService.duration);
        
        confirmationDetails.innerHTML = `
            <div class="booking-details">
                <div class="fully-booked-notice">
                    <i class="fas fa-exclamation-triangle"></i>
                    <strong>Notice:</strong> This time slot is fully booked (${result.bookingCount} people), 
                    but your booking has been saved and you will be contacted if a spot becomes available.
                </div>
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
                <p><strong>Status:</strong> <span class="status-waitlist">Waitlist</span></p>
            </div>
        `;
        
        // Hide progress bar
        document.querySelector('.progress-bar').style.display = 'none';
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            if (show) {
                overlay.style.display = 'flex';
            } else {
                overlay.style.display = 'none';
            }
        }
    }

    showError(message) {
        const modal = document.getElementById('error-modal');
        const errorMessage = document.getElementById('error-message');
        if (modal && errorMessage) {
            errorMessage.textContent = message;
            modal.style.display = 'block';
        }
    }

    closeModal() {
        const modal = document.getElementById('error-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
}

// Initialize the booking app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new BookingApp();
});

// Global function for modal close
function closeModal() {
    const modal = document.getElementById('error-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}
