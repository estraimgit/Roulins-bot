#!/usr/bin/env python3
"""
Скрипт для генерации безопасного ключа шифрования
"""
import secrets
import string
import sys

def generate_encryption_key(length=32):
    """Генерирует безопасный ключ шифрования"""
    # Используем буквы, цифры и специальные символы
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # Генерируем случайную строку
    key = ''.join(secrets.choice(characters) for _ in range(length))
    
    return key

def main():
    """Главная функция"""
    print("🔐 Генератор ключа шифрования для Roulins_Bot")
    print("=" * 50)
    
    # Генерируем ключ
    key = generate_encryption_key(32)
    
    print(f"Сгенерированный ключ шифрования:")
    print(f"ENCRYPTION_KEY={key}")
    print()
    print("⚠️  ВАЖНО:")
    print("1. Сохраните этот ключ в безопасном месте")
    print("2. Добавьте его в файл .env")
    print("3. НЕ ДЕЛИТЕСЬ этим ключом с другими")
    print("4. Без этого ключа вы не сможете расшифровать данные")
    print()
    print("📝 Добавьте в ваш .env файл:")
    print(f"ENCRYPTION_KEY={key}")

if __name__ == "__main__":
    main()
