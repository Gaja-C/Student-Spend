document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll("[data-message]");

    messages.forEach(msg => {
        alert(msg.dataset.message);
    });
});