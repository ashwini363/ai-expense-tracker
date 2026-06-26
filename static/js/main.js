document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('date').valueAsDate = new Date();
    document.getElementById('incomeDate').valueAsDate = new Date();
    fetchAllData();

    // Event Listeners
    document.getElementById('addExpenseForm').addEventListener('submit', handleAddExpense);
    document.getElementById('addIncomeForm').addEventListener('submit', handleAddIncome);
    document.getElementById('addGoalForm').addEventListener('submit', handleAddGoal);
    document.getElementById('addBudgetForm').addEventListener('submit', handleAddBudget);
    document.getElementById('addFundsForm').addEventListener('submit', handleAddFunds);
    
    // Chat Event Listeners
    document.getElementById('sendChatBtn').addEventListener('click', handleChatSubmit);
    document.getElementById('chatInput').addEventListener('keypress', function (e) {
        if (e.key === 'Enter') handleChatSubmit();
    });

    // Tab Navigation
    const menuLinks = document.querySelectorAll('#sidebarMenu a');
    menuLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            menuLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const targetId = link.getAttribute('data-target');
            document.querySelectorAll('.tab-view').forEach(view => {
                view.classList.remove('active');
            });
            document.getElementById(targetId).classList.add('active');
            
            const headerActions = document.querySelector('.header-actions');
            const pageTitle = document.getElementById('pageTitle');
            const pageSubtitle = document.getElementById('pageSubtitle');
            
            if (targetId === 'view-dashboard') {
                headerActions.style.display = 'flex';
                pageTitle.innerText = "Welcome back 👋";
                pageSubtitle.innerText = "Here's your financial overview";
            } else if (targetId === 'view-transactions') {
                headerActions.style.display = 'flex';
                pageTitle.innerText = "Transactions 💸";
                pageSubtitle.innerText = "Your complete financial ledger";
            } else if (targetId === 'view-goals') {
                headerActions.style.display = 'none';
                pageTitle.innerText = "Savings Goals 🎯";
                pageSubtitle.innerText = "Track your long-term progress";
            } else if (targetId === 'view-budgets') {
                headerActions.style.display = 'none';
                pageTitle.innerText = "Budgets & Limits ⚖️";
                pageSubtitle.innerText = "Manage limits to get smart email alerts";
            }
        });
    });
});

function fetchAllData() {
    fetchSummary();
    fetchExpensesAndIncome();
    fetchGoals();
    fetchBudgets();
}

let categoryChart = null;
const categoryIcons = { 'Food': 'fa-utensils', 'Transport': 'fa-car', 'Shopping': 'fa-bag-shopping', 'Utilities': 'fa-bolt', 'Entertainment': 'fa-gamepad', 'Other': 'fa-tag', 'Auto': 'fa-wand-magic-sparkles' };
const categoryColors = { 'Food': '#ef4444', 'Transport': '#3b82f6', 'Shopping': '#10b981', 'Utilities': '#f59e0b', 'Entertainment': '#8b5cf6', 'Other': '#64748b', 'Auto': '#8b5cf6' };

// --- Modals ---
function openAddModal() { document.getElementById('addExpenseModal').style.display = 'flex'; }
function closeAddModal() { document.getElementById('addExpenseModal').style.display = 'none'; }

function openIncomeModal() { document.getElementById('addIncomeModal').style.display = 'flex'; }
function closeIncomeModal() { document.getElementById('addIncomeModal').style.display = 'none'; }

function openGoalModal() { document.getElementById('addGoalModal').style.display = 'flex'; }
function closeGoalModal() { document.getElementById('addGoalModal').style.display = 'none'; }

function openBudgetModal() { document.getElementById('addBudgetModal').style.display = 'flex'; }
function closeBudgetModal() { document.getElementById('addBudgetModal').style.display = 'none'; }

function openFundsModal(goalId) { 
    document.getElementById('fundGoalId').value = goalId;
    document.getElementById('addFundsModal').style.display = 'flex'; 
}
function closeFundsModal() { document.getElementById('addFundsModal').style.display = 'none'; }

window.onclick = function(event) {
    if (event.target == document.getElementById('addExpenseModal')) closeAddModal();
    if (event.target == document.getElementById('addIncomeModal')) closeIncomeModal();
    if (event.target == document.getElementById('addGoalModal')) closeGoalModal();
    if (event.target == document.getElementById('addBudgetModal')) closeBudgetModal();
    if (event.target == document.getElementById('addFundsModal')) closeFundsModal();
}

function formatCurrency(amount) { return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount); }
function formatDate(dateString) { return new Date(dateString).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' }); }

// --- API Calls ---
async function fetchExpensesAndIncome() {
    try {
        const [expRes, incRes] = await Promise.all([
            fetch('/api/expenses/'),
            fetch('/api/income/')
        ]);
        const expenses = await expRes.json();
        const incomes = await incRes.json();
        
        const dashList = document.getElementById('dashboardTransactionsList');
        const allList = document.getElementById('allTransactionsList');
        dashList.innerHTML = ''; allList.innerHTML = '';
        
        let combined = [];
        expenses.forEach(e => combined.push({...e, type: 'expense'}));
        incomes.forEach(i => combined.push({...i, type: 'income'}));
        
        // Sort by date desc
        combined.sort((a, b) => new Date(b.date) - new Date(a.date));

        if (combined.length === 0) {
            dashList.innerHTML = '<p class="empty-state">No transactions yet.</p>';
            allList.innerHTML = '<p class="empty-state">No transactions yet.</p>';
            return;
        }

        combined.forEach(item => {
            const isExpense = item.type === 'expense';
            const iconClass = isExpense ? (categoryIcons[item.category] || categoryIcons['Other']) : 'fa-arrow-down';
            const iconColorClass = isExpense ? '' : 'style="color: var(--success); background: rgba(16, 185, 129, 0.1);"';
            const amountColor = isExpense ? '' : 'style="color: var(--success);"';
            const deleteFunc = isExpense ? `deleteExpense(${item.id})` : `deleteIncome(${item.id})`;
            
            const html = `
                <div class="transaction-item">
                    <div class="tx-info">
                        <div class="tx-icon" ${iconColorClass}><i class="fa-solid ${iconClass}"></i></div>
                        <div class="tx-details">
                            <h4>${isExpense ? item.category : 'Income'}</h4>
                            <p>${item.description || 'No description'} • ${formatDate(item.date)}</p>
                        </div>
                    </div>
                    <div>
                        <span class="tx-amount" ${amountColor}>${isExpense ? '-' : '+'}${formatCurrency(item.amount)}</span>
                        <button class="tx-delete" onclick="${deleteFunc}" title="Delete"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
            `;
            allList.innerHTML += html;
            dashList.innerHTML += html;
        });
    } catch (error) { console.error("Error:", error); }
}

async function fetchSummary() {
    try {
        const response = await fetch('/api/expenses/summary');
        const summary = await response.json();
        document.getElementById('bankBalance').innerText = formatCurrency(summary.bank_balance);
        document.getElementById('totalIncome').innerText = formatCurrency(summary.total_income);
        document.getElementById('totalAmount').innerText = formatCurrency(summary.total);
        updateChart(summary.by_category);
    } catch (error) { console.error("Error:", error); }
}

async function fetchGoals() {
    try {
        const response = await fetch('/api/goals/');
        const goals = await response.json();
        const grid = document.getElementById('goalsGrid');
        grid.innerHTML = '';
        if(goals.length === 0) {
            grid.innerHTML = '<p class="empty-state" style="grid-column: span 12;">No goals created yet. Click "Create New Goal" to start.</p>';
            return;
        }
        goals.forEach(goal => {
            const percentage = Math.min(100, Math.round((goal.current_amount / goal.target_amount) * 100));
            grid.innerHTML += `
                <div class="goal-card">
                    <button class="goal-delete" onclick="deleteGoal(${goal.id})"><i class="fa-solid fa-trash"></i></button>
                    <h3>${goal.name}</h3>
                    <div class="target">${formatCurrency(goal.current_amount)} <span style="font-size:1rem; color:var(--text-secondary);">/ ${formatCurrency(goal.target_amount)}</span></div>
                    
                    <div style="width: 100%; background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin: 10px 0; overflow:hidden;">
                        <div style="width: ${percentage}%; background: var(--primary-color); height: 100%; transition: width 0.5s;"></div>
                    </div>
                    
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        ${goal.deadline ? `<div class="deadline"><i class="fa-regular fa-calendar"></i> Target by ${formatDate(goal.deadline)}</div>` : '<div></div>'}
                        <button class="btn btn-secondary" style="padding:4px 8px; font-size:0.8rem;" onclick="openFundsModal(${goal.id})">Add Funds</button>
                    </div>
                </div>
            `;
        });
    } catch (error) { console.error("Error:", error); }
}

async function fetchBudgets() {
    try {
        const response = await fetch('/api/budgets/');
        const limits = await response.json();
        const grid = document.getElementById('budgetsGrid');
        grid.innerHTML = '';
        if(limits.length === 0) {
            grid.innerHTML = '<p class="empty-state" style="grid-column: span 12;">No budget limits set. Click "Set Budget Limit".</p>';
            return;
        }
        limits.forEach(limit => {
            const iconClass = categoryIcons[limit.category] || categoryIcons['Other'];
            grid.innerHTML += `
                <div class="goal-card">
                    <button class="goal-delete" onclick="deleteBudget(${limit.id})"><i class="fa-solid fa-trash"></i></button>
                    <h3 style="display:flex; align-items:center; gap:8px;"><i class="fa-solid ${iconClass}"></i> ${limit.category} Limit</h3>
                    <div class="target" style="color: var(--danger);">${formatCurrency(limit.amount)} <span style="font-size:1rem; color:var(--text-secondary);">/ month</span></div>
                    <p style="font-size:0.85rem; color:var(--text-secondary);">You'll receive email alerts if spending exceeds this.</p>
                </div>
            `;
        });
    } catch (error) { console.error("Error:", error); }
}

// Form Handlers
async function handleAddExpense(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    const ogText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing AI...';
    btn.disabled = true;

    const expense = {
        amount: parseFloat(document.getElementById('amount').value),
        category: "Auto",
        date: document.getElementById('date').value,
        description: document.getElementById('description').value
    };

    try {
        const response = await fetch('/api/expenses/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(expense)
        });
        if (response.ok) {
            closeAddModal(); document.getElementById('addExpenseForm').reset();
            document.getElementById('date').valueAsDate = new Date();
            fetchAllData();
        }
    } catch (error) { alert("Failed to add expense."); } 
    finally { btn.innerHTML = ogText; btn.disabled = false; }
}

async function handleAddIncome(e) {
    e.preventDefault();
    const income = {
        amount: parseFloat(document.getElementById('incomeAmount').value),
        date: document.getElementById('incomeDate').value,
        description: document.getElementById('incomeDesc').value
    };
    try {
        const response = await fetch('/api/income/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(income)
        });
        if (response.ok) {
            closeIncomeModal(); document.getElementById('addIncomeForm').reset();
            document.getElementById('incomeDate').valueAsDate = new Date();
            fetchAllData();
        }
    } catch (error) { alert("Failed to add income."); }
}

async function handleAddGoal(e) {
    e.preventDefault();
    const goal = {
        name: document.getElementById('goalName').value,
        target_amount: parseFloat(document.getElementById('goalAmount').value),
        deadline: document.getElementById('goalDeadline').value || null
    };
    try {
        const response = await fetch('/api/goals/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(goal)
        });
        if (response.ok) {
            closeGoalModal(); document.getElementById('addGoalForm').reset();
            fetchGoals();
        }
    } catch (error) { alert("Failed to add goal."); }
}

async function handleAddBudget(e) {
    e.preventDefault();
    const budget = {
        category: document.getElementById('budgetCategory').value,
        amount: parseFloat(document.getElementById('budgetLimit').value)
    };
    try {
        const response = await fetch('/api/budgets/', {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(budget)
        });
        if (response.ok) {
            closeBudgetModal(); document.getElementById('addBudgetForm').reset();
            fetchBudgets();
        }
    } catch (error) { alert("Failed to add budget limit."); }
}

async function handleAddFunds(e) {
    e.preventDefault();
    const goalId = document.getElementById('fundGoalId').value;
    const data = { amount_to_add: parseFloat(document.getElementById('fundAmount').value) };
    try {
        const response = await fetch(`/api/goals/${goalId}/add_funds`, {
            method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
        });
        if (response.ok) {
            closeFundsModal(); document.getElementById('addFundsForm').reset();
            fetchGoals();
        }
    } catch (error) { alert("Failed to add funds."); }
}

async function deleteExpense(id) { if(confirm("Delete expense?")) { await fetch(`/api/expenses/${id}`, { method: 'DELETE' }); fetchAllData(); } }
async function deleteIncome(id) { if(confirm("Delete income?")) { await fetch(`/api/income/${id}`, { method: 'DELETE' }); fetchAllData(); } }
async function deleteGoal(id) { if(confirm("Delete goal?")) { await fetch(`/api/goals/${id}`, { method: 'DELETE' }); fetchGoals(); } }
async function deleteBudget(id) { if(confirm("Delete budget limit?")) { await fetch(`/api/budgets/${id}`, { method: 'DELETE' }); fetchBudgets(); } }

function updateChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    const labels = categoryData.map(d => d.category);
    const data = categoryData.map(d => d.amount);
    const bgColors = labels.map(l => categoryColors[l] || categoryColors['Other']);

    if (categoryChart) categoryChart.destroy();
    Chart.defaults.color = '#94a3b8'; Chart.defaults.font.family = "'Inter', sans-serif";

    if (data.length === 0) {
        categoryChart = new Chart(ctx, { type: 'doughnut', data: { labels: ['No Data'], datasets: [{ data: [1], backgroundColor: ['#334155'], borderWidth: 0 }] }, options: { cutout: '75%', plugins: { tooltip: { enabled: false }, legend: { display: false } } } });
        return;
    }

    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: bgColors, borderWidth: 0, hoverOffset: 4 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins: { legend: { position: 'right', labels: { color: '#f8fafc', padding: 20, usePointStyle: true, pointStyle: 'circle' } }, tooltip: { backgroundColor: 'rgba(15, 23, 42, 0.9)', titleColor: '#f8fafc', bodyColor: '#f8fafc', padding: 10, cornerRadius: 8, callbacks: { label: function(context) { let label = context.label || ''; if (label) { label += ': '; } if (context.parsed !== null) { label += formatCurrency(context.parsed); } return label; } } } } }
    });
}

async function handleChatSubmit() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;
    appendMessage('user', message); input.value = '';
    const typingId = showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat/', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: message }) });
        const data = await response.json();
        removeTypingIndicator(typingId);
        let formattedResponse = data.response.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
        appendMessage('ai', formattedResponse);
        fetchAllData(); 
    } catch (error) {
        removeTypingIndicator(typingId);
        appendMessage('ai', 'Error communicating with AI. Make sure API key is correct.');
    }
}

function appendMessage(sender, text) {
    const messagesContainer = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    msgDiv.innerHTML = `<div class="message-bubble">${text}</div>`;
    messagesContainer.appendChild(msgDiv); messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messagesContainer = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div'); msgDiv.id = id; msgDiv.className = `message ai-message`;
    msgDiv.innerHTML = `<div class="message-bubble typing-indicator"><span></span><span></span><span></span></div>`;
    messagesContainer.appendChild(msgDiv); messagesContainer.scrollTop = messagesContainer.scrollHeight;
    return id;
}

function removeTypingIndicator(id) { const el = document.getElementById(id); if (el) el.remove(); }
