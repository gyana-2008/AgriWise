"""
🌾 AGRIWISE AI - Realistic Seed Data for Indian Agriculture
Covers Crops, Seed Varieties, Fertilizers, Dealers, Buyers, Transporters,
Shortage Map States, Demo Users, and Config Weights.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import json
from datetime import datetime, timedelta
from database import (
    SessionLocal, init_db, User, Farm, SoilProfile, WaterProfile,
    Crop, SeedVariety, FertilizerProduct, Dealer, MarketPrice,
    CropShortage, Buyer, TransportProvider, Order, Notification, ConfigWeights,
    PaymentTransaction
)

def populate_database():
    init_db()
    db = SessionLocal()

    # If already seeded users, check if payments exist
    if db.query(User).count() > 0:
        if db.query(PaymentTransaction).count() == 0:
            seed_payments(db)
        db.close()
        return

    print("🌾 Seeding AGRIWISE AI database with realistic Indian agriculture data...")

    # 1. Config Weights
    weights = ConfigWeights(
        climate_weight=0.20,
        soil_weight=0.20,
        water_weight=0.15,
        weather_weight=0.15,
        season_weight=0.10,
        market_weight=0.10,
        economics_weight=0.10
    )
    db.add(weights)

    # 2. Users (Roles: Farmer, Dealer, Transporter, Buyer, Admin)
    farmer_user = User(
        name="Gurpreet Singh",
        email="gurpreet.farmer@agriwise.ai",
        phone="+91 98765 43210",
        role="FARMER",
        state="Punjab",
        district="Ludhiana",
        village="Sahnewal",
        farm_size_acres=5.0,
        experience_years=14
    )
    dealer_user = User(
        name="Kisan Seva Kendra (Rajinder Kumar)",
        email="rajinder.dealer@agriwise.ai",
        phone="+91 98141 23456",
        role="DEALER",
        state="Punjab",
        district="Ludhiana",
        village="Sahnewal Mandi Road",
        farm_size_acres=0.0,
        experience_years=20
    )
    transporter_user = User(
        name="Balwinder Logistics",
        email="balwinder.transport@agriwise.ai",
        phone="+91 98722 89012",
        role="TRANSPORTER",
        state="Punjab",
        district="Ludhiana",
        village="GT Road Transport Nagar",
        farm_size_acres=0.0,
        experience_years=15
    )
    buyer_user = User(
        name="ABC Agro Foods & Mills",
        email="procurement@abcfoods.in",
        phone="+91 98555 67890",
        role="BUYER",
        state="Punjab",
        district="Ludhiana",
        village="Khanna Industrial Area",
        farm_size_acres=0.0,
        experience_years=18
    )
    admin_user = User(
        name="AgriWise System Administrator",
        email="admin@agriwise.ai",
        phone="+91 98000 11223",
        role="ADMIN",
        state="National",
        district="New Delhi",
        village="Pusa Agri Complex",
        farm_size_acres=0.0,
        experience_years=25
    )
    db.add_all([farmer_user, dealer_user, transporter_user, buyer_user, admin_user])
    db.commit()

    # 3. Demo Farms for Farmer
    farm1 = Farm(
        user_id=farmer_user.id,
        name="Sahnewal Golden Acre Farm",
        location_name="Sahnewal, Ludhiana, Punjab",
        latitude=30.9010,
        longitude=75.8573,
        elevation_m=244.0,
        area_acres=5.0,
        current_crop="Maize (Corn)",
        current_season="Kharif",
        previous_crop="Wheat (PBW 550)",
        irrigation_method="Subsurface Drip + Tube-well",
        water_source="Deep Tube-well (180 ft)",
        water_availability="Abundant (High)",
        farming_method="Precision Integrated Nutrient Management"
    )
    farm2 = Farm(
        user_id=farmer_user.id,
        name="Khamanon Canal Farm",
        location_name="Khamanon, Fatehgarh Sahib, Punjab",
        latitude=30.8200,
        longitude=76.2200,
        elevation_m=250.0,
        area_acres=3.5,
        current_crop="Basmati Rice",
        current_season="Kharif",
        previous_crop="Mustard",
        irrigation_method="Canal Siphon + Furrow",
        water_source="Sirhind Canal Distributary",
        water_availability="Seasonal Reliable",
        farming_method="Conventional Mechanized"
    )
    db.add_all([farm1, farm2])
    db.commit()

    # 4. Soil Profiles
    soil1 = SoilProfile(
        farm_id=farm1.id,
        soil_type="Alluvial Loam (Sandy Loam subsoil)",
        ph=6.8,
        nitrogen_kg_ha=260.0,
        phosphorus_kg_ha=22.5,
        potassium_kg_ha=280.0,
        organic_carbon_pct=0.62,
        moisture_pct=22.0,
        ec_ds_m=0.45,
        health_score=85
    )
    soil2 = SoilProfile(
        farm_id=farm2.id,
        soil_type="Clay Loam (Rich Alluvial)",
        ph=7.4,
        nitrogen_kg_ha=290.0,
        phosphorus_kg_ha=18.0,
        potassium_kg_ha=310.0,
        organic_carbon_pct=0.75,
        moisture_pct=28.0,
        ec_ds_m=0.52,
        health_score=88
    )
    db.add_all([soil1, soil2])

    # 5. Water Profiles
    water1 = WaterProfile(
        farm_id=farm1.id,
        source="Deep Groundwater Tube-well",
        ph=7.2,
        ec_ds_m=0.65,
        tds_ppm=420.0,
        salinity_status="Safe / Good Quality",
        hardness_mg_l=180.0,
        suitability_score=88
    )
    water2 = WaterProfile(
        farm_id=farm2.id,
        source="Canal Water",
        ph=7.1,
        ec_ds_m=0.40,
        tds_ppm=260.0,
        salinity_status="Excellent Quality (Low EC)",
        hardness_mg_l=140.0,
        suitability_score=94
    )
    db.add_all([water1, water2])
    db.commit()

    # 6. Crops
    crops_data = [
        {
            "name": "Maize",
            "hindi_name": "मक्का (Makka)",
            "punjabi_name": "ਮੱਕੀ (Makki)",
            "season": "Kharif",
            "category": "Cereal / Industrial Grain",
            "typical_duration_days": 105,
            "water_req_level": "Medium",
            "optimum_temp_min": 18.0,
            "optimum_temp_max": 33.0,
            "optimum_ph_min": 5.8,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 28.5,
            "current_mandi_price_q": 2350.0,
            "msp_price_q": 2090.0,
            "demand_status": "High (Shortage in Processing)",
            "profit_potential": "High",
            "description": "High market liquidity with surging demand from ethanol, poultry feed and starch processing plants."
        },
        {
            "name": "Soybean",
            "hindi_name": "सोयाबीन (Soybean)",
            "punjabi_name": "ਸੋਇਆਬੀਨ (Soybean)",
            "season": "Kharif",
            "category": "Oilseed / Legume",
            "typical_duration_days": 98,
            "water_req_level": "Medium-Low",
            "optimum_temp_min": 20.0,
            "optimum_temp_max": 32.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 12.0,
            "current_mandi_price_q": 4650.0,
            "msp_price_q": 4600.0,
            "demand_status": "High (Crushing Demand)",
            "profit_potential": "High",
            "description": "Nitrogen-fixing legume requiring lower chemical fertilizers, providing excellent soil health restoration."
        },
        {
            "name": "Wheat",
            "hindi_name": "गेहूं (Gehun)",
            "punjabi_name": "ਕਣਕ (Kanak)",
            "season": "Rabi",
            "category": "Cereal / Staple",
            "typical_duration_days": 135,
            "water_req_level": "Medium",
            "optimum_temp_min": 12.0,
            "optimum_temp_max": 25.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.8,
            "expected_yield_q_acre": 22.0,
            "current_mandi_price_q": 2425.0,
            "msp_price_q": 2275.0,
            "demand_status": "Very High (Government & Milling)",
            "profit_potential": "Medium-High",
            "description": "Staple winter cereal with guaranteed procurement and steady open market premiums."
        },
        {
            "name": "Basmati Rice",
            "hindi_name": "बासमती धान (Basmati Dhan)",
            "punjabi_name": "ਬਾਸਮਤੀ ਚੌਲ (Basmati Chawal)",
            "season": "Kharif",
            "category": "Aromatic Cereal",
            "typical_duration_days": 125,
            "water_req_level": "High",
            "optimum_temp_min": 22.0,
            "optimum_temp_max": 35.0,
            "optimum_ph_min": 5.5,
            "optimum_ph_max": 7.2,
            "expected_yield_q_acre": 20.0,
            "current_mandi_price_q": 3850.0,
            "msp_price_q": 2183.0,
            "demand_status": "High (Export Demand)",
            "profit_potential": "High",
            "description": "Premium aromatic rice command strong export prices in Middle East and European markets."
        },
        {
            "name": "Cotton (Bt)",
            "hindi_name": "कपास (Kapas)",
            "punjabi_name": "ਕਪਾਹ (Kapas / Narma)",
            "season": "Kharif",
            "category": "Commercial Fiber",
            "typical_duration_days": 160,
            "water_req_level": "Medium-High",
            "optimum_temp_min": 21.0,
            "optimum_temp_max": 38.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 8.0,
            "expected_yield_q_acre": 10.5,
            "current_mandi_price_q": 7100.0,
            "msp_price_q": 6620.0,
            "demand_status": "Medium",
            "profit_potential": "High (Volatility)",
            "description": "High value cash crop suited for well-drained soils; requires proactive pest monitoring."
        },
        {
            "name": "Mustard",
            "hindi_name": "सरसों (Sarson)",
            "punjabi_name": "ਸਰ੍ਹੋਂ (Sarhon)",
            "season": "Rabi",
            "category": "Oilseed",
            "typical_duration_days": 115,
            "water_req_level": "Low",
            "optimum_temp_min": 10.0,
            "optimum_temp_max": 25.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.5,
            "expected_yield_q_acre": 9.5,
            "current_mandi_price_q": 5450.0,
            "msp_price_q": 5650.0,
            "demand_status": "High (Domestic Edible Oil)",
            "profit_potential": "High",
            "description": "Low water requirement, ideal for conserving groundwater in winter rotations."
        },
        {
            "name": "Tomato",
            "hindi_name": "टमाटर (Tamatar)",
            "punjabi_name": "ਟਮਾਟਰ (Tamatar)",
            "season": "Zaid / Kharif",
            "category": "Horticulture Vegetable",
            "typical_duration_days": 90,
            "water_req_level": "Medium",
            "optimum_temp_min": 18.0,
            "optimum_temp_max": 30.0,
            "optimum_ph_min": 6.0,
            "optimum_ph_max": 7.0,
            "expected_yield_q_acre": 140.0,
            "current_mandi_price_q": 1800.0,
            "msp_price_q": 0.0,
            "demand_status": "Extreme Volatility (High Demand)",
            "profit_potential": "Very High",
            "description": "Short duration high-yield vegetable crop giving rapid cash-flow cycles."
        }
    ]

    crop_objects = {}
    for c in crops_data:
        crop = Crop(**c)
        db.add(crop)
        crop_objects[c["name"]] = crop
    db.commit()

    # 7. Seed Varieties
    seeds_data = [
        # Maize Seeds
        {
            "crop_name": "Maize",
            "name": "Pioneer P3396 Hybrid",
            "variety_code": "PIO-3396",
            "manufacturer": "Corteva Agriscience",
            "duration_days": 108,
            "expected_yield_min_q": 27.0,
            "expected_yield_max_q": 32.0,
            "seed_rate_kg_acre": 8.0,
            "price_per_kg": 260.0,
            "disease_resistance": "High (Turcicum Leaf Blight & Downy Mildew)",
            "drought_tolerance": "High",
            "soil_affinity": "Alluvial, Loamy, Well-drained soils",
            "suitability_pct": 95,
            "certified": True,
            "key_features": "Heavy cob girth, stay-green trait, excellent shelling %"
        },
        {
            "crop_name": "Maize",
            "name": "Kaveri 50 Super Hybrid",
            "variety_code": "KAV-50",
            "manufacturer": "Kaveri Seed Company",
            "duration_days": 102,
            "expected_yield_min_q": 24.5,
            "expected_yield_max_q": 28.5,
            "seed_rate_kg_acre": 7.5,
            "price_per_kg": 220.0,
            "disease_resistance": "Medium-High",
            "drought_tolerance": "Medium",
            "soil_affinity": "Sandy Loam to Clay Loam",
            "suitability_pct": 89,
            "certified": True,
            "key_features": "Early maturity, uniform orange-yellow flint grains"
        },
        {
            "crop_name": "Maize",
            "name": "CP 333 Bold Kernel",
            "variety_code": "CP-333",
            "manufacturer": "Charoen Pokphand Seeds",
            "duration_days": 112,
            "expected_yield_min_q": 26.0,
            "expected_yield_max_q": 30.5,
            "seed_rate_kg_acre": 8.0,
            "price_per_kg": 245.0,
            "disease_resistance": "High (Stalk Rot resistant)",
            "drought_tolerance": "High",
            "soil_affinity": "Loamy soil with pH 6.0 - 7.5",
            "suitability_pct": 91,
            "certified": True,
            "key_features": "Dense starch content preferred by processing mills"
        },
        # Soybean Seeds
        {
            "crop_name": "Soybean",
            "name": "JS 335 Certified",
            "variety_code": "JS-335",
            "manufacturer": "Jawaharlal Nehru Krishi Vishwavidyalaya",
            "duration_days": 98,
            "expected_yield_min_q": 11.0,
            "expected_yield_max_q": 13.5,
            "seed_rate_kg_acre": 25.0,
            "price_per_kg": 85.0,
            "disease_resistance": "High (Yellow Mosaic Virus tolerant)",
            "drought_tolerance": "Medium",
            "soil_affinity": "Deep fertile black & alluvial soils",
            "suitability_pct": 88,
            "certified": True,
            "key_features": "High oil content (21%), non-shattering pods"
        },
        # Wheat Seeds
        {
            "crop_name": "Wheat",
            "name": "PBW 550 High Yield",
            "variety_code": "PBW-550",
            "manufacturer": "Punjab Agricultural University (PAU)",
            "duration_days": 132,
            "expected_yield_min_q": 21.0,
            "expected_yield_max_q": 24.5,
            "seed_rate_kg_acre": 40.0,
            "price_per_kg": 42.0,
            "disease_resistance": "High (Yellow Rust & Karnal Bunt resistant)",
            "drought_tolerance": "Medium",
            "soil_affinity": "Medium to heavy textured alluvial soils",
            "suitability_pct": 92,
            "certified": True,
            "key_features": "Lustrous amber grains, excellent chapati making quality"
        },
        # Basmati Rice Seeds
        {
            "crop_name": "Basmati Rice",
            "name": "Pusa Basmati 1121",
            "variety_code": "PB-1121",
            "manufacturer": "ICAR - IARI New Delhi",
            "duration_days": 128,
            "expected_yield_min_q": 19.0,
            "expected_yield_max_q": 22.0,
            "seed_rate_kg_acre": 6.0,
            "price_per_kg": 110.0,
            "disease_resistance": "Medium (Bacterial blight monitoring needed)",
            "drought_tolerance": "Low",
            "soil_affinity": "Clayey loam with good water retention",
            "suitability_pct": 86,
            "certified": True,
            "key_features": "Extra-long slender grain, world-renowned elongation ratio"
        }
    ]

    for s in seeds_data:
        crop_id = crop_objects[s["crop_name"]].id
        seed = SeedVariety(
            crop_id=crop_id,
            name=s["name"],
            variety_code=s["variety_code"],
            manufacturer=s["manufacturer"],
            duration_days=s["duration_days"],
            expected_yield_min_q=s["expected_yield_min_q"],
            expected_yield_max_q=s["expected_yield_max_q"],
            seed_rate_kg_acre=s["seed_rate_kg_acre"],
            price_per_kg=s["price_per_kg"],
            disease_resistance=s["disease_resistance"],
            drought_tolerance=s["drought_tolerance"],
            soil_affinity=s["soil_affinity"],
            suitability_pct=s["suitability_pct"],
            certified=s["certified"],
            key_features=s["key_features"]
        )
        db.add(seed)
    db.commit()

    # 8. Fertilizer Products
    fertilizers_data = [
        {
            "name": "Neem Coated Urea",
            "category": "Nitrogenous",
            "nutrient_composition": "N: 46%, P: 0%, K: 0%",
            "n_pct": 46.0, "p_pct": 0.0, "k_pct": 0.0,
            "pack_size_kg": 45.0,
            "mrp_inr": 266.5,
            "subsidy_eligible": True,
            "application_stage": "Basal & 2 Split Top Dressings",
            "safety_guideline": "Apply when soil has adequate moisture. Do not broadcast immediately before heavy rains."
        },
        {
            "name": "DAP (Di-Ammonium Phosphate 18:46:0)",
            "category": "Phosphatic",
            "nutrient_composition": "N: 18%, P: 46%, K: 0%",
            "n_pct": 18.0, "p_pct": 46.0, "k_pct": 0.0,
            "pack_size_kg": 50.0,
            "mrp_inr": 1350.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Root Zone Placement at Sowing",
            "safety_guideline": "Place 3-5 cm below and to the side of seed furrow to avoid seedling burn."
        },
        {
            "name": "MOP (Muriate of Potash 0:0:60)",
            "category": "Potassic",
            "nutrient_composition": "N: 0%, P: 0%, K: 60%",
            "n_pct": 0.0, "p_pct": 0.0, "k_pct": 60.0,
            "pack_size_kg": 50.0,
            "mrp_inr": 1650.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Application",
            "safety_guideline": "Improves drought tolerance, grain filling and disease resistance."
        },
        {
            "name": "IFFCO NPK Complex 19:19:19",
            "category": "Water Soluble NPK",
            "nutrient_composition": "N: 19%, P: 19%, K: 19%",
            "n_pct": 19.0, "p_pct": 19.0, "k_pct": 19.0,
            "pack_size_kg": 1.0,
            "mrp_inr": 185.0,
            "subsidy_eligible": False,
            "application_stage": "Foliar Spray at Vegetative Stage",
            "safety_guideline": "Spray during cool morning or evening hours. Do not mix with copper fungicides."
        },
        {
            "name": "Zinc Sulfate Heptahydrate (21% Zn)",
            "category": "Micronutrient",
            "nutrient_composition": "Zn: 21%, S: 10%",
            "n_pct": 0.0, "p_pct": 0.0, "k_pct": 0.0,
            "pack_size_kg": 10.0,
            "mrp_inr": 540.0,
            "subsidy_eligible": True,
            "application_stage": "Basal Soil Application",
            "safety_guideline": "Never mix directly with phosphatic fertilizers (DAP/SSP) in the same slurry."
        },
        {
            "name": "Organic Vermicompost Premium",
            "category": "Organic",
            "nutrient_composition": "Organic Carbon: 16%, N: 1.5%, P: 0.8%, K: 0.8%",
            "n_pct": 1.5, "p_pct": 0.8, "k_pct": 0.8,
            "pack_size_kg": 50.0,
            "mrp_inr": 450.0,
            "subsidy_eligible": False,
            "application_stage": "Land Preparation",
            "safety_guideline": "Incorporate thoroughly into top 15 cm soil layer 7 days before sowing."
        }
    ]

    for f in fertilizers_data:
        fert = FertilizerProduct(**f)
        db.add(fert)
    db.commit()

    # 9. Input Dealers
    dealers_data = [
        {
            "business_name": "Kisan Seva Kendra Sahnewal",
            "owner_name": "Rajinder Kumar Gupta",
            "phone": "+91 98141 23456",
            "address": "Shop 14, Main Mandi Road, Sahnewal",
            "city": "Ludhiana",
            "state": "Punjab",
            "latitude": 30.9045,
            "longitude": 75.8620,
            "rating": 4.9,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "Pioneer P3396 Hybrid (4kg bag)", "price": 1040, "stock": "45 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "220 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "80 bags in stock", "category": "Fertilizer"},
                {"name": "MOP 0:0:60 (50kg)", "price": 1650, "stock": "65 bags in stock", "category": "Fertilizer"},
                {"name": "Zinc Sulfate 21% (10kg)", "price": 520, "stock": "30 bags in stock", "category": "Micronutrient"}
            ])
        },
        {
            "business_name": "Ludhiana Agro Inputs & Seeds",
            "owner_name": "Harpreet Singh Dhillon",
            "phone": "+91 98780 44556",
            "address": "Near Old Grain Market, Gill Road",
            "city": "Ludhiana",
            "state": "Punjab",
            "latitude": 30.8910,
            "longitude": 75.8450,
            "rating": 4.7,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "Kaveri 50 Super Hybrid (4kg bag)", "price": 880, "stock": "60 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "150 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "110 bags in stock", "category": "Fertilizer"},
                {"name": "IFFCO NPK 19:19:19 (1kg)", "price": 180, "stock": "100 packs in stock", "category": "Foliar Fertilizer"}
            ])
        },
        {
            "business_name": "Khanna Farmers Agro Hub",
            "owner_name": "Manmohan Joshi",
            "phone": "+91 98150 99887",
            "address": "Asia's Largest Grain Market Compound",
            "city": "Khanna",
            "state": "Punjab",
            "latitude": 30.7050,
            "longitude": 76.2180,
            "rating": 4.8,
            "delivery_available": True,
            "products_json": json.dumps([
                {"name": "CP 333 Bold Kernel (4kg bag)", "price": 980, "stock": "50 bags in stock", "category": "Seed"},
                {"name": "Neem Coated Urea (45kg)", "price": 266.5, "stock": "350 bags in stock", "category": "Fertilizer"},
                {"name": "DAP 18:46:0 (50kg)", "price": 1350, "stock": "140 bags in stock", "category": "Fertilizer"},
                {"name": "Organic Vermicompost (50kg)", "price": 420, "stock": "120 bags in stock", "category": "Organic"}
            ])
        }
    ]

    for d in dealers_data:
        dealer = Dealer(**d)
        db.add(dealer)
    db.commit()

    # 10. Market Prices (Mandi Intelligence)
    market_data = [
        {"crop_name": "Maize", "mandi_name": "Khanna Grain Mandi", "state": "Punjab", "modal_price_q": 2360.0, "min_price_q": 2200.0, "max_price_q": 2480.0, "daily_arrivals_tonnes": 480.0, "price_change_pct": 3.2, "demand_level": "High"},
        {"crop_name": "Maize", "mandi_name": "Ludhiana Mandi", "state": "Punjab", "modal_price_q": 2340.0, "min_price_q": 2180.0, "max_price_q": 2450.0, "daily_arrivals_tonnes": 310.0, "price_change_pct": 2.6, "demand_level": "High"},
        {"crop_name": "Maize", "mandi_name": "Karnal Mandi", "state": "Haryana", "modal_price_q": 2380.0, "min_price_q": 2250.0, "max_price_q": 2510.0, "daily_arrivals_tonnes": 520.0, "price_change_pct": 4.1, "demand_level": "Very High"},
        {"crop_name": "Soybean", "mandi_name": "Indore Mandi", "state": "Madhya Pradesh", "modal_price_q": 4720.0, "min_price_q": 4500.0, "max_price_q": 4900.0, "daily_arrivals_tonnes": 850.0, "price_change_pct": 1.8, "demand_level": "High"},
        {"crop_name": "Wheat", "mandi_name": "Ludhiana Mandi", "state": "Punjab", "modal_price_q": 2425.0, "min_price_q": 2350.0, "max_price_q": 2500.0, "daily_arrivals_tonnes": 650.0, "price_change_pct": 0.8, "demand_level": "Stable High"},
        {"crop_name": "Basmati Rice", "mandi_name": "Amritsar Mandi", "state": "Punjab", "modal_price_q": 3890.0, "min_price_q": 3600.0, "max_price_q": 4150.0, "daily_arrivals_tonnes": 410.0, "price_change_pct": 2.1, "demand_level": "High"},
        {"crop_name": "Tomato", "mandi_name": "Delhi Azadpur Mandi", "state": "Delhi", "modal_price_q": 1950.0, "min_price_q": 1500.0, "max_price_q": 2300.0, "daily_arrivals_tonnes": 920.0, "price_change_pct": 8.5, "demand_level": "Very High"}
    ]
    for m in market_data:
        db.add(MarketPrice(**m))
    db.commit()

    # 11. National Crop Shortages (For Interactive India Map)
    shortage_data = [
        # Maize
        {"crop_name": "Maize", "state_code": "PB", "state_name": "Punjab", "status": "High Shortage", "demand_tonnes": 55000.0, "supply_tonnes": 32000.0, "deficit_tonnes": 23000.0, "deficit_pct": 41.8, "current_avg_price_q": 2360.0, "price_trend": "Bullish (+4.2%)", "major_markets": "Khanna, Ludhiana, Jalandhar", "buyer_demand_summary": "Distilleries and starch mills running at 75% capacity due to grain deficit."},
        {"crop_name": "Maize", "state_code": "HR", "state_name": "Haryana", "status": "High Shortage", "demand_tonnes": 48000.0, "supply_tonnes": 30000.0, "deficit_tonnes": 18000.0, "deficit_pct": 37.5, "current_avg_price_q": 2380.0, "price_trend": "Bullish (+3.8%)", "major_markets": "Karnal, Ambala, Kaithal", "buyer_demand_summary": "Poultry feed clusters in Karnal offering premium spot cash for dry grain."},
        {"crop_name": "Maize", "state_code": "MH", "state_name": "Maharashtra", "status": "Medium Shortage", "demand_tonnes": 85000.0, "supply_tonnes": 68000.0, "deficit_tonnes": 17000.0, "deficit_pct": 20.0, "current_avg_price_q": 2310.0, "price_trend": "Stable (+1.2%)", "major_markets": "Aurangabad, Jalna, Sangli", "buyer_demand_summary": "Poultry and animal feed mills in western Maharashtra with active inquiries."},
        {"crop_name": "Maize", "state_code": "KA", "state_name": "Karnataka", "status": "Surplus", "demand_tonnes": 90000.0, "supply_tonnes": 115000.0, "deficit_tonnes": -25000.0, "deficit_pct": -27.7, "current_avg_price_q": 2180.0, "price_trend": "Softening (-1.5%)", "major_markets": "Davangere, Ranebennur, Shimoga", "buyer_demand_summary": "Heavy harvest arrivals pushing grain outward to northern deficit states."},
        {"crop_name": "Maize", "state_code": "UP", "state_name": "Uttar Pradesh", "status": "Balanced", "demand_tonnes": 62000.0, "supply_tonnes": 60000.0, "deficit_tonnes": 2000.0, "deficit_pct": 3.2, "current_avg_price_q": 2240.0, "price_trend": "Flat (0.0%)", "major_markets": "Kanpur, Bulandshahr, Bareilly", "buyer_demand_summary": "Local mill consumption balanced with arrivals."},
        {"crop_name": "Maize", "state_code": "MP", "state_name": "Madhya Pradesh", "status": "Surplus", "demand_tonnes": 50000.0, "supply_tonnes": 72000.0, "deficit_tonnes": -22000.0, "deficit_pct": -44.0, "current_avg_price_q": 2150.0, "price_trend": "Softening (-2.1%)", "major_markets": "Chhindwara, Betul, Dhar", "buyer_demand_summary": "Hub for rail transport of corn to north Indian feed mills."},

        # Soybean
        {"crop_name": "Soybean", "state_code": "MH", "state_name": "Maharashtra", "status": "High Shortage", "demand_tonnes": 120000.0, "supply_tonnes": 82000.0, "deficit_tonnes": 38000.0, "deficit_pct": 31.6, "current_avg_price_q": 4720.0, "price_trend": "Bullish (+3.5%)", "major_markets": "Latur, Akola, Nagpur", "buyer_demand_summary": "Solvent extractors aggressively bidding up yellow soybean for meal export."},
        {"crop_name": "Soybean", "state_code": "MP", "state_name": "Madhya Pradesh", "status": "Medium Shortage", "demand_tonnes": 140000.0, "supply_tonnes": 115000.0, "deficit_tonnes": 25000.0, "deficit_pct": 17.8, "current_avg_price_q": 4650.0, "price_trend": "Firm (+1.9%)", "major_markets": "Indore, Ujjain, Dewas", "buyer_demand_summary": "High capacity crushing plants operating at good margins."},

        # Wheat
        {"crop_name": "Wheat", "state_code": "PB", "state_name": "Punjab", "status": "Surplus", "demand_tonnes": 75000.0, "supply_tonnes": 160000.0, "deficit_tonnes": -85000.0, "deficit_pct": -113.3, "current_avg_price_q": 2425.0, "price_trend": "Steady (+0.5%)", "major_markets": "Khanna, Rajpura, Moga", "buyer_demand_summary": "Central pool procurement buffer state; steady private miller interest."},
        {"crop_name": "Wheat", "state_code": "TN", "state_name": "Tamil Nadu", "status": "High Shortage", "demand_tonnes": 65000.0, "supply_tonnes": 4000.0, "deficit_tonnes": 61000.0, "deficit_pct": 93.8, "current_avg_price_q": 2850.0, "price_trend": "Bullish (+5.1%)", "major_markets": "Coimbatore, Chennai, Madurai", "buyer_demand_summary": "South Indian roller flour mills relying heavily on northern rail rakes."}
    ]
    for s in shortage_data:
        db.add(CropShortage(**s))
    db.commit()

    # 12. Wholesale Buyers & Demand Tenders
    buyers_data = [
        {
            "company_name": "ABC Agro Foods & Millers",
            "buyer_type": "Food Processor & Miller",
            "contact_person": "Vikram Ahuja (VP Procurement)",
            "phone": "+91 98555 67890",
            "email": "procurement@abcfoods.in",
            "location": "Khanna Industrial Area, Punjab (22 km away)",
            "crop_required": "Maize",
            "quantity_required_tonnes": 500.0,
            "offered_price_q": 2420.0,
            "deadline_date": (datetime.utcnow() + timedelta(days=25)).strftime("%Y-%m-%d"),
            "quality_specs": "Moisture < 12%, Foreign Matter < 1.0%, Broken grains < 2%, Aflatoxin compliant",
            "rating": 4.9,
            "verified": True
        },
        {
            "company_name": "Punjab Agro Industries Corp",
            "buyer_type": "State Procurement Agency",
            "contact_person": "Gursharan Singh (District Officer)",
            "phone": "+91 98760 12345",
            "email": "procure@punjabagro.gov.in",
            "location": "Ludhiana Mandi Complex, Punjab (12 km away)",
            "crop_required": "Maize",
            "quantity_required_tonnes": 1200.0,
            "offered_price_q": 2350.0,
            "deadline_date": (datetime.utcnow() + timedelta(days=40)).strftime("%Y-%m-%d"),
            "quality_specs": "Fair Average Quality (FAQ) norms, Moisture < 14%",
            "rating": 4.8,
            "verified": True
        },
        {
            "company_name": "Karnal Premium Poultry Feed Mills",
            "buyer_type": "Feed Manufacturer",
            "contact_person": "Ramesh Chawla",
            "phone": "+91 98960 55443",
            "email": "purchase@karnalfeed.com",
            "location": "GT Road, Karnal, Haryana (130 km away)",
            "crop_required": "Maize",
            "quantity_required_tonnes": 800.0,
            "offered_price_q": 2480.0,
            "deadline_date": (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "quality_specs": "Yellow maize, High protein (>8.5%), Dry kernels (<11.5% moisture)",
            "rating": 4.7,
            "verified": True
        },
        {
            "company_name": "Adani Wilmar Agri Hub",
            "buyer_type": "National Processor & Exporter",
            "contact_person": "Sanjay Deshmukh",
            "phone": "+91 98200 77665",
            "email": "agri.procurement@adaniwilmar.in",
            "location": "Indore Agri Park, MP",
            "crop_required": "Soybean",
            "quantity_required_tonnes": 2500.0,
            "offered_price_q": 4750.0,
            "deadline_date": (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "quality_specs": "Oil content > 19.5%, Moisture < 10%, Sand/Silica < 0.5%",
            "rating": 5.0,
            "verified": True
        }
    ]
    for b in buyers_data:
        db.add(Buyer(**b))
    db.commit()

    # 13. Transport Providers
    transporters_data = [
        {
            "operator_name": "Balwinder Singh Transport (Tata 407)",
            "phone": "+91 98722 89012",
            "vehicle_type": "Tata 407 (Medium Commercial Vehicle)",
            "capacity_tonnes": 4.5,
            "base_rate_inr": 1400.0,
            "rate_per_km_inr": 28.0,
            "current_distance_km": 4.5,
            "location": "Sahnewal GT Road Bypass",
            "available_now": True,
            "rating": 4.8
        },
        {
            "operator_name": "Khanna Express Truck Fleet (10-Tonne)",
            "phone": "+91 98140 33221",
            "vehicle_type": "Ashok Leyland 10-Tonne Truck",
            "capacity_tonnes": 10.0,
            "base_rate_inr": 2400.0,
            "rate_per_km_inr": 42.0,
            "current_distance_km": 9.0,
            "location": "Khanna Transport Nagar",
            "available_now": True,
            "rating": 4.9
        },
        {
            "operator_name": "Sher-e-Punjab Mahindra Bolero Maxi-Truck",
            "phone": "+91 98788 77665",
            "vehicle_type": "Mahindra Bolero Pickup",
            "capacity_tonnes": 1.7,
            "base_rate_inr": 750.0,
            "rate_per_km_inr": 18.0,
            "current_distance_km": 3.2,
            "location": "Sahnewal Focal Point",
            "available_now": True,
            "rating": 4.7
        }
    ]
    for t in transporters_data:
        db.add(TransportProvider(**t))
    db.commit()

    # 14. Initial Notifications
    notifications_data = [
        {
            "title": "🌧 Weather Advisory: Rainfall Expected in 48 Hours",
            "message": "Light to moderate pre-monsoon showers (18-25mm) forecasted. Avoid fertilizer broadcast or foliar sprays today to prevent leaching.",
            "category": "WEATHER",
            "severity": "WARNING",
            "created_at": datetime.utcnow() - timedelta(hours=2)
        },
        {
            "title": "📈 Maize Price Surge in Khanna Mandi",
            "message": "Modal spot price crossed ₹2,360/quintal (+3.2%) due to tight industrial feed arrivals. Strong seller market.",
            "category": "MARKET",
            "severity": "INFO",
            "created_at": datetime.utcnow() - timedelta(hours=5)
        },
        {
            "title": "🌱 Sowing Stage Nutrient Alert",
            "message": "For your 5-acre Sahnewal farm, basal DAP (18:46:0) and MOP placement should be completed prior to seed drilling.",
            "category": "ADVISORY",
            "severity": "ALERT",
            "created_at": datetime.utcnow() - timedelta(days=1)
        }
    ]
    for n in notifications_data:
        db.add(Notification(**n))
    db.commit()

    # 15. Initial Demo Orders
    orders_data = [
        {
            "user_id": farmer_user.id,
            "order_type": "INPUT",
            "item_title": "Pioneer P3396 Hybrid Maize Seed (10 bags)",
            "quantity": "40 kg (10 bags of 4kg)",
            "amount_inr": 10400.0,
            "status": "CONFIRMED",
            "partner_name": "Kisan Seva Kendra Sahnewal",
            "created_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "user_id": farmer_user.id,
            "order_type": "TRANSPORT",
            "item_title": "Farm to Khanna Industrial Mill Transport",
            "quantity": "10 Tonnes Maize",
            "amount_inr": 3324.0,
            "status": "COMPLETED",
            "partner_name": "Balwinder Singh Transport",
            "created_at": datetime.utcnow() - timedelta(days=10)
        }
    ]
    for o in orders_data:
        db.add(Order(**o))
    db.commit()

    # 16. Seed Initial Demo Payments
    seed_payments(db)

    db.close()
    print("✅ AGRIWISE AI database successfully seeded with realistic Indian agricultural data!")

def seed_payments(db):
    farmer_user = db.query(User).filter(User.role == "FARMER").first()
    farmer_id = farmer_user.id if farmer_user else 1

    payments_data = [
        {
            "transaction_id": "AGRI-PAY-2026-1049",
            "utr_number": "629108447192",
            "user_id": farmer_id,
            "payment_type": "INPUT_PURCHASE",
            "payment_method": "UPI_QR",
            "amount_inr": 10400.0,
            "gst_amount_inr": 520.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 10400.0,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "Kisan Seva Kendra Sahnewal",
            "bank_name_or_vpa": "gurpreet@sbi",
            "status": "SUCCESS",
            "notes": "Purchase of Pioneer P3396 Hybrid Maize Seed (10 bags)",
            "created_at": datetime.utcnow() - timedelta(days=3),
            "completed_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1082",
            "utr_number": "629112998341",
            "user_id": farmer_id,
            "payment_type": "INPUT_PURCHASE",
            "payment_method": "KCC_RUPAY",
            "amount_inr": 14365.0,
            "gst_amount_inr": 718.25,
            "subsidy_amount_inr": 430.95,
            "net_amount_inr": 13934.05,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "IFFCO Farmer Service Centre",
            "bank_name_or_vpa": "SBI Agriculture Kisan Card (XXXX-4912)",
            "status": "SUCCESS",
            "notes": "Fertilizer seasonal package: Urea (10 bags), DAP (3 bags), MOP (2 bags) with 3% prompt subvention",
            "created_at": datetime.utcnow() - timedelta(days=2),
            "completed_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1104",
            "utr_number": "629115002914",
            "user_id": farmer_id,
            "payment_type": "TRANSPORT_ADVANCE",
            "payment_method": "UPI_VPA",
            "amount_inr": 1500.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 1500.0,
            "payer_name": "Sardar Gurpreet Singh",
            "payee_name": "Gurkirat Agri Logistics",
            "bank_name_or_vpa": "gurkirat.logistics@okaxis",
            "status": "SUCCESS",
            "notes": "50% advance dispatch fee for 10 Tonne Tata 407 transport to Khanna Mandi",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "completed_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "transaction_id": "AGRI-PAY-2026-1150",
            "utr_number": "629118330911",
            "user_id": farmer_id,
            "payment_type": "BUYER_ESCROW",
            "payment_method": "ESCROW",
            "amount_inr": 238000.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 238000.0,
            "payer_name": "Godrej Agrovet Procurement Ltd",
            "payee_name": "Sardar Gurpreet Singh (AgriWise Smart Escrow Lock)",
            "bank_name_or_vpa": "ICICI Agri Escrow Vault",
            "status": "ESCROW_LOCKED",
            "notes": "Wholesale contract procurement escrow: 100 Quintals Yellow Maize at ₹2,380/Qtl. Pending APMC quality assay test.",
            "created_at": datetime.utcnow() - timedelta(hours=6),
            "completed_at": datetime.utcnow() - timedelta(hours=6)
        },
        {
            "transaction_id": "AGRI-PAY-2026-0980",
            "utr_number": "629088421098",
            "user_id": farmer_id,
            "payment_type": "FARMER_PAYOUT",
            "payment_method": "MANDI_DIRECT",
            "amount_inr": 194000.0,
            "gst_amount_inr": 0.0,
            "subsidy_amount_inr": 0.0,
            "net_amount_inr": 194000.0,
            "payer_name": "Khanna APMC Grain Exchange",
            "payee_name": "Sardar Gurpreet Singh",
            "bank_name_or_vpa": "Punjab National Bank (A/C: 084200010091)",
            "status": "DISBURSED",
            "notes": "Previous Rabi harvest settlement: 80 Quintals Sharbati Wheat direct DBT clearance",
            "created_at": datetime.utcnow() - timedelta(days=12),
            "completed_at": datetime.utcnow() - timedelta(days=12)
        }
    ]
    for p in payments_data:
        db.add(PaymentTransaction(**p))
    db.commit()
    print("💳 Pre-seeded realistic Indian agricultural payment transactions.")

if __name__ == "__main__":
    populate_database()
