# PDF Vault

PDF Vault is a desktop application built with Python for protecting PDF documents using password-based encryption. It provides a simple interface for encrypting, decrypting, changing, and removing PDF passwords while processing all files locally.
<img width="993" height="700" alt="image" src="https://github.com/user-attachments/assets/fdd55a7b-0d57-4904-9622-4a5286c51178" />

---

## Features

* Encrypt PDF files
* Decrypt password-protected PDFs
* Change PDF passwords
* Remove passwords from PDFs
* Batch processing
* Drag and drop support
* Password generator
* Password strength analyzer
* SHA-256 file integrity verification
* Operation history
* Export logs to CSV and JSON
* Custom output directory selection

---

## Project Structure

```text
PDF-Vault/

├── app.py
├── core.py
├── README.md
└── .gitignore
```

---

## Technologies

* Python 3
* CustomTkinter
* tkinterdnd2
* PyPDF2
* hashlib
* secrets
* JSON
* CSV

---

## Installation

Clone the repository:

```bash
git clone https://github.com/sakshyampudasaini/PDF-Vault.git
```

Navigate into the project:

```bash
cd PDF-Vault
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

---

## How It Works

The application allows users to select one or more PDF files and perform password-related operations through a desktop interface.

Supported operations include:

* Encrypt
* Decrypt
* Change Password
* Remove Password

Each operation is recorded locally with its timestamp, file information, checksum, and status. Logs can be exported in CSV or JSON format.

---

## Security

* Files are processed locally.
* No data is uploaded to external servers.
* SHA-256 checksums are generated for integrity verification.
* Passwords are used only during the selected operation.

---

## Future Improvements

* Migration to pikepdf
* Digital signature support
* PDF permission management
* Automatic updates
* Unit tests
* Cross-platform packaging

---

## Disclaimer

This project is intended for educational purposes and for processing PDF files that you own or have permission to modify.

---

## Author

**Sakshyam Pudasaini**

GitHub: https://github.com/sakshyampudasaini

---

## License

This project is licensed under the MIT License.
