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
        
        // Initialize preview mode
        initPreviewMode();
        
        // Initialize color customization
        initColorCustomization();
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

/**
 * Initialize preview mode
 */
function initPreviewMode() {
    const previewButton = document.getElementById('preview-toggle');
    if (!previewButton) return;
    
    previewButton.addEventListener('click', function() {
        const tournamentId = document.getElementById('tournament-bracket').dataset.tournamentId;
        
        // Get tournament data
        fetch(`/api/tournament/${tournamentId}/bracket`)
            .then(response => response.json())
            .then(data => {
                // Populate the preview dropdown
                const rounds = Object.keys(data.rounds).sort((a, b) => parseInt(a) - parseInt(b));
                const selectElement = document.getElementById('preview-round');
                selectElement.innerHTML = '';
                
                rounds.forEach(round => {
                    const option = document.createElement('option');
                    option.value = round;
                    option.textContent = getRoundTitle(parseInt(round), rounds.length);
                    selectElement.appendChild(option);
                });
                
                // Show the preview modal
                const previewModal = new bootstrap.Modal(document.getElementById('previewModeModal'));
                previewModal.show();
                
                // Setup preview controls
                setupPreviewControls(data);
            })
            .catch(error => {
                console.error('Error loading tournament data for preview:', error);
            });
    });
}

/**
 * Setup preview controls
 * @param {Object} data - Tournament data
 */
function setupPreviewControls(data) {
    const previewRoundSelect = document.getElementById('preview-round');
    const previewNextButton = document.getElementById('preview-next');
    const autoPreviewCheckbox = document.getElementById('auto-preview');
    
    let currentRound = 1;
    let autoPreviewInterval;
    
    // Function to show a specific round
    const showRound = (roundNum) => {
        currentRound = roundNum;
        previewRoundSelect.value = roundNum;
        
        // Clone the tournament data for the preview
        const previewData = JSON.parse(JSON.stringify(data));
        
        // Only show matches up to the selected round
        Object.keys(previewData.rounds).forEach(round => {
            if (parseInt(round) > roundNum) {
                delete previewData.rounds[round];
            }
        });
        
        // Show the preview bracket
        const previewContainer = document.getElementById('preview-bracket');
        previewContainer.innerHTML = '';
        renderPreviewBracket(previewContainer, previewData);
    };
    
    // Initialize with round 1
    showRound(1);
    
    // Handle round selection change
    previewRoundSelect.addEventListener('change', function() {
        showRound(parseInt(this.value));
    });
    
    // Handle next button click
    previewNextButton.addEventListener('click', function() {
        if (currentRound < Object.keys(data.rounds).length) {
            showRound(currentRound + 1);
        }
    });
    
    // Handle auto preview toggle
    autoPreviewCheckbox.addEventListener('change', function() {
        if (this.checked) {
            // Start auto preview
            autoPreviewInterval = setInterval(() => {
                if (currentRound < Object.keys(data.rounds).length) {
                    showRound(currentRound + 1);
                } else {
                    // Restart from round 1 when reaching the end
                    showRound(1);
                }
            }, 2000); // Advance every 2 seconds
        } else {
            // Stop auto preview
            clearInterval(autoPreviewInterval);
        }
    });
    
    // Start auto preview if checkbox is checked
    if (autoPreviewCheckbox.checked) {
        autoPreviewInterval = setInterval(() => {
            if (currentRound < Object.keys(data.rounds).length) {
                showRound(currentRound + 1);
            } else {
                // Restart from round 1 when reaching the end
                showRound(1);
            }
        }, 2000); // Advance every 2 seconds
    }
    
    // Clear interval when modal is closed
    document.getElementById('previewModeModal').addEventListener('hidden.bs.modal', function() {
        clearInterval(autoPreviewInterval);
    });
}

/**
 * Render the preview bracket
 * @param {HTMLElement} container - Container element for the preview
 * @param {Object} data - Tournament data
 */
function renderPreviewBracket(container, data) {
    // Create a clone of the tournament container
    const fragment = document.createDocumentFragment();
    
    // Get the max round number
    const maxRound = Math.max(...Object.keys(data.rounds).map(round => parseInt(round)));
    
    // Create rounds
    for (let i = 1; i <= maxRound; i++) {
        const roundData = data.rounds[i] || [];
        
        // Create round element
        const roundDiv = document.createElement('div');
        roundDiv.className = 'tournament-round';
        
        // Add round title
        const titleDiv = document.createElement('div');
        titleDiv.className = 'round-title';
        titleDiv.textContent = getRoundTitle(i, maxRound);
        roundDiv.appendChild(titleDiv);
        
        // Add each match in this round
        roundData.forEach(match => {
            const matchElement = createPreviewMatchElement(match, data.players, i, maxRound);
            roundDiv.appendChild(matchElement);
        });
        
        fragment.appendChild(roundDiv);
    }
    
    container.appendChild(fragment);
}

/**
 * Create a match element for the preview bracket
 * @param {Object} match - Match data
 * @param {Object} players - Player data lookup object
 * @param {number} roundNumber - Current round number
 * @param {number} totalRounds - Total number of rounds
 * @returns {HTMLElement} The match element
 */
function createPreviewMatchElement(match, players, roundNumber, totalRounds) {
    const matchDiv = document.createElement('div');
    matchDiv.className = 'match-card';
    if (roundNumber === totalRounds) {
        matchDiv.classList.add('championship-match');
    }
    
    // Create player elements
    const player1Element = createPreviewPlayerElement(match.player1_id, players, match.winner_id);
    const player2Element = createPreviewPlayerElement(match.player2_id, players, match.winner_id);
    
    matchDiv.appendChild(player1Element);
    matchDiv.appendChild(player2Element);
    
    // Add subtle animation
    matchDiv.classList.add('pulse');
    
    return matchDiv;
}

/**
 * Create a player element for the preview match
 * @param {number|null} playerId - Player ID or null for bye/empty slot
 * @param {Object} players - Player data lookup object
 * @param {number|null} winnerId - ID of the match winner
 * @returns {HTMLElement} The player element
 */
function createPreviewPlayerElement(playerId, players, winnerId) {
    const playerDiv = document.createElement('div');
    
    if (playerId) {
        const player = players[playerId];
        const isWinner = playerId === winnerId;
        
        playerDiv.className = `player ${isWinner ? 'winner' : ''}`;
        
        // Add player name and school
        const nameSpan = document.createElement('div');
        nameSpan.className = 'player-name';
        
        // Add team color indicator if available
        const teamColor = localStorage.getItem(`school_color_${player.school}`);
        if (teamColor) {
            const colorIndicator = document.createElement('span');
            colorIndicator.className = 'team-color';
            colorIndicator.style.backgroundColor = teamColor;
            nameSpan.appendChild(colorIndicator);
        }
        
        nameSpan.appendChild(document.createTextNode(player.name));
        
        // Add seeded badge if player is seeded
        if (player.is_seeded) {
            const seededBadge = document.createElement('span');
            seededBadge.className = 'seeded-badge';
            seededBadge.textContent = 'S';
            nameSpan.appendChild(seededBadge);
        }
        
        playerDiv.appendChild(nameSpan);
        
        // Add school name
        const schoolDiv = document.createElement('div');
        schoolDiv.className = 'player-school';
        schoolDiv.textContent = player.school;
        playerDiv.appendChild(schoolDiv);
        
    } else {
        playerDiv.className = 'player bye';
        playerDiv.textContent = 'Bye';
    }
    
    return playerDiv;
}

/**
 * Initialize color customization
 */
function initColorCustomization() {
    const customizeButton = document.getElementById('customize-colors');
    if (!customizeButton) return;
    
    customizeButton.addEventListener('click', function() {
        const tournamentId = document.getElementById('tournament-bracket').dataset.tournamentId;
        
        // Get tournament data
        fetch(`/api/tournament/${tournamentId}/bracket`)
            .then(response => response.json())
            .then(data => {
                // Get unique schools
                const schools = [];
                Object.values(data.players).forEach(player => {
                    if (!schools.includes(player.school)) {
                        schools.push(player.school);
                    }
                });
                
                // Populate color picker container
                populateColorPickers(schools);
                
                // Show the modal
                const colorModal = new bootstrap.Modal(document.getElementById('customizeColorsModal'));
                colorModal.show();
            })
            .catch(error => {
                console.error('Error loading school data:', error);
            });
    });
    
    // Handle save colors button
    const saveColorsButton = document.getElementById('save-colors');
    if (saveColorsButton) {
        saveColorsButton.addEventListener('click', function() {
            // Save all color selections to localStorage
            const colorInputs = document.querySelectorAll('.color-input');
            colorInputs.forEach(input => {
                const school = input.dataset.school;
                const color = input.value;
                localStorage.setItem(`school_color_${school}`, color);
            });
            
            // Close the modal
            const colorModal = bootstrap.Modal.getInstance(document.getElementById('customizeColorsModal'));
            colorModal.hide();
            
            // Refresh the bracket to show new colors
            const tournamentId = document.getElementById('tournament-bracket').dataset.tournamentId;
            loadTournamentData(tournamentId);
        });
    }
}

/**
 * Populate color pickers for schools
 * @param {Array} schools - List of school names
 */
function populateColorPickers(schools) {
    const container = document.getElementById('team-colors-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Predefined colors
    const predefinedColors = [
        '#FF5252', '#FF4081', '#E040FB', '#7C4DFF', '#536DFE', '#448AFF', '#40C4FF', '#18FFFF',
        '#64FFDA', '#69F0AE', '#B2FF59', '#EEFF41', '#FFFF00', '#FFD740', '#FFAB40', '#FF6E40'
    ];
    
    schools.forEach((school, index) => {
        // Create a column for each school
        const col = document.createElement('div');
        col.className = 'col-md-3 col-sm-6';
        
        // Get saved color or use default
        const savedColor = localStorage.getItem(`school_color_${school}`) || predefinedColors[index % predefinedColors.length];
        
        // Create the color picker item
        const colorPickerItem = document.createElement('div');
        colorPickerItem.className = 'color-picker-item';
        
        // Create color preview
        const colorPreview = document.createElement('div');
        colorPreview.className = 'color-preview';
        colorPreview.style.backgroundColor = savedColor;
        
        // Create label with school name
        const schoolLabel = document.createElement('label');
        schoolLabel.textContent = school;
        schoolLabel.className = 'form-label mt-2';
        
        // Create color input
        const colorInput = document.createElement('input');
        colorInput.type = 'color';
        colorInput.className = 'color-input form-control form-control-color';
        colorInput.value = savedColor;
        colorInput.dataset.school = school;
        colorInput.title = `選擇 ${school} 的顏色`;
        
        // Update preview when color changes
        colorInput.addEventListener('input', function() {
            colorPreview.style.backgroundColor = this.value;
        });
        
        // Assemble the color picker
        colorPickerItem.appendChild(colorPreview);
        colorPickerItem.appendChild(schoolLabel);
        colorPickerItem.appendChild(colorInput);
        
        col.appendChild(colorPickerItem);
        container.appendChild(col);
    });
}
