import time

from labs.lab02.task1 import Admin, User, UserAccount

def demo():
    # 1. Валідація Email
    print("1. Валідація Email")
    user = User("alice", "alice@example.com", "user")
    user.set_password("secure_password_123")
    print(f"Створено користувача: {user}")

    try:
        # Спроба встановити невалідний email
        user.email = "invalid-email-without-domain"
    except ValueError as e:

        print(f"Спіймали очікувану помилку: {e}")

    # Встановлюємо правильний email
    user.email = "alice_new@example.com"
    print(f" Оновлено email на: {user.email}")

    # 2. Права Адміністратора
    print("\n2. Права Адміністратора")
    admin = Admin("bob", "bob@example.com", "admin", ["read"])
    admin.set_password("admin_pass")

    admin.grant_permission("write")
    admin.grant_permission("delete")
    admin.revoke_permission("read")

    print(f"Адмін: {admin}")
    print(f"Має право 'write': {admin.has_permission('write')}")
    print(f"Має право 'read': {admin.has_permission('read')}")

    # 3. Вхід в систему (Успішний та Невдалий)
    print("\n3. Вхід в систему (UserAccount)")
    account = UserAccount(user)

    # Невдалий вхід
    account.login("alice", "wrong_password", "192.168.1.10")
    print(
        f"Аутентифікація після невдалого входу: {account.is_authenticated()}")

    # Успішний вхід
    account.login("alice", "secure_password_123", "192.168.1.10")
    print(
        f"Аутентифікація після успішного входу: {account.is_authenticated()}")

    # Доступ через магічні методи (як до словника)
    print(
        f"Отримання username через account['user']: {account['user'].username}")

    # 4. Завершення сеансу за таймаутом
    print("\n4. Завершення сеансу за таймаутом")
    print(" Чекаємо 2 секунди для імітації неактивності")
    time.sleep(2)

    is_active = account.session.is_active(1) if account.session else False
    print(f"Сесія активна з таймаутом 1с після очікування 2с: {is_active}")

    # 5. Вихід із системи (Logout)
    print("\n5. Вихід із системи")
    account.logout()
    print(f"Аутентифікація після logout: {account.is_authenticated()}")

    # 6. Журнал аудиту
    print("\n6. Журнал аудиту (AuditLog)")
    account.audit_log.show_all()


demo()
