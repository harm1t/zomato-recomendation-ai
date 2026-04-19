import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

from restaurant_rec.core.config import load_config
from restaurant_rec.phases.phase2.catalog_loader import load_catalog
from restaurant_rec.phases.phase2.filter import distinct_localities
from restaurant_rec.phases.phase2.preferences import UserPreferences
from restaurant_rec.phases.phase3.orchestration import recommend

st.set_page_config(page_title="Zomato API Streamlit Backend", page_icon="🍔", layout="centered")

st.title("Zomato Recommender - Streamlit App")
st.write("This is the Streamlit deployment for the Next.js frontend to link to or for testing the recommendation engine directly.")

@st.cache_resource
def get_system_state():
    cfg = load_config()
    catalog_df = load_catalog(cfg=cfg)
    return cfg, catalog_df

try:
    app_cfg, catalog_df = get_system_state()
except Exception as e:
    st.error(f"Error loading catalog: {e}")
    st.stop()

# --- UI Inputs ---
st.sidebar.header("User Preferences")

locations = distinct_localities(catalog_df)
locality = st.sidebar.selectbox("Locality", options=locations)

col1, col2 = st.sidebar.columns(2)
with col1:
    budget_min = st.number_input("Min Budget (₹)", min_value=0, value=500, step=100)
with col2:
    budget_max = st.number_input("Max Budget (₹)", min_value=0, value=2000, step=100)

cuisine = st.sidebar.text_input("Cuisine", placeholder="e.g. North Indian")
min_rating = st.sidebar.slider("Min Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)
extras = st.sidebar.text_input("Extras", placeholder="family friendly, rooftop")

if st.sidebar.button("Get Recommendations", type="primary"):
    if not locality:
        st.warning("Please select a valid locality.")
    else:
        prefs = UserPreferences(
            location=locality,
            budget_min_inr=budget_min,
            budget_max_inr=budget_max,
            cuisine=cuisine if cuisine.strip() else None,
            min_rating=min_rating,
            extras=extras if extras.strip() else None
        )
        
        with st.spinner("Calling Gemini for recommendations..."):
            result = recommend(
                catalog_df=catalog_df,
                prefs=prefs,
                cfg=app_cfg
            )
            
            st.subheader("Summary")
            st.info(result.summary)
            
            if result.items:
                st.subheader("Top Picks")
                for item in result.items:
                    with st.expander(f"{item['name']} - {item['cost_display']}"):
                        st.write(f"**Rating:** {item.get('rating', 'N/A')}⭐")
                        st.write(f"**Cuisines:** {', '.join(item['cuisines'])}")
                        st.write(f"**Why we recommend it:** {item['explanation']}")
            else:
                st.warning("No recommendations found for your preferences.")
