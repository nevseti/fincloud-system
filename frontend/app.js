// Адаптивное приложение с ролевым доступом
class FinanceApp {
    constructor() {
        this.currentUser = null;
        this.currentBranch = null;
        this.allOperations = [];
        this.currentOpsPage = 1;
        this.pageSize = 5;
        this.currentSort = 'date_desc';
        this.currentSearch = '';
        this.init();
    }

    async init() {
        console.log('🚀 Инициализация приложения...');
        
        await this.checkAuth();
        await this.loadDashboardData();
        this.setupRoleBasedUI();
        await this.loadUsersIfAdmin();
        this.setupEventListeners();
    }

    async checkAuth() {
        const token = localStorage.getItem('token');
        const user = localStorage.getItem('user');

        if (!token || !user) {
            window.location.href = 'login.html';
            return;
        }

        this.currentUser = JSON.parse(user);
        this.updateUserInfo();
    }

    async loadDashboardData() {
    try {
        console.log('📊 Загрузка данных для роли:', this.currentUser.role);
        
        const token = localStorage.getItem('token');
        console.log('🔑 Токен:', token ? 'есть' : 'нет');
        
        let balanceUrl = 'http://localhost:8001/balance';
        let operationsUrl = 'http://localhost:8001/operations';

        // Для бухгалтеров добавляем branch_id по умолчанию
        if (this.currentUser.role === 'accountant' && !this.currentBranch) {
            balanceUrl += `?branch_id=${this.currentUser.branch_id}`;
            operationsUrl += `?branch_id=${this.currentUser.branch_id}`;
        } else if (this.currentBranch) {
            balanceUrl += `?branch_id=${this.currentBranch}`;
            operationsUrl += `?branch_id=${this.currentBranch}`;
        }

        console.log('🔗 URLs:', { balanceUrl, operationsUrl });

        const [balanceResponse, operationsResponse] = await Promise.all([
            fetch(balanceUrl, { headers: { 'Authorization': `Bearer ${token}` } }),
            fetch(operationsUrl, { headers: { 'Authorization': `Bearer ${token}` } })
        ]);

        console.log('📡 Ответы:', {
            balanceStatus: balanceResponse.status,
            operationsStatus: operationsResponse.status
        });

        if (!balanceResponse.ok) {
            const errorText = await balanceResponse.text();
            throw new Error(`Balance: ${balanceResponse.status} - ${errorText}`);
        }
        
        if (!operationsResponse.ok) {
            const errorText = await operationsResponse.text();
            throw new Error(`Operations: ${operationsResponse.status} - ${errorText}`);
        }

        const balance = await balanceResponse.json();
        const operations = await operationsResponse.json();

        console.log('✅ Данные получены:', { balance, operations: operations.length });

        this.updateBalance(balance);
        this.allOperations = operations;
        this.currentOpsPage = 1;
        this.renderOperationsPage();
        this.updatePaginationControls();

    } catch (error) {
        console.error('❌ Ошибка загрузки:', error);
        alert('Ошибка загрузки данных: ' + error.message);
    }
}

    updateBalance(balance) {
        const formatCurrency = (amount) => {
            return new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB'
            }).format(amount);
        };

        document.getElementById('currentBalance').textContent = formatCurrency(balance.total_balance);
        document.getElementById('totalIncome').textContent = formatCurrency(balance.total_income);
        document.getElementById('totalExpense').textContent = formatCurrency(balance.total_expense);
    }

    updateOperations(operations) {
        const table = document.getElementById('operationsTable');
        if (!table) return;

        table.innerHTML = '';

        if (operations.length === 0) {
            table.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #666;">Нет операций</td></tr>';
            return;
        }

        operations.forEach(operation => {
            const row = document.createElement('tr');
            
            const date = new Date(operation.created_at);
            const formattedDate = `${date.toLocaleDateString('ru-RU')} ${date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})}`;
            
            const typeClass = operation.type === 'income' ? 'income' : 'expense';
            const typeLabel = operation.type === 'income' ? 'Доход' : 'Расход';
            
            const formattedAmount = new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: 'RUB'
            }).format(operation.amount);

            row.innerHTML = `
                <td>${formattedDate}</td>
                <td><span class="${typeClass}">${typeLabel}</span></td>
                <td>${formattedAmount}</td>
                <td>${operation.description}</td>
                <td>Филиал ${operation.branch_id}</td>
            `;
            
            table.appendChild(row);
        });
    }

    renderOperationsPage() {
        // фильтр
        let filtered = this.allOperations;
        if (this.currentSearch) {
            const q = this.currentSearch.toLowerCase();
            filtered = filtered.filter(op => String(op.description || '').toLowerCase().includes(q));
        }
        // сортировка
        const sort = this.currentSort;
        const arr = [...filtered].sort((a,b)=>{
            if (sort === 'date_desc') return new Date(b.created_at) - new Date(a.created_at);
            if (sort === 'date_asc') return new Date(a.created_at) - new Date(b.created_at);
            if (sort === 'amount_desc') return (b.amount||0) - (a.amount||0);
            if (sort === 'amount_asc') return (a.amount||0) - (b.amount||0);
            if (sort === 'type_asc') return String(a.type).localeCompare(String(b.type));
            if (sort === 'type_desc') return String(b.type).localeCompare(String(a.type));
            return 0;
        });
        // пагинация
        const start = (this.currentOpsPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const pageItems = arr.slice(start, end);
        this.updateOperations(pageItems);
        // обновить счетчики страниц для фильтрованного набора
        const totalPages = Math.max(1, Math.ceil(arr.length / this.pageSize));
        const currentPageEl = document.getElementById('currentPage');
        const totalPagesEl = document.getElementById('totalPages');
        if (currentPageEl) currentPageEl.textContent = String(this.currentOpsPage);
        if (totalPagesEl) totalPagesEl.textContent = String(totalPages);
    }

    updatePaginationControls() {
        const totalPages = Math.max(1, Math.ceil(this.allOperations.length / this.pageSize));
        const currentPageEl = document.getElementById('currentPage');
        const totalPagesEl = document.getElementById('totalPages');
        if (currentPageEl) currentPageEl.textContent = String(this.currentOpsPage);
        if (totalPagesEl) totalPagesEl.textContent = String(totalPages);
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        if (prevBtn) prevBtn.disabled = this.currentOpsPage <= 1;
        if (nextBtn) nextBtn.disabled = this.currentOpsPage >= totalPages;
    }

    updateUserInfo() {
        const userInfoElement = document.getElementById('userInfo');
        if (userInfoElement && this.currentUser) {
            const roleLabels = {
                'system_admin': '👑 Системный администратор',
                'manager': '👔 Руководитель', 
                'accountant': '📊 Бухгалтер'
            };
            
            const branchInfo = this.currentUser.branch_id === 0 ? 'Все филиалы' : `Филиал ${this.currentUser.branch_id}`;
            
            userInfoElement.innerHTML = `
                <strong>${this.currentUser.email}</strong> 
                (${roleLabels[this.currentUser.role] || this.currentUser.role}) 
                | ${branchInfo}
            `;
        }
    }

    setupRoleBasedUI() {
        const role = this.currentUser.role;
        console.log('🎭 Настройка UI для роли:', role);

        // Скрываем форму создания операций для руководителей
        const operationForm = document.getElementById('operationForm');
        if (operationForm) {
            operationForm.style.display = role === 'manager' ? 'none' : 'block';
        }

        // Настраиваем филиалы для бухгалтеров
        if (role === 'accountant') {
            this.setupAccountantUI();
        }

        // Показываем/скрываем фильтр по филиалам
        const branchFilterSection = document.querySelector('.operations-controls');
        if (branchFilterSection) {
            branchFilterSection.style.display = role === 'accountant' ? 'none' : 'flex';
        }

        // Панель админа
        const adminPanel = document.getElementById('adminPanel');
        if (adminPanel) {
            adminPanel.style.display = role === 'system_admin' ? 'block' : 'none';
        }
    }

    async loadUsersIfAdmin() {
        if (!this.currentUser || this.currentUser.role !== 'system_admin') return;
        try {
            const token = localStorage.getItem('token');
            const resp = await fetch('http://localhost:8000/users', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!resp.ok) throw new Error(await resp.text());
            const users = await resp.json();
            this.renderUsers(users);
        } catch (e) {
            console.error('Не удалось загрузить пользователей:', e);
        }
    }

    renderUsers(users) {
        const tbody = document.getElementById('usersTable');
        if (!tbody) return;
        tbody.innerHTML = '';
        users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${u.id}</td>
                <td>${u.email}</td>
                <td>${u.role}</td>
                <td>${u.branch_id}</td>
                <td>
                    <button data-action="edit" data-id="${u.id}" class="btn-secondary">Изм.</button>
                    <button data-action="delete" data-id="${u.id}" class="btn-secondary" style="background:#dc3545;">Удалить</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    setupAccountantUI() {
        // Бухгалтер может выбирать только свой филиал
        const branchSelect = document.getElementById('branch_id');
        if (branchSelect) {
            branchSelect.innerHTML = '';
            const option = document.createElement('option');
            option.value = this.currentUser.branch_id;
            option.textContent = `Филиал ${this.currentUser.branch_id}`;
            branchSelect.appendChild(option);
        }
    }

    setupEventListeners() {
        // Форма создания операции
        const operationForm = document.getElementById('operationForm');
        if (operationForm) {
            operationForm.addEventListener('submit', (e) => this.handleCreateOperation(e));
        }

        // Фильтр по филиалу
        const branchFilter = document.getElementById('branchFilter');
        if (branchFilter) {
            branchFilter.addEventListener('change', (e) => this.handleBranchFilter(e));
        }

        // Кнопка выхода
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }

        // Кнопка обновления
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboardData());
        }

        // (theme toggle removed)

        // Поиск/сортировка
        const searchInput = document.getElementById('searchOps');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.currentSearch = e.target.value || '';
                this.currentOpsPage = 1;
                this.renderOperationsPage();
                this.updatePaginationControls();
            });
        }
        const sortSelect = document.getElementById('sortOps');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.currentSort = e.target.value;
                this.currentOpsPage = 1;
                this.renderOperationsPage();
                this.updatePaginationControls();
            });
        }

        // Пагинация операций
        const prevBtn = document.getElementById('prevPageBtn');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (this.currentOpsPage > 1) {
                    this.currentOpsPage -= 1;
                    this.renderOperationsPage();
                    this.updatePaginationControls();
                }
            });
        }
        const nextBtn = document.getElementById('nextPageBtn');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const totalPages = Math.max(1, Math.ceil(this.allOperations.length / this.pageSize));
                if (this.currentOpsPage < totalPages) {
                    this.currentOpsPage += 1;
                    this.renderOperationsPage();
                    this.updatePaginationControls();
                }
            });
        }

        // Отчеты: кнопки
        const btnSummary = document.getElementById('btnSummary');
        if (btnSummary) {
            btnSummary.addEventListener('click', () => this.handleSummary());
        }
        const btnExportCsv = document.getElementById('btnExportCsv');
        if (btnExportCsv) {
            btnExportCsv.addEventListener('click', () => this.handleExportCsv());
        }
        const btnExportPdf = document.getElementById('btnExportPdf');
        if (btnExportPdf) {
            btnExportPdf.addEventListener('click', () => this.handleExportPdf());
        }

        // Admin: обработчики CRUD
        const usersTable = document.getElementById('usersTable');
        if (usersTable) {
            usersTable.addEventListener('click', async (e) => {
                const target = e.target;
                if (!(target instanceof HTMLElement)) return;
                const id = target.getAttribute('data-id');
                const action = target.getAttribute('data-action');
                if (!id || !action) return;
                if (action === 'edit') {
                    await this.loadUserIntoForm(parseInt(id));
                } else if (action === 'delete') {
                    await this.deleteUser(parseInt(id));
                }
            });
        }

        const userForm = document.getElementById('userForm');
        if (userForm) {
            userForm.addEventListener('submit', (e) => this.handleSaveUser(e));
        }

        const resetUserFormBtn = document.getElementById('resetUserFormBtn');
        if (resetUserFormBtn) {
            resetUserFormBtn.addEventListener('click', () => this.resetUserForm());
        }
    }

    // theme toggle removed

    async loadUserIntoForm(userId) {
        // Найдём пользователя в таблице (быстрый способ без отдельного запроса)
        const row = Array.from(document.querySelectorAll('#usersTable tr')).find(tr => tr.querySelector(`[data-id="${userId}"]`));
        if (!row) return;
        const cells = row.querySelectorAll('td');
        document.getElementById('userId').value = userId;
        document.getElementById('userEmail').value = cells[1].textContent;
        document.getElementById('userPassword').value = '';
        document.getElementById('userRole').value = cells[2].textContent;
        document.getElementById('userBranch').value = cells[3].textContent;
    }

    resetUserForm() {
        document.getElementById('userId').value = '';
        document.getElementById('userEmail').value = '';
        document.getElementById('userPassword').value = '';
        document.getElementById('userRole').value = 'manager';
        document.getElementById('userBranch').value = 0;
    }

    async handleSaveUser(e) {
        e.preventDefault();
        const id = document.getElementById('userId').value;
        const email = document.getElementById('userEmail').value;
        const password = document.getElementById('userPassword').value;
        const role = document.getElementById('userRole').value;
        const branch_id = parseInt(document.getElementById('userBranch').value);
        const token = localStorage.getItem('token');

        try {
            let resp;
            if (id) {
                const payload = {};
                if (email) payload.email = email;
                if (password) payload.password = password;
                if (role) payload.role = role;
                if (!Number.isNaN(branch_id)) payload.branch_id = branch_id;
                resp = await fetch(`http://localhost:8000/users/${id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(payload)
                });
            } else {
                resp = await fetch('http://localhost:8000/users', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify({ email, password, role, branch_id })
                });
            }
            if (!resp.ok) throw new Error(await resp.text());
            await this.loadUsersIfAdmin();
            this.resetUserForm();
            alert('✅ Пользователь сохранён');
        } catch (e) {
            console.error(e);
            alert('❌ Ошибка: ' + e.message);
        }
    }

    async deleteUser(id) {
        if (!confirm('Удалить пользователя #' + id + '?')) return;
        const token = localStorage.getItem('token');
        try {
            const resp = await fetch(`http://localhost:8000/users/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!resp.ok) throw new Error(await resp.text());
            await this.loadUsersIfAdmin();
            alert('🗑️ Пользователь удалён');
        } catch (e) {
            console.error(e);
            alert('❌ Ошибка: ' + e.message);
        }
    }

    async handleSummary() {
        const token = localStorage.getItem('token');
        const branch = document.getElementById('reportBranch')?.value || '';
        const limit = document.getElementById('reportLimit')?.value || '';
        const q = new URLSearchParams();
        if (branch) q.set('branch_id', branch);
        if (limit) q.set('limit', limit);
        const params = q.toString() ? `?${q.toString()}` : '';
        const output = document.getElementById('summaryOutput');
        try {
            const resp = await fetch(`http://localhost:8002/summary${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!resp.ok) throw new Error(await resp.text());
            const data = await resp.json();
            if (output) output.textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            console.error(e);
            if (output) output.textContent = 'Ошибка: ' + e.message;
        }
    }

    async handleExportCsv() {
        const token = localStorage.getItem('token');
        const branch = document.getElementById('reportBranch')?.value || '';
        const limit = document.getElementById('reportLimit')?.value || '';
        const q = new URLSearchParams();
        if (branch) q.set('branch_id', branch);
        if (limit) q.set('limit', limit);
        const params = q.toString() ? `?${q.toString()}` : '';
        try {
            const resp = await fetch(`http://localhost:8002/export.csv${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!resp.ok) throw new Error(await resp.text());
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'operations_export.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            alert('Ошибка экспорта: ' + e.message);
        }
    }

    async handleExportPdf() {
        const token = localStorage.getItem('token');
        const branch = document.getElementById('reportBranch')?.value || '';
        const limit = document.getElementById('reportLimit')?.value || '';
        const q = new URLSearchParams();
        if (branch) q.set('branch_id', branch);
        if (limit) q.set('limit', limit);
        const params = q.toString() ? `?${q.toString()}` : '';
        try {
            const resp = await fetch(`http://localhost:8002/export.pdf${params}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!resp.ok) throw new Error(await resp.text());
            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'report.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
        } catch (e) {
            console.error(e);
            alert('Ошибка экспорта PDF: ' + e.message);
        }
    }

    async handleCreateOperation(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const operationData = {
            type: formData.get('type'),
            amount: parseFloat(formData.get('amount')),
            description: formData.get('description'),
            branch_id: parseInt(formData.get('branch_id'))
        };

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:8001/operations', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(operationData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText);
            }

            alert('✅ Операция создана!');
            e.target.reset();
            await this.loadDashboardData();
            
        } catch (error) {
            console.error('Ошибка:', error);
            alert('❌ Ошибка: ' + error.message);
        }
    }

    async handleBranchFilter(e) {
        this.currentBranch = e.target.value ? parseInt(e.target.value) : null;
        await this.loadDashboardData();
    }

    handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    }
}

// Запуск приложения
document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname.includes('dashboard.html')) {
        new FinanceApp();
    }
});