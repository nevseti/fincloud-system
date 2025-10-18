# 🚀 FinCloud CI/CD Pipeline

Этот документ описывает настройку и использование CI/CD pipeline для FinCloud системы.

## 📋 Обзор

Наш CI/CD pipeline включает:

- **Тестирование** - автоматические тесты при каждом push/PR
- **Сборка** - создание Docker образов
- **Безопасность** - сканирование уязвимостей
- **Деплой** - автоматическое развертывание в Kubernetes
- **Публикация** - публикация образов в GitHub Container Registry

## 🔧 Настройка

### 1. GitHub Secrets

Добавьте следующие secrets в настройках репозитория:

```bash
# Kubernetes конфигурации (base64 encoded)
KUBE_CONFIG_STAGING=<base64-encoded-kubeconfig-for-staging>
KUBE_CONFIG_PRODUCTION=<base64-encoded-kubeconfig-for-production>

# Docker Registry (опционально)
DOCKER_USERNAME=<your-dockerhub-username>
DOCKER_PASSWORD=<your-dockerhub-password>
```

### 2. Environments

Создайте environments в GitHub:
- `staging` - для тестового окружения
- `production` - для продакшена

### 3. Kubernetes Cluster

Настройте доступ к Kubernetes кластеру:

```bash
# Получите kubeconfig
kubectl config view --raw > kubeconfig

# Закодируйте в base64
base64 -i kubeconfig -o kubeconfig.b64

# Добавьте содержимое kubeconfig.b64 в GitHub Secrets
```

## 🎯 Workflows

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Триггеры:**
- Push в `main` или `develop`
- Pull Request в `main`

**Этапы:**
1. **Test** - запуск тестов
2. **Build** - сборка Docker образов
3. **Deploy** - деплой в Kubernetes

### 2. Testing (`.github/workflows/test.yml`)

**Триггеры:**
- Push в любую ветку
- Pull Request

**Тесты:**
- Unit тесты для каждого сервиса
- Линтинг кода (flake8, black, isort)
- Интеграционные тесты с PostgreSQL

### 3. Security (`.github/workflows/security.yml`)

**Триггеры:**
- Push в `main`
- Pull Request в `main`
- Еженедельно (понедельник 2:00)

**Сканирование:**
- Зависимости (safety)
- Docker образы (Trivy)
- Секреты (TruffleHog)

### 4. Deploy (`.github/workflows/deploy.yml`)

**Триггеры:**
- Manual dispatch
- Push в `main` (production)
- Push в `develop` (staging)

**Окружения:**
- `staging` - тестовое окружение
- `production` - продакшен

### 5. Publish (`.github/workflows/publish.yml`)

**Триггеры:**
- Создание тега `v*`
- Manual dispatch

**Действия:**
- Публикация Docker образов в GitHub Container Registry
- Генерация release notes

## 🐳 Docker Images

Образы публикуются в GitHub Container Registry:

```
ghcr.io/<username>/fincloud-system/auth-service:<tag>
ghcr.io/<username>/fincloud-system/finance-service:<tag>
ghcr.io/<username>/fincloud-system/report-service:<tag>
ghcr.io/<username>/fincloud-system/frontend:<tag>
```

## 🚀 Использование

### Запуск тестов локально

```bash
# Установка зависимостей
pip install pytest pytest-asyncio httpx

# Запуск тестов
cd auth-service && python -m pytest tests/ -v
cd finance-service && python -m pytest tests/ -v
cd report-service && python -m pytest tests/ -v
```

### Линтинг кода

```bash
# Установка инструментов
pip install flake8 black isort mypy

# Проверка стиля
flake8 .
black --check .
isort --check-only .
mypy .
```

### Создание релиза

```bash
# Создание тега
git tag v1.0.0
git push origin v1.0.0

# Это автоматически запустит publish workflow
```

### Ручной деплой

1. Перейдите в Actions → Deploy to Environments
2. Нажмите "Run workflow"
3. Выберите окружение (staging/production)
4. Укажите версию (опционально)

## 📊 Мониторинг

### Статус Pipeline

- **Зеленый** ✅ - все тесты прошли, деплой успешен
- **Желтый** ⚠️ - тесты проходят, но есть предупреждения
- **Красный** ❌ - тесты не прошли или деплой неудачен

### Логи

Все логи доступны в GitHub Actions:
- Тесты: Actions → Test
- Сборка: Actions → CI/CD Pipeline
- Деплой: Actions → Deploy to Environments

## 🔒 Безопасность

### Сканирование

- **Зависимости** - проверка уязвимостей в Python пакетах
- **Docker** - сканирование образов на уязвимости
- **Секреты** - поиск случайно закоммиченных секретов

### Рекомендации

1. Регулярно обновляйте зависимости
2. Проверяйте security alerts в GitHub
3. Используйте Dependabot для автоматических обновлений
4. Настройте branch protection rules

## 🛠️ Troubleshooting

### Частые проблемы

1. **Тесты падают**
   - Проверьте логи в Actions
   - Запустите тесты локально
   - Обновите зависимости

2. **Деплой не работает**
   - Проверьте kubeconfig
   - Убедитесь, что кластер доступен
   - Проверьте права доступа

3. **Docker build падает**
   - Проверьте Dockerfile
   - Убедитесь, что все файлы в контексте
   - Проверьте размер образа

### Полезные команды

```bash
# Проверка статуса Kubernetes
kubectl get pods -n fincloud

# Просмотр логов
kubectl logs deployment/auth-service -n fincloud

# Откат деплоя
kubectl rollout undo deployment/auth-service -n fincloud
```

## 📈 Метрики

Pipeline отслеживает:
- Время выполнения тестов
- Время сборки образов
- Время деплоя
- Успешность деплоев
- Количество уязвимостей

## 🔄 Обновление

Для обновления CI/CD:

1. Внесите изменения в workflow файлы
2. Протестируйте локально
3. Создайте PR с изменениями
4. После merge изменения применятся автоматически

---

**Поддержка:** Если у вас есть вопросы по CI/CD, создайте issue в репозитории.
