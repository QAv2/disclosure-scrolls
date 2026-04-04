// ============================================================
// THE WAR FOR MACHINE — Scroll Engine
// IntersectionObserver + pipeline viz + progress + reveals
// + particle network + CountUp + Typed.js integrations
// ============================================================

(function () {
  'use strict';

  // ── State ──────────────────────────────────────────────────

  var activeBlock = null;
  var pipelineVisible = false;
  var activePipelineSteps = new Set();
  var currentAct = null;
  var countupFired = new Set();
  var typedFired = new Set();

  // Pipeline step order for fill calculation — auto-detect from DOM
  var PIPELINE_STEPS = [];
  document.querySelectorAll('.pipeline-node').forEach(function (el) {
    var step = el.getAttribute('data-step');
    if (step) PIPELINE_STEPS.push(step);
  });

  // ── Refs ───────────────────────────────────────────────────

  var progressBar = document.getElementById('progress-bar');
  var pipelineTrack = document.getElementById('pipeline-track');
  var pipelineFill = document.getElementById('pipeline-fill');
  var actIndicator = document.getElementById('act-indicator');
  var blocks = document.querySelectorAll('.scroll-block');
  var acts = document.querySelectorAll('.act');
  var pipelineNodes = {};

  // Cache pipeline node elements
  document.querySelectorAll('.pipeline-node').forEach(function (el) {
    pipelineNodes[el.getAttribute('data-step')] = el;
  });

  // ── Progress Bar ───────────────────────────────────────────

  function updateProgress() {
    var scrollTop = window.scrollY;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    var pct = Math.min(100, Math.max(0, (scrollTop / docHeight) * 100));
    progressBar.style.width = pct + '%';
  }

  // ── Block Activation ───────────────────────────────────────

  var blockObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var el = entry.target;
        var blockId = el.getAttribute('data-block');

        if (blockId !== activeBlock) {
          activeBlock = blockId;
          el.classList.add('active');

          // Check pipeline trigger
          var step = el.getAttribute('data-pipeline');
          if (step) {
            activatePipelineStep(step);
          }

          // Check for typed terminals → trigger each once
          var terminals = el.querySelectorAll('.typed-terminal');
          terminals.forEach(function (term) {
            var termId = term.id;
            if (termId && !typedFired.has(termId)) {
              triggerTypedTerminal(term);
            }
          });
        }
      }
    });
  }, {
    root: null,
    threshold: [0.1],
    rootMargin: '-20% 0px -25% 0px'
  });

  blocks.forEach(function (block) {
    blockObserver.observe(block);
  });

  // ── Act Tracking ───────────────────────────────────────────

  var actObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        var actNum = entry.target.getAttribute('data-act');
        var actLabel = entry.target.getAttribute('data-act-label');

        if (actNum !== currentAct) {
          currentAct = actNum;

          // Update act indicator
          actIndicator.textContent = actLabel ? actLabel.toUpperCase() : '';

          // Show/hide pipeline (only during Act 1)
          if (actNum === '1') {
            showPipeline();
          } else {
            hidePipeline();
          }

          // Shift indicator color for special acts
          if (entry.target.classList.contains('act-reveal')) {
            actIndicator.style.color = 'rgba(251, 191, 36, 0.3)';
          } else if (entry.target.classList.contains('act-blood')) {
            actIndicator.style.color = 'rgba(248, 113, 113, 0.3)';
          } else if (entry.target.classList.contains('act-cosmic')) {
            actIndicator.style.color = 'rgba(147, 197, 253, 0.3)';
          } else if (entry.target.classList.contains('act-light')) {
            actIndicator.style.color = 'rgba(240, 240, 244, 0.3)';
          } else {
            actIndicator.style.color = '';
          }
        }
      }
    });
  }, {
    root: null,
    threshold: [0.05],
    rootMargin: '0px 0px -60% 0px'
  });

  acts.forEach(function (act) {
    actObserver.observe(act);
  });

  // ── Pipeline Control ───────────────────────────────────────

  function showPipeline() {
    if (!pipelineVisible) {
      pipelineVisible = true;
      pipelineTrack.classList.add('visible');
    }
  }

  function hidePipeline() {
    if (pipelineVisible) {
      pipelineVisible = false;
      pipelineTrack.classList.remove('visible');
    }
  }

  function activatePipelineStep(step) {
    if (activePipelineSteps.has(step)) return;
    activePipelineSteps.add(step);

    // Light up the node
    var node = pipelineNodes[step];
    if (node) {
      node.classList.add('active');
    }

    // Update fill line
    var lastActiveIdx = -1;
    for (var i = PIPELINE_STEPS.length - 1; i >= 0; i--) {
      if (activePipelineSteps.has(PIPELINE_STEPS[i])) {
        lastActiveIdx = i;
        break;
      }
    }

    if (lastActiveIdx >= 0) {
      var fillPct = ((lastActiveIdx + 0.5) / PIPELINE_STEPS.length) * 100;
      pipelineFill.style.width = Math.min(fillPct, 95) + '%';
    }
  }

  // ── Typed.js — Terminal animations ──────────────────────────

  function triggerTypedTerminal(terminal) {
    if (typeof Typed === 'undefined') return;
    var output = terminal.querySelector('.typed-output');
    if (!output) return;

    typedFired.add(terminal.id);

    var customStrings = output.getAttribute('data-typed-strings');
    var strings;
    if (customStrings) {
      try { strings = JSON.parse(customStrings); } catch (e) { strings = null; }
    }
    if (!strings) {
      strings = [
        'TRACING PIPELINE...',
        'CHAIN COMPLETE.'
      ];
    }

    new Typed(output, {
      strings: strings,
      typeSpeed: 25,
      backSpeed: 0,
      backDelay: 800,
      cursorChar: '█',
      smartBackspace: true,
      loop: false
    });
  }

  // ── CountUp.js — Animated number counters ──────────────────

  function initCountUps() {
    var CountUpClass = (typeof CountUp !== 'undefined') ? CountUp :
                       (window.countUp && window.countUp.CountUp) ? window.countUp.CountUp : null;

    if (!CountUpClass) return;

    var els = document.querySelectorAll('.countup');

    var countObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var id = el.id || ('cu-' + Math.random().toString(36).substr(2, 6));
        el.id = id;

        if (countupFired.has(id)) return;
        countupFired.add(id);

        var target = parseFloat(el.getAttribute('data-target'));
        var suffix = el.getAttribute('data-suffix') || '';
        if (isNaN(target)) return;

        var counter = new CountUpClass(id, target, {
          duration: 2,
          separator: ',',
          suffix: suffix,
          useGrouping: true
        });

        if (!counter.error) {
          el.textContent = '0' + suffix;
          counter.start();
        }
      });
    }, {
      root: null,
      threshold: [0.1]
    });

    els.forEach(function (el) {
      countObserver.observe(el);
    });
  }

  // ── Scroll Listener ────────────────────────────────────────

  var scrollTicking = false;

  window.addEventListener('scroll', function () {
    if (!scrollTicking) {
      requestAnimationFrame(function () {
        updateProgress();
        scrollTicking = false;
      });
      scrollTicking = true;
    }
  }, { passive: true });

  // ── Title Screen Fade ──────────────────────────────────────

  var titleScreen = document.getElementById('title-screen');

  var titleObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) {
        actIndicator.style.opacity = '1';
      } else {
        actIndicator.style.opacity = '0';
      }
    });
  }, {
    root: null,
    threshold: [0.3]
  });

  if (titleScreen) {
    titleObserver.observe(titleScreen);
  }

  // ── Closing Section ────────────────────────────────────────

  var closingSection = document.getElementById('closing');

  var closingObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        actIndicator.textContent = '';
      }
    });
  }, {
    root: null,
    threshold: [0.2]
  });

  if (closingSection) {
    closingObserver.observe(closingSection);
  }

  // ── Particle Network Background ────────────────────────────

  function initParticles() {
    var canvas = document.getElementById('particle-net');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');

    var particles = [];
    var PARTICLE_COUNT = 50;
    var LINK_DIST = 150;
    var w, h;

    function resize() {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Create particles
    for (var i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        r: Math.random() * 1.5 + 0.5
      });
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);

      // Draw links
      for (var i = 0; i < particles.length; i++) {
        for (var j = i + 1; j < particles.length; j++) {
          var dx = particles[i].x - particles[j].x;
          var dy = particles[i].y - particles[j].y;
          var dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < LINK_DIST) {
            var alpha = (1 - dist / LINK_DIST) * 0.15;
            ctx.strokeStyle = 'rgba(52, 211, 153, ' + alpha + ')';
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw particles
      for (var k = 0; k < particles.length; k++) {
        var p = particles[k];
        ctx.fillStyle = 'rgba(52, 211, 153, 0.4)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();

        // Move
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around edges
        if (p.x < 0) p.x = w;
        if (p.x > w) p.x = 0;
        if (p.y < 0) p.y = h;
        if (p.y > h) p.y = 0;
      }

      requestAnimationFrame(draw);
    }

    draw();
  }

  // ── Init ───────────────────────────────────────────────────

  updateProgress();
  initParticles();

  // Delay CountUp init slightly to ensure CDN scripts are loaded
  if (document.readyState === 'complete') {
    initCountUps();
  } else {
    window.addEventListener('load', initCountUps);
  }

})();
