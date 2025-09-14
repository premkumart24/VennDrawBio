def save_name (Name: str, file_path: str = "emails.txt") -> None:
    with open (file_path, "a") as f:
        f.write(Name + " ")

def save_email_to_file(email: str, file_path: str = "emails.txt") -> None:
    with open(file_path, "a") as f:
        f.write(email + " ")

def is_valid_email(email: str) -> bool:
    return "@" in email and len(email.split("@")[0]) >= 3
