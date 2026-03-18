// Staff Panel Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize notifications
    function checkNotifications() {
        fetch('/notifications/staff/check/')
            .then(response => response.json())
            .then(data => {
                if (data.notifications.length > 0) {
                    showNotifications(data.notifications);
                }
            });
    }

    function showNotifications(notifications) {
        const container = document.getElementById('notifications-container');
        notifications.forEach(notification => {
            const alert = document.createElement('div');
            alert.className = `alert alert-${notification.type} alert-dismissible fade show`;
            alert.innerHTML = `
                ${notification.message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            container.appendChild(alert);
        });
    }

    // Check stock levels
    function checkStockLevels() {
        fetch('/products/staff/check-stock/')
            .then(response => response.json())
            .then(data => {
                if (data.low_stock.length > 0) {
                    showStockAlerts(data.low_stock);
                }
            });
    }

    function showStockAlerts(products) {
        const container = document.getElementById('stock-alerts-container');
        products.forEach(product => {
            const alert = document.createElement('div');
            alert.className = 'alert alert-warning alert-dismissible fade show';
            alert.innerHTML = `
                Low stock alert: ${product.name} (${product.stock} remaining)
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            container.appendChild(alert);
        });
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Check notifications every minute
    setInterval(checkNotifications, 60000);
    
    // Check stock levels every hour
    setInterval(checkStockLevels, 3600000);
    
    // Initial checks
    checkNotifications();
    checkStockLevels();
});