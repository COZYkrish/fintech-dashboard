/* ==========================================================================
   FinDash® Landing Page — JavaScript
   Handles: scroll-reveal, nav shrink, parallax cursor glow
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ─────────────────────────────────────────────────────────────────────────
  // 1. NAV — Shrink on scroll
  // ─────────────────────────────────────────────────────────────────────────
  const navbar = document.getElementById('navbar');

  const onScroll = () => {
    if (window.scrollY > 60) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', onScroll, { passive: true });

  // ─────────────────────────────────────────────────────────────────────────
  // 2. SCROLL REVEAL — IntersectionObserver
  // ─────────────────────────────────────────────────────────────────────────
  const revealEls = document.querySelectorAll('.scroll-reveal, .scroll-reveal-child');

  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          revealObserver.unobserve(entry.target);
        }
      });
    },
    {
      root: null,
      rootMargin: '0px 0px -80px 0px',
      threshold: 0.12,
    }
  );

  revealEls.forEach((el) => revealObserver.observe(el));

  // ─────────────────────────────────────────────────────────────────────────
  // 3. CURSOR GLOW — ambient pointer effect on glass cards
  // ─────────────────────────────────────────────────────────────────────────
  const glassCards = document.querySelectorAll('.glass-card, .bento-card, .stack-pill');

  glassCards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.background = `
        radial-gradient(
          200px circle at ${x}px ${y}px,
          rgba(255, 255, 255, 0.045),
          rgba(255, 255, 255, 0.015) 60%,
          rgba(255, 255, 255, 0.01) 100%
        )
      `;
    });

    card.addEventListener('mouseleave', () => {
      card.style.background = '';
    });
  });

  // ─────────────────────────────────────────────────────────────────────────
  // 4. HERO — Parallax tilt on mousemove
  // ─────────────────────────────────────────────────────────────────────────
  const heroInner = document.querySelector('.hero-inner');

  if (heroInner) {
    document.addEventListener('mousemove', (e) => {
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      const dx = (e.clientX - cx) / cx;
      const dy = (e.clientY - cy) / cy;

      const tiltX = dy * -3;
      const tiltY = dx * 3;

      heroInner.style.transform = `perspective(1200px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
    }, { passive: true });

    document.addEventListener('mouseleave', () => {
      heroInner.style.transform = '';
    });
  }

  // ─────────────────────────────────────────────────────────────────────────
  // 5. SMOOTH ANCHOR SCROLL for nav logo
  // ─────────────────────────────────────────────────────────────────────────
  document.querySelector('.nav-logo')?.addEventListener('click', (e) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

});
