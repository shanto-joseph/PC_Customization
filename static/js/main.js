// Add this at the beginning of your main.js file
document.addEventListener('DOMContentLoaded', function() {
    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    

    // Cart Operations
    function addToCart(productId) {
        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateCartBadge(data.cart_items_count);
                showNotification('Product added to cart successfully');
            } else {
                showNotification(data.message || 'Error adding product to cart', 'error');
            }
        })
        .catch(handleAjaxError);
    }

    function removeFromCart(itemId) {
        if (!confirm('Are you sure you want to remove this item from your cart?')) return;

        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartBadge(data.cart_items_count);
                location.reload();
            } else {
                showNotification(data.message || 'Error removing item from cart', 'error');
            }
        })
        .catch(handleAjaxError);
    }

    function updateCartQuantity(itemId, quantity) {
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ quantity: quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartBadge(data.cart_items_count);
                location.reload();
            } else {
                showNotification(data.message || 'Error updating cart', 'error');
            }
        })
        .catch(handleAjaxError);
    }

    // Wishlist Operations
    function addToWishlist(productId) {
        fetch(`/wishlist/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification('Product added to wishlist successfully');
            } else {
                showNotification(data.message || 'Error adding product to wishlist', 'error');
            }
        })
        .catch(handleAjaxError);
    }

    function removeFromWishlist(productId) {
        if (!confirm('Are you sure you want to remove this item from your wishlist?')) return;

        fetch(`/wishlist/remove/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                location.reload();
            } else {
                showNotification(data.message || 'Error removing item from wishlist', 'error');
            }
        })
        .catch(handleAjaxError);
    }

    // Form Validation
    'use strict';
    
    // Add validation classes to all forms with needs-validation class
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        input.addEventListener('input', function() {
            const strength = checkPasswordStrength(this.value);
            const strengthBar = this.parentElement.querySelector('.password-strength');
            if (strengthBar) {
                updatePasswordStrength(strengthBar, strength);
            }
        });
    });
});

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.match(/[a-z]+/)) strength += 1;
    if (password.match(/[A-Z]+/)) strength += 1;
    if (password.match(/[0-9]+/)) strength += 1;
    if (password.match(/[^a-zA-Z0-9]+/)) strength += 1;
    if (password.length >= 8) strength += 1;
    return strength;
}

function updatePasswordStrength(element, strength) {
    const strengthClasses = ['bg-danger', 'bg-warning', 'bg-info', 'bg-primary', 'bg-success'];
    const strengthTexts = ['Very Weak', 'Weak', 'Medium', 'Strong', 'Very Strong'];
    
    element.innerHTML = `
        <div class="progress" style="height: 5px;">
            <div class="progress-bar ${strengthClasses[strength-1]}" 
                 style="width: ${strength * 20}%"></div>
        </div>
        <small class="text-${strengthClasses[strength-1].replace('bg-', '')}">${strengthTexts[strength-1]}</small>
    `;
}