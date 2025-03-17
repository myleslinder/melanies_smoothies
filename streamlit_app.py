# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd


helpful_links = [
    "https://docs.streamlit.io",
    "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit",
    "https://github.com/Snowflake-Labs/snowflake-demo-streamlit",
    "https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake",
]

# Write directly to the app
st.title("Customize your smoothie")
st.write("Choose the fruits you want in your custom smoothie:")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your smoothie will be: " + name_on_order)

cnx = st.connection("snowflake")

session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME"), col("SEARCH_ON")
)
pd_df = my_dataframe.to_pandas()
# st.dataframe(data=pd_df, use_container_width=True)


ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", my_dataframe, max_selections=5
)
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        # st.write("The search value for ", fruit_chosen, " is ", search_on, ".")

        st.subheader(fruit_chosen + " Nutrition Information")
        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )
        sf_df = st.dataframe(
            data=smoothiefroot_response.json(), use_container_width=True
        )
    # st.write(ingredients_string)

    my_insert_stmt = (
        """insert into smoothies.public.orders(ingredients, name_on_order)
            values ('"""
        + ingredients_string
        + "'"
        + ", "
        + "'"
        + name_on_order
        + """')"""
    )

    time_to_insert = st.button("Submit Order")

    # st.write(my_insert_stmt)

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(name_on_order + ", your Smoothie is ordered!", icon="✅")
