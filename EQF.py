import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
DB_URL = "mysql+pymysql://root:Vinolakshtrish*280622@localhost/earthquake_db"

# --- DATABASE CONNECTION ---
@st.cache_resource # Caches the connection so it doesn't reconnect on every click
def get_engine():
    return create_engine(DB_URL)

def run_query(sql):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)

# --- APP UI ---
st.set_page_config(page_title="Earthquake Analytics Dashboard", layout="wide")
st.title("🌍 Earthquake Data Analysis🌍")
st.markdown("Select a query from the sidebar to analyze global earthquake data.")

# --- SIDEBAR NAVIGATION ---
queries = {
    "1. Top 10 Strongest Earthquakes": 
        "SELECT place, mag, time FROM earthquake_pr ORDER BY mag DESC LIMIT 10",
    "2. Top 10 Deepest Earthquakes": 
        "SELECT place, depth_km, time FROM earthquake_pr ORDER BY depth_km DESC LIMIT 10",
    "3. Shallow & Powerful (Depth < 50km, Mag > 7.5)": 
        "SELECT place, mag, depth_km, time FROM earthquake_pr WHERE depth_km < 50 AND mag > 7.5",
    "5. Avg Magnitude per Type": 
        "SELECT magType, AVG(mag) as avg_mag FROM earthquake_pr GROUP BY magType",
      "6. Year with most earthquakes": 
        "SELECT year(time), COUNT(*) as count FROM earthquake_pr GROUP BY time ORDER BY count DESC LIMIT 1",
    "7. Month with most earthquakes": 
        "SELECT month(time), COUNT(*) as count FROM earthquake_pr GROUP BY time ORDER BY count DESC LIMIT 1",
    "8. Day of week with most earthquakes": 
       "SELECT week(time), COUNT(*) as count FROM earthquake_pr GROUP BY time ORDER BY count DESC LIMIT 1",        
    "9. Earthquakes per Hour of Day": 
        "SELECT HOUR(time) as hour, COUNT(*) as count FROM earthquake_pr GROUP BY hour ORDER BY hour",
    "10. Most active reporting network": 
        "SELECT net, COUNT(*) as count FROM earthquake_pr GROUP BY net ORDER BY count DESC LIMIT 1",
    "11. Top 5 places by significance (Impact)": 
        "SELECT place, sig FROM earthquake_pr ORDER BY sig DESC LIMIT 5",
    "12. Total impact (sig) per continent": 
        "SELECT place, SUM(sig) as total_sig FROM earthquake_pr GROUP BY place",
    "13. Avg significance by alert level": 
        "SELECT alert, AVG(sig) as avg_sig FROM earthquake_pr WHERE alert IS NOT NULL GROUP BY alert",
    "14. Reviewed vs Automatic Status": 
        "SELECT status, COUNT(*) as total FROM earthquake_pr GROUP BY status",
    "15. Count by event type": 
        "SELECT type, COUNT(*) FROM earthquake_pr GROUP BY type",
    "16. Top data types (types column)": 
        "SELECT types, COUNT(*) as count FROM earthquake_pr GROUP BY types ORDER BY count DESC LIMIT 5",
    "17. Avg RMS and Gap per continent": 
         "SELECT place, AVG(rms) as avg_rms, AVG(gap) as avg_gap FROM earthquake_pr GROUP BY place",
    "18. High station coverage (nst > 100)": 
        "SELECT place, nst FROM earthquake_pr WHERE nst > 100 ORDER BY nst DESC LIMIT 5",    
    "19. Tsunamis Triggered": 
        "SELECT time, SUM(tsunami) as total_tsunamis FROM earthquake_pr GROUP BY time",
    "20. Count by alert color": 
         "SELECT alert, COUNT(*) FROM earthquake_pr WHERE alert IS NOT NULL GROUP BY alert",  
    "21. Top 5 countries by avg mag (Past 10 Yrs)": 
        "SELECT place, AVG(mag) as avg_mag FROM earthquake_pr WHERE time >= 2015 GROUP BY place ORDER BY avg_mag DESC LIMIT 5",   
    "22. Countries with Shallow & Deep quakes in same month": 
        "SELECT place, time FROM earthquake_pr GROUP BY place, time HAVING MIN(depth_km) < 70 AND MAX(depth_km) > 300",    
    "23. Year-over-Year Growth Rate": 
        """SELECT time, COUNT(*) as total, 
        (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY time)) / LAG(COUNT(*)) OVER (ORDER BY year) * 100 as growth 
        FROM earthquake_pr GROUP BY time""",    
    "24. 3 Most active regions (Freq + Mag)": 
        "SELECT place, COUNT(*) as freq, AVG(mag) as avg_mag FROM earthquake_pr GROUP BY place ORDER BY freq DESC, avg_mag DESC LIMIT 3",    
    "25. Avg depth within 5 degrees of Equator": 
        "SELECT place, AVG(depth_km) FROM earthquake_pr WHERE latitude BETWEEN -5 AND 5 GROUP BY place",    
    "26. Highest ratio of shallow to deep quakes": 
        "SELECT place, SUM(depth_km < 70)/SUM(depth_km >= 70) as ratio FROM earthquake_pr GROUP BY place ORDER BY ratio DESC LIMIT 5",   
    "27. Mag difference (Tsunami vs No Tsunami)": 
        "SELECT tsunami, AVG(mag) FROM earthquake_pr GROUP BY tsunami",    
    "28. Events with lowest reliability (High Gap/RMS)": 
        "SELECT id, place, gap, rms FROM earthquake_pr WHERE gap > 180 OR rms > 1.0 LIMIT 5",       
    "30. Deep-focus Regions (> 300km)": 
        "SELECT place, COUNT(*) as deep_count FROM earthquake_pr WHERE depth_km > 300 GROUP BY place ORDER BY deep_count DESC LIMIT 5"
}

# You can add all 30 queries here following the same format
selected_query_name = st.sidebar.selectbox("Choose an Analysis Task", list(queries.keys()))

# --- DISPLAY RESULTS ---
if selected_query_name:
    st.subheader(f"Results: {selected_query_name}")
    
    with st.spinner("Fetching data..."):
        try:
            query_sql = queries[selected_query_name]
            results_df = run_query(query_sql)
            
            if not results_df.empty:
                # 1. Show Dataframe
                st.dataframe(results_df, use_container_width=True)
                
                # 2. Add a simple Chart for specific queries
                if "avg" in selected_query_name.lower() or "count" in selected_query_name.lower():
                    st.bar_chart(data=results_df.set_index(results_df.columns[0]))
            else:
                st.warning("No data found for this specific criteria.")
                
        except Exception as e:
            st.error(f"Error executing query: {e}")

# --- QUICK METRICS ---
st.sidebar.markdown("---")
if st.sidebar.button("Show Total Record Count"):
    count_df = run_query("SELECT COUNT(*) as total FROM earthquake_pr")
    st.sidebar.metric("Total Earthquakes", count_df['total'][0])