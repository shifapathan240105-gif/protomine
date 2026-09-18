# ProtoMine - Complete Setup Guide (From Scratch)

This guide builds ProtoMine using only free tools: PubMed (free, no key)
for searching papers, and Google Gemini's free API tier (no credit card)
for extracting structured data. No paid plans of any kind are needed.

## What You Need Before Starting
- A Windows laptop with internet access
- A Google account (any Gmail works) - for the free Gemini key
- About 20-30 minutes

---

## STEP 1: Install Python

1. Go to **python.org/downloads**
2. Download and run the installer
3. **Important:** On the first screen, check the box "Add python.exe to PATH"
4. Click "Install Now"

**Verify it worked:** Open Command Prompt and type:
```
py --version
```
You should see something like `Python 3.14.2`. If it says "not recognized",
Python didn't install correctly - reinstall and make sure to check the PATH box.

---

## STEP 2: Create your project folder

1. Create a new folder anywhere, e.g. Desktop, named `protomine`
2. Put these 5 files inside it: `search.py`, `extract.py`, `app.py`,
   `requirements.txt`, and this guide

---

## STEP 3: Get a FREE Gemini API key (no card required)

1. Go to **aistudio.google.com/apikey**
2. Sign in with any Google account
3. Click **"Create API Key"**
4. Accept the terms if prompted, choose the default project
5. Copy the key that appears (starts with `AQ.` or similar) - save it
   somewhere temporarily, like Notepad

This is completely free - no billing, no card needed, generous usage limits
for a student project.

---

## STEP 4: Install dependencies

1. Open the `protomine` folder in File Explorer
2. Click the address bar, type `cmd`, press Enter (opens Command Prompt
   already inside that folder)
3. Type:
```
py -m pip install -r requirements.txt
```
4. Wait for it to finish (a minute or two, lots of text is normal)

---

## STEP 5: Set your API key

In the same Command Prompt window, type (replace with your real key):
```
set GEMINI_API_KEY=your-actual-key-here
```
Press Enter. No message appears - that's normal, it worked.

**Note:** This only lasts for this Command Prompt session. Every time you
open a new Command Prompt window to run the app, you must repeat this step.

---

## STEP 6: Run the app

```
py -m streamlit run app.py
```

Your browser should open automatically to `http://localhost:8501`.
If Windows Firewall asks for permission, click "Allow".

---

## STEP 7: Test it

Type a research question, for example:
```
curcumin concentration used against COX-2 inflammation
```
Click **"Search & Extract Protocols"** and wait a few seconds.

Other good test queries:
```
neem extract antimicrobial activity Staphylococcus aureus
green tea EGCG concentration acne treatment
```

---

## How It Works (for your own understanding / Q&A prep)

1. **search.py** - sends your question to PubMed (a free U.S. National
   Library of Medicine database), gets back a list of matching papers
   with their abstracts
2. **extract.py** - sends each abstract's text to Google Gemini with
   instructions to pull out specific fields (compound, concentration,
   target, method, model, finding) as structured data
3. **app.py** - the Streamlit web interface that ties it together: takes
   your typed question, calls search.py, then extract.py, and displays
   the results as a table you can browse or download

## Troubleshooting

- **"pip is not recognized"** → use `py -m pip` instead of `pip`
- **"python is not recognized"** → use `py` instead of `python`
- **429 error / rate limited** → wait a few minutes and try again;
  PubMed rarely rate-limits but it can happen under heavy use
- **App runs but shows no results** → try a simpler, shorter query
- **Need to restart later** → re-open Command Prompt in the folder,
  repeat Step 5 (set the key again), then Step 6 (run the app)
