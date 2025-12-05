# Ответы на вопросы для отчета

## 1. Сервисы в Docker Swarm Stack

✅ **Правильно перечислены:**
- auth-service
- finance-service
- report-service
- frontend
- postgres (один контейнер)

**Ответ на вопрос:**
✅ **PostgreSQL — один контейнер, но разные базы данных внутри одной СУБД:**
- `auth_db` — для auth-service
- `finance_db` — для finance-service
- Оба сервиса подключаются к одному контейнеру PostgreSQL, но используют разные базы данных

**Подтверждение из кода:**
- `AUTH_DATABASE_URL: postgresql://postgres:postgres@postgres:5432/auth_db`
- `FINANCE_DATABASE_URL: postgresql://postgres:postgres@postgres:5432/finance_db`

---

## 2. Как работает frontend

✅ **Так и есть:**
- nginx раздает статику (HTML/CSS/JS)
- JS обращается напрямую к каждому backend-сервису
- API endpoints вызываются напрямую (без reverse proxy)

**Подтверждение из кода:**
- `frontend/auth.js`: `AUTH_SERVICE: 'http://localhost:8000'`
- `frontend/finance.js`: `FINANCE_SERVICE: 'http://localhost:8001'`
- Frontend делает fetch-запросы напрямую к `http://localhost:8000` и `http://localhost:8001`

**Нет единого прокси** — каждый сервис доступен на своем порту.

---

## 3. Что относится ко второй главе (CI/CD)

✅ **Во второй главе ТОЛЬКО теория CI/CD:**
- Концепция непрерывной интеграции и доставки
- Принципы работы CI/CD
- Этапы конвейера (теоретически)
- **БЕЗ:** логов, YAML, команд, тестовых результатов

**Ответ на вопрос:**
✅ **Можно добавить таблицу "Этапы конвейера"** — это будет полезно для наглядности:
- Code Quality Check
- Unit Tests
- Integration Tests
- API Tests
- Security Tests
- E2E Tests
- Performance Tests
- Docker Build
- Docker Push
- Deployment

**Но без деталей реализации** — только названия этапов и их назначение.

---

## 4. Docker Hub namespace и названия образов

✅ **Формат правильный:**
- `${DOCKERHUB_USERNAME}/fincloud-auth`
- `${DOCKERHUB_USERNAME}/fincloud-finance`
- `${DOCKERHUB_USERNAME}/fincloud-report`
- `${DOCKERHUB_USERNAME}/fincloud-frontend`

**В отчете можно указать:**
- Namespace: `nevseti` (или реальное имя пользователя, если известно)
- Или оставить как `${DOCKERHUB_USERNAME}` в описании

**Пример для отчета:**
```
Образы хранятся в Docker Hub под следующими именами:
- nevseti/fincloud-auth
- nevseti/fincloud-finance
- nevseti/fincloud-report
- nevseti/fincloud-frontend
```

---

## 5. Схема обновлений в Docker Swarm

✅ **Сейчас используется:**
```bash
docker stack rm fincloud
# ожидание удаления
docker stack deploy --with-registry-auth
```

**Ответ на вопрос:**
✅ **В теории можно упомянуть rolling updates как возможность платформы:**
- Docker Swarm поддерживает rolling updates
- Можно настроить постепенное обновление без простоя
- В текущей реализации используется полная замена стека (проще для курсовой)
- Rolling updates можно упомянуть как перспективу развития

**Рекомендация для отчета:**
- Описать текущую схему (rm + deploy)
- Упомянуть, что Swarm поддерживает rolling updates
- Отметить, что для курсовой работы выбрана простая схема полной замены

---

## 6. Описание тестов во второй главе

✅ **Во второй главе только типы тестов + краткое объяснение:**

**Что включить:**
- **Unit Tests** — проверка отдельных компонентов изолированно
- **Integration Tests** — проверка взаимодействия компонентов
- **API Tests** — проверка REST API endpoints
- **Security Tests** — проверка безопасности (JWT, пароли, валидация)
- **E2E Tests** — проверка полного пользовательского сценария
- **Performance Tests** — проверка производительности при больших объемах данных

**Без подробностей:**
- Без конкретных примеров кода
- Без результатов тестов
- Без количества проверок
- Только концепция и назначение каждого типа

**Подробности оставить для главы 4** (практическая часть).

---

## 7. Роль self-hosted runner

✅ **Рекомендация: Вариант А — в разделе 2.5 (CI/CD)**

**Почему:**
- Self-hosted runner — это часть CI/CD инфраструктуры
- Логически относится к процессу автоматизации
- Упоминается в контексте deployment процесса

**Как описать:**
- В разделе 2.5 упомянуть, что для build и deployment используется self-hosted runner
- Объяснить, что это позволяет выполнять операции на собственной инфраструктуре
- Упомянуть, что runner работает на той же VM, где развернут Docker Swarm

**В разделе 2.2 (инфраструктура)** можно упомянуть только VM и Docker Swarm, без деталей о runner.

---

## 8. Docker Swarm — один manager node

✅ **Всё так:**
- Одна VM
- Один узел (manager)
- Нет worker-ов

**Ответ:**
- Не было попыток добавлять worker-узлы
- Для курсовой работы достаточно одного manager node
- Это упрощает настройку и демонстрацию работы Swarm

**В отчете можно указать:**
- Кластер состоит из одного manager node
- Для демонстрации отказоустойчивости достаточно реплик сервисов
- В production можно расширить до multi-node кластера

---

## 9. Визуальные схемы

✅ **Рекомендация: Добавить схемы**

**Какие схемы будут полезны:**

1. **Архитектура системы** (уже есть в тексте):
   - Пользователь → Frontend → Backend сервисы → PostgreSQL
   - Показать связи между компонентами

2. **CI/CD Pipeline** (для раздела 2.5):
   - GitHub → Тесты → Build → Docker Hub → Deployment → Docker Swarm
   - Показать поток от commit до production

3. **Docker Swarm Stack** (для раздела 2.4):
   - Manager Node → Сервисы → Сеть → Volumes
   - Показать структуру развертывания

**Формат:**
- Текстовые схемы (ASCII art) или описание структуры
- Без генерации изображений (как указано в вопросе)
- Можно использовать простые блок-схемы в тексте

**Пример для CI/CD:**
```
GitHub Repository
    ↓ (push)
GitHub Actions (CI)
    ↓ (тесты)
Docker Build (self-hosted runner)
    ↓ (push)
Docker Hub
    ↓ (pull)
Docker Swarm Deployment
    ↓
Production Environment
```

---

## Итоговые рекомендации:

1. ✅ PostgreSQL — один контейнер, разные базы данных
2. ✅ Frontend — прямой доступ к backend, без proxy
3. ✅ Таблица этапов CI/CD — добавить
4. ✅ Docker Hub namespace — указать формат (nevseti/fincloud-*)
5. ✅ Rolling updates — упомянуть как возможность, описать текущую схему
6. ✅ Тесты — только типы и концепция во второй главе
7. ✅ Self-hosted runner — в разделе 2.5 (CI/CD)
8. ✅ Docker Swarm — один manager node
9. ✅ Схемы — добавить текстовые схемы для наглядности

