## **Machine Learning Environment Setup**

This project uses a Python **virtual environment** (recommended in Kali Linux due to PEP-668 restrictions).
Follow the steps below to set up the environment and install all dependencies.

---

### **1. Install Python venv (Required for Kali Linux)**

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip
```

---

### **2. Create Virtual Environment**

```bash
python3 -m venv ml-env
```

---

### **3. Activate the Environment**

```bash
source ml-env/bin/activate
```

When activated, your terminal will show:

```
(ml-env) user@kali:~/project$
```

---

### **4. Install Required Python Packages**

Inside the activated venv:

```bash
pip install numpy pandas scikit-learn xgboost lightgbm scapy
```

(Scapy can also be installed via `apt`, but pip version is fine.)

---

### **5. Deactivate Environment**

```bash
deactivate
```

---

### **6. Reactivate Later Whenever Needed**

```bash
source ml-env/bin/activate
```

---

### **Notes**

* The `ml-env/` folder is **ignored** using `.gitignore`.
* You only need to create the environment **once per machine**.
* Never upload the venv to GitHub — only share the instructions and a `requirements.txt` if needed.

