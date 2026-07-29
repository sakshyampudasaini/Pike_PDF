
import os
import csv
import json
import hashlib
import string
import secrets
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from PyPDF2 import PdfReader, PdfWriter


class PDFVaultEngine:
    def __init__(self, log_file: str = "pdf_vault_history.json"):
        self.log_file = log_file
        self.history: List[Dict] = self._load_history()

    # ------------------ FILE INTEGRITY ------------------

    @staticmethod
    def calculate_sha256(file_path: str) -> str:
        """Calculate SHA-256 checksum for file integrity verification."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    # ------------------ PASSWORD UTILITIES ------------------

    @staticmethod
    def generate_password(
        length: int = 16,
        use_digits: bool = True,
        use_symbols: bool = True,
        use_uppercase: bool = True,
    ) -> str:
        """Generate a cryptographically secure random password."""
        chars = string.ascii_lowercase
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_digits:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

        if not chars:
            chars = string.ascii_lowercase

        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def analyze_password_strength(password: str) -> Tuple[str, float, str]:
        """
        Analyze password strength.
        Returns (Rating, Score 0.0-1.0, Feedback text).
        """
        if not password:
            return "Empty", 0.0, "Password cannot be empty."

        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        score = 0
        feedback = []

        if length >= 8:
            score += 20
        else:
            feedback.append("Increase length to at least 8 characters.")

        if length >= 12:
            score += 20

        if has_upper and has_lower:
            score += 20
        else:
            feedback.append("Mix uppercase and lowercase letters.")

        if has_digit:
            score += 20
        else:
            feedback.append("Include numbers.")

        if has_symbol:
            score += 20
        else:
            feedback.append("Include special symbols.")

        normalized_score = min(1.0, max(0.0, score / 100.0))

        if score < 40:
            rating = "Weak"
        elif score < 80:
            rating = "Moderate"
        elif score < 100:
            rating = "Strong"
        else:
            rating = "Very Strong"

        feedback_str = " ".join(feedback) if feedback else "Excellent password security."
        return rating, normalized_score, feedback_str

    # ------------------ PDF CORE OPERATIONS ------------------

    def encrypt_pdf(
        self, input_path: str, output_path: str, user_pwd: str, owner_pwd: Optional[str] = None
    ) -> bool:
        """Encrypt a PDF with user and optional owner password."""
        reader = PdfReader(input_path)
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        owner = owner_pwd if owner_pwd else user_pwd
        writer.encrypt(user_password=user_pwd, owner_password=owner)

        with open(output_path, "wb") as f:
            writer.write(f)

        self.add_history_entry("Encrypt", input_path, output_path, "Success")
        return True

    def decrypt_pdf(
        self, input_path: str, output_path: str, password: str
    ) -> Tuple[bool, str]:
        """Decrypt a protected PDF using its password."""
        reader = PdfReader(input_path)

        if reader.is_encrypted:
            success = reader.decrypt(password)
            if not success:
                self.add_history_entry("Decrypt", input_path, output_path, "Failed (Bad Password)")
                return False, "Incorrect password."

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        with open(output_path, "wb") as f:
            writer.write(f)

        self.add_history_entry("Decrypt", input_path, output_path, "Success")
        return True, "Decryption successful."

    def change_password(
        self, input_path: str, output_path: str, current_pwd: str, new_pwd: str
    ) -> Tuple[bool, str]:
        """Change the password of an encrypted PDF."""
        reader = PdfReader(input_path)

        if reader.is_encrypted:
            success = reader.decrypt(current_pwd)
            if not success:
                self.add_history_entry("Change Password", input_path, output_path, "Failed (Bad Password)")
                return False, "Current password incorrect."

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(user_password=new_pwd, owner_password=new_pwd)

        with open(output_path, "wb") as f:
            writer.write(f)

        self.add_history_entry("Change Password", input_path, output_path, "Success")
        return True, "Password changed successfully."

    def remove_password(
        self, input_path: str, output_path: str, current_pwd: str
    ) -> Tuple[bool, str]:
        """Remove password from an encrypted PDF (unprotect)."""
        return self.decrypt_pdf(input_path, output_path, current_pwd)

    # ------------------ HISTORY & LOGGING ------------------

    def add_history_entry(
        self, operation: str, input_path: str, output_path: str, status: str
    ):
        """Log an operation into local memory and JSON file."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "input_file": os.path.basename(input_path),
            "input_path": input_path,
            "output_path": output_path,
            "checksum": self.calculate_sha256(input_path) if os.path.exists(input_path) else "N/A",
            "status": status,
        }
        self.history.insert(0, entry)
        self._save_history()

    def _save_history(self):
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def _load_history(self) -> List[Dict]:
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def export_logs_json(self, export_path: str):
        """Export operation log to JSON file."""
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4)

    def export_logs_csv(self, export_path: str):
        """Export operation log to CSV file."""
        if not self.history:
            return

        keys = self.history[0].keys()
        with open(export_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(self.history)