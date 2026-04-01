// ============================================================
// GSAP ScrollTrigger Effects — A/B Test
// Layered on top of existing IntersectionObserver engine
// ============================================================

(function () {
  'use strict';

  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  // ── Evidence card curtain reveals ──────────────────────────
  gsap.utils.toArray('.evidence-card').forEach(function (card) {
    gsap.from(card, {
      clipPath: 'inset(0 100% 0 0)',
      scrollTrigger: {
        trigger: card,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.8,
      ease: 'power2.out'
    });
  });

  // ── Pull quote parallax ────────────────────────────────────
  gsap.utils.toArray('.pull-quote').forEach(function (pq) {
    gsap.fromTo(pq,
      { y: 20 },
      {
        y: -20,
        ease: 'none',
        scrollTrigger: {
          trigger: pq,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1
        }
      }
    );
  });

  // ── Act headers pin + fade ─────────────────────────────────
  gsap.utils.toArray('.act-header').forEach(function (header) {
    gsap.from(header, {
      opacity: 0,
      scale: 0.95,
      scrollTrigger: {
        trigger: header,
        start: 'top 70%',
        end: 'top 30%',
        scrub: 1
      },
      ease: 'power1.out'
    });
  });

  // ── Photo scale-up on enter ────────────────────────────────
  gsap.utils.toArray('.visual-row img, .visual-portrait img, .visual-wide img, .visual-emblem img').forEach(function (img) {
    gsap.from(img, {
      scale: 0.85,
      opacity: 0.4,
      scrollTrigger: {
        trigger: img,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.7,
      ease: 'power2.out'
    });
  });

  // ── Chain summary text stagger ─────────────────────────────
  gsap.utils.toArray('.chain-link').forEach(function (link, i) {
    gsap.from(link, {
      opacity: 0,
      y: 10,
      scrollTrigger: {
        trigger: '.chain-summary',
        start: 'top 70%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.4,
      delay: i * 0.15,
      ease: 'power2.out'
    });
  });

  // ── Pattern grid rows slide in ─────────────────────────────
  gsap.utils.toArray('.pattern-row').forEach(function (row, i) {
    gsap.from(row, {
      x: -30,
      opacity: 0,
      scrollTrigger: {
        trigger: row,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.5,
      delay: i * 0.1,
      ease: 'power2.out'
    });
  });

  // ── Timeline blocks cascade ────────────────────────────────
  gsap.utils.toArray('.timeline-block').forEach(function (block, i) {
    gsap.from(block, {
      x: -20,
      opacity: 0,
      scrollTrigger: {
        trigger: block,
        start: 'top 85%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.5,
      delay: i * 0.12,
      ease: 'power2.out'
    });
  });

  // ── Incident list items cascade ────────────────────────────
  gsap.utils.toArray('.incident-list li').forEach(function (li, i) {
    gsap.from(li, {
      x: -15,
      opacity: 0,
      scrollTrigger: {
        trigger: li,
        start: 'top 90%',
        toggleActions: 'play none none reverse'
      },
      duration: 0.35,
      delay: i * 0.06,
      ease: 'power2.out'
    });
  });

})();
