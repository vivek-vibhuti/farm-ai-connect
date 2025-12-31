from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime
import logging

from models import init_db, save_prediction
from ml_model import predict_crop_health
from satellite import get_satellite_data
from voice import generate_voice_message
from whatsapp import send_whatsapp_notification

# Initialize FastAPI
app = FastAPI(title="FarmConnect AI API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Request models
class FarmerQuery(BaseModel):
    farmer_name: str
    phone: str
    region: str
    crop_type: str
    coordinates: Optional[dict] = None

@app.get("/")
def root():
    return {
        "message": "FarmConnect AI API - Hyper-Local Agricultural Advisory",
        "version": "1.0.0",
        "status": "operational"
    }

@app.post("/api/v1/predict")
async def predict_crop(
    region: str = Form(...),
    crop_type: str = Form(...),
    farmer_name: str = Form(...),
    phone: str = Form(""),
    latitude: float = Form(None),
    longitude: float = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Main prediction endpoint
    - Fetches satellite data if coordinates provided
    - Analyzes crop health using ML
    - Generates recommendation
    - Sends voice message + WhatsApp notification
    """
    try:
        logger.info(f"Prediction request for {farmer_name} in {region}")
        
        # Step 1: Get satellite data
        satellite_data = None
        if latitude and longitude:
            satellite_data = get_satellite_data(latitude, longitude)
            logger.info(f"Satellite data retrieved: NDVI={satellite_data.get('ndvi', 'N/A')}")
        
        # Step 2: Process uploaded image or use satellite data
        image_path = None
        if image:
            image_path = f"./temp/{image.filename}"
            with open(image_path, "wb") as f:
                f.write(await image.read())
        
        # Step 3: ML prediction
        prediction = predict_crop_health(
            image_path=image_path,
            satellite_data=satellite_data,
            crop_type=crop_type,
            region=region
        )
        
        # Step 4: Generate recommendation
        recommendation = generate_recommendation(
            crop_health=prediction['health_score'],
            pest_detected=prediction['pest_type'],
            disease_detected=prediction['disease_type'],
            crop_type=crop_type,
            region=region
        )
        
        # Step 5: Generate voice message (Odia)
        voice_url = generate_voice_message(
            recommendation_text=recommendation['message'],
            language="odia"
        )
        
        # Step 6: Send WhatsApp notification (if phone provided)
        if phone:
            send_whatsapp_notification(
                phone=phone,
                message=recommendation['message'],
                voice_url=voice_url
            )
        
        # Step 7: Save to database
        save_prediction(
            farmer_name=farmer_name,
            region=region,
            crop_type=crop_type,
            health_score=prediction['health_score'],
            pest_type=prediction['pest_type'],
            recommendation=recommendation['message']
        )
        
        # Response
        response = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "farmer": farmer_name,
            "region": region,
            "crop_type": crop_type,
            "analysis": {
                "crop_health": prediction['health_score'],
                "health_status": prediction['health_status'],
                "pest_detected": prediction['pest_type'],
                "disease_detected": prediction['disease_type'],
                "confidence": prediction['confidence']
            },
            "satellite_data": satellite_data,
            "recommendation": {
                "action": recommendation['action'],
                "timing": recommendation['timing'],
                "cost": recommendation['cost'],
                "market_price": recommendation['market_price'],
                "full_message": recommendation['message']
            },
            "voice_message_url": voice_url,
            "notification_sent": bool(phone)
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/history/{farmer_name}")
def get_farmer_history(farmer_name: str):
    """Get prediction history for a farmer"""
    from models import get_farmer_history
    history = get_farmer_history(farmer_name)
    return {"farmer": farmer_name, "history": history}

@app.get("/api/v1/market-prices/{region}")
def get_market_prices(region: str):
    """Get current market prices for region"""
    # Mock data - replace with real API
    prices = {
        "Cuttack": {"paddy": 450, "wheat": 520, "pulses": 680},
        "Khurda": {"paddy": 440, "wheat": 510, "pulses": 670},
        "Puri": {"paddy": 455, "wheat": 525, "pulses": 690},
    }
    return {"region": region, "prices": prices.get(region, {})}

def generate_recommendation(crop_health, pest_detected, disease_detected, crop_type, region):
    """Generate actionable recommendation"""
    
    # Disease/Pest action mapping
    actions = {
        "Brown Spot": {
            "action": "Spray neem oil or mancozeb fungicide",
            "timing": "Within 2-3 days, avoid rainy period",
            "cost": "₹300-500 per acre"
        },
        "BPH": {
            "action": "Flood field for 3 days, drain, and apply imidacloprid",
            "timing": "Immediate action required",
            "cost": "₹400-600 per acre"
        },
        "Blast": {
            "action": "Apply tricyclazole fungicide",
            "timing": "Within 48 hours",
            "cost": "₹350-550 per acre"
        },
        "Healthy": {
            "action": "Continue regular monitoring",
            "timing": "No immediate action",
            "cost": "₹0"
        }
    }
    
    # Get action details
    action_data = actions.get(pest_detected or disease_detected, actions["Healthy"])
    
    # Get market price
    market_prices = get_market_prices(region)
    price = market_prices.get("prices", {}).get(crop_type.lower(), "N/A")
    
    # Generate message
    if crop_health < 50:
        urgency = "URGENT"
    elif crop_health < 70:
        urgency = "MODERATE"
    else:
        urgency = "LOW"
    
    message = f"""
{urgency} ADVISORY for {crop_type} in {region}

Crop Health: {crop_health}% ({pest_detected or disease_detected} detected)

ACTION: {action_data['action']}
TIMING: {action_data['timing']}
ESTIMATED COST: {action_data['cost']}

MARKET UPDATE: Current {crop_type} price is ₹{price}/quintal

This is an AI-generated advisory. For complex issues, consult local agricultural officer.
    """.strip()
    
    return {
        "action": action_data['action'],
        "timing": action_data['timing'],
        "cost": action_data['cost'],
        "market_price": f"₹{price}/quintal",
        "message": message
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
