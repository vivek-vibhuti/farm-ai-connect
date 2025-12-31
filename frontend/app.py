import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(
    page_title="FarmConnect AI",
    page_icon="🌾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2D5016;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .healthy {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .danger {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# API endpoint
API_URL = "http://localhost:8000"

# Header
st.markdown('<h1 class="main-header">🌾 FarmConnect AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Hyper-Local Agricultural Advisory for Odisha Farmers</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f33e.png", width=80)
    st.title("About")
    st.markdown("""
    **FarmConnect AI** uses satellite imagery and AI to provide:
    - Real-time crop health monitoring
    - Pest & disease detection
    - Actionable recommendations
    - Voice messages in Odia
    - Market price updates
    
    **Built for:** Odisha farmers
    **Coverage:** All 30 districts
    """)
    
    st.divider()
    
    st.markdown("### Quick Stats")
    st.metric("Farmers Reached", "1,247")
    st.metric("Predictions Made", "3,891")
    st.metric("Avg Response Time", "< 5 sec")

# Main interface
tab1, tab2, tab3 = st.tabs(["🔍 New Analysis", "📊 History", "📈 Market Prices"])

with tab1:
    st.subheader("Get AI-Powered Crop Advisory")
    
    col1, col2 = st.columns(2)
    
    with col1:
        farmer_name = st.text_input("Farmer Name", placeholder="Enter your name")
        phone = st.text_input("Phone Number (Optional)", placeholder="+91 9876543210")
        region = st.selectbox(
            "Select Your Region",
            ["Cuttack", "Khurda", "Puri", "Ganjam", "Bargarh", "Sambalpur", "Balasore", "Bhadrak"]
        )
        crop_type = st.selectbox(
            "Crop Type",
            ["Paddy", "Wheat", "Pulses", "Vegetables", "Sugarcane"]
        )
    
    with col2:
        st.markdown("#### Field Location (Optional)")
        latitude = st.number_input("Latitude", value=20.4625, format="%.4f")
        longitude = st.number_input("Longitude", value=85.8830, format="%.4f")
        
        st.markdown("#### Upload Field Image (Optional)")
        uploaded_file = st.file_uploader(
            "Satellite or drone image of your field",
            type=["jpg", "jpeg", "png"]
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    st.divider()
    
    if st.button("🔬 Get AI Analysis", type="primary", use_container_width=True):
        if not farmer_name:
            st.error("Please enter your name")
        else:
            with st.spinner("Analyzing crop health... This may take 10-15 seconds"):
                # Prepare request
                files = {'image': uploaded_file} if uploaded_file else {}
                data = {
                    'farmer_name': farmer_name,
                    'phone': phone,
                    'region': region,
                    'crop_type': crop_type,
                    'latitude': latitude,
                    'longitude': longitude
                }
                
                try:
                    response = requests.post(f"{API_URL}/api/v1/predict", data=data, files=files)
                    result = response.json()
                    
                    if result['status'] == 'success':
                        st.success("✅ Analysis Complete!")
                        
                        # Display results
                        analysis = result['analysis']
                        recommendation = result['recommendation']
                        
                        # Health status box
                        health_score = analysis['crop_health']
                        if health_score >= 70:
                            box_class = "healthy"
                            status_icon = "✅"
                        elif health_score >= 50:
                            box_class = "warning"
                            status_icon = "⚠️"
                        else:
                            box_class = "danger"
                            status_icon = "🚨"
                        
                        st.markdown(f"""
                        <div class="result-box {box_class}">
                            <h3>{status_icon} Crop Health: {health_score}%</h3>
                            <p><strong>Status:</strong> {analysis['health_status']}</p>
                            <p><strong>Detection:</strong> {analysis['pest_detected']}</p>
                            <p><strong>Confidence:</strong> {analysis['confidence'] * 100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Satellite data (if available)
                        if result.get('satellite_data'):
                            sat = result['satellite_data']
                            col1, col2, col3 = st.columns(3)
                            col1.metric("NDVI", sat.get('ndvi', 'N/A'))
                            col2.metric("Soil Moisture", f"{sat.get('soil_moisture', 0)*100:.0f}%")
                            col3.metric("Cloud Cover", f"{sat.get('cloud_cover', 0)}%")
                        
                        # Recommendation
                        st.subheader("📋 Recommended Action")
                        st.info(f"**Action:** {recommendation['action']}")
                        st.warning(f"**Timing:** {recommendation['timing']}")
                        
                        col1, col2 = st.columns(2)
                        col1.metric("Estimated Cost", recommendation['cost'])
                        col2.metric("Current Market Price", recommendation['market_price'])
                        
                        # Full message
                        with st.expander("📄 Full Advisory Message"):
                            st.text(recommendation['full_message'])
                        
                        # Voice message
                        if result.get('voice_message_url'):
                            st.subheader("🔊 Voice Message (Odia)")
                            st.audio(API_URL + result['voice_message_url'])
                        
                        # Notification status
                        if result.get('notification_sent'):
                            st.success(f"✅ WhatsApp notification sent to {phone}")
                    
                    else:
                        st.error("Analysis failed. Please try again.")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Make sure the backend server is running on http://localhost:8000")

with tab2:
    st.subheader("📊 Farmer History")
    
    search_name = st.text_input("Search by Farmer Name")
    
    if st.button("Search History"):
        if search_name:
            try:
                response = requests.get(f"{API_URL}/api/v1/history/{search_name}")
                history = response.json()['history']
                
                if history:
                    df = pd.DataFrame(history)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No history found for this farmer")
            except:
                st.error("Could not fetch history")

with tab3:
    st.subheader("📈 Current Market Prices")
    
    price_region = st.selectbox("Select Region", ["Cuttack", "Khurda", "Puri"], key="price_region")
    
    if st.button("Get Prices"):
        try:
            response = requests.get(f"{API_URL}/api/v1/market-prices/{price_region}")
            prices = response.json()['prices']
            
            # Display as metrics
            cols = st.columns(len(prices))
            for idx, (crop, price) in enumerate(prices.items()):
                cols[idx].metric(crop.capitalize(), f"₹{price}/quintal")
        except:
            st.error("Could not fetch prices")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>FarmConnect AI • Made with ❤️ for Odisha Farmers</p>
    <p>For support: farmconnect@example.com | +91-1800-XXX-XXXX</p>
</div>
""", unsafe_allow_html=True)
