document.addEventListener("DOMContentLoaded", function () {
  function updateCountdowns() {
    const elements = document.querySelectorAll("[data-expires]");
    const now = new Date().getTime();

    elements.forEach(function (el) {
      const expiryAttr = el.getAttribute("data-expires");
      if (!expiryAttr) return;

      const expiryDate = new Date(expiryAttr).getTime();
      const distance = expiryDate - now;

      if (distance <= 0) {
        el.textContent = "Expired";
        el.classList.add("text-danger");
        return;
      }

      const days = Math.floor(distance / (1000 * 60 * 60 * 24));
      const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((distance % (1000 * 60)) / 1000);

      let text = "";
      if (days > 0) {
        text = `${days}d ${hours}h left`;
      } else if (hours > 0) {
        text = `${hours}h ${minutes}m left`;
      } else if (minutes > 0) {
        text = `${minutes}m ${seconds}s left`;
      } else {
        text = `${seconds}s left`;
      }

      el.textContent = text;
    });
  }

  updateCountdowns();
  setInterval(updateCountdowns, 1000);
});
