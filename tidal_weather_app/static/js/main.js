// Main JavaScript functionality for the Tidal Weather App

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize location selector
    const locationSelect = document.getElementById('locationSelect');
    if (locationSelect) {
        locationSelect.addEventListener('change', handleLocationChange);
    }
    
    // Initialize responsive behavior
    handleResponsiveLayout();
    window.addEventListener('resize', handleResponsiveLayout);
    
    // Initialize animations
    initializeAnimations();
    
    // Auto-refresh data every 5 minutes
    setInterval(refreshWeatherData, 5 * 60 * 1000);
}

function changeLocation(locationId) {
    if (!locationId) return;
    
    // Show loading state
    showLoadingState();
    
    // Update URL and reload page with new location
    const url = new URL(window.location);
    url.searchParams.set('location_id', locationId);
    window.location.href = url.toString();
}

function handleLocationChange(event) {
    changeLocation(event.target.value);
}

function showLoadingState() {
    const weatherCards = document.querySelectorAll('.weather-card');
    weatherCards.forEach(card => {
        card.classList.add('loading');
    });
}

function hideLoadingState() {
    const weatherCards = document.querySelectorAll('.weather-card');
    weatherCards.forEach(card => {
        card.classList.remove('loading');
    });
}

function handleResponsiveLayout() {
    const width = window.innerWidth;
    const body = document.body;
    
    // Remove existing responsive classes
    body.classList.remove('mobile-layout', 'tablet-layout', 'desktop-layout');
    
    // Add appropriate class based on screen size
    if (width <= 768) {
        body.classList.add('mobile-layout');
    } else if (width <= 1024) {
        body.classList.add('tablet-layout');
    } else {
        body.classList.add('desktop-layout');
    }
}

function initializeAnimations() {
    // Animate tidal wave
    animateTidalWave();
    
    // Animate coefficient display
    animateCoefficient();
    
    // Add intersection observer for scroll animations
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(handleIntersection, {
            threshold: 0.1
        });
        
        document.querySelectorAll('.weather-card').forEach(card => {
            observer.observe(card);
        });
    }
}

function animateTidalWave() {
    const waves = document.querySelectorAll('.tide-wave path');
    waves.forEach(wave => {
        const length = wave.getTotalLength();
        wave.style.strokeDasharray = length;
        wave.style.strokeDashoffset = length;
        
        // Animate the wave drawing
        wave.animate([
            { strokeDashoffset: length },
            { strokeDashoffset: 0 }
        ], {
            duration: 2000,
            easing: 'ease-in-out',
            fill: 'forwards'
        });
    });
}

function animateCoefficient() {
    const coefficients = document.querySelectorAll('.coefficient-display');
    coefficients.forEach(coeff => {
        const finalValue = parseInt(coeff.textContent) || 57;
        let currentValue = 0;
        const increment = finalValue / 50;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            coeff.textContent = Math.round(currentValue);
        }, 40);
    });
}

function handleIntersection(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}

function refreshWeatherData() {
    const currentLocation = document.getElementById('locationSelect')?.value;
    if (!currentLocation) return;
    
    console.log('Refreshing weather data...');
    
    // In a real implementation, you would make an AJAX call here
    // For now, we'll just show a subtle indication that data is being refreshed
    const weatherCards = document.querySelectorAll('.weather-card');
    weatherCards.forEach(card => {
        card.style.opacity = '0.8';
        setTimeout(() => {
            card.style.opacity = '1';
        }, 500);
    });
}

// Utility functions
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

// Export functions for global access
window.changeLocation = changeLocation;
window.refreshWeatherData = refreshWeatherData;