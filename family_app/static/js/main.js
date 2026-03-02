document.addEventListener('DOMContentLoaded', function () {
    // Auto-hide alerts after 5 seconds
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.classList.remove('show');
            alert.style.display = 'none';
        }, 5000);
    });

    // Format currency inputs to 2 decimal places on blur
    document.querySelectorAll('input[type="number"]').forEach(function (input) {
        input.addEventListener('blur', function () {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Confirm before submitting delete forms (POST-based)
    document.querySelectorAll('form.delete-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
});
