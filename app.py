import streamlit as st
import pandas as pd
import time
import base64
from Futboll_verileri_cekme import scrap  # Assuming fetch_data is the function to call
import os

league_logos = {
    "lig-1": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/lig-1.jpg",
    "coupe-de-france": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/Coupe_de_france.png",
    "lig-2": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/lig-2.png",
    "Premier League": r"/Users/muhammedaydin/Desktop/vscode/streamlit/StreamLit_Football/logos/premier_league_logo.png",
    "La Liga": r"/Users/muhammedaydin/Desktop/vscode/streamlit/StreamLit_Football/logos/la_liga_logo.png",
    "Serie A": r"/Users/muhammedaydin/Desktop/vscode/streamlit/StreamLit_Football/logos/serie_a_logo.png",
    "bundesliga": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/bundesliga.jpg",
    "France": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/france.svg",
    "Germany": r"C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/germany.png"
}

background_images = {
    "France": 'C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/france-background.jpeg',
    "Germany": 'C:/Web Development/StreamLit_Project/streamlit/StreamLit_Football/logos/germany_background.jpeg',
    "default": '/Users/muhammedaydin/Desktop/streamlit/background.jpeg'
}

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def set_background_image(image_path):
    encoded_image = get_base64_image(image_path)
    st.markdown(
        f'''
          <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap'); 

    html, body, .stApp {{
        font-family: 'Roboto', sans-serif; 
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.3)), url("data:image/jpeg;base64,{encoded_image}");        
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-size:
        background-attachment: fixed;
        animation: fadeIn 3s ease-in-out, scaleUp 3s ease-in-out;
        transition: background-image 5s ease-in-out;
        
    }}

    h1, h2, h3, h4 {{
        font-weight: 700;
        color: #FFD700;
        text_align:center;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        animation: slideIn 0.5s ease-in-out;
    }}

    p, label {{
        font-weight: 300;
        color: #FFFFFF;
    }}

    .button {{
        background-color: #FFD700; 
        color: #000; 
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: background-color 0.3s;
    }}

    .button:hover {{
        background-color: #00000;
    }}
  
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
        }}
        to {{
            opacity: 1;
        }}
    }}

    @keyframes slideIn {{
        from {{
            transform: translateY(-20px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    </style>
        ''',
        unsafe_allow_html=True
    )


def set_sidebar_style():
    sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        background-color: rgba(30, 30, 30, 0.5); /* Şeffaf arka plan */
        color: white; 
    }

    [data-testid="stSidebar"] .css-1v3fvcr {
        color: white; 
    }

    [data-testid="stSidebar"] .css-1v3fvcr p {
        color: white; 
    }

    [data-testid="stSidebar"] .stTextInput label {
        color: white; 
    }

    [data-testid="stSidebar"] .stButton button {
        background-color: rgba(30, 30, 30, 0.5); 
        color: black; 
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #0000;
    }

    </style>
    """
    st.markdown(sidebar_style, unsafe_allow_html=True)

set_sidebar_style()


@st.cache_data
def load_data_from_csv(file_path):
    try:
        data = pd.read_csv(file_path, sep=',')
        data.columns = data.columns.str.strip()  
        return data
    except FileNotFoundError:
        return None

set_background_image(background_images["default"])
data_source = st.sidebar.selectbox("Select Data Source:", ["Select", "CSV", "Ethernet"])

if data_source == "CSV":
    try:
        data = load_data_from_csv("/Users/muhammedaydin/Desktop/streamlit/ahmedim.csv")
        if data is not None:
            countries = ["Select"] + list(data['Country'].unique())
            selected_country = st.sidebar.selectbox("Select Country:", countries)

            show_results_enabled = True

            if selected_country != "Select":
                leagues = ["Select"] + ["All Leagues"] + list(data[data['Country'] == selected_country]['Lig'].unique())
                selected_league = st.sidebar.selectbox("Select League:", leagues)

                if selected_league != "Select":
                    if selected_league != "All Leagues":
                        years = ["All Seasons"] + list(data[(data["Country"] == selected_country) & (data["Lig"] ==  selected_league)]['season_year'].unique())
                    else:
                        years = ["All Seasons"] + list(data[(data["Country"] == selected_country)]['season_year'].unique())
                        
                    selected_year = st.sidebar.multiselect("Select Season:", years, default=[])

                    

                    if "All Seasons" in selected_year and len(selected_year) > 1:
                        st.warning("You cannot select other seasons along with 'All Seasons'. Please correct your selection.")
                        show_results_enabled = False

                    if selected_year:
                        home_teams = ["All Home Teams"]
                        away_teams = ["All Away Teams"]

                        if selected_league == "All Leagues":
                            home_teams += list(data[data['Country'] == selected_country]['home_team'].unique())
                        else:
                            home_teams += list(data[data['Lig'] == selected_league]['home_team'].unique())

                        selected_home_team = st.sidebar.selectbox("Select Home Team:", home_teams)

                        if selected_home_team != "All Home Teams":
                            if selected_league == "All Leagues":
                                if "All Seasons" in selected_year:
                                    away_teams = ["All Away Teams"] + list(data[data['home_team'] == selected_home_team]['away_team'].unique())
                                else:
                                    away_teams = ["All Away Teams"] + list(data[(data['home_team'] == selected_home_team) & (data['season_year'].isin(selected_year))]['away_team'].unique())
                            else:
                                if "All Seasons" in selected_year:
                                    away_teams = ["All Away Teams"] + list(data[(data['Lig'] == selected_league) & (data['home_team'] == selected_home_team)]['away_team'].unique())
                                else:
                                    away_teams = ["All Away Teams"] + list(data[(data['Lig'] == selected_league) & (data['home_team'] == selected_home_team) & (data['season_year'].isin(selected_year))]['away_team'].unique())
                        else:
                            if selected_league == "All Leagues":
                                if "All Seasons" in selected_year:
                                    away_teams = ["All Away Teams"] + list(data[data["Country"] == selected_country]['away_team'].unique())
                                else:
                                    away_teams = ["All Away Teams"] + list(data[(data["Country"] == selected_country) & (data['season_year'].isin(selected_year))]['away_team'].unique())
                            else:
                                if "All Seasons" in selected_year:
                                    away_teams = ["All Away Teams"] + list(data[(data['Lig'] == selected_league) & (data["Country"] == selected_country)]['away_team'].unique())
                                else:
                                    away_teams = ["All Away Teams"] + list(data[(data['Lig'] == selected_league) & (data["Country"] == selected_country) & (data['season_year'].isin(selected_year))]['away_team'].unique())

                        selected_away_team = st.sidebar.selectbox("Select Away Team:", away_teams)     

                        if st.sidebar.button("Show Results", disabled=not show_results_enabled):
                            placeholder = st.empty()
                            with placeholder:
                                st.markdown("<h2>MATCHES ARE LOADING..</h2>", unsafe_allow_html=True)
                                time.sleep(2)

                            placeholder.empty()  
                            
                            filtered_data = data[
                                (data['Country'] == selected_country) &
                                ((data['Lig'] == selected_league) if selected_league != "All Leagues" else True) &
                                ((data['season_year'].isin(selected_year)) | ("All Seasons" in selected_year)) &
                                ((data['home_team'] == selected_home_team) if selected_home_team != "All Home Teams" else True) &
                                ((data['away_team'] == selected_away_team) if selected_away_team != "All Away Teams" else True)
                            ]

                            if not filtered_data.empty:
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"""
                                    <div style="border: 2px solid #FFD700; border-radius: 8px; padding: 10px; background-color: rgba(30, 30, 30, 0.5); color: #FFFFFF;">
                                        <h2 style="text-align: center; color: #FFD700;">Match Information</h2>
                                    """, unsafe_allow_html=True)

                                    for index, row in filtered_data.iterrows():  # Her bir satırı döngü ile işle
                                        # Create an expander for each match
                                        with st.expander(f"Match {index + 1}: {row['home_team']} vs {row['away_team']}", expanded=False):
                                            st.markdown(f"""
                                            <div style="border: 1px solid #FFD700; border-radius: 8px; padding: 10px; background-color: rgba(30, 30, 30, 0.7); color: #FFFFFF;">
                                                <h4 style="color: #FFD700;">Match {index + 1}</h4>
                                                <div style="display: flex; justify-content: space-between;">
                                                    <div style="flex: 1; padding-right: 10px;">
                                                        <h5 style="color: #FFD700;">🏠 Home Team: {row['home_team']}</h5>
                                                        <p><strong>⚽ Score:</strong> {row['home_score']} - {row['away_score']}</p>
                                                        <p><strong> 🥅 ⚽ Home Team Goals:</strong> {row['home_team_goals']}</p>
                                                        <p><strong>⏱️ First Half Score:</strong> {row['first_half']}</p>
                                                        <p><strong>⏱️ Second Half Score:</strong> {row['second_half']}</p>
                                                        <p><strong>🟡 Yellow Cards:</strong> {row['home_team_yellow_card']}</p>
                                                        <p><strong>🟥 Red Cards:</strong> {row['home_team_red_card']}</p>
                                                        <p><strong>🏆 Home Team Substitutions:</strong> {row['home_team_substitutions']}</p>
                                                        <p><strong>🏟️ Capacity:</strong> {row['capacity']}</p>
                                                        <p><strong>👥 Attendance:</strong> {row['attendance']}</p>
                                                        <p><strong> Home Team Goals Current Time:</strong> {row['home_team_goals_current_time']}</p>
                                                        <p><strong>🏅 Home Team Goals Current Score:</strong> {row['home_team_goals_current_score']}</p>
                                                        <p><strong>🏅 Home Team Goals Assist:</strong> {row['home_team_goals_assist']}</p>
                                                    </div>
                                                    <div style="flex: 1; padding-left: 10px;">
                                                        <h5 style="color: #FFD700;">🏃 Away Team: {row['away_team']}</h5>
                                                        <p><strong>⚽ Score:</strong> {row['home_score']} - {row['away_score']}</p>
                                                        <p><strong> 🥅 ⚽ Away Team Goals:</strong> {row['away_team_goals']}</p>
                                                        <p><strong>⏱️ First Half Score:</strong> {row['first_half']}</p>
                                                        <p><strong>⏱️ Second Half Score:</strong> {row['second_half']}</p>
                                                        <p><strong>🟡 Yellow Cards:</strong> {row['away_team_yellow_card']}</p>
                                                        <p><strong>🟥 Red Cards:</strong> {row['away_team_red_card']}</p>
                                                        <p><strong>🏆 Away Team Substitutions:</strong> {row['away_team_substitutions']}</p>
                                                        <p><strong>🏟 Away Team Goals Current Time:</strong> {row['away_team_goals_current_time']}</p>
                                                        <p><strong>🏅 Away Team Goals Current Score:</strong> {row['away_team_goals_current_score']}</p>
                                                        <p><strong>🏅 Away Team Goals Assist:</strong> {row['away_team_goals_assist']}</p>
                                                    </div>
                                                </div>
                                                <div style="display: flex; justify-content: space-between;">
                                                    <div style="flex: 1; padding-right: 10px;">
                                                        <p><strong>🌍 Country:</strong> {row['Country']}</p>
                                                        <p><strong>🏆 League:</strong> {row['Lig']}</p>
                                                        <p><strong>📅 Date:</strong> {row['Date_day']} at {row['Date_hour']}</p>
                                                        <p><strong>🧑‍⚖️ Referee:</strong> {row['referee']}</p>
                                                        <p><strong>🏟️ Venue:</strong> {row['venue']}</p>
                                                    </div>
                                                </div>
                                            </div>
                                            """, unsafe_allow_html=True)

                                st.markdown("</div>", unsafe_allow_html=True)  # Div'i kapat

                            if not filtered_data.empty:
                                csv = filtered_data.to_csv(index=False)
                                b64 = base64.b64encode(csv.encode()).decode()
                                href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv"><button style="background-color: #FFD700; color: black; border: none; border-radius: 5px; padding: 10px 20px; cursor: pointer; transition: background-color 0.3s;  margin-top: 20px;">Download CSV</button></a>'
                                st.markdown(href, unsafe_allow_html=True)
                            else:
                                st.warning("No data available to download.")

                            with col2:
                                if selected_league != "Select" and selected_league != "All Leagues":
                                    if selected_league.strip() in league_logos:
                                        st.image(league_logos[selected_league.strip()], width=200) 
                                elif selected_league == "All Leagues" and selected_country != 'Select':
                                    if selected_country.strip() in league_logos:
                                        st.image(league_logos[selected_country.strip()], width=200)

                    else:
                        st.info("No matches found for the selected criteria.")
        else:
            st.error("Could not load the CSV file. Please check if 'ahmedim.csv' exists.")
    except Exception as e:
        st.error(f"An error occurred while loading the CSV file: {str(e)}")

elif data_source == "Ethernet":
    try:
        data = load_data_from_csv("country_league.csv")
        if data is not None:
            set_background_image(background_images["default"])
            countries = ["Select"] + list(data['Country'].unique())
            selected_country = st.sidebar.selectbox("Select Country:", countries)

            if selected_country != "Select":
                leagues = ["Select"] + ["All Leagues"] + list(data[data['Country'] == selected_country]['League'].unique())
                selected_league = st.sidebar.selectbox("Select League:", leagues)

                if selected_league != "Select":
                    # Limit year selection to available years (2010-2023)
                    available_years = list(range(2023, 2009, -1))
                    selected_year = st.sidebar.selectbox("Select Year:", ["Select"] + [str(year) for year in available_years])

                    if st.sidebar.button("Fetch Data"):
                        placeholder = st.empty()
                        with placeholder:
                            st.markdown("<h2>Fetching data...</h2>", unsafe_allow_html=True)
                            
                        if selected_country != "Select" and selected_league != "Select":
                            try:
                                # Ligler ve yıllar listelerini hazırla
                                if selected_league == "All Leagues":
                                    leagues_list = list(data[data['Country'] == selected_country]['League'].unique())
                                else:
                                    leagues_list = [selected_league]
                                    
                                if selected_year == "Select":
                                    years_list = [str(year) for year in available_years]
                                else:
                                    years_list = [selected_year]
                                    
                                # Scraping işlemini başlat - ülke adını küçük harfe çevir
                                country_url = selected_country.lower()
                                scrap(country_url, leagues_list, years_list)
                                    
                                # CSV dosyasının oluşmasını bekle
                                time.sleep(5)  # Daha uzun bekleme süresi
                                    
                                try:
                                    # Her lig için ayrı CSV dosyası oku ve göster
                                    for league in leagues_list:
                                        league_formatted = league.lower().replace(' ', '_').replace('.','')
                                        csv_filename = f"football_data_{country_url}_{league_formatted}.csv"
                                        
                                        # Tam dosya yolu oluştur
                                        full_path = os.path.join(os.getcwd(), csv_filename)
                                        
                                        if os.path.exists(full_path):
                                            try:
                                                scraped_data = pd.read_csv(full_path)
                                                if not scraped_data.empty:
                                                    st.success(f"Data fetched successfully for {selected_country} - {league}!")
                                                    
                                                    # Veriyi göster
                                                    st.markdown(f"""
                                                        <div style="border: 2px solid #FFD700; border-radius: 8px; padding: 10px; background-color: rgba(30, 30, 30, 0.5); color: #FFFFFF;">
                                                        <h2 style="text-align: center; color: #FFD700;">Match Data for {league}</h2>
                                                        </div>
                                                    """, unsafe_allow_html=True)
                                                    
                                                    st.dataframe(scraped_data)
                                                    
                                                    # CSV indirme butonu
                                                    csv = scraped_data.to_csv(index=False)
                                                    b64 = base64.b64encode(csv.encode()).decode()
                                                    href = f'<a href="data:file/csv;base64,{b64}" download="{csv_filename}"><button style="background-color: #FFD700; color: black; border: none; border-radius: 5px; padding: 10px 20px; cursor: pointer; transition: background-color 0.3s; margin-top: 20px;">Download CSV</button></a>'
                                                    st.markdown(href, unsafe_allow_html=True)
                                                else:
                                                    st.warning(f"No data found for {league}")
                                            except Exception as e:
                                                st.error(f"Error reading CSV for {league}: {str(e)}")
                                        else:
                                            st.warning(f"CSV file not found for {league}: {csv_filename}")
                                except Exception as e:
                                    st.error(f"An error occurred while reading the data: {str(e)}")
                            except Exception as e:
                                st.error(f"An error occurred while scraping data: {str(e)}")
                                
                        else:
                            st.warning("Please select both a country and a league.")
        else:
            st.error("country_league.csv file not found. Please make sure the file exists.")
    except Exception as e:
        st.error(f"An error occurred while loading the data: {str(e)}")

else:
    st.info("Please select a data source from the sidebar.")
