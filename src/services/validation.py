import re

from fastapi import UploadFile, HTTPException, status

phone_pattern = re.compile(r'^\+?\d{12,15}$')
password_pattern = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$")


def validate_phone_number(phone_number: str):
    if phone_number and not phone_pattern.match(phone_number):
        raise ValueError(
            "The phone number should first consist of the symbol '+' "
            "or without it, and then include 12 to 15 digits"
        )


def validate_password(password: str):
    if not password_pattern.match(password):
        raise ValueError(
            "Password is not valid! The password must consist of at least one lowercase, "
            "uppercase letter, number and symbols."
        )


async def validate_image(file: UploadFile) -> UploadFile:
    if not (file.filename.endswith(".jpg") or file.filename.endswith(".png")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is not a .jpg or .png image"
        )
    return file
