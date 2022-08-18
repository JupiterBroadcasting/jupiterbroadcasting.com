const swiper = new Swiper(".show-slider", {
    navigation: {
      nextEl: '.swiper-button-next',
      prevEl: '.swiper-button-prev',
    },
    slidesPerGroup: 1,
    slidesPerView: 1.1,
    spaceBetween: 12,
    // Responsive breakpoint
    breakpoints: {
    // when window width is >= 480px
    440: {
      slidesPerView: 1.3,
      slidesPerGroup: 1
    },
    600: {
      slidesPerView: 1.7,
      slidesPerGroup: 1
    },
    640: {
      slidesPerView: 2.1,
      slidesPerGroup: 2
    },
    850: {
      slidesPerView: 2.7,
      slidesPerGroup: 2
    },
    1000: {
      slidesPerView: 3.1,
      slidesPerGroup: 3
    },
    1216: {
      slidesPerView: 3.7,
      slidesPerGroup: 3
    },
    1450: {
      slidesPerView: 4.1,
      slidesPerGroup: 4
    },
    1550: {
        slidesPerView: 4.3,
        slidesPerGroup: 4
    }
  }
  });