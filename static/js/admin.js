// Admin Panel Scripts
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Sidebar toggle for mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
        });
    }

    // DataTables initialization
    const tables = document.querySelectorAll('.datatable');
    tables.forEach(table => {
        new simpleDatatables.DataTable(table, {
            searchable: true,
            fixedHeight: true,
            perPage: 10
        });
    });

    // Chart initialization
    const chartElements = document.querySelectorAll('.chart');
    chartElements.forEach(element => {
        const ctx = element.getContext('2d');
        const data = JSON.parse(element.dataset.chartData || '{}');
        new Chart(ctx, data);
    });
});