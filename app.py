import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Warehouse Management", layout="wide")

# Database connection details
MYSQL_HOST = "mysql-6051097-chitsanwin-fcc2.a.aivencloud.com:15227"
MYSQL_USER = "avnadmin"
MYSQL_PASSWORD = "AVNS_lHse-6jdl-kbb4dFsv0"
MYSQL_DATABASE = "defaultdb"

# SQLAlchemy setup
engine = create_engine(f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# ORM model for cold_store_in table
class ColdStoreIn(Base):
    __tablename__ = 'cold_store_in'
    ID = Column(Integer, primary_key=True)
    Sr_No = Column(Integer)
    Fi_No = Column(String, nullable=True)
    Date = Column(Date)
    Company = Column(String)
    Item = Column(String)
    Type = Column(String)
    Size = Column(String)
    Conversion = Column(String)
    Total_Mc = Column(Integer)
    Total_Kg = Column(Integer)
    Freezing_Type = Column(String)

# Sidebar
st.sidebar.title("Warehouse Management")
st.sidebar.markdown("Navigate through the options below:")

# Sidebar options
page = st.sidebar.selectbox("Choose a page", ["Dashboard", "Cold Storage", "Production", "Repacking", "Export"])

# Navbar
st.markdown(
    """
    <style>
    .navbar {
        display: flex;
        justify-content: space-around;
        background-color: #f8f9fa;
        padding: 10px;
    }
    .navbar a {
        text-decoration: none;
        color: black;
        font-weight: bold;
    }
    </style>
    <div class="navbar">
        <a href="#home">Home</a>
        <a href="#inventory">Inventory</a>
        <a href="#orders">Orders</a>
        <a href="#reports">Reports</a>
    </div>
    """,
    unsafe_allow_html=True
)

# Filter function
def filter_data(df, filters):
    for key, values in filters.items():
        if values:
            if key == 'Start_Date':
                df = df[df['Date'] >= values[0]]
            elif key == 'End_Date':
                df = df[df['Date'] <= values[0]]
            else:
                df = df[df[key].isin(values)]
    return df

# Function to convert DataFrame to Excel and return as bytes
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Page content
if page == "Dashboard":
    st.title("Dashboard")
    st.write("Welcome to the Warehouse Management System.")
elif page == "Cold Storage":
    st.title("Cold Storage")
    st.write("Manage your cold storage here.")
    
    # Fetch data from the cold_store_in table
    query = session.query(ColdStoreIn).statement
    df = pd.read_sql(query, engine)
    
    # Create filters
    with st.sidebar.expander("Filters", expanded=False):
        filters = {}
        
        # Filter by Sr_No
        sr_no_values = df['Sr_No'].dropna().unique()
        selected_sr_no = st.multiselect("Filter by Sr_No", sr_no_values)
        filters['Sr_No'] = selected_sr_no

        # Filter by Fi_No
        fi_no_values = df['Fi_No'].dropna().unique()
        selected_fi_no = st.multiselect("Filter by Fi_No", fi_no_values)
        filters['Fi_No'] = selected_fi_no

        # Filter by Start_Date
        start_date = st.date_input("Start Date", value=None)
        filters['Start_Date'] = [start_date] if start_date else []

        # Filter by End_Date
        end_date = st.date_input("End Date", value=None)
        filters['End_Date'] = [end_date] if end_date else []

        # Filter by Company
        company_values = df['Company'].dropna().unique()
        selected_company = st.multiselect("Filter by Company", company_values)
        filters['Company'] = selected_company

        # Filter by Item based on selected Company
        if selected_company:
            item_values = df[df['Company'].isin(selected_company)]['Item'].dropna().unique()
        else:
            item_values = df['Item'].dropna().unique()
        selected_item = st.multiselect("Filter by Item", item_values)
        filters['Item'] = selected_item
        
        # Filter by Type based on selected Item
        if selected_item:
            type_values = df[df['Item'].isin(selected_item)]['Type'].dropna().unique()
        else:
            type_values = df['Type'].dropna().unique()
        selected_type = st.multiselect("Filter by Type", type_values)
        filters['Type'] = selected_type
        
        # Filter by Size based on selected Type
        if selected_type:
            size_values = df[df['Type'].isin(selected_type)]['Size'].dropna().unique()
        else:
            size_values = df['Size'].dropna().unique()
        selected_size = st.multiselect("Filter by Size", size_values)
        filters['Size'] = selected_size
        
        # Filter by Conversion based on selected Size
        if selected_size:
            conversion_values = df[df['Size'].isin(selected_size)]['Conversion'].dropna().unique()
        else:
            conversion_values = df['Conversion'].dropna().unique()
        selected_conversion = st.multiselect("Filter by Conversion", conversion_values)
        filters['Conversion'] = selected_conversion
        
        # Filter by Freezing_Type
        freezing_type_values = df['Freezing_Type'].dropna().unique()
        selected_freezing_type = st.multiselect("Filter by Freezing_Type", freezing_type_values)
        filters['Freezing_Type'] = selected_freezing_type

    # Filter data
    filtered_df = filter_data(df, filters)
    
    # Ensure 'Total_Mc' and 'Total_Kg' are numeric
    filtered_df['Total_Mc'] = pd.to_numeric(filtered_df['Total_Mc'], errors='coerce')
    filtered_df['Total_Kg'] = pd.to_numeric(filtered_df['Total_Kg'], errors='coerce')

    # Calculate sums
    total_mc_sum = filtered_df['Total_Mc'].sum()
    total_kg_sum = filtered_df['Total_Kg'].sum()

    # Display the sums
    st.write(f"Total Mc: {total_mc_sum}")
    st.write(f"Total Kg: {total_kg_sum}")

    # Display the data in an interactive table with full width
    st.dataframe(filtered_df, use_container_width=True)

    # Data Analysis Section
    with st.expander("Data Analysis", expanded=False):
        st.header("Data Analysis")

        # Select columns for unique values
        unique_columns = st.multiselect("Select Columns for Unique Values", filtered_df.columns)

        # Analyze Data Button
        if st.button("Analyze Data"):
            if unique_columns:
                # Convert sum columns to numeric
                filtered_df['Total_Mc'] = pd.to_numeric(filtered_df['Total_Mc'], errors='coerce')
                filtered_df['Total_Kg'] = pd.to_numeric(filtered_df['Total_Kg'], errors='coerce')
                grouped_df = filtered_df.groupby(unique_columns)[['Total_Mc', 'Total_Kg']].sum().reset_index()
                st.write("Analysis Results:")
                st.dataframe(grouped_df)

                # Convert the analysis result to Excel
                excel_data = to_excel(grouped_df)
                st.download_button(label="Download Analysis as Excel", data=excel_data, file_name="analysis_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # Generate New Columns
        if st.button("Generate New Columns"):
            selected_column = st.selectbox("Select Column to Generate New Columns", filtered_df.columns)
            if selected_column:
                filtered_df['First_Part'] = filtered_df[selected_column].apply(lambda x: str(x).split(' ')[0])
                filtered_df['Second_Part'] = filtered_df[selected_column].apply(lambda x: str(x).split(' ')[1] if len(str(x).split(' ')) > 1 else '')
                st.write("New Columns Generated:")
                st.dataframe(filtered_df)

elif page == "Production":
    st.title("Production")
    st.write("Manage your production here.")
    # Add production management code here
elif page == "Repacking":
    st.title("Repacking")
    st.write("Manage your repacking here.")
    # Add repacking management code here
elif page == "Export":
    st.title("Export")
    st.write("Manage your export here.")
    # Add export management code here
