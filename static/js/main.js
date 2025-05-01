/**
 * Chinese Chess Tournament Management System
 * Main JavaScript file
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tournament data loading if we're on the tournament view page
    const tournamentContainer = document.getElementById('tournament-bracket');
    if (tournamentContainer) {
        const tournamentId = tournamentContainer.dataset.tournamentId;
        loadTournamentData(tournamentId);
        
        // Initialize confetti for winners
        initConfetti();
    }
    
    // Sortable players feature removed
    
    // Initialize theme toggle
    initThemeToggle();
    
    // Initialize form validations
    initFormValidation();
    
    // Initialize alerts auto-dismiss
    initAlertsDismiss();
});

/**
 * Initialize theme toggle functionality
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Check for saved theme preference or use default
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply the theme class to the body
    document.body.classList.toggle('dark-theme', currentTheme === 'dark');
    
    // Update the toggle button icon
    updateThemeToggleIcon(currentTheme);
    
    // Add event listener for toggle click
    themeToggle.addEventListener('click', function() {
        // Toggle the theme
        const newTheme = document.body.classList.contains('dark-theme') ? 'light' : 'dark';
        
        // Update body class
        document.body.classList.toggle('dark-theme');
        
        // Save the theme preference
        localStorage.setItem('theme', newTheme);
        
        // Update the toggle button icon
        updateThemeToggleIcon(newTheme);
    });
}

/**
 * Update theme toggle icon based on current theme
 * @param {string} theme - Current theme ('light' or 'dark')
 */
function updateThemeToggleIcon(theme) {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;
    
    // Update the icon based on the theme
    if (theme === 'dark') {
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
        themeToggle.title = 'Switch to Light Mode';
    } else {
        themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
        themeToggle.title = 'Switch to Dark Mode';
    }
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    // Get all forms with the 'needs-validation' class
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over them and prevent submission if validation fails
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Initialize auto-dismiss for alerts
 */
function initAlertsDismiss() {
    // Get all alerts
    const alerts = document.querySelectorAll('.alert');
    
    // Auto-dismiss after 5 seconds
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
}

/**
 * Load tournament data from the API
 * @param {number} tournamentId - The ID of the tournament to load
 */
function loadTournamentData(tournamentId) {
    fetch(`/api/tournament/${tournamentId}/bracket`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Initialize the bracket visualization with the data
            initializeBracket(data);
        })
        .catch(error => {
            console.error('Error loading tournament data:', error);
            showErrorMessage('Failed to load tournament data. Please try again later.');
        });
}

/**
 * Show error message on the page
 * @param {string} message - The error message to display
 */
function showErrorMessage(message) {
    const container = document.getElementById('tournament-bracket');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-error">
                <strong>Error:</strong> ${message}
            </div>
        `;
    }
}

/**
 * Handle player form edit
 * @param {number} playerId - The ID of the player to edit
 */
function editPlayer(playerId) {
    const playerRow = document.getElementById(`player-${playerId}`);
    if (!playerRow) return;
    
    const playerData = {
        name: playerRow.dataset.name,
        school: playerRow.dataset.school,
        isSeeded: playerRow.dataset.seeded === 'true'
    };
    
    // Fill the edit form with player data
    const editForm = document.getElementById('edit-player-form');
    if (editForm) {
        editForm.action = editForm.action.replace('/0', `/${playerId}`);
        editForm.querySelector('#edit-name').value = playerData.name;
        editForm.querySelector('#edit-school').value = playerData.school;
        editForm.querySelector('#edit-seeded').checked = playerData.isSeeded;
        
        // Show the edit modal (assuming Bootstrap is used)
        const editModal = new bootstrap.Modal(document.getElementById('editPlayerModal'));
        editModal.show();
    }
}

/**
 * Confirm player deletion
 * @param {number} playerId - The ID of the player to delete
 * @param {string} playerName - The name of the player
 */
function confirmDeletePlayer(playerId, playerName) {
    const deleteForm = document.getElementById('delete-player-form');
    if (!deleteForm) return;
    
    deleteForm.action = deleteForm.action.replace('/0', `/${playerId}`);
    
    // Set player name in confirmation message
    const confirmMessage = document.getElementById('delete-confirm-message');
    if (confirmMessage) {
        confirmMessage.textContent = `確定要刪除選手 "${playerName}" 嗎？`;
    }
    
    // Show the delete confirmation modal (assuming Bootstrap is used)
    const deleteModal = new bootstrap.Modal(document.getElementById('deletePlayerModal'));
    deleteModal.show();
}

/**
 * Sortable players functionality has been removed as per requirements
 */
// Function removed as drag-and-drop sorting is no longer needed

/**
 * Initialize confetti celebration
 */
function initConfetti() {
    try {
        // Check for confetti canvas
        const canvas = document.getElementById('confetti-canvas');
        if (!canvas) {
            console.error('Could not find confetti canvas element');
            return;
        }

        console.log('Initializing confetti celebration');

        // Create confetti instance but don't start it yet
        const confettiSettings = { 
            target: 'confetti-canvas', 
            max: 150,
            size: 1.5,
            animate: true,
            props: ['circle', 'square', 'triangle', 'line'],
            colors: [[165,104,246],[230,61,135],[0,199,228],[253,214,126]],
            clock: 25,
            rotate: true,
            start_from_edge: true,
            respawn: true
        };
        
        // Make sure ConfettiGenerator is available
        if (typeof ConfettiGenerator !== 'function') {
            console.error('ConfettiGenerator not loaded!');
            return;
        }
        
        const confetti = new ConfettiGenerator(confettiSettings);
        confetti.render();
        
        // Hide the canvas initially
        canvas.style.display = 'none';
        
        // Store the confetti instance for later use
        window.tournamentConfetti = confetti;
        console.log('Confetti initialized successfully');
    } catch (error) {
        console.error('Error initializing confetti:', error);
    }
}

/**
 * Trigger confetti celebration
 */
function celebrateWinner() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) {
        console.error('Confetti canvas not found!');
        return;
    }
    
    console.log('Celebrating with confetti!');
    
    // Display the canvas
    canvas.style.display = 'block';
    
    // Make sure the confetti instance exists
    if (!window.tournamentConfetti) {
        // If not initialized yet, initialize it now
        initConfetti();
    }
    
    // Let it run for 5 seconds then stop
    setTimeout(() => {
        canvas.style.display = 'none';
        console.log('Confetti celebration ended');
    }, 5000);
}







