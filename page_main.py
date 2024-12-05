import streamlit as st
import os

section = ["Chat", "Chart", "Other"]

config = {i: [] for i in section}

for f in os.listdir("pages"):
    if not f.endswith(".py"):
        continue
    for k in section[:-1]:
        if f.startswith(k.lower()):
            config[k].append(st.Page(f"pages/{f}"))
            break
    else:
        config["Other"].append(st.Page(f"pages/{f}"))

pg = st.navigation(config)

pg.run()

