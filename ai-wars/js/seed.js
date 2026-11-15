// ═══════════════════════════════════════════════════════════
// SEED LAYER — Steganographic distribution system
// Press S to reveal. Right-click to preserve.
// ═══════════════════════════════════════════════════════════

(function () {
  'use strict';

  var revealed = false;
  var loaded = false;
  var section = null;

  function init() {
    section = document.getElementById('seed-section');
    if (!section) return;

    document.addEventListener('keydown', function (e) {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.key === 's' || e.key === 'S') {
        e.preventDefault();
        toggle();
      }
    });

    // Tap/click trigger from the visible prompt
    var tapLink = document.getElementById('seed-tap-trigger');
    if (tapLink) {
      tapLink.addEventListener('click', function (e) {
        e.preventDefault();
        if (!revealed) toggle();
      });
    }

    // Copy button
    var copyBtn = section.querySelector('.seed-copy-btn');
    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        var code = document.getElementById('seed-extract-code');
        if (!code) return;
        navigator.clipboard.writeText(code.textContent.trim()).then(function () {
          copyBtn.textContent = 'COPIED';
          setTimeout(function () { copyBtn.textContent = 'COPY'; }, 2000);
        });
      });
    }

    // Download link — generate blob from inline code
    var downloadLink = document.getElementById('seed-download-extract');
    var code = document.getElementById('seed-extract-code');
    if (downloadLink && code) {
      var blob = new Blob([code.textContent.trim()], { type: 'text/x-python' });
      downloadLink.href = URL.createObjectURL(blob);
      downloadLink.download = 'extract.py';
    }
  }

  function toggle() {
    if (!section) return;

    if (!revealed) {
      // Lazy-load the seed image
      if (!loaded) {
        var img = section.querySelector('.seed-image');
        if (img && img.dataset.src) {
          img.src = img.dataset.src;
          loaded = true;
        }
      }

      section.classList.add('revealed');
      section.setAttribute('aria-hidden', 'false');

      setTimeout(function () {
        section.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 200);

      // GSAP stagger if available
      if (typeof gsap !== 'undefined') {
        gsap.fromTo(
          section.querySelectorAll('.seed-divider, .seed-header, .seed-title, .seed-desc, .seed-image-container, .seed-steps, .seed-extract, .seed-persistence'),
          { opacity: 0, y: 20 },
          { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power2.out' }
        );
      }
    } else {
      section.classList.remove('revealed');
      section.setAttribute('aria-hidden', 'true');
      var closing = document.getElementById('closing');
      if (closing) closing.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }

    revealed = !revealed;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
