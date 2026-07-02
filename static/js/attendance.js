/**
 * ATTENDANCE PAGE - JavaScript Functionality
 * Handles filtering, sorting, pagination, and UI interactions
 */

// ============================================
// GLOBAL STATE
// ============================================

const state = {
    currentPage: 1,
    itemsPerPage: 10,
    sortColumn: 'date',
    sortOrder: 'desc',
    filteredData: [],
    originalData: [],
    searchTerm: '',
    statusFilter: '',
    dateFilter: ''
};

// ============================================
// INITIALIZATION
// ============================================

function initializeAttendance() {
    // Get all table rows
    const rows = document.querySelectorAll('#attendanceBody .attendance-row');
    state.originalData = Array.from(rows);
    state.filteredData = [...state.originalData];
    
    // Update record count
    updateRecordCount();
    
    // Setup event listeners
    setupFilterListeners();
    setupSortListeners();
    setupPagination();
    setupSearchListener();
    
    // Render initial view
    renderTable();
}

// ============================================
// FILTERING
// ============================================

function setupFilterListeners() {
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', function() {
            state.statusFilter = this.value;
            applyFilters();
        });
    }
    
    // Date filter
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter) {
        dateFilter.addEventListener('change', function() {
            state.dateFilter = this.value;
            applyFilters();
        });
    }
}

function setupSearchListener() {
    const searchInput = document.getElementById('employeeSearch');
    if (searchInput) {
        // Debounce search
        let timeoutId;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                state.searchTerm = this.value.toLowerCase();
                applyFilters();
            }, 300);
        });
    }
}

function applyFilters() {
    const searchTerm = state.searchTerm.toLowerCase();
    const statusFilter = state.statusFilter;
    const dateFilter = state.dateFilter;
    
    state.filteredData = state.originalData.filter(row => {
        // Search filter
        const employeeName = row.dataset.employee || '';
        const matchesSearch = employeeName.includes(searchTerm);
        
        // Status filter
        const status = row.dataset.status || '';
        const matchesStatus = !statusFilter || status === statusFilter;
        
        // Date filter
        const dateCell = row.querySelector('td[data-date]');
        const date = dateCell ? dateCell.dataset.date : '';
        const matchesDate = !dateFilter || date === dateFilter;
        
        return matchesSearch && matchesStatus && matchesDate;
    });
    
    // Reset to first page when filtering
    state.currentPage = 1;
    
    // Update record count
    updateRecordCount();
    
    // Render table
    renderTable();
}

// ============================================
// SORTING
// ============================================

function setupSortListeners() {
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', function() {
            const column = this.dataset.sort;
            
            // Toggle sort order
            if (state.sortColumn === column) {
                state.sortOrder = state.sortOrder === 'asc' ? 'desc' : 'asc';
            } else {
                state.sortColumn = column;
                state.sortOrder = 'asc';
            }
            
            // Update active state
            document.querySelectorAll('.sortable').forEach(th => {
                th.classList.remove('active');
            });
            this.classList.add('active');
            
            // Apply sort
            applySort();
        });
    });
}

function applySort() {
    const column = state.sortColumn;
    const order = state.sortOrder;
    
    state.filteredData.sort((a, b) => {
        let aVal, bVal;
        
        switch(column) {
            case 'employee':
                aVal = a.dataset.employee || '';
                bVal = b.dataset.employee || '';
                break;
            case 'date':
                const aDate = a.querySelector('td[data-date]');
                const bDate = b.querySelector('td[data-date]');
                aVal = aDate ? aDate.dataset.date : '';
                bVal = bDate ? bDate.dataset.date : '';
                break;
            case 'status':
                aVal = a.dataset.status || '';
                bVal = b.dataset.status || '';
                break;
            default:
                aVal = a.dataset[column] || '';
                bVal = b.dataset[column] || '';
        }
        
        // Compare values
        if (aVal < bVal) return order === 'asc' ? -1 : 1;
        if (aVal > bVal) return order === 'asc' ? 1 : -1;
        return 0;
    });
    
    renderTable();
}

// ============================================
// PAGINATION
// ============================================

function setupPagination() {
    const controls = document.getElementById('paginationControls');
    if (controls) {
        controls.addEventListener('click', function(e) {
            const btn = e.target.closest('.pagination-btn');
            if (!btn || btn.classList.contains('disabled')) return;
            
            const page = parseInt(btn.dataset.page);
            if (!isNaN(page)) {
                state.currentPage = page;
                renderTable();
            }
        });
    }
}

function renderPagination() {
    const controls = document.getElementById('paginationControls');
    if (!controls) return;
    
    const total = state.filteredData.length;
    const totalPages = Math.ceil(total / state.itemsPerPage);
    const current = state.currentPage;
    
    if (totalPages <= 1) {
        controls.innerHTML = '';
        return;
    }
    
    let html = '';
    
    // Previous button
    html += `<button class="pagination-btn ${current <= 1 ? 'disabled' : ''}" 
                    data-page="${current - 1}" 
                    ${current <= 1 ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>`;
    
    // Page numbers
    const startPage = Math.max(1, current - 2);
    const endPage = Math.min(totalPages, current + 2);
    
    if (startPage > 1) {
        html += `<button class="pagination-btn" data-page="1">1</button>`;
        if (startPage > 2) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="pagination-btn ${i === current ? 'active' : ''}" 
                        data-page="${i}">${i}</button>`;
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
        html += `<button class="pagination-btn" data-page="${totalPages}">${totalPages}</button>`;
    }
    
    // Next button
    html += `<button class="pagination-btn ${current >= totalPages ? 'disabled' : ''}" 
                    data-page="${current + 1}"
                    ${current >= totalPages ? 'disabled' : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>`;
    
    controls.innerHTML = html;
    
    // Update pagination info
    const start = (current - 1) * state.itemsPerPage + 1;
    const end = Math.min(current * state.itemsPerPage, total);
    
    document.getElementById('startRecord').textContent = total > 0 ? start : 0;
    document.getElementById('endRecord').textContent = end;
    document.getElementById('totalRecords').textContent = total;
}

// ============================================
// TABLE RENDERING
// ============================================

function renderTable() {
    const tbody = document.getElementById('attendanceBody');
    if (!tbody) return;
    
    // Get current page data
    const start = (state.currentPage - 1) * state.itemsPerPage;
    const end = start + state.itemsPerPage;
    const pageData = state.filteredData.slice(start, end);
    
    // Hide all rows first
    state.originalData.forEach(row => {
        row.style.display = 'none';
    });
    
    // Show only filtered rows
    pageData.forEach(row => {
        row.style.display = '';
        row.style.animation = 'fadeIn 0.3s ease';
    });
    
    // Render pagination
    renderPagination();
}

function updateRecordCount() {
    const count = state.filteredData.length;
    const element = document.getElementById('recordCount');
    if (element) {
        element.textContent = count;
    }
}

// ============================================
// EXPORT FUNCTIONALITY
// ============================================

function exportTable() {
    const table = document.getElementById('attendanceTable');
    if (!table) return;
    
    // Create CSV
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const rowData = [];
        const cells = row.querySelectorAll('td, th');
        cells.forEach(cell => {
            // Clean text (remove emojis, extra spaces)
            let text = cell.textContent.trim().replace(/\s+/g, ' ');
            // Handle special cases
            if (cell.querySelector('.badge')) {
                text = cell.querySelector('.badge').textContent.trim();
            }
            rowData.push(`"${text}"`);
        });
        csv.push(rowData.join(','));
    });
    
    // Download CSV
    const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// ============================================
// MODAL FUNCTIONS
// ============================================

function openModal() {
    const modal = document.getElementById('statsModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        loadStats();
    }
}

function closeModal() {
    const modal = document.getElementById('statsModal');
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
}

function loadStats() {
    const body = document.getElementById('statsBody');
    if (!body) return;
    
    const stats = {
        total: attendanceData.totalRecords,
        present: attendanceData.presentCount,
        wfh: attendanceData.wfhCount,
        leave: attendanceData.leaveCount,
        absent: attendanceData.absentCount
    };
    
    // Calculate percentages
    const total = stats.total || 1;
    const presentPercent = (stats.present / total * 100).toFixed(1);
    const wfhPercent = (stats.wfh / total * 100).toFixed(1);
    const leavePercent = (stats.leave / total * 100).toFixed(1);
    const absentPercent = (stats.absent / total * 100).toFixed(1);
    
    body.innerHTML = `
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">✅ Present</span>
                <span class="stat-value">${stats.present}</span>
                <span class="stat-percentage">${presentPercent}%</span>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${presentPercent}%; background: #22c55e;"></div>
                </div>
            </div>
            <div class="stat-item">
                <span class="stat-label">🏡 WFH</span>
                <span class="stat-value">${stats.wfh}</span>
                <span class="stat-percentage">${wfhPercent}%</span>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${wfhPercent}%; background: #3b82f6;"></div>
                </div>
            </div>
            <div class="stat-item">
                <span class="stat-label">🌴 Leave</span>
                <span class="stat-value">${stats.leave}</span>
                <span class="stat-percentage">${leavePercent}%</span>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${leavePercent}%; background: #f59e0b;"></div>
                </div>
            </div>
            <div class="stat-item">
                <span class="stat-label">❌ Absent</span>
                <span class="stat-value">${stats.absent}</span>
                <span class="stat-percentage">${absentPercent}%</span>
                <div class="stat-bar">
                    <div class="stat-bar-fill" style="width: ${absentPercent}%; background: #ef4444;"></div>
                </div>
            </div>
        </div>
        <div class="stats-total">
            <strong>Total Records: ${stats.total}</strong>
        </div>
    `;
}

// ============================================
// DELETE CONFIRMATION
// ============================================

function confirmDelete(event) {
    if (!confirm('⚠️ Are you sure you want to delete this attendance record?\n\nThis action cannot be undone.')) {
        event.preventDefault();
        return false;
    }
    return true;
}

// ============================================
// KEYBOARD SHORTCUTS
// ============================================

document.addEventListener('keydown', function(e) {
    // ESC to close modal
    if (e.key === 'Escape') {
        closeModal();
    }
    
    // Ctrl+F to focus search
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        document.getElementById('employeeSearch')?.focus();
    }
});

// ============================================
// CLOSE MODAL ON BACKGROUND CLICK
// ============================================

document.addEventListener('click', function(e) {
    const modal = document.getElementById('statsModal');
    if (modal && e.target === modal) {
        closeModal();
    }
});

// ============================================
// EXPOSE FUNCTIONS GLOBALLY
// ============================================

window.initializeAttendance = initializeAttendance;
window.exportTable = exportTable;
window.openModal = openModal;
window.closeModal = closeModal;
window.confirmDelete = confirmDelete;