/**
 * Chinese Chess Tournament Management System
 * Tournament Bracket Visualization
 */

/**
 * Initialize the tournament bracket visualization
 * @param {Object} data - Tournament bracket data from API
 */
function initializeBracket(data) {
    console.log('Initializing bracket with data:', data);
    
    // Check if API returned an error
    if (data.error) {
        console.error('API returned error:', data.error);
        showErrorMessage(data.error || 'Failed to load tournament data. Please try again later.');
        return;
    }
    
    // First, cleanup any existing trophy elements anywhere in the DOM
    // This ensures we don't have leftover trophies from previous renders
    const existingTrophies = document.querySelectorAll('.winner-trophy');
    existingTrophies.forEach(trophy => {
        console.log('Removing existing trophy during initialization');
        trophy.remove();
    });
    
    const tournamentContainer = document.getElementById('tournament-bracket');
    if (!tournamentContainer) return;
    
    const rounds = data.rounds;
    const players = data.players;
    
    // Add checks: ensure rounds and players exist
    if (!rounds || !players) {
        console.error('Missing required data: rounds or players');
        showErrorMessage('Tournament data is incomplete. Please try again later.');
        return;
    }
    
    // Clear the container
    tournamentContainer.innerHTML = '';
    
    // Check if there's match data
    if (Object.keys(rounds).length === 0) {
        tournamentContainer.innerHTML = '<div class="alert alert-info">No matches available. Please add players and generate the bracket first.</div>';
        return;
    }
    
    // Get the number of rounds
    const roundKeys = Object.keys(rounds).sort((a, b) => parseInt(a) - parseInt(b));
    
    // Create each round column
    roundKeys.forEach(roundNumber => {
        const roundMatches = rounds[roundNumber];
        const roundTitle = getRoundTitle(roundNumber, roundKeys.length);
        
        // Create round container
        const roundElement = document.createElement('div');
        roundElement.className = 'tournament-round';
        
        // Add round title
        const titleElement = document.createElement('h3');
        titleElement.className = 'round-title';
        titleElement.textContent = roundTitle;
        roundElement.appendChild(titleElement);
        
        // Calculate the vertical spacing needed based on round number
        const matchSpacing = calculateMatchSpacing(parseInt(roundNumber), roundKeys.length);
        
        // Add matches to the round
        roundMatches.forEach((match, index) => {
            // Add match card
            const matchElement = createMatchElement(match, players, roundNumber, roundKeys.length);
            
            // Add match connector if this isn't the final round
            if (parseInt(roundNumber) < roundKeys.length) {
                const connectorElement = document.createElement('div');
                connectorElement.className = 'match-connector';
                connectorElement.style.height = `${matchSpacing}px`;
                roundElement.appendChild(connectorElement);
            }
            
            roundElement.appendChild(matchElement);
        });
        
        tournamentContainer.appendChild(roundElement);
    });
    
    // Add event listeners for player selection
    addPlayerSelectionListeners();
}

/**
 * Get descriptive title for a tournament round
 * @param {number} roundNumber - The current round number
 * @param {number} totalRounds - The total number of rounds
 * @returns {string} The round title
 */
function getRoundTitle(roundNumber, totalRounds) {
    roundNumber = parseInt(roundNumber);
    
    if (roundNumber === totalRounds) {
        return 'Final';
    } else if (roundNumber === totalRounds - 1) {
        return 'Semi-Finals';
    } else if (roundNumber === totalRounds - 2) {
        return 'Quarter-Finals';
    } else if (roundNumber === 1) {
        return 'First Round';
    } else {
        return `Round ${roundNumber}`;
    }
}

/**
 * Calculate the vertical spacing needed between matches based on round
 * @param {number} roundNumber - The current round number
 * @param {number} totalRounds - The total number of rounds
 * @returns {number} The spacing in pixels
 */
function calculateMatchSpacing(roundNumber, totalRounds) {
    // Spacing increases exponentially with each round
    const baseSpacing = 60; // 增加基本間距
    const factor = 2;
    
    return baseSpacing * Math.pow(factor, roundNumber - 1);
}

/**
 * Create a match element for the bracket
 * @param {Object} match - Match data
 * @param {Object} players - Player data lookup object
 * @param {number} roundNumber - Current round number
 * @param {number} totalRounds - Total number of rounds
 * @returns {HTMLElement} The match element
 */
function createMatchElement(match, players, roundNumber, totalRounds) {
    // Check if match and players data exists
    if (!match || !players) {
        console.error('Missing match or players data');
        return document.createElement('div');
    }
    
    const matchElement = document.createElement('div');
    matchElement.className = 'match-card';
    matchElement.dataset.matchId = match.id;
    
    // 添加右上角裝飾元素
    const cornerDecoration = document.createElement('div');
    cornerDecoration.className = 'corner-decoration';
    matchElement.appendChild(cornerDecoration);
    
    // Add championship match styling if it's the final
    const isFinalMatch = parseInt(roundNumber) === parseInt(totalRounds);
    if (isFinalMatch) {
        matchElement.classList.add('championship-match');
        matchElement.dataset.isFinal = 'true';
    }
    
    // First let's clean up any existing trophy icons in the DOM
    // before we create any new elements
    const existingTrophies = document.querySelectorAll('.winner-trophy');
    existingTrophies.forEach(trophy => {
        console.log('Removing existing trophy');
        trophy.remove();
    });
    
    // Player 1
    const player1Element = createPlayerElement(match.player1_id, players, match.winner_id);
    matchElement.appendChild(player1Element);
    
    // Player 2
    const player2Element = createPlayerElement(match.player2_id, players, match.winner_id);
    matchElement.appendChild(player2Element);
    
    // We'll only add trophy to final match with a valid winner (explicitly chosen by user)
    // Do not auto-add trophy for any match that looks like auto-bye winners
    if (isFinalMatch && match.winner_id) {
        // Define several conditions that might indicate auto-bye situations
        const hasEmptySlot = (match.player1_id === null || match.player2_id === null);
        const bothPlayersNotNull = (match.player1_id !== null && match.player2_id !== null);
        
        // Only show trophy when both players are present AND a winner is explicitly chosen by user
        // This prevents auto-crowned champions completely
        if (bothPlayersNotNull) {
            // Log the details for debugging
            console.log('Final match details:', {
                player1_id: match.player1_id,
                player2_id: match.player2_id,
                winner_id: match.winner_id,
                bothPlayersPresent: bothPlayersNotNull
            });
            
            // Determine if players exist in the database
            const player1Exists = match.player1_id && players[match.player1_id];
            const player2Exists = match.player2_id && players[match.player2_id];
            
            // Add trophy only when both players exist and user selected a winner
            if (player1Exists && match.player1_id === match.winner_id) {
                // Player 1 is the explicitly chosen winner
                if (!player1Element.classList.contains('bye')) {
                    addTrophyToElement(player1Element);
                }
            } else if (player2Exists && match.player2_id === match.winner_id) {
                // Player 2 is the explicitly chosen winner
                if (!player2Element.classList.contains('bye')) {
                    addTrophyToElement(player2Element);
                }
            }
        } else {
            console.log('Auto-bye detected in final or incomplete match, not showing trophy');
        }
    }
    
    // Helper function to add trophy to an element
    function addTrophyToElement(element) {
        // Create the trophy with unique positioning
        const trophyDiv = document.createElement('div');
        trophyDiv.className = 'winner-trophy';
        trophyDiv.innerHTML = '🏆';
        trophyDiv.title = '冠軍';
        trophyDiv.style.position = 'absolute';
        trophyDiv.style.right = '8px';
        trophyDiv.style.top = '50%';
        trophyDiv.style.transform = 'translateY(-50%)';
        trophyDiv.style.fontSize = '1.5em';
        trophyDiv.style.zIndex = '5';
        
        // Ensure the element has relative positioning
        element.style.position = 'relative';
        
        // Add trophy icon
        element.appendChild(trophyDiv);
        console.log('Trophy added to element');
    }
    
    return matchElement;
}

/**
 * Create a player element for a match
 * @param {string|null} playerId - Player ID or null for bye/empty slot
 * @param {Object} players - Player data lookup object
 * @param {string|null} winnerId - ID of the match winner
 * @returns {HTMLElement} The player element
 */
function createPlayerElement(playerId, players, winnerId) {
    // Create player element
    const playerElement = document.createElement('div');
    playerElement.classList.add('player');
    
    // Defensive check
    if (!players) {
        console.error('Players data is missing');
        playerElement.textContent = 'Error: Data missing';
        playerElement.classList.add('bye');
        return playerElement;
    }
    
    // Set player ID attribute (safely handle null/undefined)
    if (playerId) {
        playerElement.dataset.playerId = playerId;
    }
    
    // Try to get player data
    let player = null;
    if (playerId && typeof players === 'object') {
        player = players[playerId];
    }
    
    // If player data not found or playerId is empty, show TBD
    if (!player) {
        playerElement.textContent = 'TBD';
        playerElement.classList.add('bye');
        return playerElement;
    }
    
    // Build player name display
    const playerName = document.createElement('div');
    playerName.classList.add('player-name');
    playerName.textContent = player.name || 'Unnamed Player';
    
    // Build player school display
    const playerSchool = document.createElement('div');
    playerSchool.classList.add('player-school');
    playerSchool.textContent = player.school || '';
    
    // Add to element
    playerElement.appendChild(playerName);
    playerElement.appendChild(playerSchool);
    
    // Apply winner/loser styles based on winnerId
    if (winnerId) {
        if (playerId === winnerId) {
            playerElement.classList.add('winner');
        } else {
            playerElement.classList.add('loser');
        }
    }
    
    return playerElement;
}

/**
 * Add event listeners for player selection in matches
 */
function addPlayerSelectionListeners() {
    const players = document.querySelectorAll('.player[data-player-id]');
    
    players.forEach(player => {
        player.addEventListener('click', function() {
            const playerId = this.dataset.playerId;
            const matchCard = this.closest('.match-card');
            const matchId = matchCard.dataset.matchId;
            
            // Don't allow selection if this player already won
            if (this.classList.contains('winner')) {
                return;
            }
            
            // Confirm the selection
            if (confirm('Are you sure you want to mark this player as the winner?')) {
                updateMatchWinner(matchId, playerId);
            }
        });
    });
}

/**
 * Update the match with the selected winner
 * @param {number} matchId - The ID of the match
 * @param {number} winnerId - The ID of the winning player
 */
function updateMatchWinner(matchId, winnerId) {
    console.log(`Updating match ${matchId} with winner ${winnerId}`);
    
    // First remove any existing trophy icons to prevent duplicates
    const existingTrophies = document.querySelectorAll('.winner-trophy');
    existingTrophies.forEach(trophy => {
        console.log('Removing existing trophy during update');
        trophy.remove();
    });
    
    // Send the update to the server
    fetch(`/api/match/${matchId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ winner_id: winnerId }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Check if this was the final match
            const matchElement = document.querySelector(`[data-match-id="${matchId}"]`);
            if (matchElement) {
                const isFinalMatch = matchElement.closest('.championship-match') !== null;
                
                // If this was the final match, celebrate with confetti!
                if (isFinalMatch) {
                    console.log('Final match won! Celebrating...');
                    celebrateWinner();
                    
                    // Find the winner element to get the name
                    const winnerElement = document.querySelector(`[data-player-id="${winnerId}"]`);
                    let winnerName = 'Champion';
                    if (winnerElement && !winnerElement.classList.contains('bye')) {
                        const nameEl = winnerElement.querySelector('.player-name');
                        if (nameEl) {
                            winnerName = nameEl.textContent.trim();
                        }
                        
                        // Show congratulatory message
                        setTimeout(() => {
                            alert(`Congratulations! ${winnerName} is the champion of the tournament!`);
                        }, 1000);
                    }
                }
            }
            
            // Reload the tournament data to reflect the changes
            const tournamentContainer = document.getElementById('tournament-bracket');
            if (tournamentContainer) {
                const tournamentId = tournamentContainer.dataset.tournamentId;
                console.log('Reloading tournament data for ID:', tournamentId);
                loadTournamentData(tournamentId);
            }
        } else {
            showErrorMessage(data.error || 'Failed to update match');
        }
    })
    .catch(error => {
        console.error('Error updating match:', error);
        showErrorMessage('Failed to update match. Please try again.');
    });
}
