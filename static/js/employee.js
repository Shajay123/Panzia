// static/js/employee.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // ELEMENTS
    // ============================================
    const searchInput = document.getElementById('searchInput');
    const clearBtn = document.getElementById('clearSearch');
    const departmentFilter = document.getElementById('departmentFilter');
    const statusFilter = document.getElementById('statusFilter');
    const workModeFilter = document.getElementById('workModeFilter');
    const filterBtn = document.getElementById('filterBtn');
    const resetBtn = document.getElementById('resetBtn');
    const resultCount = document.getElementById('resultCount');
    const visibleCount = document.getElementById('visibleCount');
    const totalCount2 = document.getElementById('totalCount2');
    const selectAll = document.getElementById('selectAll');
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const exportBtn = document.getElementById('exportBtn');
    const rows = document.querySelectorAll('.employee-row');
    const tableRows = document.querySelectorAll('#employeeTableBody .employee-row');
    const mobileCards = document.querySelectorAll('#mobileCards .employee-card');

    // ============================================
    // FILTER FUNCTION
    // ============================================
    function filterEmployees() {
        const search = searchInput.value.toLowerCase().trim();
        const department = departmentFilter.value.toLowerCase().trim();
        const status = statusFilter.value.toLowerCase().trim();
        const workMode = workModeFilter.value.toLowerCase().trim();

        let visible = 0;

        // Filter table rows
        tableRows.forEach(row => {
            const name = row.dataset.name || '';
            const email = row.dataset.email || '';
            const id = row.dataset.id || '';
            const rowDepartment = row.dataset.department || '';
            const rowStatus = row.dataset.status || '';
            const rowWorkMode = row.dataset.workmode || '';

            const matchSearch = name.includes(search) || 
                               email.includes(search) || 
                               id.includes(search);
            const matchDepartment = !department || rowDepartment === department;
            const matchStatus = !status || rowStatus === status;
            const matchWorkMode = !workMode || rowWorkMode === workMode;

            const show = matchSearch && matchDepartment && matchStatus && matchWorkMode;
            row.style.display = show ? '' : 'none';
            if (show) visible++;
        });

        // Filter mobile cards
        mobileCards.forEach(card => {
            const name = card.dataset.name || '';
            const cardDepartment = card.dataset.department || '';
            const cardStatus = card.dataset.status || '';
            const cardWorkMode = card.dataset.workmode || '';

            const matchSearch = name.includes(search);
            const matchDepartment = !department || cardDepartment === department;
            const matchStatus = !status || cardStatus === status;
            const matchWorkMode = !workMode || cardWorkMode === workMode;

            const show = matchSearch && matchDepartment && matchStatus && matchWorkMode;
            card.style.display = show ? '' : 'none';
        });

        // Update counts
        if (resultCount) {
            resultCount.textContent = `Showing ${visible} employees`;
        }
        if (visibleCount) {
            visibleCount.textContent = visible;
        }

        // Show/hide clear button
        if (clearBtn) {
            clearBtn.style.display = search ? 'block' : 'none';
        }

        // Update empty state
        const existingEmpty = document.querySelector('.no-results-message');
        if (visible === 0 && tableRows.length > 0) {
            if (!existingEmpty) {
                const emptyMsg = document.createElement('tr');
                emptyMsg.className = 'no-results-message';
                emptyMsg.innerHTML = `
                    <td colspan="10">
                        <div class="empty-state">
                            <div class="empty-icon">🔍</div>
                            <h3>No Results Found</h3>
                            <p>Try adjusting your filters or search terms.</p>
                        </div>
                    </td>
                `;
                document.querySelector('#employeeTableBody').appendChild(emptyMsg);
            }
        } else {
            if (existingEmpty) existingEmpty.remove();
        }
    }

    // ============================================
    // SEARCH WITH DEBOUNCE
    // ============================================
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

    if (searchInput) {
        searchInput.addEventListener('input', debounce(filterEmployees, 300));
        
        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                searchInput.value = '';
                filterEmployees();
                searchInput.focus();
            });
        }

        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                filterEmployees();
                this.blur();
            }
        });
    }

    // ============================================
    // FILTER BUTTONS
    // ============================================
    if (filterBtn) {
        filterBtn.addEventListener('click', filterEmployees);
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            searchInput.value = '';
            departmentFilter.value = '';
            statusFilter.value = '';
            workModeFilter.value = '';
            filterEmployees();
        });
    }

    [departmentFilter, statusFilter, workModeFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', filterEmployees);
        }
    });

    // ============================================
    // SELECT ALL
    // ============================================
    function toggleSelectAll(checked) {
        document.querySelectorAll('.row-checkbox').forEach(cb => {
            cb.checked = checked;
        });
        if (selectAll) selectAll.checked = checked;
        if (selectAllCheckbox) selectAllCheckbox.checked = checked;
    }

    if (selectAll) {
        selectAll.addEventListener('change', function() {
            toggleSelectAll(this.checked);
        });
    }

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            toggleSelectAll(this.checked);
        });
    }

    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.addEventListener('change', function() {
            const allChecked = document.querySelectorAll('.row-checkbox:checked').length === document.querySelectorAll('.row-checkbox').length;
            if (selectAll) selectAll.checked = allChecked;
            if (selectAllCheckbox) selectAllCheckbox.checked = allChecked;
        });
    });

    // ============================================
    // EXPORT FUNCTIONALITY
    // ============================================
    if (exportBtn) {
        exportBtn.addEventListener('click', function() {
            const selected = document.querySelectorAll('.row-checkbox:checked');
            const visibleRows = document.querySelectorAll('#employeeTableBody .employee-row:not([style*="display: none"])');
            
            let rowsToExport = selected.length > 0 ? selected : visibleRows;
            
            if (rowsToExport.length === 0) {
                alert('No employees to export. Please select employees or apply filters.');
                return;
            }

            exportEmployees(rowsToExport);
        });
    }

    function exportEmployees(rowsToExport) {
        let csvContent = 'Name,Email,Employee ID,Department,Designation,Status,Work Mode,Salary,Payroll\n';
        
        rowsToExport.forEach(checkbox => {
            const row = checkbox.closest('.employee-row');
            if (row) {
                const name = row.querySelector('.employee-name')?.textContent?.trim() || '';
                const email = row.querySelector('.employee-email')?.textContent?.trim() || '';
                const id = row.querySelector('.employee-id')?.textContent?.trim() || '';
                const department = row.children[3]?.textContent?.trim() || '';
                const designation = row.children[4]?.textContent?.trim() || '';
                const status = row.querySelector('.status-badge')?.textContent?.trim() || '';
                const workMode = row.querySelector('.work-mode-badge')?.textContent?.trim() || '';
                const salary = row.children[7]?.textContent?.trim()?.replace('₹', '') || '0';
                const payroll = row.querySelector('.badge.payroll')?.textContent?.trim() || 'Disabled';
                
                csvContent += `"${name}","${email}","${id}","${department}","${designation}","${status}","${workMode}","${salary}","${payroll}"\n`;
            }
        });

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `employees_export_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            if (searchInput && document.activeElement !== searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    // ============================================
    // PAGINATION (Placeholder)
    // ============================================
    const prevPage = document.getElementById('prevPage');
    const nextPage = document.getElementById('nextPage');
    const pageInfo = document.getElementById('pageInfo');

    if (prevPage && nextPage && pageInfo) {
        prevPage.disabled = true;
        nextPage.disabled = true;
    }

    // ============================================
    // SORTING FUNCTIONALITY
    // ============================================
    document.querySelectorAll('.sortable').forEach(header => {
        header.addEventListener('click', function() {
            const sortKey = this.dataset.sort;
            const currentDir = this.classList.contains('asc') ? 'asc' : 'desc';
            
            // Remove sort classes from all headers
            document.querySelectorAll('.sortable').forEach(h => {
                h.classList.remove('asc', 'desc');
            });
            
            // Set new sort direction
            const newDir = currentDir === 'asc' ? 'desc' : 'asc';
            this.classList.add(newDir);
            
            // Sort the rows
            sortTable(sortKey, newDir);
        });
    });

    function sortTable(key, direction) {
        const tbody = document.querySelector('#employeeTableBody');
        const rows = Array.from(tbody.querySelectorAll('.employee-row:not(.no-results-message)'));
        
        rows.sort((a, b) => {
            let aVal, bVal;
            
            switch(key) {
                case 'name':
                    aVal = a.dataset.name || '';
                    bVal = b.dataset.name || '';
                    break;
                case 'id':
                    aVal = a.dataset.id || '';
                    bVal = b.dataset.id || '';
                    break;
                case 'department':
                    aVal = a.dataset.department || '';
                    bVal = b.dataset.department || '';
                    break;
                case 'designation':
                    aVal = a.querySelector('td:nth-child(5)')?.textContent?.trim() || '';
                    bVal = b.querySelector('td:nth-child(5)')?.textContent?.trim() || '';
                    break;
                case 'status':
                    aVal = a.dataset.status || '';
                    bVal = b.dataset.status || '';
                    break;
                case 'workmode':
                    aVal = a.dataset.workmode || '';
                    bVal = b.dataset.workmode || '';
                    break;
                case 'salary':
                    aVal = parseFloat(a.dataset.salary) || 0;
                    bVal = parseFloat(b.dataset.salary) || 0;
                    break;
                default:
                    aVal = a.dataset.name || '';
                    bVal = b.dataset.name || '';
            }
            
            if (typeof aVal === 'string') {
                aVal = aVal.toLowerCase();
                bVal = bVal.toLowerCase();
            }
            
            if (aVal < bVal) return direction === 'asc' ? -1 : 1;
            if (aVal > bVal) return direction === 'asc' ? 1 : -1;
            return 0;
        });
        
        // Re-append sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    // ============================================
    // INITIAL FILTER
    // ============================================
    filterEmployees();

    console.log('👥 Employee Directory initialized');
    console.log(`📊 ${tableRows.length} employees loaded`);
});