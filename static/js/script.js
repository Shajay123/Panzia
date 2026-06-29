console.log('PANZIA Loaded Successfully');

const menuToggle = document.getElementById('menu-toggle');
const navLinks = document.querySelector('.nav-links');

if(menuToggle){
    menuToggle.addEventListener('click', () => {
        navLinks.classList.toggle('active');
    });
}

const revealElements = document.querySelectorAll(
    '.workflow-card, .problem-card, .score-box, .workflow-step'
);

function revealOnScroll() {

    revealElements.forEach((element) => {

        const windowHeight = window.innerHeight;
        const revealTop = element.getBoundingClientRect().top;
        const revealPoint = 120;

        if(revealTop < windowHeight - revealPoint){
            element.classList.add('active-reveal');
        }

    });
}

window.addEventListener('scroll', revealOnScroll);