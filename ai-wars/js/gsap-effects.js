// ============================================================
// GSAP ScrollTrigger Effects — Full Coverage
// Layered on top of existing IntersectionObserver engine
// ============================================================

(function () {
  'use strict';

  if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);

  // Helper: standard reveal trigger config
  function revealTrigger(el, start) {
    return {
      trigger: el,
      start: start || 'top 85%',
      toggleActions: 'play none none reverse'
    };
  }

  // ── Title screen elements stagger ──────────────────────────
  gsap.from('.title-label', { opacity: 0, y: 30, duration: 1, delay: 0.3 });
  gsap.from('.title-main', { opacity: 0, y: 40, duration: 1, delay: 0.6 });
  gsap.from('.title-sub', { opacity: 0, y: 30, duration: 1, delay: 0.9 });
  gsap.from('.title-meta', { opacity: 0, y: 20, duration: 0.8, delay: 1.2 });
  gsap.from('.scroll-cue', { opacity: 0, duration: 0.8, delay: 1.6 });

  // ── Act headers — scale + fade with scrub ──────────────────
  gsap.utils.toArray('.act-header').forEach(function (header) {
    gsap.from(header, {
      opacity: 0,
      scale: 0.93,
      scrollTrigger: {
        trigger: header,
        start: 'top 75%',
        end: 'top 35%',
        scrub: 1
      }
    });
  });

  // ── Node titles (sub-headings) — slide from left ───────────
  gsap.utils.toArray('.node-title').forEach(function (title) {
    gsap.from(title, {
      x: -40,
      opacity: 0,
      duration: 0.6,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(title)
    });
  });

  // ── Evidence cards — curtain wipe from left ────────────────
  gsap.utils.toArray('.evidence-card').forEach(function (card) {
    gsap.from(card, {
      clipPath: 'inset(0 100% 0 0)',
      duration: 0.8,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(card)
    });
  });

  // ── Pull quotes — parallax float ───────────────────────────
  gsap.utils.toArray('.pull-quote').forEach(function (pq) {
    gsap.fromTo(pq,
      { y: 25 },
      {
        y: -25,
        ease: 'none',
        scrollTrigger: {
          trigger: pq,
          start: 'top bottom',
          end: 'bottom top',
          scrub: 1.2
        }
      }
    );
  });

  // ── ALL photos — scale up + fade on enter ──────────────────
  gsap.utils.toArray('.visual-row img, .visual-portrait img, .visual-wide img, .visual-emblem img').forEach(function (img) {
    gsap.from(img, {
      scale: 0.82,
      opacity: 0.3,
      duration: 0.7,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(img)
    });
  });

  // ── Visual captions — fade in after image ──────────────────
  gsap.utils.toArray('.visual-caption, .vr-name, .vr-role').forEach(function (cap) {
    gsap.from(cap, {
      opacity: 0,
      y: 8,
      duration: 0.5,
      delay: 0.2,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(cap, 'top 90%')
    });
  });

  // ── Company badges — pop in ────────────────────────────────
  gsap.utils.toArray('.company-badge').forEach(function (badge) {
    gsap.from(badge, {
      scale: 0.7,
      opacity: 0,
      duration: 0.4,
      ease: 'back.out(2)',
      scrollTrigger: revealTrigger(badge, 'top 80%')
    });
  });

  // ── Chain summaries — stagger links + arrows per chain ──────
  gsap.utils.toArray('.chain-summary').forEach(function (summary) {
    var links = summary.querySelectorAll('.chain-link');
    var arrows = summary.querySelectorAll('.chain-arrow');
    var trigger = {
      trigger: summary,
      start: 'top 70%',
      toggleActions: 'play none none reverse'
    };

    links.forEach(function (link, i) {
      gsap.from(link, {
        opacity: 0,
        y: 12,
        duration: 0.4,
        delay: i * 0.15,
        ease: 'power2.out',
        scrollTrigger: trigger
      });
    });

    arrows.forEach(function (arrow, i) {
      gsap.from(arrow, {
        opacity: 0,
        x: -5,
        duration: 0.3,
        delay: i * 0.15 + 0.1,
        ease: 'power2.out',
        scrollTrigger: trigger
      });
    });
  });

  // ── Pattern grid rows — slide in from left with stagger (per grid) ──
  gsap.utils.toArray('.pattern-grid').forEach(function (grid) {
    var rows = grid.querySelectorAll('.pattern-row');
    rows.forEach(function (row, i) {
      gsap.from(row, {
        x: -35,
        opacity: 0,
        duration: 0.5,
        delay: i * 0.12,
        ease: 'power2.out',
        scrollTrigger: revealTrigger(row)
      });
    });
  });

  // ── Timeline blocks — cascade in ──────────────────────────
  gsap.utils.toArray('.timeline-block').forEach(function (block, i) {
    gsap.from(block, {
      x: -25,
      opacity: 0,
      duration: 0.5,
      delay: i * 0.15,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(block)
    });
  });

  // ── Incident list items — stagger cascade ──────────────────
  gsap.utils.toArray('.incident-list li').forEach(function (li, i) {
    gsap.from(li, {
      x: -20,
      opacity: 0,
      duration: 0.35,
      delay: i * 0.07,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(li, 'top 90%')
    });
  });

  // ── Typed terminal box — scale in ──────────────────────────
  gsap.utils.toArray('.typed-terminal').forEach(function (term) {
    gsap.from(term, {
      scaleY: 0,
      transformOrigin: 'top',
      opacity: 0,
      duration: 0.5,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(term, 'top 80%')
    });
  });

  // ── Animated elements — fade/scale in ──────────────────────
  gsap.utils.toArray('.anim-sweep, .anim-network, .anim-eye, .anim-you-dot').forEach(function (el) {
    gsap.from(el, {
      scale: 0.6,
      opacity: 0,
      duration: 0.8,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(el, 'top 80%')
    });
  });

  // ── Static bars — glitch in ────────────────────────────────
  gsap.utils.toArray('.anim-static').forEach(function (bar) {
    gsap.from(bar, {
      scaleX: 0,
      transformOrigin: 'left',
      duration: 0.4,
      ease: 'power3.out',
      scrollTrigger: revealTrigger(bar, 'top 90%')
    });
  });

  // ── Closing section — stagger everything ───────────────────
  gsap.from('.closing-statement', {
    opacity: 0, y: 30, duration: 0.8,
    scrollTrigger: revealTrigger('.closing-statement', 'top 80%')
  });
  gsap.from('.closing-sub', {
    opacity: 0, y: 20, duration: 0.7, delay: 0.2,
    scrollTrigger: revealTrigger('.closing-sub', 'top 85%')
  });
  gsap.utils.toArray('.closing-legend-item').forEach(function (item, i) {
    gsap.from(item, {
      x: -20, opacity: 0, duration: 0.4, delay: i * 0.1,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(item, 'top 90%')
    });
  });
  gsap.from('.closing-cta', {
    opacity: 0, y: 15, duration: 0.6,
    scrollTrigger: revealTrigger('.closing-cta', 'top 85%')
  });
  gsap.utils.toArray('.closing-link').forEach(function (link, i) {
    gsap.from(link, {
      y: 20, opacity: 0, duration: 0.5, delay: i * 0.15,
      ease: 'power2.out',
      scrollTrigger: revealTrigger(link, 'top 90%')
    });
  });

  // ── Reveal climax — special treatment ──────────────────────
  // The big "The war for machine is a war for mind" line
  var climax = document.querySelector('.reveal-climax .pq-text');
  if (climax) {
    gsap.from(climax, {
      scale: 0.85,
      opacity: 0,
      duration: 1.2,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: climax,
        start: 'top 75%',
        toggleActions: 'play none none reverse'
      }
    });
  }

})();
