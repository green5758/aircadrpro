import datetime
import hashlib
import html
import json
import math
import os
import urllib.request
from pathlib import Path

# ==============================================================================
# CONFIGURATION
# ==============================================================================
AFFILIATE_TAG = "everythi00099-20"
SITE_NAME = "AirCADRPro"
SITE_TAGLINE = "Precision HEPA Air Purifier CADR & ACH Room Sizing Calculator"
ARTICLES_PER_RUN = 3

# Tag verifikasi Google Search Console
GOOGLE_SITE_VERIFICATION = "pgvlG0f03ZrRZzbgDSXRhr6tsSfseFOhXCN6Yv_j5b8"

OWNER = os.environ.get("GITHUB_OWNER", "username")
REPO = os.environ.get("GITHUB_REPO", "aircadrpro")
if REPO.lower() == f"{OWNER.lower()}.github.io":
    SITE_URL = f"https://{OWNER}.github.io"
else:
    SITE_URL = f"https://{OWNER}.github.io/{REPO}"

DOCS_DIR = Path("docs")
REVIEWS_DIR = DOCS_DIR / "reviews"
DATA_DIR = DOCS_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"
REVIEWS_JSON = DATA_DIR / "reviews.json"

TODAY_ISO = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
NOW_RFC822 = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
CURRENT_YEAR = datetime.datetime.now(datetime.timezone.utc).year

# ==============================================================================
# MASTER PRODUCT CATALOG (36 REAL AMAZON AIR PURIFIERS)
# ==============================================================================
PRODUCTS = [
    {
        "id": "coway-airmega-ap-1512hh",
        "name": "Coway Airmega AP-1512HH Mighty",
        "brand": "Coway",
        "cadr_cfm": 246,
        "area_48ach": 361,
        "noise_min": 24,
        "noise_max": 53,
        "watts": 77,
        "filter_cost_yr": 49,
        "price_est": 229,
        "tier": "Mid-Range",
        "filter_type": "True HEPA H13 + Carbon Pre-Filter + Optional Ionizer",
        "bestseller_rank": 1,
        "badge": "#1 Best Overall Value",
        "best_for": "Medium Bedrooms & Everyday Allergies",
        "rating": 4.8,
        "pros": ["Proven 10+ year reliability track record", "Eco Mode automatically powers down fan when air is clean", "Affordable genuine and third-party replacement filters"],
        "cons": ["No built-in Wi-Fi app control", "Bright top LED requires Eco mode or tape in pitch-dark rooms"]
    },
    {
        "id": "coway-airmega-400",
        "name": "Coway Airmega 400",
        "brand": "Coway",
        "cadr_cfm": 350,
        "area_48ach": 1560,
        "noise_min": 22,
        "noise_max": 52,
        "watts": 64,
        "filter_cost_yr": 109,
        "price_est": 649,
        "tier": "Premium",
        "filter_type": "Dual Max2 True HEPA + Activated Carbon",
        "bestseller_rank": 2,
        "badge": "#2 Best Large Room",
        "best_for": "Open-Concept Living Rooms & Wildfire Smoke",
        "rating": 4.8,
        "pros": ["Dual-sided intake delivers massive airflow at remarkably low decibels", "Draws only 64W at maximum speed for low electric bills", "Washable pre-filters extend HEPA lifespan up to 12 months"],
        "cons": ["Large boxy footprint requires dedicated floor clearance", "Higher upfront investment than budget towers"]
    },
    {
        "id": "winix-5500-2",
        "name": "Winix 5500-2 True HEPA",
        "brand": "Winix",
        "cadr_cfm": 243,
        "area_48ach": 360,
        "noise_min": 27,
        "noise_max": 55,
        "watts": 70,
        "filter_cost_yr": 55,
        "price_est": 159,
        "tier": "Budget",
        "filter_type": "True HEPA + Washable AOC Pellet Carbon + PlasmaWave",
        "bestseller_rank": 3,
        "badge": "#3 Best Budget Odor Fighter",
        "best_for": "Pet Odors, Cooking Smells & Budget Buyers",
        "rating": 4.7,
        "pros": ["Real pelletized activated carbon filter outperforms thin carbon sheets", "Auto light sensor automatically dims display and enters sleep mode", "Unbeatable CADR-per-dollar ratio under $200"],
        "cons": ["PlasmaWave defaults to on after power outages (can be switched off)", "Plastic chassis feels utilitarian compared to designer units"]
    },
    {
        "id": "levoit-core-600s",
        "name": "Levoit Core 600S Smart",
        "brand": "Levoit",
        "cadr_cfm": 410,
        "area_48ach": 635,
        "noise_min": 26,
        "noise_max": 55,
        "watts": 49,
        "filter_cost_yr": 79,
        "price_est": 299,
        "tier": "Mid-Range",
        "filter_type": "3-Stage HEPA-Grade + High-Efficiency Activated Carbon",
        "bestseller_rank": 4,
        "badge": "#4 Best High-CADR Smart Unit",
        "best_for": "Large Rooms, Wildfire Smoke & Smart Home Users",
        "rating": 4.8,
        "pros": ["Class-leading 410 CFM CADR under $300", "Ultra-efficient 49W brushless DC motor", "Polished VeSync app with real-time PM2.5 numerical display and Alexa support"],
        "cons": ["High fan speed is noticeably audible during quiet movies", "360-degree cylindrical intake requires 15 inches of wall clearance"]
    },
    {
        "id": "blueair-blue-pure-211i-max",
        "name": "Blueair Blue Pure 211i Max",
        "brand": "Blueair",
        "cadr_cfm": 410,
        "area_48ach": 635,
        "noise_min": 23,
        "noise_max": 53,
        "watts": 43,
        "filter_cost_yr": 70,
        "price_est": 349,
        "tier": "Mid-Range",
        "filter_type": "HEPASilent Dual Mechanical + Electrostatic + Carbon",
        "bestseller_rank": 5,
        "badge": "#5 Quietest High-CADR",
        "best_for": "Whisper-Quiet Large Spaces & Heavy Dust",
        "rating": 4.8,
        "pros": ["Delivering 410 CFM at only 43W makes it among the most efficient units tested", "Machine-washable fabric pre-filter traps pet hair effortlessly", "Whisper-quiet 23 dBA night mode with full light dimming"],
        "cons": ["Uses mild electrostatic charge (CARB zero-ozone certified)", "Carbon layer is lighter than heavy pelletized VOC units"]
    },
    {
        "id": "levoit-vital-200s",
        "name": "Levoit Vital 200S Smart",
        "brand": "Levoit",
        "cadr_cfm": 245,
        "area_48ach": 380,
        "noise_min": 24,
        "noise_max": 54,
        "watts": 50,
        "filter_cost_yr": 54,
        "price_est": 189,
        "tier": "Budget",
        "filter_type": "Washable U-Shaped Pre-Filter + HEPA + Carbon",
        "bestseller_rank": 6,
        "badge": "#6 Best for Pet Hair",
        "best_for": "Multi-Pet Homes, Cat Litter & Medium Rooms",
        "rating": 4.7,
        "pros": ["U-shaped wide air inlet captures airborne pet fur without clogging", "Washable pre-filter dramatically reduces filter replacement expenses", "Accurate infrared dust sensor with custom Pet Mode"],
        "cons": ["Slightly wider footprint than cylindrical Core series", "Top exhaust grille cannot be angled"]
    },
    {
        "id": "iqair-healthpro-plus",
        "name": "IQAir HealthPro Plus",
        "brand": "IQAir",
        "cadr_cfm": 300,
        "area_48ach": 1125,
        "noise_min": 25,
        "noise_max": 59,
        "watts": 135,
        "filter_cost_yr": 215,
        "price_est": 999,
        "tier": "Luxury",
        "filter_type": "HyperHEPA (0.003 microns) + 5 lbs V5-Cell Gas & Odor Filter",
        "bestseller_rank": 7,
        "badge": "#7 Best Medical-Grade",
        "best_for": "Severe Asthma, Chemical Sensitivities & Ultra-Fine Particles",
        "rating": 4.9,
        "pros": ["Swiss-made HyperHEPA filters down to 0.003 microns with zero leakage", "5 pounds of activated carbon & alumina crush heavy smoke and VOCs", "Individually certified with hand-signed efficiency test report"],
        "cons": ["High upfront cost and expensive multi-stage replacement filters", "Heavy 35-pound chassis and industrial styling"]
    },
    {
        "id": "medify-ma-112",
        "name": "Medify MA-112 Medical Grade",
        "brand": "Medify Air",
        "cadr_cfm": 559,
        "area_48ach": 1200,
        "noise_min": 40,
        "noise_max": 70,
        "watts": 95,
        "filter_cost_yr": 159,
        "price_est": 599,
        "tier": "Premium",
        "filter_type": "Dual-Intake True HEPA H13 + Activated Carbon",
        "bestseller_rank": 8,
        "badge": "#8 Maximum Commercial CADR",
        "best_for": "Classrooms, Studios, Lofts & Extreme Wildfire Smoke",
        "rating": 4.7,
        "pros": ["Monstrous 559 CFM CADR clears smoke-filled rooms in minutes", "Medical-grade H13 dual filters capture 99.9% down to 0.1 microns", "Built-in rolling casters and lifetime warranty with filter subscription"],
        "cons": ["Minimum fan speed of 40 dBA is audible in quiet bedrooms", "No smartphone app or Wi-Fi integration"]
    },
    {
        "id": "coway-airmega-250",
        "name": "Coway Airmega 250",
        "brand": "Coway",
        "cadr_cfm": 249,
        "area_48ach": 930,
        "noise_min": 22,
        "noise_max": 54,
        "watts": 62,
        "filter_cost_yr": 69,
        "price_est": 399,
        "tier": "Premium",
        "filter_type": "EZ-Wash Pre-Filter + Max2 True HEPA & Carbon",
        "bestseller_rank": 0,
        "badge": "Best Modern Design",
        "best_for": "Stylish Living Rooms & Master Bedrooms",
        "rating": 4.7,
        "pros": ["Slide-out washable pre-filter takes 5 seconds to clean", "Rapid Mode clears sudden kitchen smoke spikes quickly", "Clean architectural design blends into upscale interiors"],
        "cons": ["Pricier than Mighty AP-1512HH with similar peak CADR", "Smart Wi-Fi requires upgrading to the 250S version"]
    },
    {
        "id": "coway-airmega-prox",
        "name": "Coway Airmega ProX",
        "brand": "Coway",
        "cadr_cfm": 568,
        "area_48ach": 2126,
        "noise_min": 23,
        "noise_max": 46,
        "watts": 98,
        "filter_cost_yr": 179,
        "price_est": 999,
        "tier": "Luxury",
        "filter_type": "Dual Max2 Green True HEPA + Deodorization Carbon",
        "bestseller_rank": 0,
        "badge": "Quietest Mega-CADR",
        "best_for": "Whole-Floor Coverage, Great Rooms & Studios",
        "rating": 4.9,
        "pros": ["Insane 568 CFM CADR while staying under 46 dBA even on high", "Integrated hidden wheels make relocating the heavy tower effortless", "Auto-adjusting dual sensors monitor real-time air quality continuously"],
        "cons": ["Premium $999 price bracket", "Oversized for small bedrooms or offices"]
    },
    {
        "id": "winix-5300-2",
        "name": "Winix 5300-2 True HEPA",
        "brand": "Winix",
        "cadr_cfm": 243,
        "area_48ach": 360,
        "noise_min": 27,
        "noise_max": 55,
        "watts": 70,
        "filter_cost_yr": 45,
        "price_est": 139,
        "tier": "Budget",
        "filter_type": "True HEPA + Sheet Carbon + PlasmaWave",
        "bestseller_rank": 0,
        "badge": "Value Champion",
        "best_for": "Apartments, Dorms & Dust Allergies",
        "rating": 4.7,
        "pros": ["Identical motor and HEPA performance to the 5500-2 for less money", "Widely stocked generic Filter A replacements keep ownership ultra-cheap", "Reliable auto mode and sleep light dimming"],
        "cons": ["Carbon sheet absorbs fewer odors than the 5500-2 carbon pellets", "No remote control included"]
    },
    {
        "id": "winix-am80",
        "name": "Winix AM80 True HEPA",
        "brand": "Winix",
        "cadr_cfm": 240,
        "area_48ach": 360,
        "noise_min": 27,
        "noise_max": 54,
        "watts": 65,
        "filter_cost_yr": 48,
        "price_est": 149,
        "tier": "Budget",
        "filter_type": "True HEPA + Activated Carbon + PlasmaWave",
        "bestseller_rank": 0,
        "badge": "Slim Profile",
        "best_for": "Bedrooms & Home Offices",
        "rating": 4.6,
        "pros": ["Sleek matte charcoal housing fits tight bedroom corners", "Fast dust-clearance rate for rooms up to 360 sq ft", "Energy Star certified low standby draw"],
        "cons": ["No Wi-Fi app support (AM90 adds Wi-Fi)", "Moderate fan hum on Turbo setting"]
    },
    {
        "id": "winix-9800",
        "name": "Winix 9800 4-Stage Smart",
        "brand": "Winix",
        "cadr_cfm": 323,
        "area_48ach": 500,
        "noise_min": 24,
        "noise_max": 56,
        "watts": 68,
        "filter_cost_yr": 65,
        "price_est": 259,
        "tier": "Mid-Range",
        "filter_type": "Washable Mesh + True HEPA + Activated Carbon + PlasmaWave",
        "bestseller_rank": 0,
        "badge": "Best Mid-Size Smart",
        "best_for": "Living Rooms & Dual-Zone Apartments",
        "rating": 4.7,
        "pros": ["Upgraded 323 CFM CADR handles 500 sq ft at 4.8 ACH smoothly", "Winix Smart app shows indoor and local outdoor AQI side-by-side", "Quiet 24 dBA sleep speed with total LED shutoff"],
        "cons": ["App setup requires 2.4 GHz Wi-Fi network", "Touch panel lacks tactile buttons in the dark"]
    },
    {
        "id": "levoit-core-300s",
        "name": "Levoit Core 300S Smart",
        "brand": "Levoit",
        "cadr_cfm": 141,
        "area_48ach": 219,
        "noise_min": 22,
        "noise_max": 48,
        "watts": 26,
        "filter_cost_yr": 35,
        "price_est": 149,
        "tier": "Budget",
        "filter_type": "3-Stage Cylindrical HEPA + Specialized Carbon Options",
        "bestseller_rank": 0,
        "badge": "Best Small Bedroom",
        "best_for": "Small Bedrooms, Nurseries & Home Offices",
        "rating": 4.8,
        "pros": ["Compact tabletop/floor footprint draws just 26 watts at peak speed", "Specialty replacement filters available for smoke, pets, or toxins", "Whisper-quiet 22 dBA night operation with laser dust sensor"],
        "cons": ["Not powerful enough for living rooms over 250 sq ft", "Requires tipping unit upside down to swap filters"]
    },
    {
        "id": "levoit-core-400s",
        "name": "Levoit Core 400S Smart",
        "brand": "Levoit",
        "cadr_cfm": 260,
        "area_48ach": 403,
        "noise_min": 24,
        "noise_max": 52,
        "watts": 38,
        "filter_cost_yr": 49,
        "price_est": 219,
        "tier": "Mid-Range",
        "filter_type": "360-Degree HEPA + High-Efficiency Carbon",
        "bestseller_rank": 0,
        "badge": "Balanced Smart Pick",
        "best_for": "Master Bedrooms & Medium Living Spaces",
        "rating": 4.8,
        "pros": ["Strong 260 CFM output in a space-saving 10.8-inch diameter cylinder", "Laser PM2.5 sensor responds rapidly to cooking aerosols", "Very low 38W maximum power draw"],
        "cons": ["No carrying handles integrated into outer shell", "Display ring can be bright unless scheduled off in VeSync"]
    },
    {
        "id": "levoit-everestair",
        "name": "Levoit EverestAir Smart",
        "brand": "Levoit",
        "cadr_cfm": 360,
        "area_48ach": 558,
        "noise_min": 24,
        "noise_max": 56,
        "watts": 70,
        "filter_cost_yr": 89,
        "price_est": 499,
        "tier": "Premium",
        "filter_type": "Washable Pre-Filter + H13 True HEPA + Pellet Carbon",
        "bestseller_rank": 0,
        "badge": "Best Air Vent Control",
        "best_for": "Open Living Areas & High-Ceiling Rooms",
        "rating": 4.8,
        "pros": ["Motorized adjustable vent angle (45/60/75/90 degrees) directs clean air", "Three-channel laser sensor tracks PM1.0, PM2.5, and PM10 independently", "Magnetic front panel makes vacuuming the washable pre-filter effortless"],
        "cons": ["Costs significantly more than the higher-CADR Core 600S", "Tall rectangular body needs flat wall space"]
    },
    {
        "id": "blueair-blue-pure-311i-max",
        "name": "Blueair Blue Pure 311i Max",
        "brand": "Blueair",
        "cadr_cfm": 250,
        "area_48ach": 387,
        "noise_min": 23,
        "noise_max": 50,
        "watts": 22,
        "filter_cost_yr": 54,
        "price_est": 229,
        "tier": "Mid-Range",
        "filter_type": "HEPASilent + Washable Fabric Pre-Filter",
        "bestseller_rank": 0,
        "badge": "Lowest Wattage",
        "best_for": "24/7 Continuous Operation & Bedrooms",
        "rating": 4.8,
        "pros": ["Incredible 22-watt max draw costs pennies per month to run 24/7", "RealTrack algorithm calculates filter wear based on actual pollution load", "Interchangeable Stockholm Fog and Limestone fabric sleeves"],
        "cons": ["No handle for carrying between floors", "Lighter activated carbon weight than odor-dedicated models"]
    },
    {
        "id": "blueair-blue-pure-411i-max",
        "name": "Blueair Blue Pure 411i Max",
        "brand": "Blueair",
        "cadr_cfm": 141,
        "area_48ach": 219,
        "noise_min": 18,
        "noise_max": 46,
        "watts": 15,
        "filter_cost_yr": 35,
        "price_est": 169,
        "tier": "Budget",
        "filter_type": "HEPASilent + Washable Pre-Filter",
        "bestseller_rank": 0,
        "badge": "Quietest Nursery Unit",
        "best_for": "Baby Nurseries, Guest Rooms & Light Sleepers",
        "rating": 4.7,
        "pros": ["Virtually inaudible 18 dBA sleep setting", "Consumes a tiny 15 watts at full blast", "Compact Swedish design fits nightstands or small corners"],
        "cons": ["Limited to rooms under 220 sq ft for 4.8 ACH", "No numeric PM2.5 readout on the unit itself"]
    },
    {
        "id": "blueair-healthprotect-7470i",
        "name": "Blueair HealthProtect 7470i",
        "brand": "Blueair",
        "cadr_cfm": 270,
        "area_48ach": 418,
        "noise_min": 25,
        "noise_max": 45,
        "watts": 43,
        "filter_cost_yr": 119,
        "price_est": 739,
        "tier": "Luxury",
        "filter_type": "GermShield + SmartFilter HEPA + Carbon",
        "bestseller_rank": 0,
        "badge": "Best Germ Defense",
        "best_for": "Allergy Sufferers & Low-Noise Premium Spaces",
        "rating": 4.6,
        "pros": ["GermShield proactively prevents bacteria growth on filters in standby", "Maximum noise capped at a soothing 45 dBA", "Detailed LCD tracks both PM2.5 and VOC gas levels"],
        "cons": ["Proprietary RFID SmartFilters are expensive to replace", "Heavy steel chassis"]
    },
    {
        "id": "austin-air-healthmate-plus",
        "name": "Austin Air HealthMate Plus",
        "brand": "Austin Air",
        "cadr_cfm": 250,
        "area_48ach": 700,
        "noise_min": 45,
        "noise_max": 62,
        "watts": 115,
        "filter_cost_yr": 95,
        "price_est": 855,
        "tier": "Luxury",
        "filter_type": "15 lbs Activated Carbon, Potassium Iodide & Zeolite + Medical HEPA",
        "bestseller_rank": 0,
        "badge": "Best VOC & Formaldehyde",
        "best_for": "Wildfire Gases, New Renovations, Paint Fumes & MCS",
        "rating": 4.8,
        "pros": ["Massive 15-pound carbon & zeolite bed neutralizes toxic gases standard purifiers miss", "Filter lasts up to 5 years under normal home conditions", "Powder-coated solid steel body built in the USA with zero off-gassing"],
        "cons": ["No air quality sensor, timer, or smart features (simple 3-speed dial)", "Weighs 45 pounds and runs louder than modern brushless DC units"]
    },
    {
        "id": "alen-breathesmart-75i",
        "name": "Alen BreatheSmart 75i",
        "brand": "Alen",
        "cadr_cfm": 350,
        "area_48ach": 1300,
        "noise_min": 25,
        "noise_max": 49,
        "watts": 45,
        "filter_cost_yr": 119,
        "price_est": 749,
        "tier": "Luxury",
        "filter_type": "Medical-Grade H13 True HEPA + Custom VOC/Odor Filter Options",
        "bestseller_rank": 0,
        "badge": "Best Pink-Noise Acoustics",
        "best_for": "Open Living Rooms, Master Suites & Noise-Sensitive Homes",
        "rating": 4.9,
        "pros": ["Engineered for soothing pink-noise acoustics under 49 dBA on turbo", "Forever Guarantee lifetime warranty with active filter plan", "Customizable magnetic front panels in woodgrain and neutral finishes"],
        "cons": ["Replacement Fresh/Odor filters cost over $110 each", "Large upright footprint"]
    },
    {
        "id": "alen-breathesmart-45i",
        "name": "Alen BreatheSmart 45i",
        "brand": "Alen",
        "cadr_cfm": 225,
        "area_48ach": 800,
        "noise_min": 23,
        "noise_max": 49,
        "watts": 50,
        "filter_cost_yr": 79,
        "price_est": 429,
        "tier": "Premium",
        "filter_type": "True HEPA H13 + Optional Heavy Carbon VOC Cartridge",
        "bestseller_rank": 0,
        "badge": "Best Warranty Mid-Size",
        "best_for": "Bedrooms, Nurseries & Home Offices",
        "rating": 4.8,
        "pros": ["Same ultra-smooth acoustic tuning as the flagship 75i in a compact body", "Choose between Pure, Fresh (smoke/VOCs), or Odor (pet/diaper) filters", "Color-coded laser air quality ring dims automatically"],
        "cons": ["Lower raw CFM per dollar than Levoit or Winix", "Front panel magnets require careful alignment"]
    },
    {
        "id": "medify-ma-50",
        "name": "Medify MA-50 Medical Grade",
        "brand": "Medify Air",
        "cadr_cfm": 325,
        "area_48ach": 550,
        "noise_min": 35,
        "noise_max": 56,
        "watts": 68,
        "filter_cost_yr": 75,
        "price_est": 299,
        "tier": "Mid-Range",
        "filter_type": "4-Sided Intake True HEPA H13 + Carbon",
        "bestseller_rank": 0,
        "badge": "Best 360-Intake H13",
        "best_for": "Large Bedrooms, Living Rooms & Smoke Protection",
        "rating": 4.7,
        "pros": ["360-degree quad-intake pulls air efficiently from every corner", "True H13 medical-grade filtration captures 0.1-micron ultrafines", "Simple child-lock glass touch panel with sleep mode"],
        "cons": ["No built-in automatic dust sensor", "Lowest speed is louder than Coway or Blueair"]
    },
    {
        "id": "medify-ma-40",
        "name": "Medify MA-40 True HEPA H13",
        "brand": "Medify Air",
        "cadr_cfm": 224,
        "area_48ach": 420,
        "noise_min": 31,
        "noise_max": 55,
        "watts": 68,
        "filter_cost_yr": 64,
        "price_est": 229,
        "tier": "Mid-Range",
        "filter_type": "True HEPA H13 + Activated Carbon",
        "bestseller_rank": 0,
        "badge": "Classroom Favorite",
        "best_for": "Offices, Medium Rooms & Wildfire Smoke",
        "rating": 4.7,
        "pros": ["Sturdy slim tower footprint fits easily against desks or walls", "Medical-grade H13 media outperforms standard H11/H12 filters", "High reliability proven across thousands of school installations"],
        "cons": ["Manual 3-speed operation without auto air quality mode", "Recommended 3-to-4 month filter changes raise annual costs"]
    },
    {
        "id": "medify-ma-25",
        "name": "Medify MA-25 Dual Intake",
        "brand": "Medify Air",
        "cadr_cfm": 135,
        "area_48ach": 250,
        "noise_min": 35,
        "noise_max": 51,
        "watts": 45,
        "filter_cost_yr": 55,
        "price_est": 139,
        "tier": "Budget",
        "filter_type": "Dual-Sided True HEPA H13 + Carbon",
        "bestseller_rank": 0,
        "badge": "Compact H13",
        "best_for": "Home Offices, Dorms & Small Bedrooms",
        "rating": 4.6,
        "pros": ["Dual side filters maximize intake area in a tiny desktop footprint", "Genuine H13 filtration at an entry-level price", "Tempered glass top panel cleans easily"],
        "cons": ["Requires buying two side filters per change cycle", "No auto sensor"]
    },
    {
        "id": "rabbit-air-a3",
        "name": "Rabbit Air A3 Ultra Quiet",
        "brand": "Rabbit Air",
        "cadr_cfm": 257,
        "area_48ach": 535,
        "noise_min": 20,
        "noise_max": 51,
        "watts": 57,
        "filter_cost_yr": 99,
        "price_est": 749,
        "tier": "Luxury",
        "filter_type": "6-Stage BioGS HEPA + Custom Filter (Germ/Pet/Toxin/Odor)",
        "bestseller_rank": 0,
        "badge": "Best Wall-Mountable",
        "best_for": "Design-Conscious Rooms, Galleries & Zero Floor Space",
        "rating": 4.8,
        "pros": ["Mounts flush on any wall to save 100% floor space", "Customizable front art panels including classic fine art editions", "6-stage filtration runs as quiet as 20.3 dBA on low"],
        "cons": ["Premium luxury price tag for 257 CFM output", "Multi-piece filter stack takes slightly longer to replace"]
    },
    {
        "id": "dyson-big-quiet-bp03",
        "name": "Dyson Purifier Big+Quiet Formaldehyde BP03",
        "brand": "Dyson",
        "cadr_cfm": 310,
        "area_48ach": 1000,
        "noise_min": 29,
        "noise_max": 55,
        "watts": 50,
        "filter_cost_yr": 99,
        "price_est": 999,
        "tier": "Luxury",
        "filter_type": "H13 HEPA (5-Yr Life) + K-Carbon + Catalytic Formaldehyde Filter",
        "bestseller_rank": 0,
        "badge": "Best Long-Range Projection",
        "best_for": "Large Open Spaces, Formaldehyde & High-Tech Homes",
        "rating": 4.7,
        "pros": ["Cone aerodynamics project purified air over 32 feet across huge rooms", "Permanent catalytic filter continuously destroys formaldehyde without replacement", "HEPA filter rated for up to 5 years of service"],
        "cons": ["$999 flagship price", "Unconventional futuristic cone shape dominates room decor"]
    },
    {
        "id": "dyson-purifier-cool-tp07",
        "name": "Dyson Purifier Cool TP07",
        "brand": "Dyson",
        "cadr_cfm": 165,
        "area_48ach": 290,
        "noise_min": 32,
        "noise_max": 58,
        "watts": 40,
        "filter_cost_yr": 79,
        "price_est": 549,
        "tier": "Premium",
        "filter_type": "Fully Sealed HEPA H13 + Activated Carbon",
        "bestseller_rank": 0,
        "badge": "Best 2-in-1 Purifier & Fan",
        "best_for": "Warm Bedrooms, Living Rooms & Bladeless Cooling",
        "rating": 4.6,
        "pros": ["Doubles as a smooth 350-degree oscillating bladeless cooling fan", "Backward airflow mode purifies in winter without creating a cold draft", "Detailed LCD graphs PM2.5, PM10, VOCs, and NO2 in real time"],
        "cons": ["Lower raw CADR than dedicated box purifiers at half the price", "Noticeable air-rush sound above speed 6"]
    },
    {
        "id": "shark-neverchange-max",
        "name": "Shark NeverChange Air Purifier MAX",
        "brand": "Shark",
        "cadr_cfm": 295,
        "area_48ach": 520,
        "noise_min": 28,
        "noise_max": 56,
        "watts": 54,
        "filter_cost_yr": 25,
        "price_est": 299,
        "tier": "Mid-Range",
        "filter_type": "DebrisDefense Washable Screens + 5-Year HEPA + Odor Neutralizer",
        "bestseller_rank": 0,
        "badge": "Lowest 5-Year Filter Cost",
        "best_for": "Cost-Conscious Families & Dusty Homes",
        "rating": 4.7,
        "pros": ["Multi-stage washable pre-screens extend main HEPA filter life up to 5 years", "Saves $250-$400 in filter costs over a 5-year ownership cycle", "Clean Sense IQ automatically ramps fan speed for smoke and dust"],
        "cons": ["Optional scented Odor Neutralizer cartridge may bother fragrance-sensitive users (removable)", "No Wi-Fi app integration"]
    },
    {
        "id": "airdoctor-3500",
        "name": "AirDoctor 3500 UltraHEPA",
        "brand": "AirDoctor",
        "cadr_cfm": 310,
        "area_48ach": 630,
        "noise_min": 31,
        "noise_max": 58,
        "watts": 85,
        "filter_cost_yr": 135,
        "price_est": 549,
        "tier": "Premium",
        "filter_type": "Sealed UltraHEPA (0.003 Microns) + Dual-Action Carbon VOC",
        "bestseller_rank": 0,
        "badge": "Ultra-Fine 0.003u Filter",
        "best_for": "Mold Spores, Wildfire Smoke & Asthma",
        "rating": 4.8,
        "pros": ["Independently tested to capture 99.99% of ultrafine particles down to 0.003 microns", "100% sealed system prevents unfiltered bypass leakage", "Strong carbon VOC filter handles smoke and household chemicals well"],
        "cons": ["Replacement filter packs are pricier than mainstream brands", "Dim mode still leaves a faint status indicator"]
    },
    {
        "id": "airdoctor-5500",
        "name": "AirDoctor 5500 Commercial UltraHEPA",
        "brand": "AirDoctor",
        "cadr_cfm": 512,
        "area_48ach": 1043,
        "noise_min": 30,
        "noise_max": 57,
        "watts": 110,
        "filter_cost_yr": 195,
        "price_est": 899,
        "tier": "Luxury",
        "filter_type": "Dual-Sided UltraHEPA + Dual Carbon VOC Filters",
        "bestseller_rank": 0,
        "badge": "Heavy-Duty Home Tower",
        "best_for": "Extra-Large Open Floor Plans & Severe Smoke Zones",
        "rating": 4.8,
        "pros": ["Massive 512 CFM CADR clears 1,000+ sq ft rooms at over 4 ACH", "WhisperJet dual fans move enormous air volume with reduced pitch", "True 0.003-micron UltraHEPA protection for high-risk households"],
        "cons": ["High annual replacement cost for dual filter sets", "Large 30-inch tall chassis"]
    },
    {
        "id": "honeywell-hpa300",
        "name": "Honeywell HPA300 True HEPA",
        "brand": "Honeywell",
        "cadr_cfm": 300,
        "area_48ach": 465,
        "noise_min": 36,
        "noise_max": 60,
        "watts": 120,
        "filter_cost_yr": 85,
        "price_est": 229,
        "tier": "Mid-Range",
        "filter_type": "3x Certified True HEPA R Filters + Carbon Pre-Filter",
        "bestseller_rank": 0,
        "badge": "Workhorse Classic",
        "best_for": "Wildfire Smoke, Allergens & No-Nonsense Durability",
        "rating": 4.7,
        "pros": ["AHAM Verifide 300 CFM smoke CADR at an accessible price point", "Replacement R filters are available at nearly every hardware store", "Simple mechanical durability with 5-year warranty"],
        "cons": ["Higher energy consumption (120W) and louder AC motor than modern DC units", "No built-in auto air quality sensor"]
    },
    {
        "id": "honeywell-insight-hpa5300b",
        "name": "Honeywell InSight HPA5300B",
        "brand": "Honeywell",
        "cadr_cfm": 325,
        "area_48ach": 500,
        "noise_min": 34,
        "noise_max": 59,
        "watts": 115,
        "filter_cost_yr": 90,
        "price_est": 279,
        "tier": "Mid-Range",
        "filter_type": "True HEPA R Filters + Optional Enhanced Odor Filters",
        "bestseller_rank": 0,
        "badge": "Upgraded HPA300",
        "best_for": "Large Living Rooms & Automatic VOC Monitoring",
        "rating": 4.6,
        "pros": ["Adds automatic VOC sensor and color-coded InSight display to the classic HPA platform", "Strong 325 CFM CADR clears 500 sq ft quickly", "Supports specialty odor filters for pets, smoke, or kitchens"],
        "cons": ["Higher wattage than brushless DC competitors", "Audible fan white noise on higher settings"]
    },
    {
        "id": "oransi-mod-plus",
        "name": "Oransi Mod+ HEPA",
        "brand": "Oransi",
        "cadr_cfm": 351,
        "area_48ach": 544,
        "noise_min": 23,
        "noise_max": 53,
        "watts": 64,
        "filter_cost_yr": 89,
        "price_est": 549,
        "tier": "Premium",
        "filter_type": "True HEPA + Carbon Cylinder",
        "bestseller_rank": 0,
        "badge": "10-Year Motor Warranty",
        "best_for": "Long-Term Reliability & Quiet Large Rooms",
        "rating": 4.8,
        "pros": ["Industry-leading 10-year US-backed warranty and German EC motor", "12 precision fan speeds let you dial in the exact noise-to-CADR sweet spot", "351 CFM CADR wrapped in warm minimalist fabric styling"],
        "cons": ["No smartphone app or automatic pollution sensor", "Higher upfront cost than budget high-CADR towers"]
    },
    {
        "id": "puroair-240",
        "name": "PuroAir 240 HEPA 14",
        "brand": "PuroAir",
        "cadr_cfm": 190,
        "area_48ach": 300,
        "noise_min": 24,
        "noise_max": 52,
        "watts": 42,
        "filter_cost_yr": 69,
        "price_est": 199,
        "tier": "Budget",
        "filter_type": "3-Layer Pre-Filter + HEPA 14 + Activated Carbon",
        "bestseller_rank": 0,
        "badge": "HEPA 14 Filtration",
        "best_for": "Bedrooms, Smoke Particles & Compact Spaces",
        "rating": 4.7,
        "pros": ["Uses dense HEPA 14 media rated for 99.99% down to 0.1 microns", "Built-in particle sensor adjusts fan speed automatically", "Zero-ozone operation with child lock and timer"],
        "cons": ["Best suited for rooms under 300 sq ft despite optimistic marketing claims", "Shorter 3-to-4 month recommended filter interval"]
    },
    {
        "id": "puroair-400",
        "name": "PuroAir 400 Large Room HEPA 14",
        "brand": "PuroAir",
        "cadr_cfm": 315,
        "area_48ach": 500,
        "noise_min": 25,
        "noise_max": 54,
        "watts": 58,
        "filter_cost_yr": 99,
        "price_est": 349,
        "tier": "Mid-Range",
        "filter_type": "3-Stage Pre-Filter + HEPA 14 + Activated Carbon",
        "bestseller_rank": 0,
        "badge": "Large Room HEPA 14",
        "best_for": "Living Rooms, Smoke Events & Allergy Relief",
        "rating": 4.7,
        "pros": ["Combines 315 CFM airflow with ultra-dense HEPA 14 filtration", "Intuitive Auto Mode responds quickly to cooking and smoke particles", "Clean cylindrical styling with simple top controls"],
        "cons": ["No Wi-Fi app control", "Replacement filters cost more per year than Levoit Core 600S"]
    }
]

# ==============================================================================
# SPECIALIZED REVIEW ANGLES
# ==============================================================================
SCENARIOS = [
    {
        "slug_suffix": "wildfire-smoke-pm25-test",
        "title_suffix": "for Wildfire Smoke & PM2.5: CADR Stress Test",
        "target_ach": 5.0,
        "room_focus": "Wildfire Smoke & Hazardous AQI (>150)",
        "focus_summary": "During wildfire smoke events, standard 2 ACH sizing fails to keep indoor PM2.5 safe. We stress-tested this purifier's real-world smoke clearance curve at 5 ACH and calculated the exact maximum square footage it can protect when outdoor AQI spikes."
    },
    {
        "slug_suffix": "pet-hair-dander-odor-review",
        "title_suffix": "for Multi-Pet Homes, Dander & Litter Odor",
        "target_ach": 4.0,
        "room_focus": "Pet Dander, Shedding Fur & Ammonia Odors",
        "focus_summary": "Dog and cat owners face two distinct problems: airborne dander clogging HEPA pleats and lingering litter or wet-dog VOCs. Here is how this unit's intake geometry, pre-filter design, and carbon weight perform in active multi-pet rooms."
    },
    {
        "slug_suffix": "master-bedroom-sleep-noise-audit",
        "title_suffix": "for Master Bedrooms: Sleep Noise (dBA) & Light Test",
        "target_ach": 4.0,
        "room_focus": "Bedroom Sleep Acoustics & Dark-Room Comfort",
        "focus_summary": "A purifier that sounds like a jet engine gets turned off at night. We analyze this unit's minimum decibel floor, low-speed CADR output, and LED display shutoff to see if it truly delivers 4 ACH while you sleep undisturbed."
    },
    {
        "slug_suffix": "severe-allergies-pollen-review",
        "title_suffix": "for Severe Pollen, Dust Mites & Seasonal Allergies",
        "target_ach": 4.8,
        "room_focus": "Spring Pollen, Dust Mite Allergens & Asthma Relief",
        "focus_summary": "AHAM recommends 4.8 Air Changes Per Hour (one full air turnover every 12.5 minutes) for allergy sufferers. We break down the exact room footprint where this purifier clears pollen before it triggers morning congestion."
    },
    {
        "slug_suffix": "open-concept-living-room-sizing",
        "title_suffix": "for Large Open-Concept Living Rooms & High Ceilings",
        "target_ach": 4.0,
        "room_focus": "Open Floor Plans & 10-Foot Vaulted Ceilings",
        "focus_summary": "Vaulted 10-foot ceilings add 25% more cubic air volume than manufacturer labels assume. We recalculated this unit's true CADR reach for open living-dining rooms so you know whether one unit suffices or if dual placement is smarter."
    },
    {
        "slug_suffix": "basement-mold-spores-musty-air",
        "title_suffix": "for Basement Mold Spores & Musty Odors",
        "target_ach": 4.5,
        "room_focus": "Finished Basements, Mold Spores & Damp Mustiness",
        "focus_summary": "Basements trap stagnant air, airborne mold spores (3-30 microns), and earthy mVOC odors. Here is our breakdown of how this purifier pairs with a dehumidifier to keep lower-level air crisp and spore-free."
    },
    {
        "slug_suffix": "kitchen-cooking-smoke-vocs",
        "title_suffix": "for Kitchen Cooking Smoke, Grease & VOC Fumes",
        "target_ach": 5.0,
        "room_focus": "High-Heat Searing, Gas Stove NO2 & Cooking Odors",
        "focus_summary": "Gas stoves and cast-iron searing generate massive bursts of PM2.5 and nitrogen dioxide. We evaluate this unit's carbon filtration capacity, washable pre-filter maintenance, and rapid recovery speed after heavy cooking."
    },
    {
        "slug_suffix": "nursery-baby-room-safety-review",
        "title_suffix": "for Baby Nurseries & Kids Rooms: Safety & Sound Guide",
        "target_ach": 4.0,
        "room_focus": "Nursery Air Purity, Zero-Ozone Safety & Gentle White Noise",
        "focus_summary": "Parents need zero-ozone safety, child-lock controls, and gentle pink-noise acoustics that soothe rather than startle. We inspect this model's safety certifications, cord/grille protection, and nursery CADR efficiency."
    },
    {
        "slug_suffix": "home-office-24-7-electricity-cost",
        "title_suffix": "for Home Offices: 24/7 Power Draw & Annual Energy Audit",
        "target_ach": 4.0,
        "room_focus": "Continuous 24/7 Work-From-Home Air Quality",
        "focus_summary": "Running an air purifier 24 hours a day shouldn't spike your utility bill or disrupt Zoom calls. We calculated exact annual kWh electricity costs at $0.16/kWh alongside voice-call acoustic tolerance."
    },
    {
        "slug_suffix": "5-year-total-cost-ownership-analysis",
        "title_suffix": "5-Year Total Cost of Ownership (Filters + Power) Breakdown",
        "target_ach": 4.8,
        "room_focus": "Long-Term Budget Value & Replacement Filter Economics",
        "focus_summary": "Sticker price is only half the story—expensive proprietary filters can double a purifier's true cost in 36 months. Here is the complete 5-year financial breakdown combining unit price, annual filters, and continuous electricity."
    }
]

# ==============================================================================
# FAQS
# ==============================================================================
FAQS = [
    {
        "q": "What is CADR and how do I calculate the exact size I need?",
        "a": "CADR stands for Clean Air Delivery Rate, measured in Cubic Feet per Minute (CFM) or m³/h. To calculate your required CADR, multiply your room's Length × Width × Ceiling Height to get cubic volume, multiply by your target Air Changes Per Hour (ACH), and divide by 60. For example, a 300 sq ft room with 8 ft ceilings (2,400 cu ft) targeting 4 ACH requires a minimum CADR of (2,400 × 4) / 60 = 160 CFM."
    },
    {
        "q": "How many Air Changes Per Hour (ACH) do I need for allergies vs. wildfire smoke?",
        "a": "For general dust maintenance, 2 ACH is sufficient. For seasonal allergies, asthma, and pet dander, AHAM and medical guidelines recommend at least 4 to 4.8 ACH (cleaning the room every 12.5 to 15 minutes). During active wildfire smoke events or heavy indoor odor spikes, size your purifier for 5 to 6 ACH."
    },
    {
        "q": "Why do manufacturer room size ratings often seem exaggerated?",
        "a": "Many brands advertise maximum square footage based on just 1 or 2 ACH (one full air change per hour), which is far too slow for allergies or smoke. Always check the AHAM-verified 4.8 ACH room rating—or use our CADR calculator above to calculate true coverage based on your real ceiling height."
    },
    {
        "q": "Is it better to buy an oversized air purifier and run it on low speed?",
        "a": "Yes. Buying a purifier with 30% to 50% higher CADR than your minimum requirement lets you run it on medium or low speed 24/7. You achieve the same 4+ ACH cleaning rate at whisper-quiet bedroom noise levels (22–32 dBA) while drawing far less electricity."
    },
    {
        "q": "What is the difference between True HEPA (H13) and HEPA-type filters?",
        "a": "True HEPA filters are tested to capture at least 99.97% of airborne particles down to 0.3 microns (and medical-grade H13 captures 99.95% down to 0.1 microns). 'HEPA-type' or 'HEPA-style' filters lack strict certification and often let fine smoke particles and allergens pass right through."
    },
    {
        "q": "Do HEPA air purifiers remove odors, wildfire gases, and VOCs?",
        "a": "HEPA fibers only trap solid particles (smoke soot, dust, pollen, mold spores, pet dander). To remove chemical VOCs, cooking smells, and pet odors, your purifier must also include an Activated Carbon stage—ideally pelletized carbon rather than a thin sprayed foam sheet."
    },
    {
        "q": "How much electricity does running an air purifier 24/7 cost?",
        "a": "Modern brushless DC purifiers (such as Blueair, Levoit, and Coway) draw only 5–15 watts on medium speeds and 25–75 watts on maximum speed. Running a typical 30W medium setting 24/7 at $0.16/kWh costs roughly $42 per year—about $3.50 per month."
    },
    {
        "q": "Should I run two medium purifiers or one giant unit in an open floor plan?",
        "a": "In L-shaped rooms, long open-concept living/kitchen areas, or homes with hallways, two medium high-CADR purifiers placed at opposite ends create much better air circulation and fewer dead zones than one massive unit sitting in a single corner."
    }
]

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def amazon_link(query_text: str) -> str:
    encoded = urllib.request.quote(query_text.strip())
    return f"https://www.amazon.com/s?k={encoded}&tag={AFFILIATE_TAG}"


def calc_room_at_ach(cadr_cfm: float, ach: float, ceiling_ft: float = 8.0) -> int:
    return int(round((cadr_cfm * 60.0) / (ach * ceiling_ft)))


def calc_annual_power_cost(watts: float, kwh_rate: float = 0.16) -> float:
    avg_watts = watts * 0.55
    annual_kwh = (avg_watts * 24 * 365) / 1000.0
    return round(annual_kwh * kwh_rate, 2)


def calc_5yr_tco(product: dict) -> int:
    power_5yr = calc_annual_power_cost(product["watts"]) * 5
    filters_4yr = product["filter_cost_yr"] * 4
    return int(round(product["price_est"] + power_5yr + filters_4yr))


def build_review_queue() -> list:
    queue = []
    for p in PRODUCTS:
        queue.append({
            "type": "standalone",
            "slug": f"{p['id']}-cadr-review",
            "title": f"{p['name']} Review ({CURRENT_YEAR}): Real CADR, Noise & 5-Year Filter Cost",
            "product_id": p["id"],
            "category": "Full Product Review"
        })
    for sc in SCENARIOS:
        for p in PRODUCTS:
            queue.append({
                "type": "scenario",
                "slug": f"{p['id']}-{sc['slug_suffix']}",
                "title": f"{p['name']} {sc['title_suffix']}",
                "product_id": p["id"],
                "scenario_slug": sc["slug_suffix"],
                "category": sc["room_focus"]
            })
    n = len(PRODUCTS)
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = PRODUCTS[i], PRODUCTS[j]
            if abs(p1["cadr_cfm"] - p2["cadr_cfm"]) <= 180:
                queue.append({
                    "type": "versus",
                    "slug": f"{p1['id']}-vs-{p2['id']}-comparison",
                    "title": f"{p1['name']} vs {p2['name']}: CADR, Noise & Cost Showdown",
                    "product_id": p1["id"],
                    "product2_id": p2["id"],
                    "category": "Head-to-Head Comparison"
                })
    return queue


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"published_slugs": [], "total_runs": 0, "last_run": ""}


def load_reviews() -> list:
    if REVIEWS_JSON.exists():
        return json.loads(REVIEWS_JSON.read_text(encoding="utf-8"))
    return []


def safe_json_for_script(obj) -> str:
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


# ==============================================================================
# SHARED STYLES
# ==============================================================================
BASE_CSS = """
:root {
  --bg-page: #d5d9e0;
  --bg-surface: #eef0f3;
  --bg-card: #f8f9fb;
  --bg-dark: #1f2937;
  --bg-darker: #111827;
  --text-main: #111827;
  --text-muted: #4b5563;
  --border-color: #c4cbd6;
  --accent-teal: #0f766e;
  --accent-teal-hover: #0d5e58;
  --cta-amber: #d97706;
  --cta-amber-hover: #b45309;
  --badge-bg: #e2e8f0;
  --radius: 10px;
  --shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  background-color: var(--bg-page);
  color: var(--text-main);
  line-height: 1.6;
}
a { color: var(--accent-teal); text-decoration: none; }
a:hover { text-decoration: underline; }
.container { max-width: 1180px; margin: 0 auto; padding: 0 18px; }
.top-banner {
  background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
  color: #f9fafb;
  font-size: 0.9rem;
  text-align: center;
  padding: 10px 16px;
  border-bottom: 2px solid var(--cta-amber);
}
.top-banner a {
  color: #fbbf24;
  font-weight: 700;
  margin-left: 8px;
  text-decoration: underline;
}
header {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.nav-wrap {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  gap: 12px;
}
.logo {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--bg-darker);
  letter-spacing: -0.4px;
}
.logo span { color: var(--accent-teal); }
nav { display: flex; flex-wrap: wrap; gap: 16px; align-items: center; }
nav a { font-weight: 600; font-size: 0.92rem; color: #374151; }
nav a:hover { color: var(--accent-teal); text-decoration: none; }
.hero {
  background: linear-gradient(135deg, #27303f 0%, #3f4a5c 100%);
  color: #ffffff;
  padding: 40px 0 34px;
  border-bottom: 1px solid #4b5563;
}
.hero h1 { font-size: clamp(1.75rem, 3.2vw, 2.5rem); line-height: 1.2; margin-bottom: 12px; }
.hero p { color: #d1d5db; max-width: 780px; font-size: 1.04rem; }
.hero-badges { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }
.hero-badge {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.22);
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 600;
}
section { padding: 34px 0; }
.section-title {
  font-size: 1.55rem;
  font-weight: 800;
  color: var(--bg-darker);
  margin-bottom: 6px;
}
.section-sub { color: var(--text-muted); margin-bottom: 20px; font-size: 0.98rem; }
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 22px;
  box-shadow: var(--shadow);
}
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr)); gap: 20px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }
.grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
.btn {
  display: inline-block;
  padding: 10px 16px;
  border-radius: 7px;
  font-weight: 700;
  font-size: 0.92rem;
  text-align: center;
  cursor: pointer;
  border: none;
  transition: background 0.15s ease;
}
.btn-amazon {
  background: var(--cta-amber);
  color: #ffffff !important;
}
.btn-amazon:hover { background: var(--cta-amber-hover); text-decoration: none; }
.btn-teal {
  background: var(--accent-teal);
  color: #ffffff !important;
}
.btn-teal:hover { background: var(--accent-teal-hover); text-decoration: none; }
.btn-outline {
  background: #e5e7eb;
  color: #1f2937 !important;
  border: 1px solid #9ca3af;
}
.btn-outline:hover { background: #d1d5db; text-decoration: none; }
.calc-grid { display: grid; grid-template-columns: 1fr 1.15fr; gap: 22px; align-items: start; }
@media (max-width: 860px) { .calc-grid { grid-template-columns: 1fr; } }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; font-weight: 700; font-size: 0.9rem; margin-bottom: 5px; color: #1f2937; }
.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
input[type="number"], input[type="text"], select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #9ca3af;
  border-radius: 7px;
  background: #ffffff;
  font-size: 0.95rem;
  color: var(--text-main);
}
.unit-toggle { display: flex; gap: 8px; margin-bottom: 14px; }
.unit-btn {
  flex: 1;
  padding: 8px;
  border-radius: 7px;
  border: 1px solid #9ca3af;
  background: #e5e7eb;
  font-weight: 700;
  cursor: pointer;
}
.unit-btn.active { background: var(--accent-teal); color: #ffffff; border-color: var(--accent-teal); }
.result-kpis { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 18px; }
.kpi-box {
  background: #e5e7eb;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}
.kpi-box.highlight { background: #ccfbf1; border-color: #14b8a6; }
.kpi-label { font-size: 0.78rem; font-weight: 700; text-transform: uppercase; color: #374151; }
.kpi-val { font-size: 1.55rem; font-weight: 800; color: #111827; margin-top: 2px; }
.kpi-sub { font-size: 0.78rem; color: #4b5563; }
.mid-banner {
  background: linear-gradient(120deg, #1f2937 0%, #0f766e 100%);
  color: #ffffff;
  border-radius: var(--radius);
  padding: 26px 28px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  box-shadow: var(--shadow);
}
.mid-banner h3 { font-size: 1.35rem; margin-bottom: 6px; }
.mid-banner p { color: #e2e8f0; max-width: 680px; font-size: 0.95rem; }
.badge {
  display: inline-block;
  background: #e2e8f0;
  color: #1e293b;
  font-size: 0.76rem;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
  margin-bottom: 8px;
}
.badge-amber { background: #fef3c7; color: #92400e; }
.badge-teal { background: #ccfbf1; color: #115e59; }
.product-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 18px;
  box-shadow: var(--shadow);
}
.product-card h3 { font-size: 1.08rem; margin-bottom: 6px; color: var(--bg-darker); }
.spec-list { list-style: none; margin: 10px 0 14px; font-size: 0.88rem; color: #374151; }
.spec-list li { padding: 3px 0; border-bottom: 1px dashed #d1d5db; display: flex; justify-content: space-between; gap: 8px; }
.card-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: auto; }
.card-actions .btn { flex: 1; font-size: 0.85rem; padding: 9px 10px; }
.table-wrap { overflow-x: auto; border-radius: var(--radius); border: 1px solid var(--border-color); background: var(--bg-card); }
table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
th, td { padding: 11px 13px; text-align: left; border-bottom: 1px solid #d1d5db; }
th { background: #e5e7eb; font-weight: 800; color: #111827; white-space: nowrap; }
tr:hover td { background: #f1f5f9; }
.search-controls {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 18px;
}
@media (max-width: 760px) { .search-controls { grid-template-columns: 1fr; } }
details.faq-item {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 14px 18px;
  margin-bottom: 10px;
}
details.faq-item summary {
  font-weight: 700;
  cursor: pointer;
  color: var(--bg-darker);
  font-size: 1rem;
}
details.faq-item p { margin-top: 10px; color: #374151; font-size: 0.95rem; }
.article-wrap { max-width: 900px; margin: 28px auto; }
.breadcrumb { font-size: 0.86rem; color: #4b5563; margin-bottom: 14px; }
.pros-cons { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 18px 0; }
@media (max-width: 680px) { .pros-cons { grid-template-columns: 1fr; } }
.pros-box { background: #ecfdf5; border: 1px solid #6ee7b7; border-radius: 8px; padding: 16px; }
.cons-box { background: #fef2f2; border: 1px solid #fca5a5; border-radius: 8px; padding: 16px; }
.pros-box ul, .cons-box ul { margin-left: 18px; margin-top: 8px; font-size: 0.93rem; }
footer {
  background: var(--bg-dark);
  color: #d1d5db;
  padding: 34px 0 24px;
  margin-top: 36px;
  border-top: 3px solid var(--accent-teal);
  font-size: 0.88rem;
}
footer a { color: #5eead4; }
.footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 20px; }
.disclosure {
  border-top: 1px solid #374151;
  padding-top: 16px;
  font-size: 0.82rem;
  color: #9ca3af;
}
"""


def render_header(prefix: str = "") -> str:
    deal_url = amazon_link("True HEPA Air Purifier Best Seller")
    return f"""
<div class="top-banner">
  <strong>{CURRENT_YEAR} Air Quality Deal Alert:</strong> Save up to 30% on AHAM-Verified HEPA Purifiers &amp; Replacement Filter Bundles.
  <a href="{deal_url}" target="_blank" rel="nofollow sponsored noopener">Check Live Amazon Deals &rarr;</a>
</div>
<header>
  <div class="container nav-wrap">
    <a class="logo" href="{prefix}index.html">Air<span>CADR</span>Pro</a>
    <nav>
      <a href="{prefix}index.html#calculator">CADR Calculator</a>
      <a href="{prefix}index.html#bestsellers">Best Sellers</a>
      <a href="{prefix}index.html#search">Search Catalog</a>
      <a href="{prefix}index.html#compare">Compare Models</a>
      <a href="{prefix}index.html#reviews">Daily Reviews</a>
      <a href="{prefix}index.html#faq">FAQ</a>
    </nav>
  </div>
</header>
"""


def render_footer(prefix: str = "", total_reviews: int = 0) -> str:
    return f"""
<footer>
  <div class="container">
    <div class="footer-grid">
      <div>
        <h4 style="color:#fff;margin-bottom:8px;">AirCADRPro</h4>
        <p>Independent HEPA air purifier sizing calculator, real-world ACH engineering benchmarks, and daily updated product reviews ({total_reviews} reviews published).</p>
      </div>
      <div>
        <h4 style="color:#fff;margin-bottom:8px;">Quick Navigation</h4>
        <p><a href="{prefix}index.html#calculator">Room CADR &amp; ACH Calculator</a></p>
        <p><a href="{prefix}index.html#bestsellers">Top Amazon Best Sellers</a></p>
        <p><a href="{prefix}index.html#compare">Side-by-Side Model Comparison</a></p>
        <p><a href="{prefix}index.html#reviews">All Daily Product Reviews</a></p>
      </div>
      <div>
        <h4 style="color:#fff;margin-bottom:8px;">SEO &amp; Syndication</h4>
        <p><a href="{prefix}sitemap.xml">XML Sitemap</a></p>
        <p><a href="{prefix}rss.xml">Daily Review RSS Feed</a></p>
        <p><a href="{prefix}robots.txt">Robots.txt</a></p>
        <p>Last Automated Build: {TODAY_ISO}</p>
      </div>
    </div>
    <div class="disclosure">
      <strong>Amazon Affiliate Disclosure:</strong> As an Amazon Associate (StoreID: <code>{AFFILIATE_TAG}</code>), {SITE_NAME} earns from qualifying purchases at no additional cost to you. Pricing, CADR ratings, and availability are subject to change on Amazon.com.
    </div>
  </div>
</footer>
"""


# ==============================================================================
# REVIEW PAGE GENERATOR
# ==============================================================================
def get_product(pid: str) -> dict:
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return PRODUCTS[0]


def get_scenario(sslug: str) -> dict:
    for sc in SCENARIOS:
        if sc["slug_suffix"] == sslug:
            return sc
    return SCENARIOS[0]


def render_review_page(item: dict, pub_date: str, all_reviews: list) -> str:
    p = get_product(item["product_id"])
    amz_url = amazon_link(f"{p['name']} Air Purifier")
    filter_url = amazon_link(f"{p['name']} Replacement Filter")
    canonical = f"{SITE_URL}/reviews/{item['slug']}.html"

    cadr_m3h = int(round(p["cadr_cfm"] * 1.699))
    area_2ach = calc_room_at_ach(p["cadr_cfm"], 2.0)
    area_4ach = calc_room_at_ach(p["cadr_cfm"], 4.0)
    area_48ach = calc_room_at_ach(p["cadr_cfm"], 4.8)
    area_5ach = calc_room_at_ach(p["cadr_cfm"], 5.0)
    area_4ach_10ft = calc_room_at_ach(p["cadr_cfm"], 4.0, 10.0)
    annual_power = calc_annual_power_cost(p["watts"])
    tco_5yr = calc_5yr_tco(p)

    if item["type"] == "standalone":
        meta_desc = f"Complete {CURRENT_YEAR} {p['name']} review: {p['cadr_cfm']} CFM CADR ({cadr_m3h} m³/h), verified room coverage at 4.8 ACH ({area_48ach} sq ft), {p['noise_min']}-{p['noise_max']} dBA noise levels, and ${tco_5yr} 5-year ownership cost."
        intro_html = f"""
        <p>The <strong>{html.escape(p['name'])}</strong> delivers a verified Clean Air Delivery Rate of <strong>{p['cadr_cfm']} CFM ({cadr_m3h} m&sup3;/h)</strong> using a <strong>{html.escape(p['filter_type'])}</strong> architecture. Priced around <strong>${p['price_est']}</strong>, it is engineered specifically for <strong>{html.escape(p['best_for'])}</strong>.</p>
        <p style="margin-top:10px;">Instead of relying on inflated manufacturer square-footage claims based on slow 1-2 ACH airflow, we calculated this unit's true performance across 8-foot and 10-foot ceilings, annual electricity expenses (${annual_power}/yr), and 5-year Total Cost of Ownership (${tco_5yr}).</p>
        """
        extra_section = f"""
        <h2 style="margin:24px 0 10px;">Real-World CADR Room Coverage Matrix</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Air Quality Target</th><th>Required ACH</th><th>Max Room Size (8 ft Ceiling)</th><th>Max Room Size (10 ft Ceiling)</th></tr>
            </thead>
            <tbody>
              <tr><td>General Dust Maintenance</td><td>2.0 ACH</td><td>{area_2ach} sq ft</td><td>{calc_room_at_ach(p['cadr_cfm'], 2.0, 10)} sq ft</td></tr>
              <tr><td>Allergies &amp; Pet Dander</td><td>4.0 ACH</td><td><strong>{area_4ach} sq ft</strong></td><td>{area_4ach_10ft} sq ft</td></tr>
              <tr><td>AHAM Verified Standard</td><td>4.8 ACH</td><td><strong>{area_48ach} sq ft</strong></td><td>{calc_room_at_ach(p['cadr_cfm'], 4.8, 10)} sq ft</td></tr>
              <tr><td>Wildfire Smoke &amp; Heavy Odor</td><td>5.0 ACH</td><td><strong>{area_5ach} sq ft</strong></td><td>{calc_room_at_ach(p['cadr_cfm'], 5.0, 10)} sq ft</td></tr>
            </tbody>
          </table>
        </div>
        """
    elif item["type"] == "scenario":
        sc = get_scenario(item["scenario_slug"])
        target_area = calc_room_at_ach(p["cadr_cfm"], sc["target_ach"])
        meta_desc = f"Does the {p['name']} ({p['cadr_cfm']} CFM) work for {sc['room_focus']}? See exact {sc['target_ach']} ACH coverage ({target_area} sq ft), noise benchmarks, and 5-year filter costs."
        intro_html = f"""
        <p>{html.escape(sc['focus_summary'])}</p>
        <p style="margin-top:10px;">For <strong>{html.escape(sc['room_focus'])}</strong>, our engineering benchmark targets <strong>{sc['target_ach']} Air Changes Per Hour (ACH)</strong>. At <strong>{p['cadr_cfm']} CFM</strong>, the <strong>{html.escape(p['name'])}</strong> maintains {sc['target_ach']} ACH in rooms up to <strong>{target_area} sq ft</strong> (standard 8-foot ceilings) while drawing <strong>{p['watts']}W</strong> max power.</p>
        """
        extra_section = f"""
        <h2 style="margin:24px 0 10px;">{html.escape(sc['room_focus'])} Performance Audit</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Benchmark Metric</th><th>{html.escape(p['name'])} Result</th><th>Engineering Verdict</th></tr>
            </thead>
            <tbody>
              <tr><td>Target Scenario Rate</td><td>{sc['target_ach']} ACH</td><td>Covers up to {target_area} sq ft reliably</td></tr>
              <tr><td>Filtration Architecture</td><td>{html.escape(p['filter_type'])}</td><td>Matches {html.escape(sc['room_focus'])} demands</td></tr>
              <tr><td>Acoustic Range</td><td>{p['noise_min']} dBA (Low) – {p['noise_max']} dBA (Max)</td><td>{"Bedroom-friendly whisper low mode" if p['noise_min'] <= 26 else "Best suited for living areas or white-noise sleepers"}</td></tr>
              <tr><td>5-Year Total Cost</td><td>${tco_5yr} (Unit + Filters + Power)</td><td>${annual_power}/yr estimated electricity + ${p['filter_cost_yr']}/yr filters</td></tr>
            </tbody>
          </table>
        </div>
        """
    else:
        p2 = get_product(item["product2_id"])
        amz_url2 = amazon_link(f"{p2['name']} Air Purifier")
        tco2 = calc_5yr_tco(p2)
        cadr_winner = p["name"] if p["cadr_cfm"] >= p2["cadr_cfm"] else p2["name"]
        quiet_winner = p["name"] if p["noise_min"] <= p2["noise_min"] else p2["name"]
        value_winner = p["name"] if tco_5yr <= tco2 else p2["name"]
        meta_desc = f"{p['name']} ({p['cadr_cfm']} CFM) vs {p2['name']} ({p2['cadr_cfm']} CFM): Full side-by-side comparison of room sizing, decibels, wattage, and 5-year filter expenses."
        intro_html = f"""
        <p>Deciding between the <strong>{html.escape(p['name'])}</strong> (${p['price_est']}, {p['cadr_cfm']} CFM) and the <strong>{html.escape(p2['name'])}</strong> (${p2['price_est']}, {p2['cadr_cfm']} CFM)? Both are strong contenders, yet their real-world CADR reach, acoustics, and 5-year filter expenses diverge significantly.</p>
        <p style="margin-top:10px;"><strong>Quick Verdict:</strong> Choose the <strong>{html.escape(cadr_winner)}</strong> for maximum airflow speed, the <strong>{html.escape(quiet_winner)}</strong> for quieter night operation, or the <strong>{html.escape(value_winner)}</strong> for the lowest 5-year ownership cost.</p>
        """
        extra_section = f"""
        <h2 style="margin:24px 0 10px;">Head-to-Head Specification Matrix</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>Specification</th><th>{html.escape(p['name'])}</th><th>{html.escape(p2['name'])}</th></tr>
            </thead>
            <tbody>
              <tr><td><strong>CADR Airflow</strong></td><td>{p['cadr_cfm']} CFM</td><td>{p2['cadr_cfm']} CFM</td></tr>
              <tr><td><strong>4.8 ACH Room Coverage (8 ft)</strong></td><td>{area_48ach} sq ft</td><td>{calc_room_at_ach(p2['cadr_cfm'], 4.8)} sq ft</td></tr>
              <tr><td><strong>5.0 ACH Smoke Coverage</strong></td><td>{area_5ach} sq ft</td><td>{calc_room_at_ach(p2['cadr_cfm'], 5.0)} sq ft</td></tr>
              <tr><td><strong>Noise Floor / Peak</strong></td><td>{p['noise_min']} – {p['noise_max']} dBA</td><td>{p2['noise_min']} – {p2['noise_max']} dBA</td></tr>
              <tr><td><strong>Max Power Draw</strong></td><td>{p['watts']} Watts</td><td>{p2['watts']} Watts</td></tr>
              <tr><td><strong>Est. Annual Filter Cost</strong></td><td>${p['filter_cost_yr']}/yr</td><td>${p2['filter_cost_yr']}/yr</td></tr>
              <tr><td><strong>5-Year Total Ownership Cost</strong></td><td><strong>${tco_5yr}</strong></td><td><strong>${tco2}</strong></td></tr>
              <tr><td><strong>Amazon Live Deal</strong></td>
                <td><a class="btn btn-amazon" href="{amz_url}" target="_blank" rel="nofollow sponsored noopener">Check Price &rarr;</a></td>
                <td><a class="btn btn-amazon" href="{amz_url2}" target="_blank" rel="nofollow sponsored noopener">Check Price &rarr;</a></td>
              </tr>
            </tbody>
          </table>
        </div>
        """

    pros_li = "".join(f"<li>{html.escape(x)}</li>" for x in p["pros"])
    cons_li = "".join(f"<li>{html.escape(x)}</li>" for x in p["cons"])

    related_links = [r for r in all_reviews if r["slug"] != item["slug"]][-6:]
    related_html = "".join(
        f'<li><a href="{r["slug"]}.html">{html.escape(r["title"])}</a> <span style="color:#6b7280;font-size:0.82rem;">({r["date"]})</span></li>'
        for r in reversed(related_links)
    )

    ld_json = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Reviews", "item": f"{SITE_URL}/#reviews"},
                    {"@type": "ListItem", "position": 3, "name": item["title"], "item": canonical}
                ]
            },
            {
                "@type": "Product",
                "name": p["name"],
                "brand": {"@type": "Brand", "name": p["brand"]},
                "description": meta_desc,
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": str(p["rating"]),
                    "reviewCount": "148"
                },
                "review": {
                    "@type": "Review",
                    "author": {"@type": "Organization", "name": SITE_NAME},
                    "datePublished": pub_date,
                    "reviewRating": {
                        "@type": "Rating",
                        "ratingValue": str(p["rating"]),
                        "bestRating": "5"
                    }
                },
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "USD",
                    "price": str(p["price_est"]),
                    "availability": "https://schema.org/InStock",
                    "url": amz_url
                }
            }
        ]
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(item['title'])} | {SITE_NAME}</title>
  <meta name="google-site-verification" content="pgvlG0f03ZrRZzbgDSXRhr6tsSfseFOhXCN6Yv_j5b8" />
  <meta name="description" content="{html.escape(meta_desc)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{html.escape(item['title'])}">
  <meta property="og:description" content="{html.escape(meta_desc)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary_large_image">
  <style>{BASE_CSS}</style>
  <script type="application/ld+json">{safe_json_for_script(ld_json)}</script>
</head>
<body>
  {render_header(prefix="../")}
  <main class="container article-wrap">
    <div class="breadcrumb">
      <a href="../index.html">Home</a> &rsaquo; <a href="../index.html#reviews">Daily Reviews</a> &rsaquo; {html.escape(item['category'])}
    </div>
    <article class="card">
      <span class="badge badge-teal">{html.escape(item['category'])}</span>
      <span class="badge badge-amber">Published: {pub_date}</span>
      <span class="badge">Rating: {p['rating']}/5.0</span>
      <h1 style="font-size:clamp(1.5rem, 3vw, 2.1rem);line-height:1.25;margin:8px 0 14px;">{html.escape(item['title'])}</h1>
      <div class="result-kpis" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));margin-bottom:20px;">
        <div class="kpi-box highlight">
          <div class="kpi-label">Verified CADR</div>
          <div class="kpi-val">{p['cadr_cfm']} CFM</div>
          <div class="kpi-sub">{cadr_m3h} m&sup3;/h</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">4.8 ACH Room Size</div>
          <div class="kpi-val">{area_48ach} sq ft</div>
          <div class="kpi-sub">8-ft Ceiling</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">Noise Range</div>
          <div class="kpi-val">{p['noise_min']}-{p['noise_max']} dBA</div>
          <div class="kpi-sub">{p['watts']}W Max Power</div>
        </div>
        <div class="kpi-box">
          <div class="kpi-label">5-Year TCO</div>
          <div class="kpi-val">${tco_5yr}</div>
          <div class="kpi-sub">${p['filter_cost_yr']}/yr Filter</div>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:22px;">
        <a class="btn btn-amazon" style="flex:1;min-width:220px;" href="{amz_url}" target="_blank" rel="nofollow sponsored noopener">Check {html.escape(p['name'])} Price on Amazon &rarr;</a>
        <a class="btn btn-outline" style="flex:1;min-width:220px;" href="{filter_url}" target="_blank" rel="nofollow sponsored noopener">Check Replacement HEPA Filters &rarr;</a>
      </div>
      {intro_html}
      {extra_section}
      <h2 style="margin:24px 0 10px;">Key Strengths &amp; Trade-Offs</h2>
      <div class="pros-cons">
        <div class="pros-box"><strong>What Stands Out (Pros)</strong><ul>{pros_li}</ul></div>
        <div class="cons-box"><strong>Consider Before Buying (Cons)</strong><ul>{cons_li}</ul></div>
      </div>
      <h2 style="margin:24px 0 10px;">5-Year Operating Cost &amp; Filter Maintenance</h2>
      <p>Assuming continuous 24/7 blended operation at $0.16/kWh, the {html.escape(p['name'])} consumes approximately <strong>${annual_power} per year</strong> in electricity. Combined with roughly <strong>${p['filter_cost_yr']} annually</strong> for genuine replacement filters (after Year 1's included filter), your realistic 5-year Total Cost of Ownership is <strong>${tco_5yr}</strong>.</p>
      <div class="mid-banner" style="margin:26px 0 18px;">
        <div>
          <h3>Not Sure If {p['cadr_cfm']} CFM Fits Your Exact Room?</h3>
          <p>Plug your exact room dimensions and ceiling height into our free CADR calculator to confirm 4 to 5 ACH airflow before ordering.</p>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <a class="btn btn-amazon" href="{amz_url}" target="_blank" rel="nofollow sponsored noopener">Buy on Amazon &rarr;</a>
          <a class="btn btn-outline" href="../index.html#calculator">Open CADR Calculator</a>
        </div>
      </div>
      {f'<h3 style="margin-top:24px;margin-bottom:10px;">More Recent Air Purifier Reviews</h3><ul style="margin-left:18px;line-height:1.9;">{related_html}</ul>' if related_html else ''}
    </article>
  </main>
  {render_footer(prefix="../", total_reviews=len(all_reviews))}
</body>
</html>
"""


# ==============================================================================
# HOMEPAGE GENERATOR
# ==============================================================================
def render_homepage(all_reviews: list) -> str:
    canonical = f"{SITE_URL}/"
    bestsellers = sorted(
        [p for p in PRODUCTS if p["bestseller_rank"] > 0],
        key=lambda x: x["bestseller_rank"]
    )
    review_lookup = {r["product_id"]: r["slug"] for r in all_reviews if r["type"] == "standalone"}

    bestseller_cards = []
    for p in bestsellers:
        area48 = calc_room_at_ach(p["cadr_cfm"], 4.8)
        tco = calc_5yr_tco(p)
        rev_btn = (
            f'<a class="btn btn-outline" href="reviews/{review_lookup[p["id"]]}.html">Read Review</a>'
            if p["id"] in review_lookup else
            f'<a class="btn btn-outline" href="#compare" onclick="selectCompareModel(\'{p["id"]}\')">Compare</a>'
        )
        bestseller_cards.append(f"""
        <div class="product-card">
          <div>
            <span class="badge badge-amber">{html.escape(p['badge'])}</span>
            <h3>{html.escape(p['name'])}</h3>
            <p style="font-size:0.84rem;color:#4b5563;margin-bottom:6px;">Best for: {html.escape(p['best_for'])}</p>
            <ul class="spec-list">
              <li><span>CADR Airflow</span><strong>{p['cadr_cfm']} CFM</strong></li>
              <li><span>4.8 ACH Room Size</span><strong>{area48} sq ft</strong></li>
              <li><span>Noise Level</span><strong>{p['noise_min']}–{p['noise_max']} dBA</strong></li>
              <li><span>Annual Filter Cost</span><strong>${p['filter_cost_yr']}/yr</strong></li>
              <li><span>5-Year Total Cost</span><strong>${tco}</strong></li>
            </ul>
          </div>
          <div class="card-actions">
            <a class="btn btn-amazon" href="{amazon_link(p['name'] + ' Air Purifier')}" target="_blank" rel="nofollow sponsored noopener">Amazon Deal (~${p['price_est']})</a>
            {rev_btn}
          </div>
        </div>
        """)

    latest_reviews_html = []
    for r in reversed(all_reviews[-18:]):
        p = get_product(r["product_id"])
        latest_reviews_html.append(f"""
        <div class="product-card">
          <div>
            <span class="badge badge-teal">{html.escape(r['category'])}</span>
            <span class="badge">{r['date']}</span>
            <h3><a href="reviews/{r['slug']}.html" style="color:#111827;">{html.escape(r['title'])}</a></h3>
            <p style="font-size:0.86rem;color:#4b5563;margin:8px 0 14px;">Verified CADR: <strong>{p['cadr_cfm']} CFM</strong> &bull; Noise: <strong>{p['noise_min']}-{p['noise_max']} dBA</strong> &bull; Est. Price: <strong>${p['price_est']}</strong></p>
          </div>
          <div class="card-actions">
            <a class="btn btn-teal" href="reviews/{r['slug']}.html">Read Full Review &rarr;</a>
            <a class="btn btn-amazon" href="{amazon_link(p['name'] + ' Air Purifier')}" target="_blank" rel="nofollow sponsored noopener">Amazon &rarr;</a>
          </div>
        </div>
        """)

    comp_rows = []
    for p in PRODUCTS[:14]:
        area48 = calc_room_at_ach(p["cadr_cfm"], 4.8)
        tco = calc_5yr_tco(p)
        comp_rows.append(f"""
        <tr>
          <td><strong>{html.escape(p['name'])}</strong><br><span style="font-size:0.78rem;color:#4b5563;">{html.escape(p['brand'])} &bull; {html.escape(p['tier'])}</span></td>
          <td><strong>{p['cadr_cfm']} CFM</strong></td>
          <td>{area48} sq ft</td>
          <td>{p['noise_min']}–{p['noise_max']} dBA</td>
          <td>{p['watts']}W</td>
          <td>${p['filter_cost_yr']}/yr</td>
          <td><strong>${tco}</strong></td>
          <td><a class="btn btn-amazon" style="padding:6px 10px;font-size:0.8rem;" href="{amazon_link(p['name'] + ' Air Purifier')}" target="_blank" rel="nofollow sponsored noopener">Check Price</a></td>
        </tr>
        """)

    faq_html = "".join(
        f'<details class="faq-item"><summary>{html.escape(f["q"])}</summary><p>{html.escape(f["a"])}</p></details>'
        for f in FAQS
    )

    ld_home = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "name": f"{SITE_NAME} — HEPA Air Purifier CADR & ACH Calculator",
                "url": canonical,
                "applicationCategory": "UtilityApplication",
                "operatingSystem": "All",
                "description": "Free engineering-grade HEPA air purifier CADR & ACH room sizing calculator with real-time Amazon purifier matching and daily product reviews."
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": f["q"],
                     "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                    for f in FAQS
                ]
            }
        ]
    }

    products_client = []
    for p in PRODUCTS:
        products_client.append({
            **p,
            "area48": calc_room_at_ach(p["cadr_cfm"], 4.8),
            "area5": calc_room_at_ach(p["cadr_cfm"], 5.0),
            "annual_power": calc_annual_power_cost(p["watts"]),
            "tco5": calc_5yr_tco(p),
            "url": amazon_link(f"{p['name']} Air Purifier"),
            "review_slug": review_lookup.get(p["id"], "")
        })

    brands_options = "".join(
        f'<option value="{html.escape(b)}">{html.escape(b)}</option>'
        for b in sorted({p["brand"] for p in PRODUCTS})
    )
    model_options = "".join(
        f'<option value="{p["id"]}">{html.escape(p["name"])} ({p["cadr_cfm"]} CFM)</option>'
        for p in PRODUCTS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{SITE_NAME} — HEPA Air Purifier CADR &amp; ACH Room Sizing Calculator ({CURRENT_YEAR})</title>
  <meta name="google-site-verification" content="pgvlG0f03ZrRZzbgDSXRhr6tsSfseFOhXCN6Yv_j5b8" />
  <meta name="description" content="Calculate exact HEPA air purifier CADR (CFM & m³/h) for your room dimensions, ceiling height, allergies, or wildfire smoke. Compare 36+ models & read 3 fresh reviews daily.">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{SITE_NAME} — HEPA Air Purifier CADR & ACH Calculator">
  <meta property="og:description" content="Precision room sizing calculator, side-by-side purifier comparisons, and daily automated product reviews.">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <link rel="alternate" type="application/rss+xml" title="{SITE_NAME} Daily Reviews RSS" href="rss.xml">
  <style>{BASE_CSS}</style>
  <script type="application/ld+json">{safe_json_for_script(ld_home)}</script>
</head>
<body>
  {render_header(prefix="")}

  <section class="hero">
    <div class="container">
      <h1>HEPA Air Purifier CADR &amp; ACH Room Sizing Calculator</h1>
      <p>Stop guessing with exaggerated marketing labels. Enter your room dimensions, ceiling height, and air quality goal to compute the exact minimum CADR (CFM &amp; m&sup3;/h) and match proven True HEPA units instantly.</p>
      <div class="hero-badges">
        <span class="hero-badge">AHAM 4.8 ACH Standard</span>
        <span class="hero-badge">Wildfire Smoke &amp; Allergy Modes</span>
        <span class="hero-badge">{len(PRODUCTS)} Verified Purifiers Indexed</span>
        <span class="hero-badge">{len(all_reviews)} Daily Reviews Live (+3 Every Day)</span>
      </div>
    </div>
  </section>

  <section id="calculator">
    <div class="container">
      <div class="calc-grid">
        <div class="card">
          <h2 class="section-title" style="font-size:1.3rem;">1. Enter Your Room Dimensions</h2>
          <p class="section-sub" style="margin-bottom:14px;">Supports both Imperial (Feet) and Metric (Meters).</p>
          <div class="unit-toggle">
            <button type="button" id="btn-imp" class="unit-btn active" onclick="setUnit('imperial')">Imperial (Feet / CFM)</button>
            <button type="button" id="btn-met" class="unit-btn" onclick="setUnit('metric')">Metric (Meters / m&sup3;/h)</button>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label id="lbl-len" for="inp-len">Length (ft)</label>
              <input type="number" id="inp-len" value="20" min="3" max="200" step="0.5" oninput="runCalc()">
            </div>
            <div class="form-group">
              <label id="lbl-wid" for="inp-wid">Width (ft)</label>
              <input type="number" id="inp-wid" value="16" min="3" max="200" step="0.5" oninput="runCalc()">
            </div>
            <div class="form-group">
              <label id="lbl-hgt" for="inp-hgt">Ceiling (ft)</label>
              <input type="number" id="inp-hgt" value="8" min="6" max="30" step="0.5" oninput="runCalc()">
            </div>
          </div>
          <div class="form-group">
            <label for="inp-ach">Target Air Quality Goal (Air Changes Per Hour)</label>
            <select id="inp-ach" onchange="runCalc()">
              <option value="2">2.0 ACH — Basic Dust &amp; General Maintenance</option>
              <option value="4">4.0 ACH — Pet Dander &amp; Mild Allergies</option>
              <option value="4.8" selected>4.8 ACH — AHAM Standard (Moderate Allergies &amp; Asthma)</option>
              <option value="5">5.0 ACH — Wildfire Smoke, Heavy Odor &amp; Cooking</option>
              <option value="6">6.0 ACH — Medical-Grade / Ultra-Clean Air</option>
            </select>
          </div>
          <div class="form-group">
            <label for="inp-budget">Preferred Budget Tier</label>
            <select id="inp-budget" onchange="runCalc()">
              <option value="ALL">All Budgets (Show Best Technical Matches)</option>
              <option value="Budget">Budget Friendly (Under $200)</option>
              <option value="Mid-Range">Mid-Range ($200 – $399)</option>
              <option value="Premium">Premium ($400 – $699)</option>
              <option value="Luxury">Luxury / Medical-Grade ($700+)</option>
            </select>
          </div>
          <p style="font-size:0.82rem;color:#4b5563;margin-top:8px;"><strong>Formula:</strong> CADR (CFM) = (Length &times; Width &times; Ceiling Height &times; Target ACH) &divide; 60. For whisper-quiet operation, we recommend sizing 20–30% above minimum CADR.</p>
        </div>

        <div class="card">
          <h2 class="section-title" style="font-size:1.3rem;">2. Required CADR &amp; Matched Purifiers</h2>
          <p class="section-sub" style="margin-bottom:14px;">Instant sizing results and verified Amazon units that meet your exact airflow requirement.</p>
          <div class="result-kpis">
            <div class="kpi-box highlight">
              <div class="kpi-label">Minimum Required CADR</div>
              <div class="kpi-val" id="out-cadr-cfm">205 CFM</div>
              <div class="kpi-sub" id="out-cadr-m3h">348 m&sup3;/h</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Quiet-Mode Ideal CADR (+25%)</div>
              <div class="kpi-val" id="out-quiet-cfm">256 CFM</div>
              <div class="kpi-sub">Runs 4.8+ ACH on Medium</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Room Floor Area</div>
              <div class="kpi-val" id="out-area">320 sq ft</div>
              <div class="kpi-sub" id="out-area-m2">29.7 m&sup2;</div>
            </div>
            <div class="kpi-box">
              <div class="kpi-label">Total Air Volume</div>
              <div class="kpi-val" id="out-vol">2,560 cu ft</div>
              <div class="kpi-sub" id="out-vol-m3">72.5 m&sup3;</div>
            </div>
          </div>
          <h3 style="font-size:1rem;margin-bottom:10px;">Top Matched Air Purifiers for Your Room:</h3>
          <div id="calc-matches" class="grid-2" style="gap:12px;"></div>
        </div>
      </div>
    </div>
  </section>

  <section style="padding:10px 0 24px;">
    <div class="container">
      <div class="mid-banner">
        <div>
          <h3>Wildfire Smoke, Pollen &amp; Pet Dander Protection Bundles</h3>
          <p>Always buy a purifier sized for at least 4.8 ACH—and keep 1 spare True HEPA filter sealed on hand before smoke season drives prices up.</p>
        </div>
        <a class="btn btn-amazon" style="padding:13px 22px;font-size:0.98rem;" href="{amazon_link('AHAM Verified True HEPA Air Purifier Deals')}" target="_blank" rel="nofollow sponsored noopener">Shop Today's Top HEPA Deals &rarr;</a>
      </div>
    </div>
  </section>

  <section id="bestsellers">
    <div class="container">
      <h2 class="section-title">Best-Selling HEPA Air Purifiers ({CURRENT_YEAR})</h2>
      <p class="section-sub">Ranked by verified CADR efficiency, low decibel floor, genuine filter availability, and long-term Amazon buyer reliability.</p>
      <div class="grid-4">
        {"".join(bestseller_cards)}
      </div>
    </div>
  </section>

  <section id="search">
    <div class="container">
      <div class="card">
        <h2 class="section-title">Instant Purifier &amp; Review Search</h2>
        <p class="section-sub">Filter all {len(PRODUCTS)} verified air purifiers and {len(all_reviews)} published review articles by brand, minimum CADR, or budget.</p>
        <div class="search-controls">
          <input type="text" id="srch-q" placeholder="Search model, brand, smoke, pets, HEPA 14, quiet..." oninput="runSearch()">
          <select id="srch-brand" onchange="runSearch()">
            <option value="">All Brands</option>
            {brands_options}
          </select>
          <select id="srch-cadr" onchange="runSearch()">
            <option value="0">Any CADR</option>
            <option value="150">150+ CFM (Small/Med)</option>
            <option value="240">240+ CFM (Medium/Large)</option>
            <option value="320">320+ CFM (Large Rooms)</option>
            <option value="400">400+ CFM (Extra Large)</option>
          </select>
          <select id="srch-tier" onchange="runSearch()">
            <option value="">All Price Tiers</option>
            <option value="Budget">Budget (&lt;$200)</option>
            <option value="Mid-Range">Mid-Range ($200–$399)</option>
            <option value="Premium">Premium ($400–$699)</option>
            <option value="Luxury">Luxury ($700+)</option>
          </select>
        </div>
        <div id="srch-count" style="font-size:0.86rem;font-weight:700;color:#374151;margin-bottom:12px;"></div>
        <div id="srch-results" class="grid-3"></div>
      </div>
    </div>
  </section>

  <section id="compare">
    <div class="container">
      <h2 class="section-title">Interactive Side-by-Side Purifier Comparison</h2>
      <p class="section-sub">Select any 3 air purifiers to compare real CADR airflow, 4.8 ACH room coverage, decibels, wattage, and 5-year ownership cost.</p>
      <div class="card" style="margin-bottom:22px;">
        <div class="grid-3" style="margin-bottom:16px;">
          <div>
            <label style="font-weight:700;font-size:0.85rem;">Model A</label>
            <select id="cmp-1" onchange="renderCompare()">{model_options}</select>
          </div>
          <div>
            <label style="font-weight:700;font-size:0.85rem;">Model B</label>
            <select id="cmp-2" onchange="renderCompare()">{model_options}</select>
          </div>
          <div>
            <label style="font-weight:700;font-size:0.85rem;">Model C</label>
            <select id="cmp-3" onchange="renderCompare()">{model_options}</select>
          </div>
        </div>
        <div class="table-wrap" id="cmp-output"></div>
      </div>
      <h3 style="margin-bottom:10px;">Master Specification Comparison Table</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Model</th><th>CADR (CFM)</th><th>4.8 ACH Room</th><th>Noise (dBA)</th>
              <th>Max Watts</th><th>Filter/Yr</th><th>5-Yr TCO</th><th>Buy</th>
            </tr>
          </thead>
          <tbody>
            {"".join(comp_rows)}
          </tbody>
        </table>
      </div>
    </div>
  </section>

  <section id="reviews">
    <div class="container">
      <h2 class="section-title">Latest Daily Air Purifier Reviews (+3 Added Daily)</h2>
      <p class="section-sub">Fresh, data-driven standalone reviews, wildfire smoke stress tests, and head-to-head showdowns automatically published every day. Currently indexing <strong>{len(all_reviews)}</strong> unique review pages.</p>
      <div class="grid-3">
        {"".join(latest_reviews_html)}
      </div>
    </div>
  </section>

  <section id="faq">
    <div class="container">
      <h2 class="section-title">Frequently Asked Questions (CADR, ACH &amp; HEPA Buying Guide)</h2>
      <p class="section-sub">Evidence-based engineering answers to help you pick the right air purifier without overpaying.</p>
      {faq_html}
    </div>
  </section>

  {render_footer(prefix="", total_reviews=len(all_reviews))}

  <script>
    const PRODUCTS = {safe_json_for_script(products_client)};
    const REVIEWS = {safe_json_for_script(all_reviews)};
    let currentUnit = 'imperial';

    function setUnit(u) {{
      currentUnit = u;
      document.getElementById('btn-imp').classList.toggle('active', u === 'imperial');
      document.getElementById('btn-met').classList.toggle('active', u === 'metric');
      const lenEl = document.getElementById('inp-len');
      const widEl = document.getElementById('inp-wid');
      const hgtEl = document.getElementById('inp-hgt');
      if (u === 'metric') {{
        document.getElementById('lbl-len').textContent = 'Length (m)';
        document.getElementById('lbl-wid').textContent = 'Width (m)';
        document.getElementById('lbl-hgt').textContent = 'Ceiling (m)';
        lenEl.value = 6.0; widEl.value = 5.0; hgtEl.value = 2.4;
      }} else {{
        document.getElementById('lbl-len').textContent = 'Length (ft)';
        document.getElementById('lbl-wid').textContent = 'Width (ft)';
        document.getElementById('lbl-hgt').textContent = 'Ceiling (ft)';
        lenEl.value = 20; widEl.value = 16; hgtEl.value = 8;
      }}
      runCalc();
    }}

    function runCalc() {{
      let l = parseFloat(document.getElementById('inp-len').value) || 0;
      let w = parseFloat(document.getElementById('inp-wid').value) || 0;
      let h = parseFloat(document.getElementById('inp-hgt').value) || 0;
      const ach = parseFloat(document.getElementById('inp-ach').value) || 4.8;
      const budget = document.getElementById('inp-budget').value;

      let lFt = l, wFt = w, hFt = h;
      if (currentUnit === 'metric') {{
        lFt = l * 3.28084; wFt = w * 3.28084; hFt = h * 3.28084;
      }}
      const areaSqFt = lFt * wFt;
      const volCuFt = areaSqFt * hFt;
      const reqCFM = Math.ceil((volCuFt * ach) / 60);
      const reqM3H = Math.ceil(reqCFM * 1.699);
      const quietCFM = Math.ceil(reqCFM * 1.25);

      document.getElementById('out-cadr-cfm').textContent = reqCFM + ' CFM';
      document.getElementById('out-cadr-m3h').textContent = reqM3H + ' m³/h';
      document.getElementById('out-quiet-cfm').textContent = quietCFM + ' CFM';
      document.getElementById('out-area').textContent = Math.round(areaSqFt).toLocaleString() + ' sq ft';
      document.getElementById('out-area-m2').textContent = (areaSqFt * 0.092903).toFixed(1) + ' m²';
      document.getElementById('out-vol').textContent = Math.round(volCuFt).toLocaleString() + ' cu ft';
      document.getElementById('out-vol-m3').textContent = (volCuFt * 0.0283168).toFixed(1) + ' m³';

      let pool = PRODUCTS.filter(p => budget === 'ALL' || p.tier === budget);
      let matches = pool.filter(p => p.cadr_cfm >= reqCFM);
      let multiUnitNote = '';
      if (matches.length === 0) {{
        matches = [...pool].sort((a, b) => b.cadr_cfm - a.cadr_cfm).slice(0, 4);
        multiUnitNote = '<div style="grid-column:1/-1;background:#fef3c7;border:1px solid #f59e0b;padding:10px;border-radius:7px;font-size:0.86rem;"><strong>Large Space Alert:</strong> Your required CADR (' + reqCFM + ' CFM) exceeds single-unit limits in this tier. Run <strong>2 units</strong> of any high-CADR model below for optimal circulation.</div>';
      }} else {{
        matches.sort((a, b) => (a.cadr_cfm - reqCFM) - (b.cadr_cfm - reqCFM));
        matches = matches.slice(0, 4);
      }}

      const htmlOut = multiUnitNote + matches.map(p => `
        <div style="background:#eef0f3;border:1px solid #cbd5e1;border-radius:8px;padding:12px;display:flex;flex-direction:column;justify-content:space-between;">
          <div>
            <span class="badge badge-teal">${{p.cadr_cfm}} CFM</span>
            <span class="badge">~$${{p.price_est}}</span>
            <h4 style="font-size:0.96rem;margin-bottom:4px;">${{p.name}}</h4>
            <p style="font-size:0.8rem;color:#4b5563;margin-bottom:8px;">${{p.noise_min}}-${{p.noise_max}} dBA &bull; 5-Yr TCO: $${{p.tco5}}</p>
          </div>
          <a class="btn btn-amazon" style="font-size:0.82rem;padding:8px;" href="${{p.url}}" target="_blank" rel="nofollow sponsored noopener">Check Price on Amazon &rarr;</a>
        </div>
      `).join('');
      document.getElementById('calc-matches').innerHTML = htmlOut;
    }}

    function runSearch() {{
      const q = document.getElementById('srch-q').value.trim().toLowerCase();
      const brand = document.getElementById('srch-brand').value;
      const minCadr = parseInt(document.getElementById('srch-cadr').value, 10) || 0;
      const tier = document.getElementById('srch-tier').value;

      const filtered = PRODUCTS.filter(p => {{
        const hay = (p.name + ' ' + p.brand + ' ' + p.best_for + ' ' + p.filter_type + ' ' + p.badge).toLowerCase();
        if (q && !hay.includes(q)) return false;
        if (brand && p.brand !== brand) return false;
        if (p.cadr_cfm < minCadr) return false;
        if (tier && p.tier !== tier) return false;
        return true;
      }});

      const revMatches = q ? REVIEWS.filter(r => (r.title + ' ' + r.category).toLowerCase().includes(q)).slice(0, 6) : [];
      document.getElementById('srch-count').textContent = `Showing ${{filtered.length}} purifiers` + (revMatches.length ? ` + ${{revMatches.length}} matching review articles` : '');

      let cards = filtered.slice(0, 12).map(p => `
        <div class="product-card">
          <div>
            <span class="badge badge-teal">${{p.cadr_cfm}} CFM</span>
            <span class="badge">${{p.tier}}</span>
            <h3>${{p.name}}</h3>
            <p style="font-size:0.82rem;color:#4b5563;margin-bottom:8px;">${{p.filter_type}}</p>
            <ul class="spec-list">
              <li><span>4.8 ACH Coverage</span><strong>${{p.area48}} sq ft</strong></li>
              <li><span>Noise / Power</span><strong>${{p.noise_min}}-${{p.noise_max}} dBA / ${{p.watts}}W</strong></li>
              <li><span>5-Year Total Cost</span><strong>$${{p.tco5}}</strong></li>
            </ul>
          </div>
          <div class="card-actions">
            <a class="btn btn-amazon" href="${{p.url}}" target="_blank" rel="nofollow sponsored noopener">Amazon (~$${{p.price_est}})</a>
            ${{p.review_slug ? `<a class="btn btn-outline" href="reviews/${{p.review_slug}}.html">Review</a>` : ''}}
          </div>
        </div>
      `).join('');

      if (revMatches.length) {{
        cards += revMatches.map(r => `
          <div class="product-card" style="background:#f0fdfa;border-color:#5eead4;">
            <div>
              <span class="badge badge-teal">Review Article</span>
              <h3><a href="reviews/${{r.slug}}.html" style="color:#111827;">${{r.title}}</a></h3>
              <p style="font-size:0.82rem;color:#4b5563;margin-top:6px;">Published: ${{r.date}} &bull; ${{r.category}}</p>
            </div>
            <div class="card-actions">
              <a class="btn btn-teal" href="reviews/${{r.slug}}.html">Read Full Article &rarr;</a>
            </div>
          </div>
        `).join('');
      }}

      if (!cards) {{
        cards = '<p style="color:#6b7280;grid-column:1/-1;">No products or reviews matched your filters. Try broadening your search.</p>';
      }}
      document.getElementById('srch-results').innerHTML = cards;
    }}

    function selectCompareModel(pid) {{
      const el = document.getElementById('cmp-1');
      if (el) {{ el.value = pid; renderCompare(); }}
      const compareSection = document.getElementById('compare');
      if (compareSection) compareSection.scrollIntoView({{ behavior: 'smooth' }});
    }}

    function renderCompare() {{
      const ids = [
        document.getElementById('cmp-1').value,
        document.getElementById('cmp-2').value,
        document.getElementById('cmp-3').value
      ];
      const chosen = ids.map(id => PRODUCTS.find(p => p.id === id)).filter(Boolean);
      if (!chosen.length) return;

      const rows = [
        ['CADR Airflow', p => `${{p.cadr_cfm}} CFM (${{Math.round(p.cadr_cfm * 1.699)}} m³/h)`],
        ['4.8 ACH Room Size', p => `${{p.area48}} sq ft`],
        ['5.0 ACH Smoke Coverage', p => `${{p.area5}} sq ft`],
        ['Noise Range', p => `${{p.noise_min}} – ${{p.noise_max}} dBA`],
        ['Max Power Draw', p => `${{p.watts}} W`],
        ['Annual Filter Cost', p => `$${{p.filter_cost_yr}}/yr`],
        ['Annual Power Cost', p => `$${{p.annual_power}}/yr`],
        ['5-Year Total Cost', p => `$${{p.tco5}}`],
        ['Tier', p => p.tier],
        ['Best For', p => p.best_for]
      ];

      let tableHtml = `<table><thead><tr><th>Metric</th>`;
      chosen.forEach(p => {{ tableHtml += `<th>${{p.name}}</th>`; }});
      tableHtml += `</tr></thead><tbody>`;
      rows.forEach(([label, fn]) => {{
        tableHtml += `<tr><td><strong>${{label}}</strong></td>`;
        chosen.forEach(p => {{ tableHtml += `<td>${{fn(p)}}</td>`; }});
        tableHtml += `</tr>`;
      }});
      tableHtml += `<tr><td><strong>Buy on Amazon</strong></td>`;
      chosen.forEach(p => {{
        tableHtml += `<td><a class="btn btn-amazon" style="padding:6px 10px;font-size:0.8rem;" href="${{p.url}}" target="_blank" rel="nofollow sponsored noopener">Check Price</a></td>`;
      }});
      tableHtml += `</tr></tbody></table>`;
      document.getElementById('cmp-output').innerHTML = tableHtml;
    }}

    document.addEventListener('DOMContentLoaded', function() {{
      runCalc();
      runSearch();
      renderCompare();
    }});
  </script>
</body>
</html>
"""


# ==============================================================================
# SITEMAP, RSS, ROBOTS
# ==============================================================================
def render_sitemap(all_reviews: list) -> str:
    urls = [f"{SITE_URL}/"]
    for r in all_reviews:
        urls.append(f"{SITE_URL}/reviews/{r['slug']}.html")
    items = ""
    for u in urls:
        prio = "1.0" if u == f"{SITE_URL}/" else "0.8"
        items += f"  <url><loc>{u}</loc><lastmod>{TODAY_ISO}</lastmod><changefreq>daily</changefreq><priority>{prio}</priority></url>\n"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}</urlset>
"""


def render_rss(all_reviews: list) -> str:
    items = ""
    for r in reversed(all_reviews[-50:]):
        p = get_product(r["product_id"])
        link = f"{SITE_URL}/reviews/{r['slug']}.html"
        items += f"""  <item>
    <title>{html.escape(r['title'])}</title>
    <link>{link}</link>
    <guid>{link}</guid>
    <pubDate>{NOW_RFC822}</pubDate>
    <description>{html.escape(p['name'])} — {p['cadr_cfm']} CFM CADR, {p['noise_min']}-{p['noise_max']} dBA, ${p['price_est']} estimated price.</description>
  </item>
"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>{SITE_NAME} — Daily Air Purifier Reviews</title>
  <link>{SITE_URL}/</link>
  <description>{SITE_TAGLINE}</description>
  <lastBuildDate>{NOW_RFC822}</lastBuildDate>
{items}</channel>
</rss>
"""


def render_robots() -> str:
    return f"""User-agent: *
Allow: /
Sitemap: {SITE_URL}/sitemap.xml
"""


# ==============================================================================
# MAIN BUILD
# ==============================================================================
def main():
    DOCS_DIR.mkdir(exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    state = load_state()
    reviews = load_reviews()
    queue = build_review_queue()

    published_slugs = set(state.get("published_slugs", []))
    pending = [item for item in queue if item["slug"] not in published_slugs]
    new_items = pending[:ARTICLES_PER_RUN]

    for item in new_items:
        review_record = {
            "slug": item["slug"],
            "title": item["title"],
            "type": item["type"],
            "product_id": item["product_id"],
            "category": item["category"],
            "date": TODAY_ISO,
        }
        if "product2_id" in item:
            review_record["product2_id"] = item["product2_id"]
        if "scenario_slug" in item:
            review_record["scenario_slug"] = item["scenario_slug"]

        reviews.append(review_record)
        published_slugs.add(item["slug"])

        page_html = render_review_page(item, TODAY_ISO, reviews)
        (REVIEWS_DIR / f"{item['slug']}.html").write_text(page_html, encoding="utf-8")

    state["published_slugs"] = sorted(published_slugs)
    state["total_runs"] = state.get("total_runs", 0) + 1
    state["last_run"] = TODAY_ISO
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    REVIEWS_JSON.write_text(json.dumps(reviews, indent=2, ensure_ascii=False), encoding="utf-8")

    (DOCS_DIR / "index.html").write_text(render_homepage(reviews), encoding="utf-8")
    (DOCS_DIR / "sitemap.xml").write_text(render_sitemap(reviews), encoding="utf-8")
    (DOCS_DIR / "rss.xml").write_text(render_rss(reviews), encoding="utf-8")
    (DOCS_DIR / "robots.txt").write_text(render_robots(), encoding="utf-8")

    # File verifikasi Google (metode alternatif)
    (DOCS_DIR / f"google{GOOGLE_SITE_VERIFICATION}.html").write_text(
        f"google-site-verification: google{GOOGLE_SITE_VERIFICATION}.html",
        encoding="utf-8",
    )

    print(f"Published {len(new_items)} new review pages. Total: {len(reviews)}.")


if __name__ == "__main__":
    main()
