/**
 * Chinese Chess Tournament Management System
 * Theme switching functionality
 */

/**
 * Set the theme based on user preference or system setting
 */
function setTheme() {
    // Check for saved user preference
    const savedTheme = localStorage.getItem('theme');
    
    if (savedTheme) {
        // Use saved preference
        applyTheme(savedTheme);
    } else {
        // Check for system preference
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        
        if (prefersDarkScheme.matches) {
            applyTheme('dark');
        } else {
            applyTheme('light');
        }
    }
    
    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        // Only change if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });
}

/**
 * Apply the selected theme to the document
 * @param {string} theme - The theme to apply ('light' or 'dark')
 */
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeToggleIcon('dark');
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeToggleIcon('light');
    }
}

/**
 * Toggle between light and dark themes
 */
function toggleTheme() {
    const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Save user preference
    localStorage.setItem('theme', newTheme);
    
    // Apply the new theme
    applyTheme(newTheme);
}

// Initialize theme when script loads
document.addEventListener('DOMContentLoaded', setTheme);
