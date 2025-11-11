from app.core.security import hash_password

password = "SecurePass123!"
hashed = hash_password(password)
print(hashed)
