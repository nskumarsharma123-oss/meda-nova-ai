/**
 * MedNova AI - Client Scripts
 * Provides responsive navigation, loading state triggers, and client UX helpers.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Menu Toggle
  const mobileBtn = document.getElementById("mobileMenuBtn");
  const navMenu = document.getElementById("navMenu");

  if (mobileBtn && navMenu) {
    mobileBtn.addEventListener("click", function () {
      navMenu.classList.toggle("active");
    });
  }

  // 2. Patient Analysis Form Loading State & Submission Lock
  const analysisForm = document.getElementById("analysisForm");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const submitBtn = document.getElementById("submitBtn");

  if (analysisForm && loadingOverlay && submitBtn) {
    analysisForm.addEventListener("submit", function (e) {
      // Basic check if form is valid before showing spinner
      const ageInput = document.getElementById("age");
      const symptomsInput = document.getElementById("symptoms");
      const consentInput = document.getElementById("consent");

      if (consentInput && !consentInput.checked) {
        // Let normal browser/server validation fire
        return;
      }

      if (ageInput && (!ageInput.value || ageInput.value < 0 || ageInput.value > 120)) {
        return;
      }

      if (symptomsInput && symptomsInput.value.trim().length < 5) {
        return;
      }

      // Show spinner and disable button to avoid duplicate submissions
      loadingOverlay.classList.add("active");
      submitBtn.disabled = true;
      submitBtn.value = "Analyzing Case with MedNova AI...";
    });
  }

  // 3. Auto-scroll on hash or smooth UX for alerts
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    alert.setAttribute("role", "alert");
  });
});
