def validate_password_strength(password: str) -> str:
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter.")
    return password


def check_password_match(password: str, confirm_password: str) -> str:
    if password != confirm_password:
        raise ValueError("Passwords do not match.")
    return confirm_password
