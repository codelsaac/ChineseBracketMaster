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
    
    // Clear the container
    tournamentContainer.innerHTML = '';
    
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
 * @param {number|null} playerId - Player ID or null for bye/empty slot
 * @param {Object} players - Player data lookup object
 * @param {number|null} winnerId - ID of the match winner
 * @returns {HTMLElement} The player element
 */
function createPlayerElement(playerId, players, winnerId) {
    const playerElement = document.createElement('div');
    playerElement.className = 'player';
    
    if (playerId && players[playerId]) {
        const player = players[playerId];
        
        // Check if this player is the winner
        if (playerId === winnerId) {
            playerElement.classList.add('winner');
        }
        
        // Set data attributes for player selection
        playerElement.dataset.playerId = playerId;
        
        // Create player name and details
        const playerNameDiv = document.createElement('div');
        playerNameDiv.className = 'player-name';
        
        // 添加與學校相關的顏色（保持 Chinese Chess 主題顏色）
        const schoolColorClass = player.school.length % 2 === 0 ? 'player-red' : 'player-black';
        playerElement.classList.add(schoolColorClass);
        
        playerNameDiv.appendChild(document.createTextNode(player.name));
        
        // Add seeded badge if applicable
        if (player.is_seeded) {
            const seededBadge = document.createElement('span');
            seededBadge.className = 'seeded-badge';
            seededBadge.textContent = 'S';
            seededBadge.title = 'Seeded Player';
            playerNameDiv.appendChild(seededBadge);
        }
        
        // Add school info
        const playerSchoolDiv = document.createElement('div');
        playerSchoolDiv.className = 'player-school';
        playerSchoolDiv.textContent = player.school;
        
        // Combine elements
        const playerDetailsDiv = document.createElement('div');
        playerDetailsDiv.className = 'player-details';
        playerDetailsDiv.appendChild(playerNameDiv);
        playerDetailsDiv.appendChild(playerSchoolDiv);
        
        playerElement.appendChild(playerDetailsDiv);
    } else if (playerId) {
        // Player exists in database but not in current tournament (edge case)
        playerElement.classList.add('bye');
        playerElement.textContent = 'Bye';
    } else {
        // Empty slot or bye
        playerElement.classList.add('bye');
        playerElement.textContent = 'TBD';
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
            if (confirm('確定將這名選手標記為比賽勝利者嗎?')) {
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
                            alert(`\u606d\u559c\uff01 ${winnerName} \u662f\u8cfd\u4e8b\u7684\u51a0\u8ecd\uff01`);
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
