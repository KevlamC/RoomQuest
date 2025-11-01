// Data Analytics App - Interactive UI (No Backend)
// This file provides UI interactivity without any backend functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupFileUpload();
    setupAIChat();
    setupNavigationMenu();
    setupChartTypeSelection();
    setupFilters();
    setupVizCards();
    setupDragAndDrop();
}

// File Upload Functionality
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            handleFiles(e.target.files);
        });
    }

    if (uploadArea) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight upload area when dragging
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('drag-over');
            }, false);
        });

        // Handle dropped files
        uploadArea.addEventListener('drop', function(e) {
            const files = e.dataTransfer.files;
            handleFiles(files);
        }, false);
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleFiles(files) {
    if (files.length === 0) return;

    const fileList = Array.from(files);
    const dataSourceList = document.querySelector('.data-source-list');
    
    fileList.forEach(file => {
        // Validate file size (max 50MB)
        if (file.size > 50 * 1024 * 1024) {
            showToast(`File ${file.name} is too large. Maximum size is 50MB.`, 'error');
            return;
        }

        // Validate file type
        const validTypes = ['csv', 'xlsx', 'xls', 'json', 'sql'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        if (!validTypes.includes(fileExtension)) {
            showToast(`File type .${fileExtension} is not supported.`, 'error');
            return;
        }

        // Add file to data sources list
        addDataSource(file.name, fileExtension);
        showToast(`${file.name} uploaded successfully!`, 'success');
    });
}

function addDataSource(fileName, fileType) {
    const dataSourceList = document.querySelector('.data-source-list');
    if (!dataSourceList) return;

    const icons = {
        'csv': 'fa-file-csv',
        'xlsx': 'fa-file-excel',
        'xls': 'fa-file-excel',
        'json': 'fa-file-alt',
        'sql': 'fa-database'
    };

    const newSource = document.createElement('div');
    newSource.className = 'data-source-item';
    newSource.innerHTML = `
        <i class="fas ${icons[fileType] || 'fa-file'}"></i>
        <span>${fileName}</span>
        <button class="btn-remove"><i class="fas fa-times"></i></button>
    `;

    // Add click event to activate
    newSource.addEventListener('click', function(e) {
        if (!e.target.closest('.btn-remove')) {
            document.querySelectorAll('.data-source-item').forEach(item => {
                item.classList.remove('active');
            });
            newSource.classList.add('active');
        }
    });

    // Add remove functionality
    const removeBtn = newSource.querySelector('.btn-remove');
    removeBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        newSource.remove();
        showToast(`${fileName} removed`, 'info');
    });

    dataSourceList.appendChild(newSource);
}

// AI Chat Functionality
function setupAIChat() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const suggestionChips = document.querySelectorAll('.suggestion-chip');

    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', () => sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Handle suggestion chips
    suggestionChips.forEach(chip => {
        chip.addEventListener('click', function() {
            const text = this.textContent.trim();
            if (chatInput) {
                chatInput.value = `Create a ${text.split(' ')[1]} for my data`;
                sendMessage();
            }
        });
    });
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatInput || !chatMessages) return;
    
    const message = chatInput.value.trim();
    if (message === '') return;

    // Add user message
    addChatMessage(message, 'user');
    chatInput.value = '';

    // Simulate AI response after a delay
    setTimeout(() => {
        const responses = [
            "I'll create that visualization for you right away! Here's a preview of what I'm generating...",
            "Great idea! I'm analyzing your data to create the perfect chart. This will take just a moment...",
            "Perfect! Let me process your data and generate that visualization...",
            "I understand what you need. I'm creating a custom visualization based on your data...",
            "Excellent request! I'm generating your visualization with the latest insights from your data..."
        ];
        const randomResponse = responses[Math.floor(Math.random() * responses.length)];
        addChatMessage(randomResponse, 'ai');
        
        // Simulate visualization creation
        setTimeout(() => {
            showToast('New visualization created!', 'success');
        }, 2000);
    }, 800);
}

function addChatMessage(text, type) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}-message`;
    
    const avatarIcon = type === 'ai' ? 'fa-robot' : 'fa-user';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${avatarIcon}"></i>
        </div>
        <div class="message-content">
            <p>${text}</p>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Navigation Menu
function setupNavigationMenu() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            const page = this.getAttribute('href').substring(1);
            showToast(`Navigated to ${page}`, 'info');
        });
    });
}

// Chart Type Selection
function setupChartTypeSelection() {
    const chartTypeBtns = document.querySelectorAll('.chart-type-btn');
    
    chartTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            chartTypeBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const chartType = this.getAttribute('title');
            showToast(`Selected ${chartType}`, 'info');
        });
    });
}

// Filters
function setupFilters() {
    const filterSelect = document.querySelector('.filter-select');
    const checkboxes = document.querySelectorAll('.checkbox-label input[type="checkbox"]');
    const applyBtn = document.querySelector('.btn-secondary.btn-full');

    if (filterSelect) {
        filterSelect.addEventListener('change', function() {
            console.log('Date range changed:', this.value);
        });
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log('Filter changed:', this.parentElement.textContent.trim(), this.checked);
        });
    });

    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            showToast('Filters applied successfully!', 'success');
        });
    }
}

// Visualization Cards
function setupVizCards() {
    const vizCards = document.querySelectorAll('.viz-card:not(.add-viz-card)');
    
    vizCards.forEach(card => {
        const downloadBtn = card.querySelector('.viz-actions .btn-icon[title="Download"]');
        const shareBtn = card.querySelector('.viz-actions .btn-icon[title="Share"]');
        const moreBtn = card.querySelector('.viz-actions .btn-icon[title="More"]');

        if (downloadBtn) {
            downloadBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const vizName = card.querySelector('.viz-header h3').textContent;
                showToast(`Downloading ${vizName}...`, 'success');
            });
        }

        if (shareBtn) {
            shareBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const vizName = card.querySelector('.viz-header h3').textContent;
                showToast(`Share link copied for ${vizName}!`, 'success');
            });
        }

        if (moreBtn) {
            moreBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                showToast('More options coming soon!', 'info');
            });
        }
    });

    // Add new visualization card
    const addVizCard = document.querySelector('.add-viz-card');
    if (addVizCard) {
        addVizCard.addEventListener('click', function() {
            showToast('Upload data or use AI chat to create a new visualization!', 'info');
            // Scroll to upload section
            document.querySelector('.upload-section').scrollIntoView({ behavior: 'smooth' });
        });
    }
}

// View Controls
function setupViewControls() {
    const viewBtns = document.querySelectorAll('.view-btn');
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const viewType = this.getAttribute('title');
            showToast(`Changed to ${viewType}`, 'info');
        });
    });
}

// Drag and Drop for Data Sources
function setupDragAndDrop() {
    // Setup existing data source items
    const dataSourceItems = document.querySelectorAll('.data-source-item');
    
    dataSourceItems.forEach(item => {
        const removeBtn = item.querySelector('.btn-remove');
        
        item.addEventListener('click', function(e) {
            if (!e.target.closest('.btn-remove')) {
                dataSourceItems.forEach(i => i.classList.remove('active'));
                item.classList.add('active');
            }
        });

        if (removeBtn) {
            removeBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                const fileName = item.querySelector('span').textContent;
                item.remove();
                showToast(`${fileName} removed`, 'info');
            });
        }
    });
}

// Toast Notification System
function showToast(message, type = 'info') {
    // Remove existing toast if any
    const existingToast = document.querySelector('.toast');
    if (existingToast) {
        existingToast.remove();
    }

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        info: 'fa-info-circle',
        warning: 'fa-exclamation-triangle'
    };

    const colors = {
        success: '#10b981',
        error: '#ef4444',
        info: '#667eea',
        warning: '#f59e0b'
    };

    toast.innerHTML = `
        <i class="fas ${icons[type] || icons.info}" style="color: ${colors[type] || colors.info}; font-size: 1.25rem;"></i>
        <span style="color: #1f2937; font-weight: 500;">${message}</span>
    `;

    document.body.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInUp 0.3s ease reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

// User Profile Click
document.querySelector('.user-profile')?.addEventListener('click', function() {
    showToast('Profile settings coming soon!', 'info');
});

// Notification Bell Click
document.querySelector('.btn-icon[title="Notifications"]')?.addEventListener('click', function(e) {
    e.stopPropagation();
    showToast('You have 3 new notifications', 'info');
});

// Initialize view controls
setupViewControls();

// Add animation to stats cards on scroll
function animateOnScroll() {
    const statCards = document.querySelectorAll('.stat-card');
    const vizCards = document.querySelectorAll('.viz-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                
                setTimeout(() => {
                    entry.target.style.transition = 'all 0.5s ease';
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, 100);
            }
        });
    }, { threshold: 0.1 });

    [...statCards, ...vizCards].forEach(card => {
        observer.observe(card);
    });
}

animateOnScroll();

// Console welcome message
console.log('%c DataViz AI ', 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 20px; padding: 10px; border-radius: 5px;');
console.log('%c This is a design prototype with no backend functionality ', 'color: #667eea; font-size: 12px;');
console.log('%c All interactions are UI-only simulations ', 'color: #666; font-size: 11px;');
