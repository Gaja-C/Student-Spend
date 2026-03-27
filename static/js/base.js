document.addEventListener("DOMContentLoaded", function () {
    const messages = document.querySelectorAll("[message]");

    messages.forEach(msg => {
        alert(msg.dataset.message);
    });
});