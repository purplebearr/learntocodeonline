document.addEventListener("DOMContentLoaded", function () {
  // Dropdown menu toggling
  const dropdownMenu = document.querySelector(".dropdown-menu");
  const dropdownButton = document.querySelector(".dropdown-button");

  if (dropdownButton) {
    dropdownButton.addEventListener("click", function () {
      dropdownMenu.classList.toggle("show");
    });
  }

  // Upload Image Preview
  const photoInput = document.querySelector("#avatar");
  const photoPreview = document.querySelector("#preview-avatar");

  if (photoInput) {
    photoInput.addEventListener("change", function () {
      const [file] = photoInput.files;
      if (file) {
        photoPreview.src = URL.createObjectURL(file);
      }
    });
  }

  // Scroll to Bottom (If required, based on your application)
  const conversationThread = document.querySelector(".room__box");
  if (conversationThread) {
    conversationThread.scrollTop = conversationThread.scrollHeight;
  }
});
