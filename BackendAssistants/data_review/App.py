import sys
sys.path.append("/Users/lucasvilsen/Desktop/GrammatikTAK/BackendAssistants/")
import json
import streamlit as st
import pandas as pd

from get_firestore_text import FirestoreClient

st.header("Data Review Site")
st.write("Select the appropriate page to see more info on each statistic.")
update = st.button("Update from datastore")
if update:
    firestoreClient = FirestoreClient()
    firestoreClient.save_and_delete("Feedback")
    firestoreClient.save_and_delete("Backend-alltext")
    st.experimental_rerun()
