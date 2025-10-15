// Функции для работы с финансовым API
const FinanceAPI = {
    // Создание операции
    async createOperation(operationData) {
        const token = Storage.getToken();
        const response = await fetch(`${API_CONFIG.FINANCE_SERVICE}/operations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(operationData)
        });

        if (!response.ok) {
            throw new Error('Ошибка создания операции');
        }

        return await response.json();
    },

    // Получение списка операций
    async getOperations(branchId = null) {
        const token = Storage.getToken();
        let url = `${API_CONFIG.FINANCE_SERVICE}/operations`;
        
        if (branchId) {
            url += `?branch_id=${branchId}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка получения операций');
        }

        return await response.json();
    },

    // Получение баланса
    async getBalance(branchId = null) {
        const token = Storage.getToken();
        let url = `${API_CONFIG.FINANCE_SERVICE}/balance`;
        
        if (branchId) {
            url += `?branch_id=${branchId}`;
        }

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка получения баланса');
        }

        return await response.json();
    }
};

// Утилиты для форматирования
// Утилиты для форматирования
const Formatter = {
    formatCurrency: (amount) => {
        console.log(`💰 Форматируем валюту: ${amount}`);
        const result = new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB'
        }).format(amount);
        console.log(`💰 Результат: ${result}`);
        return result;
    },

    formatDate: (dateString) => {
        console.log(`📅 Форматируем дату: ${dateString}`);
        const date = new Date(dateString);
        const result = date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'});
        console.log(`📅 Результат: ${result}`);
        return result;
    },

    getOperationTypeLabel: (type) => {
        console.log(`🏷️ Получаем label для типа: ${type}`);
        return type === 'income' ? 'Доход' : 'Расход';
    },

    getOperationTypeClass: (type) => {
        console.log(`🎨 Получаем класс для типа: ${type}`);
        return type === 'income' ? 'income' : 'expense';
    }
};