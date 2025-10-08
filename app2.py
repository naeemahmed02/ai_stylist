import streamlit as st
from dotenv import load_dotenv
import os
import json
import re
from llm_interface import LLMInterface
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize LLM
llm = LLMInterface(model_name="gemini-2.5-flash")

# Page config
st.set_page_config(page_title="AI Stylist", layout="wide")

# Sidebar: User preferences
st.sidebar.header("Your Preferences")

gender = st.sidebar.selectbox("Gender", ["Female", "Male", "Other"])
country = st.sidebar.selectbox("Country", ["Pakistan", "India", "Bangladesh", "Other"])
body_shape = st.sidebar.selectbox(
    "Body Shape",
    ["Hourglass", "Pear", "Apple", "Rectangle", "Inverted Triangle", "All"],
)

styles = st.sidebar.multiselect(
    "Personal Style (choose up to 3)",
    [
        "Minimal",
        "Elegant",
        "Modern",
        "Casual",
        "Feminine",
        "Street",
        "Office",
        "Vintage",
    ],
    default=["Minimal"],
)
event_type = st.sidebar.multiselect(
    "Event Type",
    ["Office", "Casual", "Date", "Party", "Travel", "Formal", "Interview"],
    default=["Casual"],
)
budget = st.sidebar.number_input("Budget (USD)", min_value=0, value=120)
exclude_colors = st.sidebar.text_input(
    "Exclude Colors (comma-separated)", value="light blue, sky blue"
)

# Main panel
st.title("AI Virtual Stylist 👗")
st.markdown(
    "Set your preferences in the sidebar, then click **Generate Recommendations** to get personalized outfit suggestions."
)

# Button
if st.button("Generate Recommendations"):
    # Prepare prompt for LLM
    prompt = f"""
You are an AI fashion stylist. Suggest **three different outfits** based on the following preferences:

Gender: {gender}
Country: {country}
Body Shape: {body_shape}
Personal Style: {', '.join(styles)}
Event Type: {', '.join(event_type)}
Budget: ${budget}
Exclude Colors: {exclude_colors}

Provide the output in **JSON format ONLY** like this:

[
    {{
        "outfit_name": "Outfit 1",
        "items": [
            {{"category": "Top", "name": "...", "brand": "...", "color": "...", "material": "...", "price": 0}},
            {{"category": "Bottom", "name": "...", "brand": "...", "color": "...", "material": "...", "price": 0}},
            ...
        ],
        "total_price": 0
    }},
    ...
]

Do not include any text outside the JSON array.
"""

    with st.spinner("AI is making combination..."):
        try:
            system_prompt = "You are a helpful AI fashion stylist. You have to suggest outfit according to the user inputs. Please suggest according to culture of the selected country."
            user_prompt = "{input}"
            response = llm.run(system_prompt, user_prompt, {"input": prompt})

            # -------------------------
            # Safely extract JSON
            # -------------------------
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if not match:
                st.error("Could not extract JSON from LLM response. Raw output:")
                st.write(response)
            else:
                outfits = json.loads(match.group(0))

                # Display outfits
                for outfit in outfits:
                    st.markdown(f"### {outfit.get('outfit_name', 'Outfit')}")
                    total_price = outfit.get("total_price", "N/A")
                    st.markdown(f"**Total Price:** ${total_price}")
                    items = outfit.get("items", [])
                    if items:
                        # Convert to DataFrame
                        df = pd.DataFrame(
                            [
                                {
                                    "Category": i.get("category", ""),
                                    "Item": i.get("name", ""),
                                    "Brand": i.get("brand", ""),
                                    "Color": i.get("color", ""),
                                    "Material": i.get("material", ""),
                                    "Price (USD)": i.get("price", 0),
                                }
                                for i in items
                            ]
                        )

                        # Styling: color rows based on category
                        def highlight_category(row):
                            colors = {
                                "Top": "#FFD1DC",  # light pink
                                "Bottom": "#D1F0FF",  # light blue
                                "Shoes": "#FFF0D1",  # light orange
                                "Accessory": "#E2FFD1",  # light green
                                "Outer": "#F0D1FF",  # light purple
                            }
                            return [
                                "background-color: {}".format(
                                    colors.get(row.Category, "#FFFFFF")
                                )
                            ] * len(row)

                        # Style the price column
                        styled_df = (
                            df.style.apply(highlight_category, axis=1)
                            .format({"Price (USD)": "${:.2f}"})
                            .set_properties(**{"text-align": "center"})
                        )

                        st.dataframe(styled_df, height=200)
                    st.markdown("---")

        except Exception as e:
            st.error(f"Error generating recommendations: {e}")
