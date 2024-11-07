import streamlit as st
import streamlit.components.v1 as components

components.html(
    """
    <div style="background-color: #333; padding: 20px;">
        <h1 style="color: #fff; text-align: center;">Stylish Heading</h1>
        <p style="color: #ccc; font-size: 18px;">This is a custom-styled paragraph.</p>
    </div>
    """,
    height=200,
)
