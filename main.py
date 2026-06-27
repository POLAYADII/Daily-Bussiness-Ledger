import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from groq import Groq

# 1. Load your secret key from the .env file safely
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 2. Initialize FastAPI
app = FastAPI()

# 3. Enable CORS so your index.html file can talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Initialize the Groq AI client
groq_client = Groq(api_key=GROQ_API_KEY)

# 5. This is our temporary memory (The Commerce Ledger Notebook)
commerce_ledger = ["Sold 2 items for ₹500", "Paid shop rent ₹2000"]


# --- THE THREE SIMPLE OPERATIONS ---

# OPERATION 1: GET (View the ledger)
@app.get("/ledger")
def view_ledger():
    return {"daily_records": commerce_ledger}

# OPERATION 2: POST (Add a new transaction)
@app.post("/ledger")
def add_transaction(text_detail: str):
    commerce_ledger.append(text_detail)
    return {"message": "Transaction logged!", "current_ledger": commerce_ledger}

# OPERATION 3: DELETE (Reset the ledger for a new day)
@app.delete("/ledger")
def reset_ledger():
    commerce_ledger.clear()
    return {"message": "Ledger cleared for the next business day!"}


# --- THE AI ENDPOINT ---

@app.post("/ai-analysis")
def analyze_business():
    if not commerce_ledger:
        return {"business_insight": "Your ledger is currently empty. Add some transactions first!"}

    # Convert our list of transactions into one big paragraph for the AI to read
    ledger_text = ", ".join(commerce_ledger)
    
    # Send the ledger text to Groq AI
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful business consultant. Analyze the following shop ledger transactions and give a short 1-sentence summary of how the business is doing financially."},
            {"role": "user", "content": ledger_text}
        ]
    )
    
    ai_answer = response.choices[0].message.content
    return {"business_insight": ai_answer}


# --- RUN WITHOUT MANUAL UVICORN COMMAND ---
# This block lets you run the app by clicking the VS Code "Play" button!
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)