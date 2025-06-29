import streamlit as st
import requests
import os

API_ENDPOINT = os.environ.get("API_ENDPOINT", "http://localhost:8000/predict") # Default for local testing

st.title("Abalone Age Prediction")

st.markdown("""
Enter the physical characteristics of an abalone to predict its age (number of rings).
""")

with st.form("prediction_form"):
    sex = st.selectbox("Sex", options=["M", "F", "I"], help="M: Male, F: Female, I: Infant")
    length = st.number_input("Length (mm)", value=0.455, format="%.3f")
    diameter = st.number_input("Diameter (mm)", value=0.365, format="%.3f")
    height = st.number_input("Height (mm)", value=0.095, format="%.3f")
    whole_weight = st.number_input("Whole Weight (grams)", value=0.514, format="%.3f")
    shucked_weight = st.number_input("Shucked Weight (grams)", value=0.2245, format="%.3f")
    viscera_weight = st.number_input("Viscera Weight (grams)", value=0.101, format="%.3f")
    shell_weight = st.number_input("Shell Weight (grams)", value=0.150, format="%.3f")

    submitted = st.form_submit_button("Predict Age")

    if submitted:
        payload = {
            "sex": sex,
            "length": length,
            "diameter": diameter,
            "height": height,
            "whole_weight": whole_weight,
            "shucked_weight": shucked_weight,
            "viscera_weight": viscera_weight,
            "shell_weight": shell_weight,
        }

        try:
            with st.spinner("Getting prediction..."):
                response = requests.post(API_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"Predicted Age (Rings): **{result['predicted_age']}**")
            else:
                st.error(f"Error: Could not get prediction. Status Code: {response.status_code}")
                st.json(response.json())

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the API: {e}")

st.markdown("---")
st.markdown("This UI interacts with a FastAPI backend, which in turn invokes a deployed AWS SageMaker endpoint.") 