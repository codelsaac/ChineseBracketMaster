/**
 * 中國象棋比賽管理系統
 * 增強動畫和互動效果
 */

/**
 * 當DOM加載完成後初始化動畫效果
 */
document.addEventListener('DOMContentLoaded', function() {
    // 初始化動畫和互動效果
    initAnimations();
    
    // 初始化賽程表特效
    if (document.getElementById('tournament-bracket')) {
        initBracketAnimations();
    }
});

/**
 * 初始化頁面動畫效果
 */
function initAnimations() {
    // 添加滾動動畫效果
    window.addEventListener('scroll', handleScroll);
    
    // 應用浮動動畫到特定元素
    const floatElements = document.querySelectorAll('.float');
    floatElements.forEach(element => {
        applyFloatAnimation(element);
    });
    
    // 為卡片添加進入動畫
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 150));
    });
    
    // 為按鈕添加波紋效果
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', createRipple);
    });
}

/**
 * 當用戶滾動頁面時處理動畫
 */
function handleScroll() {
    // 定義應該進入視區的元素
    const elementsToAnimate = document.querySelectorAll('.card, h1, h2, .table, .tournament-round');
    
    elementsToAnimate.forEach(elem => {
        if (isElementInViewport(elem) && !elem.classList.contains('animated')) {
            elem.classList.add('animated');
            
            // 根據元素類型應用不同的動畫
            if (elem.classList.contains('card')) {
                elem.style.animation = 'fadeIn 0.8s forwards';
            } else if (elem.tagName.toLowerCase() === 'h1' || elem.tagName.toLowerCase() === 'h2') {
                elem.style.animation = 'slideIn 0.5s forwards';
            } else if (elem.classList.contains('table')) {
                elem.style.animation = 'fadeIn 1s forwards';
            } else if (elem.classList.contains('tournament-round')) {
                elem.style.animation = 'slideIn 0.7s forwards';
            }
        }
    });
}

/**
 * 判斷元素是否在視區內
 * @param {Element} el - 要檢查的元素
 * @returns {boolean}
 */
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * 為按鈕創建波紋效果
 * @param {Event} e - 點擊事件
 */
function createRipple(e) {
    const button = e.currentTarget;
    
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - button.getBoundingClientRect().left - radius}px`;
    circle.style.top = `${e.clientY - button.getBoundingClientRect().top - radius}px`;
    circle.classList.add('ripple');
    
    // 如果已有波紋效果，先移除
    const ripple = button.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
    
    // 動畫完成後移除元素
    setTimeout(() => {
        circle.remove();
    }, 600);
}

/**
 * 應用浮動動畫到元素
 * @param {Element} element - 要應用浮動效果的元素
 */
function applyFloatAnimation(element) {
    // 隨機延遲開始時間使動畫適合
    const delay = Math.random() * 2;
    element.style.animation = `floatAnimation 4s ease-in-out ${delay}s infinite`;
}

/**
 * 初始化賽程表特別動畫
 */
function initBracketAnimations() {
    // 動畫顯示回合
    const bracketContainer = document.getElementById('tournament-bracket');
    if (!bracketContainer) return;
    
    // 為比賽括式圖添加動態動畫效果
    bracketContainer.addEventListener('mouseover', function(e) {
        if (e.target.classList.contains('match-card')) {
            highlightMatchPath(e.target);
        } else if (e.target.closest('.match-card')) {
            highlightMatchPath(e.target.closest('.match-card'));
        }
    });
    
    bracketContainer.addEventListener('mouseout', function(e) {
        resetHighlights();
    });
    
    // 為比賽動態加載添加動畫
    const originalLoadTournamentData = window.loadTournamentData;
    if (originalLoadTournamentData) {
        window.loadTournamentData = function(tournamentId) {
            // 在加載前顯示清空動畫
            const container = document.getElementById('tournament-bracket');
            container.innerHTML = `
                <div class="loading-animation">
                    <div class="spinner"></div>
                    <p>正在加載賽程表...</p>
                </div>
            `;
            
            // 調用原始加載函數
            originalLoadTournamentData(tournamentId);
        };
    }
}

/**
 * 高亮顯示比賽路徑
 * @param {Element} matchCard - 比賽卡片元素
 */
function highlightMatchPath(matchCard) {
    // 重置所有高亮
    resetHighlights();
    
    // 高亮當前卡片
    matchCard.classList.add('highlight');
    
    // 找到這場比賽的 ID
    const matchId = matchCard.dataset.matchId;
    if (!matchId) return;
    
    // 將相關的前後場比賽高亮
    const relatedMatches = document.querySelectorAll(`[data-next-match-id="${matchId}"]`);
    relatedMatches.forEach(match => {
        match.classList.add('related');
    });
    
    // 將相關的后續比賽高亮
    const nextMatchId = matchCard.dataset.nextMatchId;
    if (nextMatchId) {
        const nextMatch = document.querySelector(`[data-match-id="${nextMatchId}"]`);
        if (nextMatch) {
            nextMatch.classList.add('related');
        }
    }
}

/**
 * 重置所有高亮效果
 */
function resetHighlights() {
    document.querySelectorAll('.match-card.highlight, .match-card.related').forEach(match => {
        match.classList.remove('highlight', 'related');
    });
}

/**
 * 用於顯示冠軍慶祝效果
 * 增強版本
 */
function celebrateWinner() {
    // 添加自訂中國象棋風格的快樂升級動畫效果
    console.log('Celebrating with confetti!');
    
    // 清除現有的快樂動畫
    const existingConfetti = document.getElementById('confetti-canvas');
    if (existingConfetti) {
        existingConfetti.style.display = 'block';
    }
    
    // 添加更多中國風格元素
    const confettiSettings = {
        target: 'confetti-canvas',
        max: 200,
        size: 2,
        animate: true,
        props: ['circle', 'square', 'triangle', 'line'],
        colors: [
            [255, 0, 0], // 中國紅
            [255, 215, 0], // 金色
            [255, 165, 0], // 橘色
            [128, 0, 0]  // 深紅
        ],
        clock: 25,
        rotate: true,
        start_from_edge: true,
        respawn: true
    };
    
    // 創建新的 confetti 實例
    try {
        const confetti = new ConfettiGenerator(confettiSettings);
        confetti.render();
        
        // 8 秒後清除快樂效果
        setTimeout(() => {
            confetti.clear();
            existingConfetti.style.display = 'none';
            console.log('Confetti celebration ended');
        }, 8000);
        
        // 添加聲音效果（如果可用）
        if (window.Audio) {
            try {
                const audio = new Audio();
                audio.src = 'https://soundbible.com/grab.php?id=1003&type=mp3'; // 或使用您的本地音效
                audio.volume = 0.5;
                audio.play().catch(e => console.log('Audio autoplay prevented:', e));
            } catch (audioError) {
                console.error('Error playing celebration sound:', audioError);
            }
        }
    } catch (error) {
        console.error('Error creating confetti:', error);
    }
    
    // 添加顯示冠軍效果的額外動畫
    const bracketContainer = document.getElementById('tournament-bracket');
    if (bracketContainer) {
        const winnerCard = bracketContainer.querySelector('.championship-match .player.winner');
        if (winnerCard) {
            // 高亮動畫
            winnerCard.classList.add('winner-celebration');
            
            // 8 秒後移除高亮
            setTimeout(() => {
                winnerCard.classList.remove('winner-celebration');
            }, 8000);
        }
    }
}
