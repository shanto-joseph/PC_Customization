// PC Builder Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Component selection handling
    const componentSelectors = document.querySelectorAll('.component-selector');
    componentSelectors.forEach(selector => {
        selector.addEventListener('change', function() {
            updateBuildSummary();
            checkCompatibility();
        });
    });

    // Compatibility checking
    function checkCompatibility() {
        const cpu = document.getElementById('cpu').value;
        const motherboard = document.getElementById('motherboard').value;
        
        if (cpu && motherboard) {
            fetch('/customization/check-compatibility/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ cpu, motherboard })
            })
            .then(response => response.json())
            .then(data => {
                const alert = document.getElementById('compatibility-alert');
                alert.className = `alert ${data.compatible ? 'alert-success' : 'alert-danger'}`;
                alert.textContent = data.message;
            });
        }
    }

    // Build summary updates
    function updateBuildSummary() {
        let total = 0;
        const selectedComponents = document.querySelectorAll('.component-selector select');
        selectedComponents.forEach(select => {
            const price = select.options[select.selectedIndex].dataset.price;
            if (price) {
                total += parseFloat(price);
            }
        });

        const serviceCharge = parseFloat(document.getElementById('service-charge').dataset.charge);
        total += serviceCharge;

        document.getElementById('build-total').textContent = `₹${total.toFixed(2)}`;
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});