/**
 * Chinese Chess Tournament Management System
 * Tournament Bracket Visualization
 */

/**
 * Initialize the tournament bracket visualization
 * @param {Object} data - Tournament bracket data from API
 */
function initializeBracket(data) {
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
    const baseSpacing = 20;
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
    const matchElement = document.createElement('div');
    matchElement.className = 'match-card';
    matchElement.dataset.matchId = match.id;
    
    // Add championship match styling if it's the final
    const isFinalMatch = parseInt(roundNumber) === parseInt(totalRounds);
    if (isFinalMatch) {
        matchElement.classList.add('championship-match');
        matchElement.dataset.isFinal = 'true';
    }
    
    // Player 1
    const player1Element = createPlayerElement(match.player1_id, players, match.winner_id);
    if (isFinalMatch && match.winner_id === match.player1_id) {
        // Add trophy to player 1 if they are the winner in the final
        const trophyIcon = document.createElement('span');
        trophyIcon.className = 'winner-trophy';
        trophyIcon.innerHTML = '🏆';
        trophyIcon.title = '冠軍';
        trophyIcon.style.marginLeft = '5px';
        trophyIcon.style.fontSize = '1.2em';
        player1Element.appendChild(trophyIcon);
    }
    matchElement.appendChild(player1Element);
    
    // Player 2
    const player2Element = createPlayerElement(match.player2_id, players, match.winner_id);
    if (isFinalMatch && match.winner_id === match.player2_id) {
        // Add trophy to player 2 if they are the winner in the final
        const trophyIcon = document.createElement('span');
        trophyIcon.className = 'winner-trophy';
        trophyIcon.innerHTML = '🏆';
        trophyIcon.title = '冠軍';
        trophyIcon.style.marginLeft = '5px';
        trophyIcon.style.fontSize = '1.2em';
        player2Element.appendChild(trophyIcon);
    }
    matchElement.appendChild(player2Element);
    
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
        
        // 移除顏色功能
        
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
                    
                    // Show congratulatory message
                    const winnerElement = document.querySelector(`[data-player-id="${winnerId}"]`);
                    let winnerName = 'Champion';
                    if (winnerElement) {
                        const nameEl = winnerElement.querySelector('.player-name');
                        if (nameEl) {
                            winnerName = nameEl.textContent.trim();
                        }
                    }
                    
                    setTimeout(() => {
                        alert(`\u606d\u559c\uff01 ${winnerName} \u662f\u8cfd\u4e8b\u7684\u51a0\u8ecd\uff01`);
                    }, 1000);
                }
            }
            
            // Reload the tournament data to reflect the changes
            const tournamentContainer = document.getElementById('tournament-bracket');
            if (tournamentContainer) {
                const tournamentId = tournamentContainer.dataset.tournamentId;
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
