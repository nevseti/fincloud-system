// Конфигурация API
const API_CONFIG = {
    AUTH_SERVICE: (window.ENV && window.ENV.AUTH_SERVICE) || 'http://localhost:8000',
    FINANCE_SERVICE: (window.ENV && window.ENV.FINANCE_SERVICE) || 'http://localhost:8001'
};

// Утилиты для работы с localStorage (должны быть ТОЛЬКО ЗДЕСЬ)
window.Storage = {
    getToken: () => localStorage.getItem('token'),
    setToken: (token) => localStorage.setItem('token', token),
    removeToken: () => localStorage.removeItem('token'),
    getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
    setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
    removeUser: () => localStorage.removeItem('user')
};

// Функции для работы с API
const AuthAPI = {
    // Логин пользователя
    async login(email, password) {
        const response = await fetch(`${API_CONFIG.AUTH_SERVICE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            throw new Error('Ошибка авторизации');
        }

        return await response.json();
    },

    // Получение информации о пользователе
    async getCurrentUser() {
        const token = Storage.getToken();
        if (!token) throw new Error('Токен не найден');

        const response = await fetch(`${API_CONFIG.AUTH_SERVICE}/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Ошибка получения данных пользователя');
        }

        return await response.json();
    }
};

// Обработчик формы логина
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const messageDiv = document.getElementById('message');

    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                // Показываем загрузку
                messageDiv.innerHTML = '⏳ Вход в систему...';
                messageDiv.className = 'message';

                // Авторизация
                const authData = await AuthAPI.login(email, password);
                
                // Сохраняем токен
                Storage.setToken(authData.access_token);
                
                // Получаем данные пользователя
                const userData = await AuthAPI.getCurrentUser();
                Storage.setUser(userData);
                
                // Успех
                messageDiv.innerHTML = '✅ Успешный вход! Перенаправление...';
                messageDiv.className = 'message success';
                
                // Перенаправляем на дашборд
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1000);

            } catch (error) {
                console.error('Ошибка авторизации:', error);
                messageDiv.innerHTML = `❌ Ошибка: ${error.message}`;
                messageDiv.className = 'message error';
            }
        });
    }

    // Проверяем авторизацию при загрузке страниц
    const token = Storage.getToken();
    const user = Storage.getUser();
    
    if (token && user && window.location.pathname.includes('login.html')) {
        // Если уже авторизован, перенаправляем на дашборд
        window.location.href = 'dashboard.html';
    }
});