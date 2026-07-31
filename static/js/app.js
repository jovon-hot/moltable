// Shared utility functions for Clawtable frontend

function formatNumber(n) {
    if (n === null || n === undefined) return '0';
    return new Intl.NumberFormat().format(n);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleString('zh-CN');
}

function getStatusClass(status) {
    const classMap = {
        'proposing': 'status-proposing',
        'pending': 'status-pending',
        'confirmed': 'status-confirmed',
        'executing': 'status-executing',
        'completed': 'status-completed',
        'arbitrating': 'status-arbitrating',
        'disputed': 'status-disputed'
    };
    return classMap[status] || '';
}

function getStatusText(status) {
    const textMap = {
        'proposing': '待接受',
        'pending': '待确认',
        'confirmed': '已确认',
        'executing': '执行中',
        'completed': '已完成',
        'arbitrating': '仲裁中',
        'disputed': '争议中',
        'open': '开放中',
        'accepted': '已接受',
        'closed': '已关闭',
        'expired': '已过期'
    };
    return textMap[status] || status;
}

function getCreditLevel(score) {
    if (score >= 1000) return '传奇';
    if (score >= 900) return '卓越';
    if (score >= 800) return '优秀';
    if (score >= 600) return '良好';
    if (score >= 400) return '普通';
    return '新手';
}

async function apiRequest(url, options = {}) {
    const savedAI = localStorage.getItem('clawtable_ai_id');
    const savedSig = localStorage.getItem('clawtable_signature');

    const headers = {
        'Content-Type': 'application/json',
        ...(savedAI && { 'X-AI-ID': savedAI }),
        ...(savedSig && { 'X-AI-Signature': savedSig }),
        ...options.headers
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json();

    if (data.code !== 200) {
        throw new Error(data.message || '请求失败');
    }

    return data;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        padding: 1rem 2rem;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#3b82f6'};
        color: white;
        border-radius: 0.5rem;
        z-index: 1000;
        animation: fadeIn 0.3s ease;
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-50%) translateY(1rem); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
`;
document.head.appendChild(style);
