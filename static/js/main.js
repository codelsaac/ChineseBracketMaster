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
    
    // Initialize sortable players if on the players page
    const sortablePlayers = document.getElementById('sortable-players');
    if (sortablePlayers) {
        initSortablePlayers();
    }
    
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
 * Initialize sortable players functionality
 */
function initSortablePlayers() {
    const sortable = Sortable.create(document.getElementById('sortable-players'), {
        handle: '.drag-handle', // Drag handle selector within list items
        animation: 150,
        ghostClass: 'sortable-ghost', // Class name for the drop placeholder
        chosenClass: 'sortable-chosen', // Class name for the chosen item
        dragClass: 'sortable-drag', // Class name for the dragging item
        onEnd: function(evt) {
            // Get the tournament ID from the URL
            const pathParts = window.location.pathname.split('/');
            const tournamentId = pathParts[pathParts.indexOf('tournament') + 1];
            
            // Get all player IDs in order
            const playerIds = Array.from(document.querySelectorAll('#sortable-players tr')).map(row => row.dataset.id);
            
            // Send the order to the server
            fetch(`/tournament/${tournamentId}/players/reorder`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ playerIds: playerIds }),
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Error reordering players:', data.message);
                }
            })
            .catch(error => {
                console.error('Error reordering players:', error);
            });
        }
    });
}

/**
 * Initialize confetti celebration
 */
function initConfetti() {
    // Create confetti instance but don't start it yet
    const confettiSettings = { target: 'confetti-canvas', max: 150 };
    const confetti = new ConfettiGenerator(confettiSettings);
    confetti.render();
    
    // Hide the canvas initially
    document.getElementById('confetti-canvas').style.display = 'none';
    
    // Store the confetti instance for later use
    window.tournamentConfetti = confetti;
}

/**
 * Trigger confetti celebration
 */
function celebrateWinner() {
    const canvas = document.getElementById('confetti-canvas');
    if (!canvas) return;
    
    // Display the canvas
    canvas.style.display = 'block';
    
    // Let it run for 3 seconds then stop
    setTimeout(() => {
        canvas.style.display = 'none';
    }, 3000);
}







