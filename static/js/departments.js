// static/js/people/departments.js

document.addEventListener('DOMContentLoaded', function() {
    
    // ============================================
    // SEARCH / FILTER FUNCTIONALITY
    // ============================================
    
    const searchInput = document.getElementById('departmentSearch');
    const tableRows = document.querySelectorAll('.table-card tbody tr');
    const departmentCards = document.querySelectorAll('.department-card');
    
    // Check if there are any rows (not empty state)
    const hasTableRows = tableRows.length > 0 && !tableRows[0].querySelector('.empty-state');
    
    function filterDepartments(query) {
        const searchTerm = query.toLowerCase().trim();
        
        // Filter table rows
        if (hasTableRows) {
            tableRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                // Check department name (index 1), code (index 2), description (index 3)
                let match = false;
                if (cells.length >= 4) {
                    const name = cells[1]?.textContent?.toLowerCase() || '';
                    const code = cells[2]?.textContent?.toLowerCase() || '';
                    const description = cells[3]?.textContent?.toLowerCase() || '';
                    match = name.includes(searchTerm) || 
                            code.includes(searchTerm) || 
                            description.includes(searchTerm);
                }
                row.style.display = match || searchTerm === '' ? '' : 'none';
            });
        }
        
        // Filter department cards
        departmentCards.forEach(card => {
            const name = card.querySelector('h3')?.textContent?.toLowerCase() || '';
            const description = card.querySelector('p')?.textContent?.toLowerCase() || '';
            const code = card.querySelector('li:first-child')?.textContent?.toLowerCase() || '';
            
            const match = name.includes(searchTerm) || 
                         description.includes(searchTerm) || 
                         code.includes(searchTerm);
            
            card.style.display = match || searchTerm === '' ? '' : 'none';
        });
    }
    
    // Debounce function for better performance
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
    
    // Add search event listener with debounce
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function(e) {
            filterDepartments(e.target.value);
        }, 300));
        
        // Clear search on Escape key
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                filterDepartments('');
                this.blur();
            }
        });
    }
    
    // ============================================
    // EXPORT FUNCTIONALITY
    // ============================================
    
    const exportBtn = document.querySelector('.btn-secondary');
    
    if (exportBtn) {
        exportBtn.addEventListener('click', function(e) {
            e.preventDefault();
            exportDepartments();
        });
    }
    
    function exportDepartments() {
        // Get all visible rows (respecting current filter)
        const visibleRows = document.querySelectorAll('.table-card tbody tr:not([style*="display: none"])');
        
        // Check if we're in empty state
        if (visibleRows.length === 0 || visibleRows[0].querySelector('.empty-state')) {
            alert('No departments to export.');
            return;
        }
        
        // Build CSV data
        let csvContent = 'Department,Code,Description,Employees,Created\n';
        
        visibleRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 6) {
                const name = cells[1]?.textContent?.trim() || '';
                const code = cells[2]?.textContent?.trim() || '--';
                const description = cells[3]?.textContent?.trim() || 'No description';
                const employees = cells[4]?.textContent?.trim() || '0';
                const created = cells[5]?.textContent?.trim() || '';
                
                // Escape commas and quotes for CSV
                const escapeCSV = (str) => {
                    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
                        return `"${str.replace(/"/g, '""')}"`;
                    }
                    return str;
                };
                
                csvContent += `${escapeCSV(name)},${escapeCSV(code)},${escapeCSV(description)},${employees},${created}\n`;
            }
        });
        
        // Create and download CSV file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `departments_export_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
    
    // ============================================
    // KEYBOARD SHORTCUTS
    // ============================================
    
    document.addEventListener('keydown', function(e) {
        // Ctrl+F or Cmd+F to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            if (searchInput && document.activeElement !== searchInput) {
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }
        }
    });
    
    // ============================================
    // TOOLTIP / CONFIRMATION FOR DELETE
    // ============================================
    
    const deleteButtons = document.querySelectorAll('.action-btn.delete');
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const confirmed = confirm('Are you sure you want to delete this department? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
    
    // ============================================
    // ANIMATION ON LOAD
    // ============================================
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.department-card, .summary-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 50));
    });
    
    // ============================================
    // LIVE COUNTER (optional)
    // ============================================
    
    function updateVisibleCount() {
        const visibleRows = document.querySelectorAll('.table-card tbody tr:not([style*="display: none"]):not(:has(.empty-state))');
        const totalDisplay = document.querySelector('.summary-card.blue h2');
        if (totalDisplay && visibleRows.length > 0) {
            // Only update if we want to show filtered count
            // Currently we keep total count static, but could show filtered count
        }
    }
    
    // Update count when filtering (optional)
    // Uncomment if you want dynamic count
    // searchInput?.addEventListener('input', updateVisibleCount);
    
    console.log('🏢 Departments page initialized');
    console.log(`📊 ${departmentCards.length} departments loaded`);
});