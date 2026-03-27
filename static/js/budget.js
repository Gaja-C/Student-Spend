function confirmDeleteGoal() {
    return confirm("Are you sure you want to delete this goal?\n");
}

document.addEventListener("DOMContentLoaded", function () {
    const selectGoal = document.getElementById("selectGoal");
    const progressBar = document.getElementById("progressBar");

    function updateProgress() {
        if (!selectGoal || !progressBar) return;

        const selectedOption = selectGoal.options[selectGoal.selectedIndex];
        const budget = parseFloat(selectedOption.getAttribute("budget")) || 0;
        const currentAmount = parseFloat(selectedOption.getAttribute("currentAmount")) || 0;
        const progress = budget > 0 ? (currentAmount / budget) * 100 : 0;

        progressBar.style.width = Math.min(progress, 100) + "%";
    }

    updateProgress();
    if (selectGoal) {
        selectGoal.addEventListener("change", updateProgress);
    }

    const editGoal = document.getElementById("editGoal");
    const amountInput = document.getElementById("addOrSub");

    if (editGoal) {
        editGoal.addEventListener("submit", function(e) {
            e.preventDefault();
            const selectedOption = selectGoal.options[selectGoal.selectedIndex];
            const budget = parseFloat(selectedOption.getAttribute("budget")) || 0;
            const currentAmount = parseFloat(selectedOption.getAttribute("currentAmount")) || 0;
            const addOrSub = parseFloat(amountInput.value || 0);
            const total = currentAmount + addOrSub;

            if (total >= budget && budget > 0) {
                const confirmed = confirm("You are about to meet the budget for this goal. Doing this will remove the goal. Are you sure you want to do this?\n");
                if (!confirmed) {
                    return;
                } 
            }

            const formData = new FormData(editGoal);
            fetch(editGoal.dataset.url, {
                method: "POST",
                body: formData,
                headers: {"X-Requested-With": "XMLHttpRequest"}
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {alert(data.message)}
                if (data.deleted) {
                    selectedOption.remove();
                    if (selectGoal.options.length > 0) {updateProgress();}
                    else {progressBar.style.width = "0%";}
                    amountInput.value = "";
                    return;
                }
                selectedOption.setAttribute("currentAmount", data.currentAmount);
                progressBar.style.width = Math.min(data.progress, 100) + "%";
                amountInput.value = "";
            })
        });
    }
});