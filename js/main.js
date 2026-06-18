(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.sticky-top').css('top', '0px');
        } else {
            $('.sticky-top').css('top', '-100px');
        }
    });
    
    
    // Dropdown on mouse hover
    const $dropdown = $(".dropdown");
    const $dropdownToggle = $(".dropdown-toggle");
    const $dropdownMenu = $(".dropdown-menu");
    const showClass = "show";
    
    $(window).on("load resize", function() {
        if (this.matchMedia("(min-width: 992px)").matches) {
            $dropdown.hover(
            function() {
                const $this = $(this);
                $this.addClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "true");
                $this.find($dropdownMenu).addClass(showClass);
            },
            function() {
                const $this = $(this);
                $this.removeClass(showClass);
                $this.find($dropdownToggle).attr("aria-expanded", "false");
                $this.find($dropdownMenu).removeClass(showClass);
            }
            );
        } else {
            $dropdown.off("mouseenter mouseleave");
        }
    });
    
    
    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });


    // Header carousel
    $(".header-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        items: 1,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ]
    });


    // Testimonials carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1000,
        center: true,
        margin: 24,
        dots: true,
        loop: true,
        nav : false,
        responsive: {
            0:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            }
        }
    });
    
})(jQuery);

const iBtn = document.querySelector('.button-unstyled');
iBtn.addEventListener('click', function () {
    const popupOverlay = document.getElementById('popupOverlay');
    
    const popup = document.getElementById('popup');

    const closePopup = document.getElementById('closePopup');

    const emailInput = document.getElementById('emailInput');

    // Function to open the popup

    function openPopup() {

        popupOverlay.style.display = 'block';

    }

    // Function to close the popup

    function closePopupFunc() {

        popupOverlay.style.display = 'none';

    }

    // Function to submit the signup form

    function submitForm() {

        const email = emailInput.value;

        // Add your form submission logic here

        console.log(`Email submitted: ${email}`);

        closePopupFunc(); // Close the popup after form submission

    }

    // Event listeners

    // Trigger the popup to open (you can call this function on a button click or any other event)

    openPopup();

    // Close the popup when the close button is clicked

    closePopup.addEventListener('click', closePopupFunc);

    // Close the popup when clicking outside the popup content

    popupOverlay.addEventListener('click', function (event) {

        if (event.target === popupOverlay) {

            closePopupFunc();

        }

    });

    // You can customize and expand these functions based on your specific requirements.

});
const btnApply = document.getElementById('apply-btn');
btnApply.addEventListener('click', function () {
    const popupOverlay = document.getElementById('popupOverlay');
    
    const popup = document.getElementById('popup');

    const closePopup = document.getElementById('closePopup');

    const emailInput = document.getElementById('emailInput');

    // Function to open the popup

    function openPopup() {

        popupOverlay.style.display = 'block';

    }

    // Function to close the popup

    function closePopupFunc() {

        popupOverlay.style.display = 'none';

    }

    // Function to submit the signup form

    function submitForm() {

        const email = emailInput.value;

        // Add your form submission logic here

        console.log(`Email submitted: ${email}`);

        closePopupFunc(); // Close the popup after form submission

    }

    // Event listeners

    // Trigger the popup to open (you can call this function on a button click or any other event)

    openPopup();

    // Close the popup when the close button is clicked

    closePopup.addEventListener('click', closePopupFunc);

    // Close the popup when clicking outside the popup content

    popupOverlay.addEventListener('click', function (event) {

        if (event.target === popupOverlay) {

            closePopupFunc();

        }

    });

    // You can customize and expand these functions based on your specific requirements.

});
