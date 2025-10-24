// ========================================
// PROBLEMSCOPE - FIXED JAVASCRIPT
// No conflicting animations
// ========================================

document.addEventListener("DOMContentLoaded", function () {
  // ========================================
  // 1. SMOOTH SCROLLING
  // ========================================
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // ========================================
  // 2. AUTO-HIDE ALERTS AFTER 5 SECONDS
  // ========================================
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // ========================================
  // 3. ADD LOADING ANIMATION ON FORM SUBMIT
  // ========================================
  const forms = document.querySelectorAll("form");
  forms.forEach((form) => {
    form.addEventListener("submit", function (e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML =
          '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';

        // Re-enable after 3 seconds in case of validation errors
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 3000);
      }
    });
  });

  // ========================================
  // 4. SEARCH FILTER LIVE PREVIEW
  // ========================================
  const searchInput = document.querySelector('input[name="search"]');
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const value = this.value.toLowerCase();
      if (value.length > 2) {
        this.style.borderColor = "#27ae60";
        this.style.boxShadow = "0 0 0 0.2rem rgba(39, 174, 96, 0.15)";
      } else {
        this.style.borderColor = "#dfe6e9";
        this.style.boxShadow = "none";
      }
    });
  }

  // ========================================
  // 5. CONFIRM BEFORE MARKING AS SOLVED
  // ========================================
  const solvedButtons = document.querySelectorAll(
    'form[action*="Solved"] button'
  );
  solvedButtons.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      if (
        !confirm(
          "Are you sure you want to mark this problem as SOLVED? This action shows the problem has been resolved."
        )
      ) {
        e.preventDefault();
      } else {
        // Show confetti on solve
        createConfettiEffect();
      }
    });
  });

  // ========================================
  // 6. IMAGE PREVIEW ON UPLOAD
  // ========================================
  const imageInput = document.querySelector('input[type="file"][name="image"]');
  if (imageInput) {
    imageInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          // Create preview
          let preview = document.querySelector(".image-preview");
          if (!preview) {
            preview = document.createElement("div");
            preview.className = "image-preview mt-3";
            imageInput.parentElement.appendChild(preview);
          }
          preview.innerHTML = `
                        <p class="text-success"><i class="fas fa-check-circle"></i> Image selected</p>
                        <img src="${event.target.result}" class="img-fluid rounded shadow" style="max-height: 200px;">
                    `;
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Profile picture preview
  const profilePicInput = document.querySelector(
    'input[type="file"][name="profile_picture"]'
  );
  if (profilePicInput) {
    profilePicInput.addEventListener("change", function (e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
          const img = document.querySelector("img.rounded-circle");
          if (img) {
            img.src = event.target.result;
          }
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // ========================================
  // 7. SCROLL TO TOP BUTTON
  // ========================================
  const scrollTopBtn = document.createElement("button");
  scrollTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
  scrollTopBtn.className = "btn btn-primary scroll-top-btn";
  scrollTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: none;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
  document.body.appendChild(scrollTopBtn);

  window.addEventListener("scroll", () => {
    if (window.pageYOffset > 300) {
      scrollTopBtn.style.display = "block";
    } else {
      scrollTopBtn.style.display = "none";
    }
  });

  scrollTopBtn.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });

  // ========================================
  // 8. REAL-TIME CHARACTER COUNT FOR TEXTAREAS
  // ========================================
  const textareas = document.querySelectorAll("textarea");
  textareas.forEach((textarea) => {
    const maxLength = textarea.getAttribute("maxlength") || 1000;
    const counter = document.createElement("small");
    counter.className = "text-muted form-text d-block mt-1";
    counter.textContent = `0 / ${maxLength} characters`;
    textarea.parentElement.appendChild(counter);

    textarea.addEventListener("input", function () {
      const length = this.value.length;
      counter.textContent = `${length} / ${maxLength} characters`;
      if (length > maxLength * 0.9) {
        counter.classList.add("text-danger");
        counter.classList.remove("text-muted");
      } else {
        counter.classList.add("text-muted");
        counter.classList.remove("text-danger");
      }
    });
  });

  // ========================================
  // 9. CONFETTI ANIMATION ON SOLVED
  // ========================================
  if (
    window.location.search.includes("solved=true") ||
    window.location.hash === "#solved"
  ) {
    createConfettiEffect();
  }

  function createConfettiEffect() {
    for (let i = 0; i < 50; i++) {
      setTimeout(() => createConfetti(), i * 30);
    }
  }

  function createConfetti() {
    const confetti = document.createElement("div");
    const colors = ["#3498db", "#27ae60", "#f39c12", "#e74c3c", "#9b59b6"];
    confetti.style.cssText = `
            position: fixed;
            width: 10px;
            height: 10px;
            background: ${colors[Math.floor(Math.random() * colors.length)]};
            top: -10px;
            left: ${Math.random() * 100}vw;
            opacity: ${Math.random()};
            transform: rotate(${Math.random() * 360}deg);
            animation: confetti-fall ${2 + Math.random() * 3}s linear;
            z-index: 9999;
            pointer-events: none;
        `;
    document.body.appendChild(confetti);
    setTimeout(() => confetti.remove(), 5000);
  }

  // Add confetti animation
  if (!document.getElementById("confetti-style")) {
    const style = document.createElement("style");
    style.id = "confetti-style";
    style.textContent = `
            @keyframes confetti-fall {
                to {
                    transform: translateY(100vh) rotate(720deg);
                    opacity: 0;
                }
            }
        `;
    document.head.appendChild(style);
  }

  // ========================================
  // 10. ACTIVE NAV LINK HIGHLIGHTING
  // ========================================
  const currentPath = window.location.pathname;
  const navLinks = document.querySelectorAll(".nav-link");

  navLinks.forEach((link) => {
    const linkPath = new URL(link.href).pathname;
    if (linkPath === currentPath) {
      link.classList.add("active");
    }
  });

  // ========================================
  // 11. BOOTSTRAP TOOLTIPS INITIALIZATION
  // ========================================
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // ========================================
  // 12. PREVENT DOUBLE FORM SUBMISSION
  // ========================================
  let formSubmitted = false;
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function (e) {
      if (formSubmitted) {
        e.preventDefault();
        return false;
      }
      formSubmitted = true;
      setTimeout(() => {
        formSubmitted = false;
      }, 3000);
    });
  });

  // ========================================
  // 13. AUTO-DISMISS MESSAGES
  // ========================================
  const dismissButtons = document.querySelectorAll('[data-bs-dismiss="alert"]');
  dismissButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const alert = this.closest(".alert");
      if (alert) {
        alert.style.transition = "opacity 0.3s";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 300);
      }
    });
  });

  // ========================================
  // 14. FORM VALIDATION FEEDBACK
  // ========================================
  const formInputs = document.querySelectorAll(".form-control, .form-select");
  formInputs.forEach((input) => {
    input.addEventListener("blur", function () {
      if (this.value.trim() !== "") {
        this.classList.add("is-valid");
        this.classList.remove("is-invalid");
      }
    });
  });

  console.log("✅ ProblemScope JavaScript loaded successfully!");
});

// ========================================
// PREVENT BLANK PAGE FLASH
// ========================================
window.addEventListener("load", function () {
  document.body.style.opacity = "1";
});
