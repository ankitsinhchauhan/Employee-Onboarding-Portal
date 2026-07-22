document.addEventListener("DOMContentLoaded", () => {
  "use strict";

  function initPasswordToggle() {
    document.querySelectorAll("[data-toggle-password]").forEach((button) => {
      button.addEventListener("click", () => {
        const targetSelector = button.getAttribute("data-target");
        const input = targetSelector
          ? document.querySelector(targetSelector)
          : null;
        if (!input) return;

        const icon = button.querySelector("i");
        const isHidden = input.type === "password";

        input.type = isHidden ? "text" : "password";
        if (icon) icon.className = isHidden ? "bi bi-eye-slash" : "bi bi-eye";
      });
    });
  }

  function initPasswordStrength() {
    const passwordInput = document.querySelector(
      "[data-password-field], #password",
    );
    const strengthBar = document.getElementById("strengthBar");
    const strengthText = document.getElementById("strengthText");
    if (!passwordInput || !strengthBar || !strengthText) return;

    const updateStrength = () => {
      const value = passwordInput.value;
      let score = 0;

      if (value.length >= 8) score += 25;
      if (/[A-Z]/.test(value)) score += 25;
      if (/[0-9]/.test(value)) score += 25;
      if (/[^A-Za-z0-9]/.test(value)) score += 25;

      strengthBar.style.width = `${score}%`;

      if (!value) {
        strengthText.textContent = "Not set";
        strengthBar.style.backgroundColor = "#EF4444";
      } else if (score <= 25) {
        strengthText.textContent = "Weak";
        strengthBar.style.backgroundColor = "#EF4444";
      } else if (score <= 50) {
        strengthText.textContent = "Fair";
        strengthBar.style.backgroundColor = "#F59E0B";
      } else if (score <= 75) {
        strengthText.textContent = "Good";
        strengthBar.style.backgroundColor = "#22C55E";
      } else {
        strengthText.textContent = "Strong";
        strengthBar.style.backgroundColor = "#16A34A";
      }
    };

    passwordInput.addEventListener("input", updateStrength);
    updateStrength();
  }

  function initFormValidation() {
    document.querySelectorAll(".needs-validation").forEach((form) => {
      const confirmPassword = form.querySelector("[data-confirm-password]");

      const validateConfirmPassword = () => {
        if (!confirmPassword) return;

        const primarySelector = confirmPassword.getAttribute(
          "data-confirm-password",
        );
        const primary = primarySelector
          ? document.querySelector(primarySelector)
          : null;
        if (!primary) return;

        if (confirmPassword.value && confirmPassword.value !== primary.value) {
          confirmPassword.setCustomValidity("Passwords do not match");
        } else {
          confirmPassword.setCustomValidity("");
        }
      };

      if (confirmPassword) {
        const primarySelector = confirmPassword.getAttribute(
          "data-confirm-password",
        );
        const primary = primarySelector
          ? document.querySelector(primarySelector)
          : null;

        if (primary) {
          primary.addEventListener("input", validateConfirmPassword);
        }
        confirmPassword.addEventListener("input", validateConfirmPassword);
      }

      form.addEventListener(
        "submit",
        (event) => {
          if (confirmPassword) validateConfirmPassword();

          if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
          }

          form.classList.add("was-validated");
        },
        false,
      );
    });
  }

  function initLoadingButtons() {
    document.querySelectorAll(".needs-validation").forEach((form) => {
      const button = form.querySelector('button[type="submit"]');
      if (!button) return;

      form.addEventListener("submit", (event) => {
        if (!form.checkValidity() || button.disabled) return;

        button.classList.add("loading-state");
        button.disabled = true;
      });
    });
  }

  function initSmoothPageAnimation() {
    document.body.classList.add("fade-up");
  }

  initPasswordToggle();
  initPasswordStrength();
  initFormValidation();
  initLoadingButtons();
  initSmoothPageAnimation();
});
