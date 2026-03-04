// 全局变量
let returnsChart = null;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    updateTime();
    setInterval(updateTime, 1000);

    loadStatus();
    loadHoldings();
    loadPerformance();

    // 定期刷新数据
    setInterval(refreshData, 30000); // 每30秒刷新一次
});

// 更新时间
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeStr;
}

// 加载系统状态
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // 更新总资金
        document.getElementById('total-capital').textContent =
            '¥' + data.total_capital.toLocaleString();

        // 更新各层信息
        updateLayerInfo('layer1', data.layers.layer1);
        updateLayerInfo('layer2', data.layers.layer2);
        updateLayerInfo('layer3', data.layers.layer3);

    } catch (error) {
        console.error('加载状态失败:', error);
        showToast('加载状态失败', 'error');
    }
}

// 更新层级信息
function updateLayerInfo(layerId, data) {
    if (layerId === 'layer3') {
        document.getElementById(`${layerId}-position`).textContent =
            (data.position * 100).toFixed(0);
    } else {
        document.getElementById(`${layerId}-holdings`).textContent =
            data.holdings_count;
    }

    document.getElementById(`${layerId}-capital`).textContent =
        data.capital.toLocaleString();
}

// 加载持仓信息
async function loadHoldings() {
    try {
        const response = await fetch('/api/holdings');
        const data = await response.json();

        // 更新基石层持仓
        updateHoldingsList('layer1-holdings-list', data.layer1);

        // 更新轮动层持仓
        updateHoldingsList('layer2-holdings-list', data.layer2);

        // 更新择时层状态
        const layer3Status = document.getElementById('layer3-status');
        layer3Status.innerHTML = `
            <div class="holding-item">
                <span class="code">当前仓位</span>
                <span class="weight">${data.layer3.position.toFixed(1)}%</span>
            </div>
        `;

    } catch (error) {
        console.error('加载持仓失败:', error);
    }
}

// 更新持仓列表
function updateHoldingsList(elementId, holdings) {
    const container = document.getElementById(elementId);

    if (!holdings || holdings.length === 0) {
        container.innerHTML = '<p class="empty">暂无持仓</p>';
        return;
    }

    container.innerHTML = holdings.map(h => `
        <div class="holding-item">
            <span class="code">${h.code}</span>
            <span class="weight">${h.weight.toFixed(2)}%</span>
        </div>
    `).join('');
}

// 加载性能数据
async function loadPerformance() {
    try {
        const response = await fetch('/api/performance');
        const data = await response.json();

        // 更新性能指标
        document.getElementById('total-return').textContent =
            (data.metrics.total_return >= 0 ? '+' : '') +
            data.metrics.total_return.toFixed(2) + '%';
        document.getElementById('sharpe-ratio').textContent =
            data.metrics.sharpe_ratio.toFixed(2);
        document.getElementById('max-drawdown').textContent =
            data.metrics.max_drawdown.toFixed(2) + '%';

        // 绘制收益曲线
        drawReturnsChart(data.dates, data.cumulative_returns);

    } catch (error) {
        console.error('加载性能数据失败:', error);
    }
}

// 绘制收益曲线
function drawReturnsChart(dates, returns) {
    const ctx = document.getElementById('returnsChart').getContext('2d');

    if (returnsChart) {
        returnsChart.destroy();
    }

    returnsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: '累计收益率',
                data: returns.map(r => (r * 100).toFixed(2)),
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return '收益率: ' + context.parsed.y.toFixed(2) + '%';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// 运行全部策略
async function runAllLayers() {
    showToast('开始运行全部策略...', 'info');
    addLog('开始运行全部策略...', 'info');

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success) {
            showToast('全部策略运行完成！', 'success');
            addLog('✓ 全部策略运行完成', 'success');

            // 刷新数据
            setTimeout(refreshData, 1000);
        } else {
            showToast('运行失败: ' + data.message, 'error');
            addLog('✗ 运行失败: ' + data.message, 'error');
        }

    } catch (error) {
        console.error('运行失败:', error);
        showToast('运行失败: ' + error.message, 'error');
        addLog('✗ 运行失败: ' + error.message, 'error');
    }
}

// 运行单个层级
async function runLayer(layerName) {
    const layerNames = {
        'layer1': '基石层',
        'layer2': '轮动层',
        'layer3': '择时层'
    };

    showToast(`开始运行${layerNames[layerName]}...`, 'info');
    addLog(`开始运行${layerNames[layerName]}...`, 'info');

    try {
        const response = await fetch(`/api/run_layer/${layerName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });

        const data = await response.json();

        if (data.success) {
            showToast(`${layerNames[layerName]}运行完成！`, 'success');
            addLog(`✓ ${layerNames[layerName]}运行完成`, 'success');

            // 刷新数据
            setTimeout(refreshData, 1000);
        } else {
            showToast(`运行失败: ${data.message}`, 'error');
            addLog(`✗ 运行失败: ${data.message}`, 'error');
        }

    } catch (error) {
        console.error('运行失败:', error);
        showToast('运行失败: ' + error.message, 'error');
        addLog('✗ 运行失败: ' + error.message, 'error');
    }
}

// 刷新数据
async function refreshData() {
    showToast('刷新数据中...', 'info');

    await Promise.all([
        loadStatus(),
        loadHoldings(),
        loadPerformance()
    ]);

    showToast('数据刷新完成', 'success');
}

// 显示Toast消息
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// 添加日志
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');

    // 移除空状态
    const empty = logContainer.querySelector('.empty');
    if (empty) {
        empty.remove();
    }

    const now = new Date().toLocaleTimeString('zh-CN');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${now}] ${message}`;

    logContainer.insertBefore(logEntry, logContainer.firstChild);

    // 限制日志数量
    const logs = logContainer.querySelectorAll('.log-entry');
    if (logs.length > 50) {
        logs[logs.length - 1].remove();
    }
}
