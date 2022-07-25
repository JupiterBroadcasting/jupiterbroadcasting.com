const swiper = new Swiper(".show-slider", {
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    slidesPerView: 1.1,
    spaceBetween: 12,
    // Responsive breakpoint
    breakpoints: {
    // when window width is >= 480px
    440: {
      slidesPerView: 1.3
    },
    600: {
      slidesPerView: 1.7
    },
    640: {
      slidesPerView: 2.1
    },
    850: {
      slidesPerView: 2.7
    },
    1000: {
      slidesPerView: 3.1
    },
    1216: {
      slidesPerView: 3.7
    },
    1450: {
      slidesPerView: 4.1
    },
    1550: {
        slidesPerView: 4.3
    }
  }
  });