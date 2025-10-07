import string
import secrets
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))
print(generate_password())
if __name__ == "__main__":
    generate_password()
    print(generate_password())
    print(generate_password(16))
    print(generate_password(20))
    print(generate_password(24))
    print(generate_password(28))
    print(generate_password(32))
    print(generate_password(36))
    print(generate_password(40))
    print(generate_password(44))
    print(generate_password(48))
