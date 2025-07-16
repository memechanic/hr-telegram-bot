import re

def is_text(text: str) -> bool:
    return text.strip().isalpha()

def is_phone_number(number: str) -> bool:
    number = number.strip()
    return bool(re.match(r'^((\+7)|(8))\d{10}$', number))

def is_email(email: str) -> bool:
    email = email.strip()
    return bool(re.match(r'^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$', email))