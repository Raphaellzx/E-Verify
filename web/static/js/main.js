/**
 * Everify 网页核查自动化系统 - JavaScript主文件
 */

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化页面
    initializePage();
});

function initializePage() {
    // 检查是否有active tab，用于标签页导航
    // 添加响应式设计
    handleResponsiveDesign();
}

function handleResponsiveDesign() {
    // 处理窗口大小变化
    window.addEventListener('resize', function() {
        adjustLayout();
    });

    adjustLayout();
}

function adjustLayout() {
    const width = window.innerWidth;

    // 小屏幕设备处理
    if (width <= 768) {
        // 调整侧边栏和内容区布局
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content');

        if (sidebar && content) {
            sidebar.style.width = '200px';
            content.style.marginLeft = '0';
        }
    } else {
        // 大屏幕设备恢复原状
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content');

        if (sidebar && content) {
            sidebar.style.width = '250px';
            content.style.marginLeft = '0';
        }
    }
}

// 平滑滚动
function smoothScroll(element, duration) {
    const target = document.querySelector(element);
    if (!target) return;

    const targetPosition = target.getBoundingClientRect().top;
    const startPosition = window.pageYOffset;
    const distance = targetPosition - startPosition;
    let startTime = null;

    function animation(currentTime) {
        if (startTime === null) startTime = currentTime;
        const timeElapsed = currentTime - startTime;
        const run = ease(timeElapsed, startPosition, distance, duration);
        window.scrollTo(0, run);

        if (timeElapsed < duration) {
            requestAnimationFrame(animation);
        }
    }

    function ease(t, b, c, d) {
        t /= d;
        t--;
        return c * (t * t * t * t * t + 1) + b;
    }

    requestAnimationFrame(animation);
}

// 本地存储
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('存储失败:', e);
        return false;
    }
}

function loadFromStorage(key, defaultValue) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : defaultValue;
    } catch (e) {
        console.error('加载失败:', e);
        return defaultValue;
    }
}

function removeFromStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('删除失败:', e);
        return false;
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            ${message}
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 12px;
            min-width: 300px;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        .notification.success {
            border-left: 4px solid #28a745;
            background: #f8fff9;
        }

        .notification.error {
            border-left: 4px solid #dc3545;
            background: #fff9f9;
        }

        .notification.warning {
            border-left: 4px solid #ffc107;
            background: #fffef8;
        }

        .notification.info {
            border-left: 4px solid #17a2b8;
            background: #f8fcff;
        }

        .notification-content {
            flex: 1;
        }

        .notification-close {
            background: none;
            border: none;
            color: #999;
            cursor: pointer;
            font-size: 18px;
            padding: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .notification-close:hover {
            color: #666;
        }
    `;
    if (!document.querySelector('style[data-notification]')) {
        style.setAttribute('data-notification', '');
        document.head.appendChild(style);
    }

    document.body.appendChild(notification);

    // 自动移除
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);

    return notification;
}

// 显示加载动画
function showLoading(message = '加载中...') {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-content">
            <div class="spinner">
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
                <div class="spinner-ring"></div>
            </div>
            <div class="loading-text">${message}</div>
        </div>
    `;

    const style = document.createElement('style');
    style.textContent = `
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }

        .loading-content {
            background: white;
            border-radius: 8px;
            padding: 48px 64px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            text-align: center;
        }

        .spinner {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 24px;
        }

        .spinner-ring {
            width: 40px;
            height: 40px;
            border: 3px solid #f3f3f3;
            border-top-color: #4A90E2;
            border-radius: 50%;
            animation: spin 1s ease-in-out infinite;
            margin: 0 4px;
        }

        .spinner-ring:nth-child(2) {
            animation-delay: 0.1s;
        }

        .spinner-ring:nth-child(3) {
            animation-delay: 0.2s;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: #333;
            font-size: 16px;
            font-weight: 500;
        }
    `;
    if (!document.querySelector('style[data-loading]')) {
        style.setAttribute('data-loading', '');
        document.head.appendChild(style);
    }

    document.body.appendChild(overlay);

    return overlay;
}

function hideLoading(overlay) {
    if (overlay && overlay.parentNode) {
        overlay.remove();
    }
}

// API请求封装
function apiRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        fetch(url, {
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            body: options.body ? JSON.stringify(options.body) : null
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') {
                showNotification(data.message, 'error');
                reject(data);
            } else {
                if (data.message) {
                    showNotification(data.message, 'success');
                }
                resolve(data);
            }
        })
        .catch(error => {
            console.error('API请求失败:', error);
            showNotification('网络请求失败，请重试', 'error');
            reject(error);
        });
    });
}

// 表单验证
function validateForm(form, validators = {}) {
    const errors = [];

    form.querySelectorAll('[required]').forEach(field => {
        if (!field.value.trim()) {
            errors.push(`${field.getAttribute('placeholder') || '此字段'}不能为空`);
        }
    });

    Object.keys(validators).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (field) {
            const validator = validators[fieldName];
            if (typeof validator === 'function') {
                const error = validator(field.value);
                if (error) {
                    errors.push(error);
                }
            }
        }
    });

    if (errors.length > 0) {
        showNotification(errors[0], 'error');
        return false;
    }

    return true;
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 工具函数
function formatDate(date, format = 'YYYY-MM-DD HH:mm:ss') {
    const d = new Date(date);
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');

    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hours)
        .replace('mm', minutes)
        .replace('ss', seconds);
}

function copyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();

    try {
        document.execCommand('copy');
        showNotification('复制成功', 'success');
        return true;
    } catch (error) {
        console.error('复制失败:', error);
        showNotification('复制失败', 'error');
        return false;
    } finally {
        document.body.removeChild(textarea);
    }
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', initializePage);
