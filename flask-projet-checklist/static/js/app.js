// Mobile menu toggle with animation
document.getElementById('mobile-menu-button').addEventListener('click', function() {
    const menu = document.getElementById('mobile-menu');
    menu.classList.toggle('hidden');
    menu.classList.toggle('animate-fade-in');
});

// Add ripple effect to buttons
document.querySelectorAll('button, a[href="#"]').forEach(button => {
    button.addEventListener('click', function(e) {
        // Only apply to elements that don't have specific actions
        if (this.getAttribute('type') !== 'submit' && this.tagName !== 'A') {
            e.preventDefault();
        }
        
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple-effect';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .ripple-effect {
        position: absolute;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.7);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
        width: 20px;
        height: 20px;
    }
    
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Dynamic card hover effects
document.querySelectorAll('.card-hover-effect').forEach(card => {
    card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    });
});

// Add CSS for card hover effect
const cardStyle = document.createElement('style');
cardStyle.textContent = `
    .card-hover-effect {
        position: relative;
        overflow: hidden;
    }
    
    .card-hover-effect::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(
            600px circle at var(--mouse-x) var(--mouse-y),
            rgba(14, 165, 233, 0.1),
            transparent 40%
        );
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .card-hover-effect:hover::before {
        opacity: 1;
    }
`;
document.head.appendChild(cardStyle);

// Confirmation avant suppression
document.querySelectorAll('.delete-history-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément?')) {
            e.preventDefault();
        }
    });
});
