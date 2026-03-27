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
            const selectedOption = selectGoal.options[selectGoal.selectedIndex];
            const budget = parseFloat(selectedOption.getAttribute("budget")) || 0;
            const currentAmount = parseFloat(selectedOption.getAttribute("currentAmount")) || 0;
            const addOrSub = parseFloat(amountInput.value || 0);
            const total = currentAmount + addOrSub;

            if (total >= budget && budget > 0) {
                const confirmed = confirm("You are about to meet the budget for this goal. Doing this will remove the goal. Are you sure you want to do this?\n");
                if (!confirmed) {
                    e.preventDefault();
                } 
            }
        });
    }
});