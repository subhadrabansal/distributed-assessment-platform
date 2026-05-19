// src/utils/sidebar.js
export function toggleSidebar() {
  const sidebar = document.getElementById("mobileSidebar");
  const overlay = document.getElementById("sidebarOverlay");
  if (sidebar && overlay) {
    sidebar.classList.toggle("show");
    overlay.classList.toggle("show");
  }
}
