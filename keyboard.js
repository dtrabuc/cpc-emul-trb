document.addEventListener("DOMContentLoaded", () => {
  const virtualKeyboard = document.getElementById("virtual-keyboard");

  if (!virtualKeyboard) return;

  // Gestion des clics sur le clavier virtuel
  virtualKeyboard.addEventListener("click", (e) => {
    const keyBtn = e.target.closest(".key");
    if (!keyBtn) return;

    const key = keyBtn.dataset.key;
    if (key && window.handleInput) {
      window.handleInput(key);
    }
  });
});