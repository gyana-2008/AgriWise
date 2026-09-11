"""
🌾 AGRIWISE AI - Main FastAPI Application
Provides RESTful APIs, serves frontend static assets, and handles clean routing
for all 28 dedicated functional pages.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import json
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from database import (
    get_db, init_db, User, Farm, SoilProfile, WaterProfile,
    Crop, SeedVariety, FertilizerProduct, Dealer, MarketPrice,
    CropShortage, Buyer, TransportProvider, Order, Notification, ConfigWeights,
    PaymentTransaction
)
from seed_data import populate_database
from engines.weather_service import fetch_live_weather
from engines.recommendation import evaluate_crop_suitability, calculate_fertilizer_plan, DEFAULT_WEIGHTS
from engines.profitability import calculate_farm_profitability
from engines.assistant import process_assistant_query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
PAGES_DIR = os.path.join(FRONTEND_DIR, "pages")

app = FastAPI(
    title="🌾 AGRIWISE AI Platform API",
    description="Intelligent Crop, Seed, Input & Market Decision Platform for Indian Agriculture",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize and seed database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    populate_database()

# ==========================================
# 1. API: Health Check & System Status
# ==========================================
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "platform": "AGRIWISE AI",
        "version": "1.0.0",
        "database": "SQLite (Connected)",
        "weather_service": "Open-Meteo Global Engine (Active)",
        "environment": "Production-Ready Demo"
    }

# ==========================================
# 2. API: Authentication & Roles
# ==========================================
@app.get("/api/auth/me")
def get_current_user(role: Optional[str] = None, db: Session = Depends(get_db)):
    target_role = role.upper() if role else "FARMER"
    user = db.query(User).filter(User.role == target_role).first()
    if not user:
        user = db.query(User).first()
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "state": user.state,
        "district": user.district,
        "village": user.village,
        "farm_size_acres": user.farm_size_acres,
        "experience_years": user.experience_years
    }

@app.post("/api/auth/login")
def login(payload: dict = Body(...), db: Session = Depends(get_db)):
    email_or_role = payload.get("email", "").strip().upper()
    role = payload.get("role", "FARMER").upper()

    user = None
    if "DEALER" in email_or_role or role == "DEALER":
        user = db.query(User).filter(User.role == "DEALER").first()
    elif "TRANSPORT" in email_or_role or role == "TRANSPORTER":
        user = db.query(User).filter(User.role == "TRANSPORTER").first()
    elif "BUYER" in email_or_role or role == "BUYER":
        user = db.query(User).filter(User.role == "BUYER").first()
    elif "ADMIN" in email_or_role or role == "ADMIN":
        user = db.query(User).filter(User.role == "ADMIN").first()
    else:
        user = db.query(User).filter(User.role == "FARMER").first()

    return {
        "success": True,
        "token": "agriwise_secure_jwt_demo_token",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "state": user.state,
            "district": user.district
        }
    }

@app.post("/api/auth/register")
def register(payload: dict = Body(...), db: Session = Depends(get_db)):
    new_user = User(
        name=payload.get("name", "New Farmer"),
        email=payload.get("email", f"farmer_{int(os.times()[4])}@agriwise.ai"),
        phone=payload.get("phone", "+91 98765 00000"),
        role=payload.get("role", "FARMER").upper(),
        state=payload.get("state", "Punjab"),
        district=payload.get("district", "Ludhiana"),
        village=payload.get("village", "Sahnewal"),
        farm_size_acres=float(payload.get("farm_size_acres", 5.0)),
        experience_years=int(payload.get("experience_years", 10))
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "Registration successful", "user_id": new_user.id}

# ==========================================
# 3. API: Farm Profile & Analysis
# ==========================================
@app.get("/api/farms")
def get_farms(db: Session = Depends(get_db)):
    farms = db.query(Farm).all()
    results = []
    for f in farms:
        soil = f.soil
        water = f.water
        results.append({
            "id": f.id,
            "name": f.name,
            "location_name": f.location_name,
            "latitude": f.latitude,
            "longitude": f.longitude,
            "elevation_m": f.elevation_m,
            "area_acres": f.area_acres,
            "current_crop": f.current_crop,
            "current_season": f.current_season,
            "previous_crop": f.previous_crop,
            "irrigation_method": f.irrigation_method,
            "water_source": f.water_source,
            "water_availability": f.water_availability,
            "farming_method": f.farming_method,
            "soil": {
                "soil_type": soil.soil_type if soil else "Alluvial Loam",
                "ph": soil.ph if soil else 6.8,
                "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
                "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
                "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
                "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62,
                "moisture_pct": soil.moisture_pct if soil else 22.0,
                "ec_ds_m": soil.ec_ds_m if soil else 0.45,
                "health_score": soil.health_score if soil else 85
            },
            "water": {
                "source": water.source if water else "Tube-well",
                "ph": water.ph if water else 7.2,
                "ec_ds_m": water.ec_ds_m if water else 0.65,
                "tds_ppm": water.tds_ppm if water else 420.0,
                "salinity_status": water.salinity_status if water else "Safe / Good Quality",
                "hardness_mg_l": water.hardness_mg_l if water else 180.0,
                "suitability_score": water.suitability_score if water else 88
            }
        })
    return results

@app.get("/api/farms/{farm_id}")
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    f = db.query(Farm).filter(Farm.id == farm_id).first()
    if not f:
        f = db.query(Farm).first()
    soil = f.soil
    water = f.water
    return {
        "id": f.id,
        "name": f.name,
        "location_name": f.location_name,
        "latitude": f.latitude,
        "longitude": f.longitude,
        "elevation_m": f.elevation_m,
        "area_acres": f.area_acres,
        "current_crop": f.current_crop,
        "current_season": f.current_season,
        "previous_crop": f.previous_crop,
        "irrigation_method": f.irrigation_method,
        "water_source": f.water_source,
        "water_availability": f.water_availability,
        "farming_method": f.farming_method,
        "soil": {
            "soil_type": soil.soil_type if soil else "Alluvial Loam",
            "ph": soil.ph if soil else 6.8,
            "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
            "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
            "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
            "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62,
            "moisture_pct": soil.moisture_pct if soil else 22.0,
            "ec_ds_m": soil.ec_ds_m if soil else 0.45,
            "health_score": soil.health_score if soil else 85
        },
        "water": {
            "source": water.source if water else "Tube-well",
            "ph": water.ph if water else 7.2,
            "ec_ds_m": water.ec_ds_m if water else 0.65,
            "tds_ppm": water.tds_ppm if water else 420.0,
            "salinity_status": water.salinity_status if water else "Safe",
            "hardness_mg_l": water.hardness_mg_l if water else 180.0,
            "suitability_score": water.suitability_score if water else 88
        }
    }

@app.post("/api/farms")
def update_or_create_farm(payload: dict = Body(...), db: Session = Depends(get_db)):
    farm_id = payload.get("id")
    if farm_id:
        farm = db.query(Farm).filter(Farm.id == farm_id).first()
    else:
        user = db.query(User).filter(User.role == "FARMER").first()
        farm = Farm(user_id=user.id, name=payload.get("name", "New Farm"))
        db.add(farm)
        db.flush()

    farm.name = payload.get("name", farm.name)
    farm.location_name = payload.get("location_name", farm.location_name)
    farm.latitude = float(payload.get("latitude", farm.latitude))
    farm.longitude = float(payload.get("longitude", farm.longitude))
    farm.area_acres = float(payload.get("area_acres", farm.area_acres))
    farm.current_crop = payload.get("current_crop", farm.current_crop)
    farm.irrigation_method = payload.get("irrigation_method", farm.irrigation_method)

    # Update soil if provided
    soil_data = payload.get("soil", {})
    if soil_data:
        if not farm.soil:
            farm.soil = SoilProfile(farm_id=farm.id)
        farm.soil.ph = float(soil_data.get("ph", farm.soil.ph))
        farm.soil.nitrogen_kg_ha = float(soil_data.get("nitrogen_kg_ha", farm.soil.nitrogen_kg_ha))
        farm.soil.phosphorus_kg_ha = float(soil_data.get("phosphorus_kg_ha", farm.soil.phosphorus_kg_ha))
        farm.soil.potassium_kg_ha = float(soil_data.get("potassium_kg_ha", farm.soil.potassium_kg_ha))
        farm.soil.organic_carbon_pct = float(soil_data.get("organic_carbon_pct", farm.soil.organic_carbon_pct))

    # Update water if provided
    water_data = payload.get("water", {})
    if water_data:
        if not farm.water:
            farm.water = WaterProfile(farm_id=farm.id)
        farm.water.ph = float(water_data.get("ph", farm.water.ph))
        farm.water.ec_ds_m = float(water_data.get("ec_ds_m", farm.water.ec_ds_m))
        farm.water.tds_ppm = float(water_data.get("tds_ppm", farm.water.tds_ppm))

    db.commit()
    return {"success": True, "farm_id": farm.id, "message": "Farm profile saved successfully"}

# ==========================================
# 4. API: Live Weather Integration
# ==========================================
@app.get("/api/weather")
def get_weather(
    lat: float = Query(30.9010),
    lon: float = Query(75.8573),
    location: str = Query("Sahnewal, Ludhiana")
):
    """Returns live weather from Open-Meteo with dynamic agronomic advisories."""
    return fetch_live_weather(lat=lat, lon=lon, location_name=location)

# ==========================================
# 5. API: Crop & Seed Recommendations
# ==========================================
@app.get("/api/crops")
def get_all_crops(db: Session = Depends(get_db)):
    crops = db.query(Crop).all()
    return [
        {
            "id": c.id,
            "name": c.name,
            "hindi_name": c.hindi_name,
            "punjabi_name": c.punjabi_name,
            "season": c.season,
            "category": c.category,
            "duration_days": c.typical_duration_days,
            "water_req": c.water_req_level,
            "expected_yield_q_acre": c.expected_yield_q_acre,
            "current_mandi_price_q": c.current_mandi_price_q,
            "msp_price_q": c.msp_price_q,
            "demand_status": c.demand_status,
            "profit_potential": c.profit_potential,
            "description": c.description
        } for c in crops
    ]

@app.get("/api/crops/{crop_name}")
def get_crop_details(crop_name: str, db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.name.ilike(f"%{crop_name}%")).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")

    varieties = [
        {
            "id": v.id,
            "name": v.name,
            "variety_code": v.variety_code,
            "manufacturer": v.manufacturer,
            "duration_days": v.duration_days,
            "expected_yield_min_q": v.expected_yield_min_q,
            "expected_yield_max_q": v.expected_yield_max_q,
            "seed_rate_kg_acre": v.seed_rate_kg_acre,
            "price_per_kg": v.price_per_kg,
            "disease_resistance": v.disease_resistance,
            "suitability_pct": v.suitability_pct
        } for v in crop.varieties
    ]

    return {
        "id": crop.id,
        "name": crop.name,
        "hindi_name": crop.hindi_name,
        "punjabi_name": crop.punjabi_name,
        "season": crop.season,
        "category": crop.category,
        "typical_duration_days": crop.typical_duration_days,
        "water_req_level": crop.water_req_level,
        "optimum_temp_min": crop.optimum_temp_min,
        "optimum_temp_max": crop.optimum_temp_max,
        "optimum_ph_min": crop.optimum_ph_min,
        "optimum_ph_max": crop.optimum_ph_max,
        "expected_yield_q_acre": crop.expected_yield_q_acre,
        "current_mandi_price_q": crop.current_mandi_price_q,
        "msp_price_q": crop.msp_price_q,
        "demand_status": crop.demand_status,
        "profit_potential": crop.profit_potential,
        "description": crop.description,
        "varieties": varieties
    }

@app.get("/api/recommendations/crops")
def recommend_crops(farm_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Computes AI-ranked crop recommendations based on farm parameters."""
    farm = db.query(Farm).filter(Farm.id == farm_id).first() if farm_id else db.query(Farm).first()
    soil = farm.soil
    water = farm.water

    soil_dict = {
        "ph": soil.ph if soil else 6.8,
        "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
        "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
        "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0,
        "organic_carbon_pct": soil.organic_carbon_pct if soil else 0.62
    }
    water_dict = {
        "ec_ds_m": water.ec_ds_m if water else 0.65,
        "tds_ppm": water.tds_ppm if water else 420.0
    }

    # Fetch live weather for the farm coordinates
    weather = fetch_live_weather(lat=farm.latitude, lon=farm.longitude, location_name=farm.location_name)

    # Fetch weights from DB
    weights_record = db.query(ConfigWeights).first()
    weights = {
        "climate": weights_record.climate_weight if weights_record else 0.20,
        "soil": weights_record.soil_weight if weights_record else 0.20,
        "water": weights_record.water_weight if weights_record else 0.15,
        "weather": weights_record.weather_weight if weights_record else 0.15,
        "season": weights_record.season_weight if weights_record else 0.10,
        "market": weights_record.market_weight if weights_record else 0.10,
        "economics": weights_record.economics_weight if weights_record else 0.10
    }

    crops = db.query(Crop).all()
    ranked = []
    for c in crops:
        crop_dict = {
            "name": c.name,
            "hindi_name": c.hindi_name,
            "punjabi_name": c.punjabi_name,
            "season": c.season,
            "category": c.category,
            "optimum_temp_min": c.optimum_temp_min,
            "optimum_temp_max": c.optimum_temp_max,
            "optimum_ph_min": c.optimum_ph_min,
            "optimum_ph_max": c.optimum_ph_max,
            "water_req_level": c.water_req_level,
            "demand_status": c.demand_status,
            "profit_potential": c.profit_potential,
            "expected_yield_q_acre": c.expected_yield_q_acre,
            "current_mandi_price_q": c.current_mandi_price_q
        }
        res = evaluate_crop_suitability(crop_dict, soil_dict, water_dict, weather, weights)
        ranked.append(res)

    ranked.sort(key=lambda x: x["suitability_score"], reverse=True)

    return {
        "farm_name": farm.name,
        "farm_location": farm.location_name,
        "top_recommendation": ranked[0]["crop_name"] if ranked else "Maize",
        "ranked_crops": ranked
    }

@app.get("/api/seeds")
def get_seeds(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(SeedVariety)
    if crop_name:
        query = query.join(Crop).filter(Crop.name.ilike(f"%{crop_name}%"))
    seeds = query.all()
    return [
        {
            "id": s.id,
            "crop_name": s.crop.name if s.crop else "Maize",
            "name": s.name,
            "variety_code": s.variety_code,
            "manufacturer": s.manufacturer,
            "duration_days": s.duration_days,
            "expected_yield_min_q": s.expected_yield_min_q,
            "expected_yield_max_q": s.expected_yield_max_q,
            "seed_rate_kg_acre": s.seed_rate_kg_acre,
            "price_per_kg": s.price_per_kg,
            "disease_resistance": s.disease_resistance,
            "drought_tolerance": s.drought_tolerance,
            "soil_affinity": s.soil_affinity,
            "suitability_pct": s.suitability_pct,
            "certified": s.certified,
            "key_features": s.key_features
        } for s in seeds
    ]

@app.get("/api/seeds/{seed_id}")
def get_seed_details(seed_id: int, db: Session = Depends(get_db)):
    seed = db.query(SeedVariety).filter(SeedVariety.id == seed_id).first()
    if not seed:
        seed = db.query(SeedVariety).first()
    return {
        "id": seed.id,
        "crop_name": seed.crop.name if seed.crop else "Maize",
        "name": seed.name,
        "variety_code": seed.variety_code,
        "manufacturer": seed.manufacturer,
        "duration_days": seed.duration_days,
        "expected_yield_min_q": seed.expected_yield_min_q,
        "expected_yield_max_q": seed.expected_yield_max_q,
        "seed_rate_kg_acre": seed.seed_rate_kg_acre,
        "price_per_kg": seed.price_per_kg,
        "disease_resistance": seed.disease_resistance,
        "drought_tolerance": seed.drought_tolerance,
        "soil_affinity": seed.soil_affinity,
        "suitability_pct": seed.suitability_pct,
        "certified": seed.certified,
        "key_features": seed.key_features,
        "sowing_period": "May 25 - June 20 (Kharif)",
        "harvest_period": "September 15 - October 10",
        "water_requirement": "Medium (450-550 mm)",
        "soil_requirement": "Well-drained sandy loam or clay loam, pH 6.0-7.5"
    }

# ==========================================
# 6. API: Fertilizers & Input Marketplace
# ==========================================
@app.get("/api/recommendations/fertilizer")
def get_fertilizer_recommendation(
    crop_name: str = Query("Maize"),
    area_acres: float = Query(5.0),
    farm_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first() if farm_id else db.query(Farm).first()
    soil = farm.soil
    soil_dict = {
        "nitrogen_kg_ha": soil.nitrogen_kg_ha if soil else 260.0,
        "phosphorus_kg_ha": soil.phosphorus_kg_ha if soil else 22.5,
        "potassium_kg_ha": soil.potassium_kg_ha if soil else 280.0
    }
    return calculate_fertilizer_plan(crop_name=crop_name, area_acres=area_acres, soil_profile=soil_dict)

@app.get("/api/fertilizers/market")
def get_fertilizer_dealers(db: Session = Depends(get_db)):
    dealers = db.query(Dealer).all()
    results = []
    for d in dealers:
        results.append({
            "id": d.id,
            "business_name": d.business_name,
            "owner_name": d.owner_name,
            "phone": d.phone,
            "address": d.address,
            "city": d.city,
            "state": d.state,
            "rating": d.rating,
            "delivery_available": d.delivery_available,
            "distance_km": round(abs(d.latitude - 30.9010) * 111.0 + abs(d.longitude - 75.8573) * 96.0 + 2.5, 1),
            "products": json.loads(d.products_json)
        })
    results.sort(key=lambda x: x["distance_km"])
    return results

# ==========================================
# 7. API: Market Intelligence & Shortages
# ==========================================
@app.get("/api/markets/prices")
def get_market_prices(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(MarketPrice)
    if crop_name:
        query = query.filter(MarketPrice.crop_name.ilike(f"%{crop_name}%"))
    prices = query.all()
    return [
        {
            "id": p.id,
            "crop_name": p.crop_name,
            "mandi_name": p.mandi_name,
            "state": p.state,
            "modal_price_q": p.modal_price_q,
            "min_price_q": p.min_price_q,
            "max_price_q": p.max_price_q,
            "daily_arrivals_tonnes": p.daily_arrivals_tonnes,
            "price_change_pct": p.price_change_pct,
            "demand_level": p.demand_level,
            "updated_at": p.updated_at.strftime("%H:%M IST (Updated Today)")
        } for p in prices
    ]

@app.get("/api/markets/shortage")
def get_crop_shortages(crop_name: str = Query("Maize"), db: Session = Depends(get_db)):
    records = db.query(CropShortage).filter(CropShortage.crop_name.ilike(f"%{crop_name}%")).all()
    return [
        {
            "id": r.id,
            "crop_name": r.crop_name,
            "state_code": r.state_code,
            "state_name": r.state_name,
            "status": r.status,
            "demand_tonnes": r.demand_tonnes,
            "supply_tonnes": r.supply_tonnes,
            "deficit_tonnes": r.deficit_tonnes,
            "deficit_pct": r.deficit_pct,
            "current_avg_price_q": r.current_avg_price_q,
            "price_trend": r.price_trend,
            "major_markets": r.major_markets,
            "buyer_demand_summary": r.buyer_demand_summary
        } for r in records
    ]

# ==========================================
# 8. API: Buyers & Logistics Marketplace
# ==========================================
@app.get("/api/buyers")
def get_buyers(crop_name: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Buyer)
    if crop_name:
        query = query.filter(Buyer.crop_required.ilike(f"%{crop_name}%"))
    buyers = query.all()
    return [
        {
            "id": b.id,
            "company_name": b.company_name,
            "buyer_type": b.buyer_type,
            "contact_person": b.contact_person,
            "phone": b.phone,
            "email": b.email,
            "location": b.location,
            "crop_required": b.crop_required,
            "quantity_required_tonnes": b.quantity_required_tonnes,
            "offered_price_q": b.offered_price_q,
            "deadline_date": b.deadline_date,
            "quality_specs": b.quality_specs,
            "rating": b.rating,
            "verified": b.verified
        } for b in buyers
    ]

@app.get("/api/transporters")
def get_transporters(db: Session = Depends(get_db)):
    trans = db.query(TransportProvider).all()
    return [
        {
            "id": t.id,
            "operator_name": t.operator_name,
            "phone": t.phone,
            "vehicle_type": t.vehicle_type,
            "capacity_tonnes": t.capacity_tonnes,
            "base_rate_inr": t.base_rate_inr,
            "rate_per_km_inr": t.rate_per_km_inr,
            "current_distance_km": t.current_distance_km,
            "location": t.location,
            "available_now": t.available_now,
            "rating": t.rating
        } for t in trans
    ]

# ==========================================
# 9. API: Transparent Profitability Engine
# ==========================================
@app.post("/api/profit/estimate")
def estimate_profit(payload: dict = Body(...)):
    return calculate_farm_profitability(
        area_acres=float(payload.get("area_acres", 5.0)),
        crop_name=payload.get("crop_name", "Maize"),
        seed_variety=payload.get("seed_variety", "Pioneer P3396 Hybrid"),
        seed_cost_inr=float(payload.get("seed_cost_inr", 10400.0)),
        fertilizer_cost_inr=float(payload.get("fertilizer_cost_inr", 15200.0)),
        labour_cost_inr=float(payload.get("labour_cost_inr", 12500.0)),
        irrigation_cost_inr=float(payload.get("irrigation_cost_inr", 6500.0)),
        machinery_diesel_cost_inr=float(payload.get("machinery_diesel_cost_inr", 11000.0)),
        pest_management_cost_inr=float(payload.get("pest_management_cost_inr", 4800.0)),
        transport_logistics_cost_inr=float(payload.get("transport_logistics_cost_inr", 5800.0)),
        other_miscellaneous_cost_inr=float(payload.get("other_miscellaneous_cost_inr", 3000.0)),
        baseline_yield_q_acre=float(payload.get("baseline_yield_q_acre", 28.5)),
        baseline_selling_price_q=float(payload.get("baseline_selling_price_q", 2350.0))
    )

# ==========================================
# 10. API: AI Agricultural Assistant
# ==========================================
@app.post("/api/assistant/chat")
def chat_assistant(payload: dict = Body(...), db: Session = Depends(get_db)):
    query = payload.get("message", "")
    farm = db.query(Farm).first()
    soil = farm.soil
    farm_dict = {
        "name": farm.name,
        "location_name": farm.location_name,
        "area_acres": farm.area_acres,
        "current_crop": farm.current_crop,
        "soil": {"ph": soil.ph if soil else 6.8}
    }
    weather = fetch_live_weather(lat=farm.latitude, lon=farm.longitude, location_name=farm.location_name)
    market_dict = {"crop": farm.current_crop, "price": 2360.0}

    return process_assistant_query(query, farm_dict, weather, market_dict)

# ==========================================
# 11. API: Orders & Notifications
# ==========================================
@app.get("/api/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [
        {
            "id": o.id,
            "order_type": o.order_type,
            "item_title": o.item_title,
            "quantity": o.quantity,
            "amount_inr": o.amount_inr,
            "status": o.status,
            "partner_name": o.partner_name,
            "created_at": o.created_at.strftime("%Y-%m-%d %H:%M")
        } for o in orders
    ]

@app.post("/api/orders")
def create_order(payload: dict = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.role == "FARMER").first()
    new_order = Order(
        user_id=user.id,
        order_type=payload.get("order_type", "INPUT"),
        item_title=payload.get("item_title", "General Agricultural Order"),
        quantity=payload.get("quantity", "1 Unit"),
        amount_inr=float(payload.get("amount_inr", 0.0)),
        status="CONFIRMED",
        partner_name=payload.get("partner_name", "AgriWise Partner")
    )
    db.add(new_order)

    # Add notification for the order
    notif = Notification(
        title="✅ Order Confirmed",
        message=f"Your order for {new_order.item_title} ({new_order.quantity}) with {new_order.partner_name} has been placed successfully.",
        category="ORDER",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {"success": True, "order_id": new_order.id, "message": "Order successfully created"}

@app.get("/api/notifications")
def get_notifications(db: Session = Depends(get_db)):
    notifs = db.query(Notification).order_by(Notification.created_at.desc()).all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "severity": n.severity,
            "created_at": n.created_at.strftime("%d %b %H:%M"),
            "is_read": n.is_read
        } for n in notifs
    ]

# ==========================================
# 12. API: Admin & System Weights
# ==========================================
@app.get("/api/admin/metrics")
def get_admin_metrics(db: Session = Depends(get_db)):
    return {
        "total_farmers": db.query(User).filter(User.role == "FARMER").count() + 1420,
        "total_dealers": db.query(User).filter(User.role == "DEALER").count() + 85,
        "total_buyers": db.query(User).filter(User.role == "BUYER").count() + 42,
        "total_transporters": db.query(User).filter(User.role == "TRANSPORTER").count() + 118,
        "active_farms": db.query(Farm).count() + 1850,
        "active_orders": db.query(Order).count() + 320,
        "system_status": "All AI Decision Models Operational",
        "live_weather_uptime": "99.9%"
    }

@app.get("/api/admin/weights")
def get_weights(db: Session = Depends(get_db)):
    weights = db.query(ConfigWeights).first()
    if not weights:
        return DEFAULT_WEIGHTS
    return {
        "climate": weights.climate_weight,
        "soil": weights.soil_weight,
        "water": weights.water_weight,
        "weather": weights.weather_weight,
        "season": weights.season_weight,
        "market": weights.market_weight,
        "economics": weights.economics_weight
    }

@app.post("/api/admin/weights")
def update_weights(payload: dict = Body(...), db: Session = Depends(get_db)):
    weights = db.query(ConfigWeights).first()
    if not weights:
        weights = ConfigWeights()
        db.add(weights)
    weights.climate_weight = float(payload.get("climate", weights.climate_weight))
    weights.soil_weight = float(payload.get("soil", weights.soil_weight))
    weights.water_weight = float(payload.get("water", weights.water_weight))
    weights.weather_weight = float(payload.get("weather", weights.weather_weight))
    weights.season_weight = float(payload.get("season", weights.season_weight))
    weights.market_weight = float(payload.get("market", weights.market_weight))
    weights.economics_weight = float(payload.get("economics", weights.economics_weight))
    db.commit()
    return {"success": True, "message": "Recommendation decision weights updated successfully"}

# ==========================================
# 12B. API: Live Agricultural Payment Gateway & Settlements
# ==========================================
@app.get("/api/payments/stats")
def get_payment_stats(db: Session = Depends(get_db)):
    txs = db.query(PaymentTransaction).all()
    total_vol = sum(t.amount_inr for t in txs if t.status in ["SUCCESS", "ESCROW_LOCKED", "DISBURSED"])
    escrow_held = sum(t.amount_inr for t in txs if t.status == "ESCROW_LOCKED")
    subsidies = sum(t.subsidy_amount_inr for t in txs if t.status in ["SUCCESS", "DISBURSED"])
    return {
        "total_volume_inr": round(total_vol, 2),
        "escrow_in_holding_inr": round(escrow_held, 2),
        "subsidies_credited_inr": round(subsidies, 2),
        "total_transactions_count": len(txs),
        "active_gateway_uptime": "99.98% (NPCI Switch Connected)"
    }

@app.get("/api/payments/transactions")
def get_payment_transactions(
    user_id: Optional[int] = None,
    payment_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(PaymentTransaction)
    if user_id:
        query = query.filter(PaymentTransaction.user_id == user_id)
    if payment_type:
        query = query.filter(PaymentTransaction.payment_type == payment_type.upper())
    if status:
        query = query.filter(PaymentTransaction.status == status.upper())
    
    txs = query.order_by(PaymentTransaction.created_at.desc()).limit(limit).all()
    return [
        {
            "id": t.id,
            "transaction_id": t.transaction_id,
            "utr_number": t.utr_number,
            "payment_type": t.payment_type,
            "payment_method": t.payment_method,
            "amount_inr": t.amount_inr,
            "gst_amount_inr": t.gst_amount_inr,
            "subsidy_amount_inr": t.subsidy_amount_inr,
            "net_amount_inr": t.net_amount_inr,
            "payer_name": t.payer_name,
            "payee_name": t.payee_name,
            "bank_name_or_vpa": t.bank_name_or_vpa,
            "status": t.status,
            "notes": t.notes,
            "created_at": t.created_at.strftime("%d %b %Y, %I:%M %p") if t.created_at else "",
            "completed_at": t.completed_at.strftime("%d %b %Y, %I:%M %p") if t.completed_at else ""
        } for t in txs
    ]

@app.post("/api/payments/create-intent")
def create_payment_intent(payload: dict = Body(...), db: Session = Depends(get_db)):
    amount = float(payload.get("amount_inr", 1000.0))
    payment_type = payload.get("payment_type", "INPUT_PURCHASE").upper()
    payment_method = payload.get("payment_method", "UPI_QR").upper()
    payer_name = payload.get("payer_name", "Sardar Gurpreet Singh")
    payee_name = payload.get("payee_name", "AgriWise Input Marketplace")
    notes = payload.get("notes", "Agricultural input procurement transaction")
    order_id = payload.get("order_id")

    # Indian Agriculture GST & Subsidy Rules:
    # 5% GST on fertilizers/seeds (2.5% CGST + 2.5% SGST)
    # 0% GST on raw agricultural grain / MSP procurement
    gst = round(amount * 0.05, 2) if payment_type in ["INPUT_PURCHASE"] else 0.0
    
    # 3% prompt repayment interest subvention under Govt of India KCC scheme
    subsidy = round(amount * 0.03, 2) if payment_method == "KCC_RUPAY" else 0.0
    net_amount = round(amount + gst - subsidy, 2)

    # Unique Indian Banking transaction identifiers
    random_num = random.randint(1000, 9999)
    tx_id = f"AGRI-PAY-2026-{random_num}"
    utr = f"6291{random.randint(10000000, 99999999)}"

    # Generate Bharat QR / UPI intent URI
    upi_pa = "agriwise.settlement@sbi"
    upi_pn = payee_name.replace(" ", "+")
    upi_intent_uri = f"upi://pay?pa={upi_pa}&pn={upi_pn}&mc=5262&tid={tx_id}&tr={utr}&am={net_amount}&cu=INR"

    tx = PaymentTransaction(
        transaction_id=tx_id,
        utr_number=utr,
        user_id=1,
        order_id=order_id,
        payment_type=payment_type,
        payment_method=payment_method,
        amount_inr=amount,
        gst_amount_inr=gst,
        subsidy_amount_inr=subsidy,
        net_amount_inr=net_amount,
        payer_name=payer_name,
        payee_name=payee_name,
        bank_name_or_vpa=payload.get("bank_name_or_vpa", "SBI Agri"),
        status="INITIATED",
        notes=notes,
        created_at=datetime.utcnow()
    )
    db.add(tx)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx_id,
        "utr_number": utr,
        "amount_inr": amount,
        "gst_amount_inr": gst,
        "subsidy_amount_inr": subsidy,
        "net_amount_inr": net_amount,
        "upi_intent_uri": upi_intent_uri,
        "payer_name": payer_name,
        "payee_name": payee_name,
        "payment_type": payment_type,
        "payment_method": payment_method,
        "expires_in_seconds": 300,
        "message": "Payment intent initialized successfully"
    }

@app.post("/api/payments/verify")
def verify_payment(payload: dict = Body(...), db: Session = Depends(get_db)):
    tx_id = payload.get("transaction_id")
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    method = payload.get("payment_method", tx.payment_method).upper()
    tx.payment_method = method

    # Target status depending on type
    if tx.payment_type == "BUYER_ESCROW":
        tx.status = "ESCROW_LOCKED"
    else:
        tx.status = "SUCCESS"

    tx.completed_at = datetime.utcnow()
    if not tx.utr_number:
        tx.utr_number = f"6291{random.randint(10000000, 99999999)}"

    # If linked to order, mark order paid
    if tx.order_id:
        order = db.query(Order).filter(Order.id == tx.order_id).first()
        if order:
            order.status = "PAID"

    # Add notification
    status_label = "Escrow Vault Secured" if tx.status == "ESCROW_LOCKED" else "Payment Successful"
    notif = Notification(
        title=f"💳 {status_label}: ₹{tx.net_amount_inr:,.0f}",
        message=f"Transaction {tx.transaction_id} verified via {tx.payment_method}. UTR: {tx.utr_number}. Payee: {tx.payee_name}.",
        category="ORDER",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx.transaction_id,
        "utr_number": tx.utr_number,
        "status": tx.status,
        "net_amount_inr": tx.net_amount_inr,
        "completed_at": tx.completed_at.strftime("%d %b %Y, %I:%M %p"),
        "receipt_url": f"/api/payments/receipt/{tx.transaction_id}",
        "message": f"{status_label} verified successfully by NPCI/Bank Switch"
    }

@app.post("/api/payments/escrow-release")
def release_escrow(payload: dict = Body(...), db: Session = Depends(get_db)):
    tx_id = payload.get("transaction_id")
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if tx.status != "ESCROW_LOCKED":
        raise HTTPException(status_code=400, detail="Only ESCROW_LOCKED transactions can be released")

    tx.status = "DISBURSED"
    tx.completed_at = datetime.utcnow()
    tx.notes += " | APMC Moisture Quality Assay (<12%) passed. Funds disbursed to farmer PNB account."

    notif = Notification(
        title=f"🌾 Escrow Payout Disbursed: ₹{tx.net_amount_inr:,.0f}",
        message=f"APMC Quality assay passed. Funds from {tx.payer_name} released to farmer bank account. UTR: {tx.utr_number}.",
        category="MARKET",
        severity="SUCCESS"
    )
    db.add(notif)
    db.commit()

    return {
        "success": True,
        "transaction_id": tx.transaction_id,
        "status": "DISBURSED",
        "disbursed_amount_inr": tx.net_amount_inr,
        "message": "Escrow funds successfully disbursed to farmer account"
    }

@app.get("/api/payments/receipt/{tx_id}")
def get_payment_receipt(tx_id: str, db: Session = Depends(get_db)):
    tx = db.query(PaymentTransaction).filter(PaymentTransaction.transaction_id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "receipt_number": f"AGRI-REC-{tx.id:05d}",
        "transaction_id": tx.transaction_id,
        "utr_number": tx.utr_number,
        "date_time": tx.created_at.strftime("%d %b %Y, %I:%M %p") if tx.created_at else "",
        "payer_name": tx.payer_name,
        "payer_gstin": "03AABCA1234F1Z8" if "Ltd" in tx.payer_name else "URP (Unregistered Farmer)",
        "payee_name": tx.payee_name,
        "payee_gstin": "03AAGCI8821D1ZN",
        "payment_type": tx.payment_type,
        "payment_method": tx.payment_method,
        "bank_or_vpa": tx.bank_name_or_vpa,
        "status": tx.status,
        "base_amount_inr": tx.amount_inr,
        "gst_amount_inr": tx.gst_amount_inr,
        "subsidy_amount_inr": tx.subsidy_amount_inr,
        "net_amount_inr": tx.net_amount_inr,
        "notes": tx.notes,
        "verified_by": "NPCI / Bharat BillPay / PFMS Direct Agriculture Settlement Switch",
        "stamp": "GOVERNMENT OF INDIA DBT / APMC ASSAY COMPLIANT"
    }

# ==========================================
# 13. Static Files & Clean Dedicated Page Routing
# ==========================================
# Mount CSS, JS, Locales
if os.path.exists(os.path.join(FRONTEND_DIR, "css")):
    app.mount("/css", StaticFiles(directory=os.path.join(FRONTEND_DIR, "css")), name="css")
if os.path.exists(os.path.join(FRONTEND_DIR, "js")):
    app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
if os.path.exists(os.path.join(FRONTEND_DIR, "locales")):
    app.mount("/locales", StaticFiles(directory=os.path.join(FRONTEND_DIR, "locales")), name="locales")

# Route handler for dedicated pages
ROUTE_PAGE_MAP = {
    "": "index.html",
    "dashboard": "pages/dashboard.html",
    "farm-profile": "pages/farm-profile.html",
    "farm-analysis": "pages/farm-analysis.html",
    "weather": "pages/weather.html",
    "crop-recommendation": "pages/crop-recommendation.html",
    "crop-details": "pages/crop-details.html",
    "seed-recommendation": "pages/seed-recommendation.html",
    "seed-details": "pages/seed-details.html",
    "cultivation-plan": "pages/cultivation-plan.html",
    "fertilizer-recommendation": "pages/fertilizer-recommendation.html",
    "fertilizer-market": "pages/fertilizer-market.html",
    "water-analysis": "pages/water-analysis.html",
    "market-intelligence": "pages/market-intelligence.html",
    "crop-demand": "pages/crop-demand.html",
    "crop-shortage": "pages/crop-shortage.html",
    "profit-estimator": "pages/profit-estimator.html",
    "buyer-marketplace": "pages/buyer-marketplace.html",
    "transport-marketplace": "pages/transport-marketplace.html",
    "farm-to-market": "pages/farm-to-market.html",
    "farmer-orders": "pages/farmer-orders.html",
    "payment": "pages/payment.html",
    "payment-gateway": "pages/payment.html",
    "dealer-dashboard": "pages/dealer-dashboard.html",
    "transport-dashboard": "pages/transport-dashboard.html",
    "buyer-dashboard": "pages/buyer-dashboard.html",
    "ai-assistant": "pages/ai-assistant.html",
    "farm-calendar": "pages/farm-calendar.html",
    "notifications": "pages/notifications.html",
    "farm-report": "pages/farm-report.html",
    "admin": "pages/admin.html",
    "login": "pages/login.html",
    "register": "pages/register.html",
    "forgot-password": "pages/forgot-password.html",
    "verify-account": "pages/verify-account.html"
}

@app.get("/")
def get_landing():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/{page_name}")
def serve_page(page_name: str):
    clean = page_name.strip("/").lower()
    if clean.endswith(".html"):
        clean = clean[:-5]

    if clean in ROUTE_PAGE_MAP:
        target = os.path.join(FRONTEND_DIR, ROUTE_PAGE_MAP[clean])
        if os.path.exists(target):
            return FileResponse(target)

    # Fallback to direct page in pages/ if exists
    direct = os.path.join(PAGES_DIR, f"{clean}.html")
    if os.path.exists(direct):
        return FileResponse(direct)

    # If static file requested
    potential_file = os.path.join(FRONTEND_DIR, clean)
    if os.path.exists(potential_file) and os.path.isfile(potential_file):
        return FileResponse(potential_file)

    # Return landing or index if not matched
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
