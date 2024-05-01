import streamlit as st
import yaml
from jinja2 import Template
from streamlit_monaco import st_monaco

st.title("Jinja Live Parser")

col_1, col_2 = st.columns(2)

with col_1:

    st.caption("Enter Jinja template")
    template_text = st_monaco('''Dear {{ name }},

    {% if not asleep %}
    Once upon a time ...
    {% endif %}'''
    , language="yaml", height=200)

    st.caption("Enter variables in YAML format")
    variable_value = st_monaco('name: Jane\n'
                                'asleep: false', 
    language="yaml")


with col_2:
    # Render button
    if st.button("Render", type="primary"):
        try:
            # Create Jinja template object
            template = Template(template_text)
            variable_dict = yaml.safe_load(variable_value)
            # Render the template with variable
            rendered_template = template.render(**variable_dict)

            # Display the rendered template
            st.code(rendered_template, language="html")
        except Exception as e:
            st.error(f"Error: {e}")
