/*
 * Copyright (c) 2024.
 *
 */

document.addEventListener('DOMContentLoaded', () => {
    const selectAllCheckbox = document.querySelector('#select-all');
    const checkboxes = document.querySelectorAll('[data-invoice-id]');

    const toggleRowBackground = (checkbox) => {
        const invoiceRow = checkbox.closest('tr');
        invoiceRow.classList.toggle('bg-gray-100', checkbox.checked);
    };

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', () => {
            checkboxes.forEach(checkbox => {
                checkbox.checked = selectAllCheckbox.checked;
                toggleRowBackground(checkbox);
            });
        });
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => toggleRowBackground(checkbox));
    });
});
