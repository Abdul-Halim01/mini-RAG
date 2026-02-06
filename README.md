# mini-RAG

this is a minimal implemntaion of the RAG model for question answering.

## Requiremnents
- python 3.8 or higher

## 📦 Project Setup (Using uv)

This project uses **[uv](https://github.com/astral-sh/uv)** — a fast Python package manager and environment tool — instead of traditional `pip` or `poetry`.

---

## 🚀 1. Install uv

### ✅ Recommended (Official Installer)

#### Linux / macOS:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

### 👉 Alternative (via pip)

If Python is already installed:

```bash
pip install uv
```

---

## 📥 2. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

Replace the URL with your repository link.

---

## 🐍 3. Create Virtual Environment

```bash
uv venv
```

This will create a local `.venv` environment.

---

## ▶️ 4. Activate the Environment

### Windows:

```bash
.venv\Scripts\activate
```

### Linux / macOS:

```bash
source .venv/bin/activate
```

---

## 📚 5. Install Dependencies

```bash
uv sync
```

This installs all dependencies listed in:

* `pyproject.toml`
* `uv.lock`

---

## ▶️ 6. Run the Project

Example:

```bash
uv run python src/main.py
```

(Adjust the entry file depending on your project.)

---

## 🧪 Development Dependencies (Optional)

To install dev dependencies:

```bash
uv sync --dev
```

---

## 📌 Notes

* No `requirements.txt` needed
* Dependencies managed via `pyproject.toml`
* `uv.lock` ensures reproducible installs
* Much faster than traditional pip workflows
