// PANZIA - Main Script
console.log('PANZIA Loaded Successfully');

// ============================================
// MENU TOGGLE - With null check and safe declaration
// ============================================
(function() {
    // Check if menuToggle already exists in global scope
    if (typeof menuToggle === 'undefined') {
        var menuToggle = document.getElementById('menu-toggle');
    } else {
        var menuToggle = document.getElementById('menu-toggle');
    }
    
    var navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
})();

// ============================================
// REVEAL ON SCROLL
// ============================================
(function() {
    var revealElements = document.querySelectorAll(
        '.workflow-card, .problem-card, .score-box, .workflow-step'
    );

    function revealOnScroll() {
        var windowHeight = window.innerHeight;
        var revealPoint = 120;

        revealElements.forEach(function(element) {
            var revealTop = element.getBoundingClientRect().top;

            if (revealTop < windowHeight - revealPoint) {
                element.classList.add('active-reveal');
            }
        });
    }

    // Only add scroll listener if there are elements to reveal
    if (revealElements.length > 0) {
        window.addEventListener('scroll', revealOnScroll);
        // Initial check
        revealOnScroll();
    }
})();

// ============================================
// HANDLE NAVIGATION LINKS ACTIVE STATE
// ============================================
(function() {
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.nav-links a, .sidebar ul li a');

    navLinks.forEach(function(link) {
        var href = link.getAttribute('href');
        if (href && href !== '#' && href !== '/') {
            if (currentPath.includes(href) || currentPath === href) {
                link.classList.add('active');
            }
        }
    });
})();

// ============================================
// AUTO-DISMISS ALERTS
// ============================================
(function() {
    var alerts = document.querySelectorAll('.alert, .alert-dismissible, .error-message');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                alert.style.transition = 'all 0.3s ease';
                setTimeout(function() {
                    if (alert && alert.parentElement) {
                        alert.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
})();