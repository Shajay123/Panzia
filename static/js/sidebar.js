document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll(".menu-link").forEach(link => {

        link.addEventListener("click", function(e){

            const parent = this.parentElement;

            if(parent.querySelector(".submenu")){

                e.preventDefault();

                parent.classList.toggle("open");

            }

        });

    });

});