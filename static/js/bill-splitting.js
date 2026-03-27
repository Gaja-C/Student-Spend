function confirmDeleteCategory() {
    return confirm("Are you sure you want to delete this group?\nDeleting it will remove it for all members.");
}

function addMember() {
    const addMembers = document.getElementById('members');
    const input = document.createElement('input');
    input.type = "text";
    input.name = "members";
    input.placeholder = "Add Group Member";
    addMembers.appendChild(input);
}