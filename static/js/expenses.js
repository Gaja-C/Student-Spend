function confirmDeleteCategory() {
    return confirm("Are you sure you want to delete this category?\nDeleting it will also remove all expenses in the category.");
}

document.addEventListener("DOMContentLoaded", function () {
    const selectCategoryExpense = document.getElementById("selectCategoryExpense");
    const selectExpense = document.getElementById("selectExpense");

    function updateExpenses() {
        if (!selectCategoryExpense || !selectExpense) return;

        const selectedOption = selectCategoryExpense.options[selectCategoryExpense.selectedIndex];
        const expenses = JSON.parse(selectedOption.getAttribute('expenseNames') || '[]');

        selectExpense.innerHTML = "";

        for (const expense of expenses) {
            const opt = document.createElement('option');
            opt.value = expense.name;
            opt.textContent = expense.name;
            selectExpense.appendChild(opt);
        }
    }

    updateExpenses();
    if (selectCategoryExpense) {
        selectCategoryExpense.addEventListener("change", updateExpenses);
    }
});