import os
import random

import numpy as np
import openai
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ResponseTemplate(BaseModel):
    value: float


def generate_policy(field):
    # Generate a comma-separated list of key words to identify relevant government policies related to a start-up in the {topic} field.
    prompt = f"Generate a comma-separated list of 10 key words to identify relevant government policies related to a start-up in the {field} field."
    response = client.beta.chat.completions.parse(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful lawyer who understands the US/UK legal/governmental system very well. You want to help a potential investor assess the feasibility of a start-up through regulatory policies",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.parsed


def generate_feasibility(policy, field):
    # Generate a number between +1 (very supportive) and -1 (very unsupportive) to indicate whether the following policy '{policy}' supports the start-up field '{field}'"
    prompt = f"Generate a number between +1 (very supportive) and -1 (very unsupportive) to indicate whether the following policy '{policy}' supports the start-up field '{field}'"
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that can assess whether the policy supports the start-up field in order to assess the feasibility of that business at that time in history based on regulation",
            },
            {"role": "user", "content": prompt},
        ],
        response_format=ResponseTemplate,
        max_tokens=200,
        n=1,
        temperature=0.7,
    )
    return response.choices[0].message.parsed


def generate_favorability_data(topic1, topic2, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    topic1_favorability = np.random.randint(30, 71, size=len(date_range)) / 100
    topic2_favorability = np.random.randint(30, 71, size=len(date_range)) / 100

    df = pd.DataFrame(
        {"Date": date_range, topic1: topic1_favorability, topic2: topic2_favorability}
    )

    return df


st.set_page_config(page_title="Topic Favorability Comparison", layout="wide")

st.title("Topic Favorability Comparison Over Time")

col1, col2 = st.columns(2)

with col1:
    field = st.text_input("Enter the field", value="Fintech")

with col2:
    policy = st.text_input(
        "Enter the policy",
        value="This government shall provide more corporation tax for fintech start-ups",
    )

# start_date = st.date_input("Start date", value=pd.to_datetime("2023-01-01"))
# end_date = st.date_input("End date", value=pd.to_datetime("2023-12-31"))

if st.button("Generate Favorability Data and Features"):
    with st.spinner("Generating features and data..."):
        # Generate features
        topic1_features = generate_policy(policy)
        topic2_features = generate_feasibility(policy, field)
        st.write(topic1_features)
        st.write(topic2_features)


# if st.button("Generate Favorability Data and Features"):
#     if start_date < end_date:
#         with st.spinner("Generating features and data..."):
#             # Generate features
#             topic1_features = generate_features(topic1)
#             topic2_features = generate_features(topic2)

#             # Generate tag points
#             tag_points = generate_tag_points(topic1, topic2)

#             # Generate favorability data
#             df = generate_favorability_data(topic1, topic2, start_date, end_date)

#             # Display features
#             st.subheader("Key Features")
#             col1, col2 = st.columns(2)
#             with col1:
#                 st.write(f"{topic1} Features:")
#                 for feature in topic1_features:
#                     st.write(f"- {feature}")
#             with col2:
#                 st.write(f"{topic2} Features:")
#                 for feature in topic2_features:
#                     st.write(f"- {feature}")

#             # Create the line chart
#             fig = px.line(df, x='Date', y=[topic1, topic2], title=f"Favorability Comparison: {topic1} vs {topic2}")
#             fig.update_layout(yaxis_title="Favorability", xaxis_title="Date")

#             # Add annotation points
#             num_annotations = min(len(tag_points), 5)
#             annotation_dates = random.sample(df['Date'].tolist(), num_annotations)
#             annotation_dates.sort()

#             for i, date in enumerate(annotation_dates):
#                 y_position = df.loc[df['Date'] == date, topic1].values[0]
#                 fig.add_annotation(
#                     x=date,
#                     y=y_position,
#                     text=f"Point {i+1}",
#                     showarrow=True,
#                     arrowhead=2,
#                     arrowsize=1,
#                     arrowwidth=2,
#                     arrowcolor="#636363",
#                     ax=0,
#                     ay=-40
#                 )

#             st.plotly_chart(fig, use_container_width=True)

#             # Display tag points
#             st.subheader("Key Events/Quotes")
#             for i, (date, tag) in enumerate(zip(annotation_dates, tag_points)):
#                 st.write(f"**Point {i+1} ({date.strftime('%Y-%m-%d')}):** {tag}")

#             st.write("Sample Data:")
#             st.dataframe(df)
#     else:
#         st.error("Error: End date must be after the start date.")

st.sidebar.header("About")
st.sidebar.info(
    "This Streamlit app compares the favorability of two topics over time. "
    "Enter the topics you want to compare, select a date range, and click 'Generate Favorability Data and Features' "
    "to see a time series visualization of their relative favorability, along with key features and events."
)
