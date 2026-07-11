// Main JavaScript file for Smart Farmer Marketplace

// Cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add to cart confirmation
    const addToCartButtons = document.querySelectorAll('[data-add-to-cart]');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productName = this.getAttribute('data-product-name');
            // Show a temporary notification
            showNotification(`${productName} added to cart!`, 'success');
        });
    });

    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) {
                this.value = 1;
            }
        });
    });

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-confirm-delete');
            if (!confirm(`Are you sure you want to ${action}?`)) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Handle rating selection in feedback form
    if (document.querySelector('.rating-input')) {
        const ratingInputs = document.querySelectorAll('.rating-input input[type="radio"]');
        ratingInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Remove 'active' class from all labels
                document.querySelectorAll('.rating-input label').forEach(label => {
                    label.classList.remove('active');
                });
                
                // Add 'active' class to selected and previous labels
                const value = parseInt(this.value);
                for (let i = 1; i <= value; i++) {
                    const label = document.querySelector(`[for="rating${i}"]`);
                    if (label) {
                        label.classList.add('active');
                    }
                }
            });
        });
    }
});

// Utility function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; min-width: 300px; z-index: 9999;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Function to update cart count in navbar
function updateCartCount(count) {
    const cartBadge = document.querySelector('.nav-item.dropdown .badge');
    if (cartBadge) {
        cartBadge.textContent = count;
    }
}

// Search functionality
function searchProducts() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const productName = card.querySelector('.card-title').textContent.toLowerCase();
        if (productName.includes(searchTerm)) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}

// Filter products by category
function filterByCategory(category) {
    const productCards = document.querySelectorAll('.product-card');
    
    productCards.forEach(card => {
        const productCategory = card.getAttribute('data-category').toLowerCase();
        if (category === 'all' || productCategory === category) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
}