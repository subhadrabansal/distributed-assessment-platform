function toggleSidebar() {
      const sidebar = document.getElementById("mobileSidebar");
      const overlay = document.getElementById("sidebarOverlay");
      sidebar.classList.toggle("show");
      overlay.classList.toggle("show");
    }


// Flash message display logic
// document.addEventListener("DOMContentLoaded", () => {
//   const flash = document.getElementById("flash");
//   if (flash) {
//     flash.classList.remove("d-none");
//     setTimeout(() => {
//       flash.classList.add("d-none");
//     }, 10000);
//   }
// });
