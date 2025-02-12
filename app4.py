import streamlit as st
import pandas as pd
import itertools


# Title of the app
st.title("Researcher Profile Page")

# Collect basic information
name = "N Manzini"
field = "MSc Nanoscience"
institution = "University of Johannesburg"

# Display basic profile information
st.header("Researcher Overview")
st.write(f"**Name:** {name}")
st.write(f"**Field of Research:** {field}")
st.write(f"**Institution:** {institution}")

# Add a section for results
st.header("Results")
uploaded_files = st.file_uploader("Upload CSV files of Results", type="csv", accept_multiple_files=True)

# Initialize session state for stored results
if "stored_results" not in st.session_state:
    st.session_state.stored_results = {}
    st.session_state.plot_colors = itertools.cycle(["red", "blue", "green", "purple", "orange", "brown", "pink", "cyan"])  # Extended color cycle

# Process uploaded files
for uploaded_file in uploaded_files:
    if uploaded_file.name not in st.session_state.stored_results:
        results = pd.read_csv(uploaded_file, skiprows=1)  # Skip first row to use actual headers
        st.session_state.stored_results[uploaded_file.name] = (results, next(st.session_state.plot_colors))

if st.session_state.stored_results:
    all_results = pd.concat([r[0] for r in st.session_state.stored_results.values()], ignore_index=True)
    st.dataframe(all_results)

    # Print column names for debugging
    st.write("Columns in uploaded file:", all_results.columns.tolist())

    # Normalize column names (remove spaces, lowercase, and special characters)
    def normalize_col(name):
        return re.sub(r'[^a-zA-Z0-9]', '', name).lower()

    normalized_cols = {col: normalize_col(col) for col in all_results.columns}
    all_results.rename(columns=normalized_cols, inplace=True)

    # Add filtering for year or keyword
    keyword = st.text_input("Filter by keyword", "")
    if keyword:
        filtered = all_results[
            all_results.apply(lambda row: keyword.lower() in row.astype(str).str.lower().values, axis=1)
        ]
        st.write(f"Filtered Results for '{keyword}':")
        st.dataframe(filtered)
    else:
        filtered = all_results
        st.write("Showing all results")

    # Download filtered results
    csv = filtered.to_csv(index=False)
    st.download_button("Download Filtered Results", data=csv, file_name="filtered_results.csv", mime="text/csv")

    # Add a section for visualizing result trends
    st.header("Result Trends")
    if "year" in all_results.columns:
        year_counts = all_results["year"].value_counts().sort_index()
        st.bar_chart(year_counts)
    else:
        st.write("The CSV does not have a 'Year' column to visualize trends.")

    # Add a section for FTIR plot
    st.header("FTIR Results Plot")
    combined_fig, combined_ax = plt.subplots()

    for file_name, (results, color) in st.session_state.stored_results.items():
        fig, ax = plt.subplots()

        # Detect columns for FTIR plot
        wavenumber_col = next((col for col in results.columns if "cm" in col.lower()), None)
        intensity_col = next((col for col in results.columns if "%t" in col.lower()), None)

        if wavenumber_col and intensity_col:
            # Individual Plot
            ax.plot(results[wavenumber_col], results[intensity_col], marker='o', linestyle='-', color=color, label=file_name)
            ax.set_xlabel("Wavenumber (cm⁻¹)")
            ax.set_ylabel("% Transmittance")
            ax.set_title(f"FTIR Spectrum: {file_name}")
            ax.invert_xaxis()
            ax.legend()
            st.pyplot(fig)

            # Add to combined plot
            combined_ax.plot(results[wavenumber_col], results[intensity_col], marker='o', linestyle='-', color=color, label=file_name)

            # Add download button for each plot
            img_buffer = BytesIO()
            fig.savefig(img_buffer, format="png")
            img_buffer.seek(0)
            st.download_button(label=f"Download FTIR Plot ({file_name})", data=img_buffer, file_name=f"FTIR_{file_name}.png", mime="image/png")
        else:
            st.write(f"Could not detect appropriate columns for FTIR plotting in {file_name}. Please check your CSV format.")

    # Show combined FTIR plot if more than one file uploaded
    if len(st.session_state.stored_results) > 1:
        combined_ax.set_xlabel("Wavenumber (cm⁻¹)")
        combined_ax.set_ylabel("% Transmittance")
        combined_ax.set_title("Combined FTIR Spectra")
        combined_ax.invert_xaxis()
        combined_ax.legend()
        st.pyplot(combined_fig)

        # Download combined plot
        img_buffer_combined = BytesIO()
        combined_fig.savefig(img_buffer_combined, format="png")
        img_buffer_combined.seek(0)
        st.download_button(label="Download Combined FTIR Plot", data=img_buffer_combined, file_name="FTIR_Combined.png", mime="image/png")

# Add a contact section
st.header("Contact Information")
email = "Ngcebolee@gmail.com"
st.write(f"You can reach {name} at {email}.")
