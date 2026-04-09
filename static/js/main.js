// Main JavaScript for LDAP Employee Directory

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Enhanced search input with debounce
    const searchInput = document.getElementById('searchQuery');
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                // Implement autocomplete here if needed
                console.log('Search query:', this.value);
            }, 300);
        });
    }
    
    // Table row click to navigate to profile
    const tableRows = document.querySelectorAll('tbody tr[data-href]');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function(e) {
            if (!e.target.closest('a, button')) {
                window.location.href = this.dataset.href;
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Confirm dialogs for sensitive actions
    const confirmLinks = document.querySelectorAll('[data-confirm]');
    confirmLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Loading spinner for long operations
    function showLoadingSpinner(button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        return () => {
            button.disabled = false;
            button.innerHTML = originalText;
        };
    }
    
    // Smooth scroll to top
    const scrollTopBtn = document.getElementById('scrollTopBtn');
    if (scrollTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                scrollTopBtn.style.display = 'block';
            } else {
                scrollTopBtn.style.display = 'none';
            }
        });
        
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy;
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            });
        });
    });
    
    // Tooltip initialization (if using Bootstrap tooltips)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Console message
    console.log('%c🔐 LDAP Employee Directory', 'font-size: 20px; color: #0d6efd; font-weight: bold;');
    console.log('%cSecure | Fast | Reliable', 'font-size: 14px; color: #6c757d;');
    
});

// API helper functions
const API = {
    async searchUsers(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('Search failed');
            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            return { results: [] };
        }
    },
    
    async getDepartments() {
        try {
            const response = await fetch('/api/departments');
            if (!response.ok) throw new Error('Failed to fetch departments');
            return await response.json();
        } catch (error) {
            console.error('Departments error:', error);
            return { departments: [] };
        }
    },
    
    async healthCheck() {
        try {
            const response = await fetch('/api/health');
            return await response.json();
        } catch (error) {
            console.error('Health check error:', error);
            return { status: 'error' };
        }
    }
};

// Export API for use in other scripts
window.DirectoryAPI = API;
