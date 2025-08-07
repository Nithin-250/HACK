// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// Global state
let authToken = localStorage.getItem('authToken');
let currentUser = localStorage.getItem('currentUser');

// DOM Elements
const authModal = document.getElementById('authModal');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn');
const mainContent = document.getElementById('mainContent');
const userInfo = document.getElementById('userInfo');
const usernameSpan = document.getElementById('username');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    
    if (authToken && currentUser) {
        showMainContent();
    } else {
        showLoginButton();
    }
});

function initializeApp() {
    // Set current timestamp for transaction form
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 16);
    document.getElementById('timestamp').value = timestamp;
}

function setupEventListeners() {
    // Auth modal events
    document.querySelector('.close').addEventListener('click', closeAuthModal);
    document.getElementById('authToggleLink').addEventListener('click', toggleAuthForm);
    
    // Auth form events
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('signupForm').addEventListener('submit', handleSignup);
    
    // Header events
    loginBtn.addEventListener('click', openAuthModal);
    logoutBtn.addEventListener('click', handleLogout);
    
    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });
    
    // Transaction form
    document.getElementById('transactionForm').addEventListener('submit', handleTransactionSubmit);
    
    // Refresh buttons
    document.getElementById('refreshHistory').addEventListener('click', loadTransactionHistory);
    document.getElementById('refreshFlagged').addEventListener('click', loadFlaggedTransactions);
    document.getElementById('refreshBlacklist').addEventListener('click', loadBlacklist);
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === authModal) {
            closeAuthModal();
        }
    });
}

// Authentication Functions
function openAuthModal() {
    authModal.style.display = 'block';
}

function closeAuthModal() {
    authModal.style.display = 'none';
    resetAuthForms();
}

function toggleAuthForm() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const authTitle = document.getElementById('authTitle');
    const authToggleText = document.getElementById('authToggleText');
    const authToggleLink = document.getElementById('authToggleLink');
    
    if (loginForm.style.display !== 'none') {
        // Switch to signup
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        authTitle.textContent = 'Sign Up';
        authToggleText.innerHTML = 'Already have an account? <a href="#" id="authToggleLink">Sign in</a>';
        document.getElementById('authToggleLink').addEventListener('click', toggleAuthForm);
    } else {
        // Switch to login
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        authTitle.textContent = 'Sign In';
        authToggleText.innerHTML = 'Don\'t have an account? <a href="#" id="authToggleLink">Sign up</a>';
        document.getElementById('authToggleLink').addEventListener('click', toggleAuthForm);
    }
}

function resetAuthForms() {
    document.getElementById('loginForm').reset();
    document.getElementById('signupForm').reset();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = username;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', currentUser);
            
            showToast('Login successful!', 'success');
            closeAuthModal();
            showMainContent();
        } else {
            showToast(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    const username = document.getElementById('signupUsername').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Account created successfully! Please sign in.', 'success');
            toggleAuthForm(); // Switch to login form
        } else {
            showToast(data.detail || 'Signup failed', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    showLoginButton();
    showToast('Logged out successfully', 'info');
}

function showMainContent() {
    mainContent.style.display = 'block';
    loginBtn.style.display = 'none';
    userInfo.style.display = 'flex';
    usernameSpan.textContent = currentUser;
    
    // Load initial data
    loadTransactionHistory();
    loadFlaggedTransactions();
    loadBlacklist();
}

function showLoginButton() {
    mainContent.style.display = 'none';
    loginBtn.style.display = 'block';
    userInfo.style.display = 'none';
}

// Tab Navigation
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// Transaction Functions
async function handleTransactionSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const transactionData = {
        transaction_id: document.getElementById('transactionId').value,
        timestamp: document.getElementById('timestamp').value.replace('T', ' ') + ':00',
        amount: parseFloat(document.getElementById('amount').value),
        location: document.getElementById('location').value,
        card_type: document.getElementById('cardType').value,
        currency: document.getElementById('currency').value,
        recipient_account_number: document.getElementById('recipientAccount').value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/check_fraud`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`,
            },
            body: JSON.stringify(transactionData),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayTransactionResult(data);
            document.getElementById('transactionForm').reset();
            initializeApp(); // Reset timestamp
            
            if (data.is_fraud) {
                showToast('Fraudulent transaction detected!', 'warning');
            } else {
                showToast('Transaction processed successfully', 'success');
            }
        } else {
            showToast(data.detail || 'Error processing transaction', 'error');
        }
    } catch (error) {
        console.error('Transaction error:', error);
        showToast('Network error. Please try again.', 'error');
    }
}

function displayTransactionResult(data) {
    const resultDiv = document.getElementById('transactionResult');
    const resultContent = document.getElementById('resultContent');
    
    const isfraud = data.is_fraud;
    const riskLevel = data.risk_score >= 70 ? 'high' : data.risk_score >= 30 ? 'medium' : 'low';
    
    resultContent.innerHTML = `
        <div class="result-header ${isfraud ? 'result-fraud' : 'result-safe'}">
            <div>
                <h4>
                    <i class="fas ${isfraud ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                    ${isfraud ? 'FRAUDULENT TRANSACTION' : 'TRANSACTION SAFE'}
                </h4>
                <p>Transaction ID: ${data.transaction_id}</p>
            </div>
            <div class="risk-score">
                <span>Risk Score: ${data.risk_score}%</span>
                <div class="risk-meter">
                    <div class="risk-fill risk-${riskLevel}" style="width: ${data.risk_score}%"></div>
                </div>
            </div>
        </div>
        
        <div class="result-details">
            <div class="result-item">
                <strong>Amount:</strong>
                <span>${data.currency} ${data.amount.toLocaleString()}</span>
            </div>
            <div class="result-item">
                <strong>Location:</strong>
                <span>${data.location}</span>
            </div>
            <div class="result-item">
                <strong>Card Type:</strong>
                <span>${data.card_type}</span>
            </div>
            <div class="result-item">
                <strong>Recipient Account:</strong>
                <span>${data.recipient_account_number}</span>
            </div>
            <div class="result-item">
                <strong>Timestamp:</strong>
                <span>${data.timestamp}</span>
            </div>
        </div>
        
        ${isfraud && data.fraud_reasons.length > 0 ? `
            <div class="fraud-reasons">
                <h4><i class="fas fa-exclamation-triangle"></i> Fraud Indicators:</h4>
                <ul>
                    ${data.fraud_reasons.map(reason => `<li>${reason}</li>`).join('')}
                </ul>
            </div>
        ` : ''}
    `;
    
    resultDiv.style.display = 'block';
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Data Loading Functions
async function loadTransactionHistory() {
    const container = document.getElementById('transactionHistory');
    container.innerHTML = '<div class="loading">Loading transactions...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/transactions`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayTransactionHistory(data.transactions);
        } else {
            container.innerHTML = '<div class="empty-state"><h3>Error loading transactions</h3></div>';
        }
    } catch (error) {
        console.error('Error loading transactions:', error);
        container.innerHTML = '<div class="empty-state"><h3>Network error</h3></div>';
    }
}

function displayTransactionHistory(transactions) {
    const container = document.getElementById('transactionHistory');
    
    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-receipt"></i>
                <h3>No transactions found</h3>
                <p>Start by checking your first transaction</p>
            </div>
        `;
        return;
    }
    
    const tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Transaction ID</th>
                    <th>Amount</th>
                    <th>Location</th>
                    <th>Card Type</th>
                    <th>Timestamp</th>
                    <th>Status</th>
                    <th>Risk Score</th>
                </tr>
            </thead>
            <tbody>
                ${transactions.map(t => `
                    <tr>
                        <td>${t.transaction_id}</td>
                        <td>${t.currency} ${t.amount.toLocaleString()}</td>
                        <td>${t.location}</td>
                        <td>${t.card_type}</td>
                        <td>${new Date(t.checked_at).toLocaleString()}</td>
                        <td>
                            <span class="status-badge ${t.is_fraud ? 'status-fraud' : 'status-safe'}">
                                ${t.is_fraud ? 'Fraud' : 'Safe'}
                            </span>
                        </td>
                        <td>${t.risk_score}%</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

async function loadFlaggedTransactions() {
    const container = document.getElementById('flaggedTransactions');
    container.innerHTML = '<div class="loading">Loading flagged transactions...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/flagged_transactions`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayFlaggedTransactions(data.flagged_transactions);
        } else {
            container.innerHTML = '<div class="empty-state"><h3>Error loading flagged transactions</h3></div>';
        }
    } catch (error) {
        console.error('Error loading flagged transactions:', error);
        container.innerHTML = '<div class="empty-state"><h3>Network error</h3></div>';
    }
}

function displayFlaggedTransactions(transactions) {
    const container = document.getElementById('flaggedTransactions');
    
    if (transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-shield-alt"></i>
                <h3>No flagged transactions</h3>
                <p>Great! No fraudulent activity detected</p>
            </div>
        `;
        return;
    }
    
    const tableHTML = `
        <table class="table">
            <thead>
                <tr>
                    <th>Transaction ID</th>
                    <th>Amount</th>
                    <th>Location</th>
                    <th>Recipient Account</th>
                    <th>Risk Score</th>
                    <th>Fraud Reasons</th>
                    <th>Flagged At</th>
                </tr>
            </thead>
            <tbody>
                ${transactions.map(t => `
                    <tr>
                        <td>${t.transaction_id}</td>
                        <td>${t.currency} ${t.amount.toLocaleString()}</td>
                        <td>${t.location}</td>
                        <td>${t.recipient_account_number}</td>
                        <td><span class="status-badge status-fraud">${t.risk_score}%</span></td>
                        <td>
                            <ul style="margin: 0; padding-left: 1rem; font-size: 0.8rem;">
                                ${t.fraud_reasons.map(reason => `<li>${reason}</li>`).join('')}
                            </ul>
                        </td>
                        <td>${new Date(t.checked_at).toLocaleString()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = tableHTML;
}

async function loadBlacklist() {
    const container = document.getElementById('blacklistContent');
    container.innerHTML = '<div class="loading">Loading blacklist...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/blacklist`, {
            headers: {
                'Authorization': `Bearer ${authToken}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBlacklist(data.blacklist);
        } else {
            container.innerHTML = '<div class="empty-state"><h3>Error loading blacklist</h3></div>';
        }
    } catch (error) {
        console.error('Error loading blacklist:', error);
        container.innerHTML = '<div class="empty-state"><h3>Network error</h3></div>';
    }
}

function displayBlacklist(blacklist) {
    const container = document.getElementById('blacklistContent');
    
    if (blacklist.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-ban"></i>
                <h3>No blacklisted items</h3>
                <p>The blacklist is currently empty</p>
            </div>
        `;
        return;
    }
    
    const blacklistHTML = blacklist.map(item => `
        <div class="blacklist-item fade-in">
            <div>
                <div class="blacklist-type">${item.type}</div>
                <div class="blacklist-value">${item.value}</div>
                ${item.reason ? `<div style="font-size: 0.8rem; color: #6c757d; margin-top: 0.25rem;">${item.reason}</div>` : ''}
            </div>
            <div class="blacklist-date">
                Added: ${new Date(item.added_at).toLocaleDateString()}
            </div>
        </div>
    `).join('');
    
    container.innerHTML = blacklistHTML;
}

// Toast Notification System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas ${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        case 'info': return 'fa-info-circle';
        default: return 'fa-info-circle';
    }
}