import streamlit as st
import pandas as pd
# use list
x = st.selectbox("Select a fruit from list", ["apple", "banana", "cherry"])
st.write(x)

# use dict
d = {"apple": "red", "banana": "yellow", "cherry": "red"}
y = st.selectbox("Select a fruit and see its color from dict", d)
st.write(y, d[y])

# use dataframe
df = pd.DataFrame({
    "fruit": ["apple", "banana", "cherry", "banana"],
    "color": ["red", "yellow", "red", "green"]
})
st.write(df)
z = st.selectbox("Select a fruit and see its color from dataframe", df)
st.write(z, df.loc[df["fruit"] == z])

