# 📚 AI-Powered Smart Library Management System

Welcome to the **AI-Powered Smart Library Management System** – a Python-based project built for managing a library using smart features like AI-based recommendations, automated borrowing logs, and a simple database.

This project is designed for high schoolers, hobby coders, or beginners with a basic understanding of Python, file handling, and libraries like SQLite and `scikit-learn`.

---

## ✅ Key Features

### 1. **📖 Book Database & Storage**
- Stores book details (title, author, genre, ISBN, availability) in an **SQLite database**.
- Supports **CSV/JSON** export for backups.
- Import bulk books from text files.

### 2. **🧠 AI-Based Book Recommendations**
- Recommends books based on **genre**, **author**, or **past borrow history**.
- Uses **TF-IDF** from `scikit-learn` to compare book descriptions.

### 3. **🔍 Smart Search & Filtering**
- Search for books by **title, author, genre, or keywords**.
- Filter by **available** or **borrowed** status.

### 4. **🔁 Borrowing & Return System**
- Lets users **borrow or return** books.
- Tracks **due dates** and **notifies** (text logs) users for overdue books.

### 5. **📛 Duplicate Book Detection**
- Detects duplicate books using **MD5 hashing**.
- Warns admin if a book already exists in the database.