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
    spinner(0);
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.sticky-top').addClass('shadow-sm').css('top', '0px');
        } else {
            $('.sticky-top').removeClass('shadow-sm').css('top', '-100px');
        }
    });


    // Hero Header carousel
    $(".header-carousel").owlCarousel({
        animateOut: 'slideOutDown',
        items: 1,
        autoplay: true,
        autoplayTimeout: 9000, // ← ESTE es el tiempo entre slides (en milisegundos)
        smartSpeed: 700,
        dots: false,
        loop: true,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-down"></i>'
        ],
    });


    // attractions carousel
    $(".attractions-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 2000,
        center: false,
        dots: false,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="fa fa-angle-right"></i>',
            '<i class="fa fa-angle-left"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:2
            },
            768:{
                items:2
            },
            992:{
                items:3
            },
            1200:{
                items:4
            },
            1400:{
                items:4
            }
        }
    });


    // testimonial carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="fa fa-angle-right"></i>',
            '<i class="fa fa-angle-left"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:1
            },
            992:{
                items:1
            },
            1200:{
                items:1
            }
        }
    });


    // Facts counter
    $('[data-toggle="counter-up"]').counterUp({
        delay: 5,
        time: 2000
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

    // Quitar los mensajes despues de 5 segundos
    setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
      alert.classList.remove('show');
      alert.classList.add('hide');
    });
  }, 5000); // 5 segundos
  
})(jQuery);



document.addEventListener("DOMContentLoaded", function () {
  const rows = document.querySelectorAll(".selectable-row");
  const equipoSeleccionadoSpan = document.getElementById("equipo-seleccionado");
  let equipoSeleccionadoId = null;

  function deseleccionar() {
    rows.forEach(r => r.classList.remove("selected"));
    equipoSeleccionadoId = null;
    if (equipoSeleccionadoSpan) {
      equipoSeleccionadoSpan.textContent = "Ninguno";
    }
  }

  rows.forEach(row => {
    row.addEventListener("click", () => {
      deseleccionar();
      row.classList.add("selected");

      const equipoId = row.dataset.equipoId;
      equipoSeleccionadoId = equipoId;
      if (equipoSeleccionadoSpan) {
        equipoSeleccionadoSpan.textContent = row.cells[1].textContent;
      }

      fetch("/juez/seleccionar_equipo/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": window.configBatalla.csrfToken
        },
        body: JSON.stringify({
          equipo_id: equipoId,
          ronda_id: window.configBatalla.rondaId
        })
      });
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      deseleccionar();
    }
  });

  document.addEventListener("click", function (event) {
    const tabla = document.getElementById("tabla-equipos");
    if (!tabla.contains(event.target)) {
      deseleccionar();
    }
  });
});



