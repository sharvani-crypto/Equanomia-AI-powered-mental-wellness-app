/**
 * Equanomia – Main JavaScript File
 * Handles animations, interactions, and UI logic
 */
 
/* ──────────────────────────────────────────────
   DOCUMENT READY
────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", function () {
  initAnimations();
  initScrollEffects();
  setCurrentDate();
  initSmoothScroll();
  initPageTransitions();
});
 
/* ──────────────────────────────────────────────
   PAGE TRANSITIONS
────────────────────────────────────────────── */
function initPageTransitions() {
  // Fade in on load
  document.body.style.opacity = "0";
  document.body.style.transition = "opacity 0.4s ease";
  setTimeout(() => {
    document.body.style.opacity = "1";
  }, 50);
 
  // Fade out on navigation
  document.querySelectorAll("a[href]").forEach((link) => {
    if (
      link.href &&
      link.href.startsWith(window.location.origin) &&
      !link.href.includes("#") &&
      !link.hasAttribute("data-no-transition") &&
      !link.href.startsWith("tel:") &&
      !link.href.startsWith("sms:")
    ) {
      link.addEventListener("click", function (e) {
        const href = this.href;
        e.preventDefault();
        document.body.style.opacity = "0";
        setTimeout(() => {
          window.location.href = href;
        }, 300);
      });
    }
  });
}
 
/* ──────────────────────────────────────────────
   ANIMATIONS
────────────────────────────────────────────── */
function initAnimations() {
  // Staggered children animation
  document.querySelectorAll(".stagger-children").forEach((parent) => {
    Array.from(parent.children).forEach((child, i) => {
      child.style.animationDelay = i * 0.1 + "s";
      child.style.animationFillMode = "both";
      child.classList.add("animate-slide-up");
    });
  });
}
 
/* ──────────────────────────────────────────────
   SCROLL EFFECTS
────────────────────────────────────────────── */
function initScrollEffects() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1, rootMargin: "0px 0px -40px 0px" }
  );
 
  document.querySelectorAll(".animate-on-scroll").forEach((el) => {
    observer.observe(el);
  });
 
  // Parallax for blobs on landing page
  if (document.querySelector(".bg-blobs")) {
    window.addEventListener("scroll", function () {
      const scrollY = window.scrollY;
      const blobs = document.querySelectorAll(".blob");
      blobs.forEach((blob, i) => {
        const speed = 0.1 + i * 0.05;
        blob.style.transform = `translateY(${scrollY * speed}px)`;
      });
    });
  }
}
 
/* ──────────────────────────────────────────────
   SMOOTH SCROLL
────────────────────────────────────────────── */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
}
 
/* ──────────────────────────────────────────────
   DATE HELPERS
────────────────────────────────────────────── */
function setCurrentDate() {
  const dateEls = document.querySelectorAll(
    "#topbarDate, #todayDate, #currentDate"
  );
  const now = new Date();
  const formatted = now.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
  dateEls.forEach((el) => {
    if (el) el.textContent = formatted;
  });
}
 
/* ──────────────────────────────────────────────
   SIDEBAR TOGGLE
────────────────────────────────────────────── */
function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const mainContent = document.getElementById("mainContent");
  if (sidebar) {
    sidebar.classList.toggle("open");
  }
  if (mainContent) {
    mainContent.classList.toggle("sidebar-open");
  }
}
 
/* ──────────────────────────────────────────────
   COUNTER ANIMATIONS
────────────────────────────────────────────── */
function animateCounter(el, target, duration = 1500) {
  let start = 0;
  const increment = target / (duration / 16);
  const timer = setInterval(() => {
    start += increment;
    if (start >= target) {
      start = target;
      clearInterval(timer);
    }
    el.textContent = Math.floor(start).toLocaleString();
  }, 16);
}
 
// Auto-run counters when visible
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting && entry.target.dataset.target) {
      animateCounter(
        entry.target,
        parseInt(entry.target.dataset.target),
        1500
      );
      counterObserver.unobserve(entry.target);
    }
  });
});
document.querySelectorAll("[data-target]").forEach((el) => {
  counterObserver.observe(el);
});
 
/* ──────────────────────────────────────────────
   TOAST NOTIFICATIONS
────────────────────────────────────────────── */
function showToastMessage(message, icon = "✨", duration = 3000) {
  // Create dynamic toast
  const toast = document.createElement("div");
  toast.className = "toast-notification";
  toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <div class="toast-content">
      <strong>${message}</strong>
    </div>
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add("visible"), 10);
  setTimeout(() => {
    toast.classList.remove("visible");
    setTimeout(() => toast.remove(), 400);
  }, duration);
}
 
/* ──────────────────────────────────────────────
   ACHIEVEMENT POPUP
────────────────────────────────────────────── */
function showAchievementPopup(icon, title, description) {
  const popup = document.getElementById("achievementToast");
  if (!popup) return;
  document.getElementById("achIcon").textContent = icon;
  document.getElementById("achTitle").textContent = title;
  document.getElementById("achDesc").textContent = description;
  popup.classList.add("visible");
  setTimeout(() => popup.classList.remove("visible"), 4500);
}
 
/* ──────────────────────────────────────────────
   FORM VALIDATION HELPERS
────────────────────────────────────────────── */
function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
 
function validatePassword(password) {
  return password.length >= 6;
}
 
function showFieldError(fieldId, message) {
  const field = document.getElementById(fieldId);
  if (!field) return;
  field.style.borderColor = "#FF6B6B";
  let errorEl = field.nextElementSibling;
  if (!errorEl || !errorEl.classList.contains("field-error")) {
    errorEl = document.createElement("span");
    errorEl.className = "field-error";
    errorEl.style.cssText =
      "color:#FF6B6B;font-size:0.78rem;margin-top:4px;display:block;";
    field.parentNode.insertBefore(errorEl, field.nextSibling);
  }
  errorEl.textContent = message;
}
 
function clearFieldError(fieldId) {
  const field = document.getElementById(fieldId);
  if (!field) return;
  field.style.borderColor = "";
  const errorEl = field.nextElementSibling;
  if (errorEl && errorEl.classList.contains("field-error")) {
    errorEl.remove();
  }
}
 
/* ──────────────────────────────────────────────
   RIPPLE EFFECT FOR BUTTONS
────────────────────────────────────────────── */
document.querySelectorAll(".btn-primary, .btn-primary-full, .btn-primary-lg").forEach((btn) => {
  btn.addEventListener("click", function (e) {
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const ripple = document.createElement("span");
    ripple.style.cssText = `
      position:absolute;left:${x}px;top:${y}px;
      width:0;height:0;border-radius:50%;
      background:rgba(255,255,255,0.4);
      transform:translate(-50%,-50%);
      animation:ripple 0.6s ease-out forwards;
      pointer-events:none;
    `;
    if (!btn.style.position || btn.style.position === "static") {
      btn.style.position = "relative";
    }
    btn.style.overflow = "hidden";
    btn.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
});
 
// Add ripple keyframe dynamically
const rippleStyle = document.createElement("style");
rippleStyle.textContent = `
  @keyframes ripple {
    to { width: 200px; height: 200px; opacity: 0; }
  }
`;
document.head.appendChild(rippleStyle);
 
/* ──────────────────────────────────────────────
   WELLNESS SLIDER GRADIENT UPDATE
────────────────────────────────────────────── */
document.querySelectorAll(".wellness-slider").forEach((slider) => {
  function updateSliderFill() {
    const value = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
    slider.style.setProperty("--fill-percent", value + "%");
  }
  slider.addEventListener("input", updateSliderFill);
  updateSliderFill();
});
 
/* ──────────────────────────────────────────────
   MOOD CARD HOVER GLOW
────────────────────────────────────────────── */
document.querySelectorAll(".meditation-card, .feature-card").forEach((card) => {
  card.addEventListener("mousemove", function (e) {
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    card.style.background = `radial-gradient(circle at ${x}% ${y}%, rgba(255,255,255,0.9), rgba(255,255,255,0.65))`;
  });
  card.addEventListener("mouseleave", function () {
    card.style.background = "";
  });
});
 
/* ──────────────────────────────────────────────
   PROGRESS BAR ANIMATIONS
────────────────────────────────────────────── */
function animateProgressBar(barEl, targetWidth, duration = 1000) {
  barEl.style.width = "0%";
  barEl.style.transition = `width ${duration}ms cubic-bezier(0.4,0,0.2,1)`;
  setTimeout(() => {
    barEl.style.width = targetWidth;
  }, 100);
}
 
// Auto-animate progress bars when visible
const progressObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      const bar = entry.target;
      const targetWidth = bar.style.width || bar.dataset.width || "0%";
      animateProgressBar(bar, targetWidth);
      progressObserver.unobserve(bar);
    }
  });
});
document.querySelectorAll(".progress-bar-inner, .xp-bar-fill").forEach((bar) => {
  const w = bar.style.width;
  bar.dataset.width = w;
  bar.style.width = "0%";
  progressObserver.observe(bar);
});
 
/* ──────────────────────────────────────────────
   LOCAL STORAGE HELPERS
────────────────────────────────────────────── */
const Storage = {
  set(key, value) {
    try {
      localStorage.setItem("equanomia_" + key, JSON.stringify(value));
    } catch (e) {}
  },
  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem("equanomia_" + key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
      return defaultValue;
    }
  },
  remove(key) {
    try {
      localStorage.removeItem("equanomia_" + key);
    } catch (e) {}
  },
};
 
/* ──────────────────────────────────────────────
   THEME PREFERENCE
────────────────────────────────────────────── */
const savedTheme = Storage.get("theme", "light");
if (savedTheme === "dark") {
  document.body.classList.add("dark-theme");
}
 
/* ──────────────────────────────────────────────
   NOTIFICATION PERMISSION
────────────────────────────────────────────── */
function requestNotificationPermission() {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }
}
 
function sendWellnessReminder(title, body) {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification(title, {
      body: body,
      icon: "/static/images/icon.png",
    });
  }
}
 
/* ──────────────────────────────────────────────
   KEYBOARD SHORTCUTS
────────────────────────────────────────────── */
document.addEventListener("keydown", function (e) {
  // Ctrl/Cmd + K: focus chat input
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    const chatInput = document.getElementById("chatInput");
    if (chatInput) chatInput.focus();
  }
  // Escape: close modals
  if (e.key === "Escape") {
    document.querySelectorAll(".modal-overlay.active").forEach((modal) => {
      modal.classList.remove("active");
    });
  }
});
 
/* ──────────────────────────────────────────────
   LAZY LOADING IMAGES
────────────────────────────────────────────── */
if ("IntersectionObserver" in window) {
  const imgObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) {
          img.src = img.dataset.src;
          img.removeAttribute("data-src");
        }
        imgObserver.unobserve(img);
      }
    });
  });
  document.querySelectorAll("img[data-src]").forEach((img) => {
    imgObserver.observe(img);
  });
}
 
/* ──────────────────────────────────────────────
   GLASSMORPHISM TILT EFFECT
────────────────────────────────────────────── */
document.querySelectorAll(".glass-card.tilt-effect").forEach((card) => {
  card.addEventListener("mousemove", function (e) {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    const rotateX = (y / rect.height) * -10;
    const rotateY = (x / rect.width) * 10;
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(4px)`;
  });
  card.addEventListener("mouseleave", function () {
    card.style.transform = "";
  });
});
 
/* ──────────────────────────────────────────────
   EMOJI PARTICLE BURST (for completions)
────────────────────────────────────────────── */
function emojiParticleBurst(emoji = "✨", x, y) {
  const count = 8;
  for (let i = 0; i < count; i++) {
    const particle = document.createElement("div");
    particle.textContent = emoji;
    particle.style.cssText = `
      position:fixed;
      left:${x}px;top:${y}px;
      font-size:1.2rem;
      pointer-events:none;
      z-index:9999;
      animation:particleBurst 0.8s ease-out forwards;
      --dx:${(Math.random() - 0.5) * 200}px;
      --dy:${(Math.random() - 0.5) * 200}px;
      animation-delay:${Math.random() * 0.2}s;
    `;
    document.body.appendChild(particle);
    setTimeout(() => particle.remove(), 1200);
  }
}
 
const particleBurstStyle = document.createElement("style");
particleBurstStyle.textContent = `
  @keyframes particleBurst {
    0%  { transform: translate(0,0) scale(1); opacity:1; }
    100%{ transform: translate(var(--dx), var(--dy)) scale(0); opacity:0; }
  }
`;
document.head.appendChild(particleBurstStyle);
 
// Trigger bursts on btn-primary click in specific contexts
document.querySelectorAll(".btn-primary-full, .btn-primary-lg").forEach((btn) => {
  btn.addEventListener("click", function (e) {
    emojiParticleBurst("✨", e.clientX, e.clientY);
  });
});
 
/* ──────────────────────────────────────────────
   WELLNESS TIP ROTATOR
────────────────────────────────────────────── */
const wellnessTips = [
  "💙 Drink a glass of water right now.",
  "🌿 Step outside for 5 minutes of fresh air.",
  "🧘 Take 3 deep breaths before your next task.",
  "😊 Smile — even a forced smile can lift mood.",
  "📵 Put your phone face-down for 10 minutes.",
  "🙏 Think of one thing you're grateful for.",
  "🚶 Stand up and stretch for 2 minutes.",
  "🎵 Listen to a song that makes you feel good.",
  "📓 Write down one positive thing about today.",
  "💤 Try to sleep 30 minutes earlier tonight.",
];
 
function showWellnessTip() {
  const tipBanners = document.querySelectorAll(".wellness-tip-banner");
  if (tipBanners.length === 0) return;
  const tip = wellnessTips[Math.floor(Math.random() * wellnessTips.length)];
  tipBanners.forEach((banner) => {
    banner.textContent = tip;
    banner.style.opacity = "0";
    setTimeout(() => {
      banner.style.transition = "opacity 0.5s ease";
      banner.style.opacity = "1";
    }, 100);
  });
}
setInterval(showWellnessTip, 30000);
 
/* ──────────────────────────────────────────────
   SOUND AMBIENCE (Web Audio API simulation)
────────────────────────────────────────────── */
let audioContext = null;
let currentSoundNode = null;
 
function initAudio() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
}
 
function playAmbienceSound(type) {
  initAudio();
  if (currentSoundNode) {
    currentSoundNode.stop();
    currentSoundNode = null;
  }
 
  const bufferSize = 4096;
  const node = audioContext.createScriptProcessor(bufferSize, 1, 1);
 
  node.onaudioprocess = function (e) {
    const output = e.outputBuffer.getChannelData(0);
    for (let i = 0; i < bufferSize; i++) {
      if (type === "white") {
        output[i] = Math.random() * 2 - 1;
      } else if (type === "pink") {
        // Pink noise approximation
        output[i] = (Math.random() * 2 - 1) * 0.5;
      } else if (type === "brown") {
        // Brown noise
        output[i] = (Math.random() * 2 - 1) * 0.3;
      }
    }
  };
 
  const gainNode = audioContext.createGain();
  gainNode.gain.value = 0.05;
  node.connect(gainNode);
  gainNode.connect(audioContext.destination);
  currentSoundNode = node;
  return node;
}
 
function stopAmbienceSound() {
  if (currentSoundNode) {
    currentSoundNode.disconnect();
    currentSoundNode = null;
  }
}
 
/* ──────────────────────────────────────────────
   RESPONSIVE SIDEBAR CLOSE ON OUTSIDE CLICK
────────────────────────────────────────────── */
document.addEventListener("click", function (e) {
  const sidebar = document.getElementById("sidebar");
  const toggle = document.querySelector(".sidebar-toggle");
  if (
    sidebar &&
    sidebar.classList.contains("open") &&
    !sidebar.contains(e.target) &&
    toggle &&
    !toggle.contains(e.target)
  ) {
    sidebar.classList.remove("open");
  }
});
 
/* ──────────────────────────────────────────────
   CHART.JS GLOBAL DEFAULTS
────────────────────────────────────────────── */
if (typeof Chart !== "undefined") {
  Chart.defaults.font.family = "'Nunito', sans-serif";
  Chart.defaults.color = "#6B6580";
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.tooltip.backgroundColor = "rgba(255,255,255,0.95)";
  Chart.defaults.plugins.tooltip.titleColor = "#2D2A3E";
  Chart.defaults.plugins.tooltip.bodyColor = "#6B6580";
  Chart.defaults.plugins.tooltip.borderColor = "rgba(123,108,246,0.2)";
  Chart.defaults.plugins.tooltip.borderWidth = 1;
  Chart.defaults.plugins.tooltip.padding = 12;
  Chart.defaults.plugins.tooltip.cornerRadius = 12;
  Chart.defaults.plugins.tooltip.displayColors = false;
}
 
/* ──────────────────────────────────────────────
   PRINT / EXPORT HELPERS
────────────────────────────────────────────── */
function printWellnessReport() {
  window.print();
}
 
/* ──────────────────────────────────────────────
   APP VERSION & INIT LOG
────────────────────────────────────────────── */
console.log(
  "%c🌸 Equanomia v1.0 — AI Mental Wellness Platform",
  "color:#7B6CF6;font-size:14px;font-weight:bold;"
);
console.log(
  "%cYour daily emotional wellness companion.",
  "color:#6B6580;font-size:12px;"
);
