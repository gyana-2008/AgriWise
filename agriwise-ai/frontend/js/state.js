/**
 * 🌾 AGRIWISE AI - State Management System
 * Persists user session, active farm, active role, demo journey progression, and preferences.
 */

const AgriState = {
  // Current active role: FARMER, DEALER, TRANSPORTER, BUYER, ADMIN
  currentRole: localStorage.getItem('agriwise_role') || 'FARMER',

  // Current language: en, hi, pa
  currentLang: localStorage.getItem('agriwise_lang') || 'en',

  // Active Farm Profile
  activeFarm: {
    id: 1,
    name: "Sahnewal Golden Acre Farm",
    location_name: "Sahnewal, Ludhiana, Punjab",
    latitude: 30.9010,
    longitude: 75.8573,
    area_acres: 5.0,
    current_crop: "Maize",
    current_season: "Kharif",
    soil: {
      soil_type: "Alluvial Loam",
      ph: 6.8,
      nitrogen_kg_ha: 260.0,
      phosphorus_kg_ha: 22.5,
      potassium_kg_ha: 280.0,
      organic_carbon_pct: 0.62,
      health_score: 85
    },
    water: {
      source: "Deep Groundwater Tube-well",
      ph: 7.2,
      ec_ds_m: 0.65,
      tds_ppm: 420.0,
      suitability_score: 88
    }
  },

  // Selected crop & seed across decision pipeline
  selectedCrop: localStorage.getItem('agriwise_selected_crop') || 'Maize',
  selectedSeed: localStorage.getItem('agriwise_selected_seed') || 'Pioneer P3396 Hybrid',

  // Guided Demo Journey Pipeline Steps
  demoJourneySteps: [
    { id: 1, title: "1. Demo Farm Profile", route: "/farm-profile", desc: "Select & configure farm location" },
    { id: 2, title: "2. Farm & Soil Analysis", route: "/farm-analysis", desc: "Analyze soil, water & climate score" },
    { id: 3, title: "3. Live Weather", route: "/weather", desc: "Check live forecast & agronomic advice" },
    { id: 4, title: "4. Crop Recommendation", route: "/crop-recommendation", desc: "AI ranks most suitable crops" },
    { id: 5, title: "5. Seed Recommendation", route: "/seed-recommendation", desc: "Compare certified seed varieties" },
    { id: 6, title: "6. Cultivation Plan", route: "/cultivation-plan", desc: "Day 0 to Harvest chronological timeline" },
    { id: 7, title: "7. Fertilizer Dosing", route: "/fertilizer-recommendation", desc: "Scientific N-P-K nutrient dosage" },
    { id: 8, title: "8. Input Marketplace", route: "/fertilizer-market", desc: "Compare nearby dealers & prices" },
    { id: 9, title: "9. Market Intelligence", route: "/market-intelligence", desc: "Live mandi trends & demand meters" },
    { id: 10, title: "10. National Shortage Map", route: "/crop-shortage", desc: "Interactive India state deficit map" },
    { id: 11, title: "11. Buyer Marketplace", route: "/buyer-marketplace", desc: "Connect with wholesale food millers" },
    { id: 12, title: "12. Transport Logistics", route: "/transport-marketplace", desc: "Book trucks and pickup transport" },
    { id: 13, title: "13. Farm-to-Market", route: "/farm-to-market", desc: "Connected end-to-end flow" },
    { id: 14, title: "14. Payment Gateway & Escrow", route: "/payment", desc: "Live UPI, KCC subvention & Smart Escrow settlement" },
    { id: 15, title: "15. Profit Estimator", route: "/profit-estimator", desc: "Conservative, Expected, Optimistic ROI" },
    { id: 16, title: "16. Final Farm Dossier", route: "/farm-report", desc: "Comprehensive downloadable report" }
  ],

  setRole(role) {
    this.currentRole = role.toUpperCase();
    localStorage.setItem('agriwise_role', this.currentRole);
    window.location.reload();
  },

  setLang(lang) {
    this.currentLang = lang;
    localStorage.setItem('agriwise_lang', lang);
    if (window.AgriI18n) {
      window.AgriI18n.applyTranslations();
    }
  },

  setSelectedCrop(cropName) {
    this.selectedCrop = cropName;
    localStorage.setItem('agriwise_selected_crop', cropName);
  },

  setSelectedSeed(seedName) {
    this.selectedSeed = seedName;
    localStorage.setItem('agriwise_selected_seed', seedName);
  },

  formatCurrency(num) {
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(num);
  },

  formatNumber(num) {
    return new Intl.NumberFormat('en-IN').format(num);
  }
};

window.AgriState = AgriState;
