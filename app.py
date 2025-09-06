# app.py
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import joblib

app = FastAPI()

# Mount static folder (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory="images"), name="images")

templates = Jinja2Templates(directory="templates")

# Load model
model = joblib.load("happiness-model.pkl")

# ---- Auth ----
USERNAME = "gokul"
PASSWORD = "bitsathy"

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == USERNAME and password == PASSWORD:
        return RedirectResponse(url="/input", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials!"})


# ---- Input Page ----
@app.get("/input", response_class=HTMLResponse)
async def input_page(request: Request):
    return templates.TemplateResponse("input.html", {"request": request})


# ---- Prediction ----
@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request,
    economy: float = Form(...),
    family: float = Form(...),
    health: float = Form(...),
    freedom: float = Form(...),
    trust: float = Form(...),
    generosity: float = Form(...)
):
    input_data = pd.DataFrame({
        'Economy (GDP per Capita)': [economy],
        'Family': [family],
        'Health (Life Expectancy)': [health],
        'Freedom': [freedom],
        'Trust (Government Corruption)': [trust],
        'Generosity': [generosity]
    })
    
    prediction = model.predict(input_data)[0]
    predicted_rank = int(round(prediction))

    # Determine label, image, and the new level_class for styling
    if predicted_rank <= 30:
        label, image, level_class = "Very High 😊", "very_high.png", "very-high"
    elif predicted_rank <= 60:
        label, image, level_class = "High 🙂", "high.png", "high"
    elif predicted_rank <= 90:
        label, image, level_class = "Medium 😐", "medium.png", "medium"
    elif predicted_rank <= 120:
        label, image, level_class = "Low 🙁", "low.png", "low"
    else:
        label, image, level_class = "Very Low 😞", "very_low.png", "very-low"

    return templates.TemplateResponse("result.html", {
        "request": request,
        "rank": predicted_rank,
        "label": label,
        "image": f"/images/{image}",
        "level_class": level_class,  # <-- This is the key change!
        "inputs": {
            "Economy": economy,
            "Family": family,
            "Health": health,
            "Freedom": freedom,
            "Trust": trust,
            "Generosity": generosity
        }
    })
