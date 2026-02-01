# Food Based Web Service (RAG Powered)

A Django-based project for food image processing and health advice using Retrieval-Augmented Generation (RAG).


## ⚠️ Important: Hardware Requirements
* **GPU:** NVIDIA RTX 3050, Tesla T4, or higher (Minimum 4GB VRAM).
* **Storage:** 15GB free space .
* **Performance:** This project requires an NVIDIA GPU. It will be extremely slow or crash on a normal CPU.

---

## 🚀 How to Run (Full A-Z Steps)

### Step 1: Install Required Software
Install these 3 tools in this order:
1. **Python 3.10+**: [Download here](https://www.python.org/downloads/). (**IMPORTANT:** During installation, you MUST check the box that says **"Add Python to PATH"**).
2. **Git**: [Download here](https://git-scm.com/downloads).
3. **VS Code**: [Download here](https://code.visualstudio.com/).

### Step 2: Download the Project
1. Go to your Desktop.
2. Right-click on your wallpaper and select **"Git Bash Here"**.
3. Copy and paste this command, then press Enter:
   ```bash
   git clone [https://github.com/seshu-green/Food_based_service.git](https://github.com/seshu-green/Food_based_service.git)
You will see a folder called Food_based_service on your Desktop.

Step 3: Open and Setup in VS Code
Open VS Code.

Go to File > Open Folder and select the Food_based_service folder from your Desktop.

Open the Terminal inside VS Code (Go to top menu: Terminal > New Terminal).

Step 4: Install AI Libraries
In the terminal at the bottom of VS Code, paste this and press Enter:

Bash
pip install -r requirements.txt
(Wait 5-10 minutes. It is downloading the data required).

Step 5: Start the Server
In the same terminal, type this and press Enter:

Bash
python manage.py runserver

Keep this window open. Now open your browser and go to: http://127.0.0.1:8000/user/log
This si a demo or prototype not ready for deplyoment use this details.
🔑 Demo Login Details
Email: lseshu3@gmail.com

Name: seshu

Password: Lseeshu@201

DOB: 01-11-2006

📌 Usage Tips & Drawbacks
Add New Dishes: To make the bot smarter, go to the Admin Panel at http://127.0.0.1:8000/admin/ and add more food images and nutrition tips.

Database Limit: If a food item is not in the database, the bot cannot identify it correctly.

GPU Only: Strictly requires an NVIDIA GPU for the AI to process images and answer quickly.

📧 Contact any doubt or problem plz contact me at this:
Email: lseshu3@gmail.com
IIT TIRUPATI ch24b019@iittp.ac.in
GitHub: https://github.com/seshu-green/Food_based_service
