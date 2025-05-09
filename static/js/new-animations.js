/**
 * 中國象棋比賽管理系統
 * 進階動畫和互動效果
 */

document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有動畫
    initAnimations();
    
    // 瀑布效果初始化
    initConfetti();
    
    // 如果在比賽賽程頁面，初始化特殊動畫
    if (document.getElementById('tournament-bracket')) {
        initBracketAnimations();
    }
});

/**
 * 初始化基本動畫效果
 */
function initAnimations() {
    // 監聽滾動事件來添加動畫
    window.addEventListener('scroll', handleScroll);
    
    // 初始化時觸發一次滾動檢查
    handleScroll();
    
    // 為所有按鈕增加波紋效果
    const buttons = document.querySelectorAll('button:not(.btn-close), .btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });
    
    // 為顯著元素增加浮動效果
    const floatingElements = document.querySelectorAll('.chess-title, .chess-piece-card');
    floatingElements.forEach(element => {
        applyFloatAnimation(element);
    });
    
    // 自動關閉通知
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        }, 5000);
    });
}

/**
 * 處理滾動事件，顯示元素時添加動畫
 */
function handleScroll() {
    const fadeElements = document.querySelectorAll('.fade-in:not(.animated)');
    const slideElements = document.querySelectorAll('.slide-in:not(.animated)');
    
    fadeElements.forEach(element => {
        if (isElementInViewport(element)) {
            element.classList.add('animated');
            element.style.opacity = '0';
            element.style.animation = 'fadeIn 0.8s forwards';
            element.style.animationDelay = Math.random() * 0.3 + 's';
        }
    });
    
    slideElements.forEach(element => {
        if (isElementInViewport(element)) {
            element.classList.add('animated');
            element.style.opacity = '0';
            element.style.animation = 'slideIn 0.6s forwards';
            element.style.animationDelay = Math.random() * 0.3 + 's';
        }
    });
}

/**
 * 檢查元素是否在可見範圍內
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
 * 為按鈕增加波紋效果
 * @param {Event} e - 點擊事件
 */
function createRipple(e) {
    const button = e.currentTarget;
    
    // 如果按鈕已經有波紋元素，先移除
    const ripples = button.querySelectorAll('.ripple');
    ripples.forEach(ripple => {
        button.removeChild(ripple);
    });
    
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.classList.add('ripple');
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${e.clientX - button.getBoundingClientRect().left - radius}px`;
    circle.style.top = `${e.clientY - button.getBoundingClientRect().top - radius}px`;
    
    // 根據按鈕類型設置波紋顔色
    if (button.classList.contains('btn-primary') || button.classList.contains('btn-chinese')) {
        circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
    } else if (button.classList.contains('btn-danger')) {
        circle.style.backgroundColor = 'rgba(255, 255, 255, 0.4)';
    } else {
        circle.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
    }
    
    button.appendChild(circle);
    
    // 300ms 後移除波紋元素
    setTimeout(() => {
        if (circle.parentElement === button) {
            button.removeChild(circle);
        }
    }, 600);
}

/**
 * 為元素添加浮動動畫
 * @param {Element} element - 要添加浮動動畫的元素
 */
function applyFloatAnimation(element) {
    // 為每個元素添加不同的動畫延遲
    const delay = Math.random() * 2;
    
    // 添加浮動動畫樣式
    element.style.animation = `float 5s ease-in-out ${delay}s infinite`;
}

/**
 * 初始化比賽賽程表特殊動畫
 */
function initBracketAnimations() {
    // 監聽鼠標移入比賽卡片事件
    document.addEventListener('click', function() {
        // 重置所有高亮效果
        resetHighlights();
    });
    
    // 添加高亮路徑的事件監聽器
    // 注意：這在動態生成賽程表後填充
    document.addEventListener('DOMNodeInserted', function(e) {
        if (e.target.classList && e.target.classList.contains('match-card')) {
            e.target.addEventListener('mouseenter', function() {
                highlightMatchPath(this);
            });
            
            e.target.addEventListener('mouseleave', function() {
                resetHighlights();
            });
        }
    });
}

/**
 * 高亮顯示比賽路徑
 * @param {Element} matchCard - 比賽卡片元素
 */
function highlightMatchPath(matchCard) {
    // 重置之前的高亮
    resetHighlights();
    
    // 然後添加特殊效果類名
    matchCard.classList.add('highlight-path');
    
    // 取得比賽的ID
    const matchId = matchCard.getAttribute('data-match-id');
    if (!matchId) return;
    
    // 高亮所有相關的比賽卡片
    // 找到下一個比賽（如果有）
    const nextMatchId = matchCard.getAttribute('data-next-match');
    if (nextMatchId) {
        const nextMatch = document.querySelector(`[data-match-id="${nextMatchId}"]`);
        if (nextMatch) {
            nextMatch.classList.add('highlight-path');
            // 這裡可以遞歸地繼續高亮下去
        }
    }
    
    // 高亮前一個比賽（如果有）
    const prevMatches = document.querySelectorAll(`[data-next-match="${matchId}"]`);
    prevMatches.forEach(prevMatch => {
        prevMatch.classList.add('highlight-path');
        // 同樣可以遞歸地繼續高亮上去
    });
    
    // 添加一個輕微的質感
    const allHighlighted = document.querySelectorAll('.highlight-path');
    allHighlighted.forEach((el, index) => {
        el.style.boxShadow = '0 0 15px rgba(230, 57, 70, 0.5)';
        el.style.transform = 'scale(1.03)';
        el.style.zIndex = '10';
        el.style.transition = 'all 0.3s ease';
    });
}

/**
 * 重置所有高亮效果
 */
function resetHighlights() {
    const highlightedElements = document.querySelectorAll('.highlight-path');
    highlightedElements.forEach(el => {
        el.classList.remove('highlight-path');
        el.style.boxShadow = '';
        el.style.transform = '';
        el.style.zIndex = '';
    });
}

/**
 * 初始化瀑布效果
 */
function initConfetti() {
    const confettiCanvas = document.getElementById('confetti-canvas');
    if (!confettiCanvas) return;

    // 準備瀑布配置
    window.confettiSettings = {
        target: 'confetti-canvas',
        max: 150,
        size: 1.5,
        animate: true,
        props: ['circle', 'square', 'triangle', 'line'],
        colors: [[165,104,246], [230,61,135], [0,199,228], [253,214,126]],
        clock: 25,
        rotate: true,
        start_from_edge: true,
        respawn: false,
        ticks: 200
    };
    
    window.confetti = new ConfettiGenerator(window.confettiSettings);
}

/**
 * 張顯冠軍慶祥效果 - 瀑布與視覺效果
 */
function celebrateWinner() {
    const confettiCanvas = document.getElementById('confetti-canvas');
    if (!confettiCanvas) return;
    
    // 顯示瀑布畫布
    confettiCanvas.style.display = 'block';
    
    // 從新生成瀑布配置並開始
    if (window.confetti) {
        window.confetti.clear();
        window.confetti.render();
    }
    
    // 尋找冠軍比賽
    const championshipMatch = document.querySelector('.championship-match');
    if (championshipMatch) {
        // 找到冠軍選手
        const winner = championshipMatch.querySelector('.winner');
        if (winner) {
            // 添加質感光晉
            championshipMatch.style.animation = 'chessPulse 2s infinite';
            championshipMatch.style.boxShadow = '0 0 25px rgba(255, 215, 0, 0.7)';
        }
    }
    
    // 5秒後關閉瀑布
    setTimeout(() => {
        if (window.confetti) {
            window.confetti.clear();
        }
        confettiCanvas.style.display = 'none';
    }, 5000);
}

/**
 * 重生動畫樣式
 */
document.head.insertAdjacentHTML('beforeend', `
<style>
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    
    .highlight-path {
        position: relative;
    }
    
    .btn {
        position: relative;
        overflow: hidden;
    }
</style>
`);
