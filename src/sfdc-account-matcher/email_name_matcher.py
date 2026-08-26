import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
from datetime import datetime
import re
import time
import chardet

# Set page config
st.set_page_config(
    page_title="Email + Name Contact Matcher",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to detect file encoding
def detect_encoding(file):
    """Detect file encoding to handle special characters"""
    try:
        raw_data = file.read(10000)
        file.seek(0)
        result = chardet.detect(raw_data)
        confidence = result.get('confidence', 0)
        encoding = result.get('encoding', 'utf-8')
        if confidence < 0.7:
            encoding = 'utf-8'
        return encoding
    except:
        return 'utf-8'

# Enhanced CSV loading function
def load_csv_with_encoding(file):
    """Load CSV with automatic encoding detection"""
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    try:
        detected_encoding = detect_encoding(file)
        encodings_to_try.insert(0, detected_encoding)
    except:
        pass
    
    for encoding in encodings_to_try:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=encoding)
            if encoding != 'utf-8':
                st.info(f"📄 Loaded file using {encoding} encoding")
            return df
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    try:
        file.seek(0)
        df = pd.read_csv(file, encoding='utf-8', errors='replace')
        st.warning("⚠️ Loaded file with some character encoding issues (replaced problematic characters)")
        return df
    except Exception as e:
        st.error(f"❌ Could not load file: {str(e)}")
        return None

def clean_email(email):
    """Clean and standardize email addresses"""
    if pd.isna(email) or email == '':
        return ''
    return str(email).strip().lower()

def clean_name(name):
    """Clean and standardize names"""
    if pd.isna(name) or name == '':
        return ''
    # Remove extra spaces and standardize
    name = str(name).strip()
    name = re.sub(r'\s+', ' ', name)
    return name

def extract_first_last_name(full_name):
    """Extract first and last name from full name"""
    if not full_name:
        return '', ''
    
    parts = full_name.strip().split()
    if len(parts) == 0:
        return '', ''
    elif len(parts) == 1:
        return parts[0], ''
    else:
        return parts[0], parts[-1]

@st.cache_data
def load_sfdc_contacts(file):
    """Load and preprocess SFDC contacts data"""
    df = load_csv_with_encoding(file)
    if df is None:
        return pd.DataFrame()
    
    # Handle SFDC format columns
    if 'Email' in df.columns:
        df['Clean_Email'] = df['Email'].apply(clean_email)
    else:
        df['Clean_Email'] = ''
        st.warning("⚠️ No Email column found in SFDC file")
    
    # Handle various name formats
    if 'Contact Full Name' in df.columns:
        df['Full_Name'] = df['Contact Full Name'].apply(clean_name)
        df['First_Name'], df['Last_Name'] = zip(*df['Full_Name'].apply(extract_first_last_name))
        st.info("✅ Using 'Contact Full Name' for name extraction")
    elif 'First Name' in df.columns and 'Last Name' in df.columns:
        df['First_Name'] = df['First Name'].apply(clean_name)
        df['Last_Name'] = df['Last Name'].apply(clean_name)
        df['Full_Name'] = (df['First_Name'] + ' ' + df['Last_Name']).str.strip()
        st.info("✅ Using 'First Name' + 'Last Name' columns")
    else:
        df['First_Name'] = ''
        df['Last_Name'] = ''
        df['Full_Name'] = ''
        st.warning("⚠️ No usable name columns found")
    
    # Store Contact ID
    if 'CASE SAFE ID - CNT' in df.columns:
        df['Contact_ID'] = df['CASE SAFE ID - CNT']
    elif 'Id' in df.columns:
        df['Contact_ID'] = df['Id']
    else:
        df['Contact_ID'] = ''
        st.warning("⚠️ No Contact ID column found")
    
    return df

def email_name_matching(input_df, sfdc_df, email_col, name_col, name_type='full', threshold=85):
    """
    Email + Name matching with flexible name strategies
    
    name_type options:
    - 'full': Match full name to full name
    - 'first': Match to first name only
    - 'last': Match to last name only
    - 'flexible': Try all combinations
    """
    
    results = []
    
    # Build email lookup for instant matches
    st.write("📧 **Building email lookup index...**")
    email_lookup = {}
    for idx, row in sfdc_df.iterrows():
        email = row.get('Clean_Email', '')
        if email and '@' in email:
            if email not in email_lookup:
                email_lookup[email] = []
            email_lookup[email].append(idx)
    
    st.success(f"✅ Built email index: {len(email_lookup)} unique emails")
    
    # Process input data
    batch_size = 1000
    total_rows = len(input_df)
    matches_found = 0
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    match_counter = st.empty()
    
    for batch_start in range(0, total_rows, batch_size):
        batch_end = min(batch_start + batch_size, total_rows)
        batch = input_df.iloc[batch_start:batch_end]
        
        batch_matches = 0
        
        for idx, row in batch.iterrows():
            target_email = clean_email(row.get(email_col, ''))
            target_name = clean_name(row.get(name_col, ''))
            
            if not target_email and not target_name:
                continue
            
            best_match = None
            best_score = 0
            best_method = ''
            
            # Strategy 1: Email exact match with name validation
            if target_email and target_email in email_lookup:
                email_candidates = email_lookup[target_email]
                
                for candidate_idx in email_candidates:
                    candidate_row = sfdc_df.iloc[candidate_idx]
                    
                    if not target_name:
                        # Email only match
                        best_match = candidate_row
                        best_score = 100
                        best_method = 'Email Exact (No Name Validation)'
                        break
                    else:
                        # Email + name validation
                        name_scores = []
                        
                        if name_type in ['full', 'flexible']:
                            full_score = fuzz.token_set_ratio(target_name, candidate_row.get('Full_Name', ''))
                            name_scores.append(('Full Name', full_score))
                        
                        if name_type in ['first', 'flexible']:
                            first_score = fuzz.ratio(target_name, candidate_row.get('First_Name', ''))
                            name_scores.append(('First Name', first_score))
                        
                        if name_type in ['last', 'flexible']:
                            last_score = fuzz.ratio(target_name, candidate_row.get('Last_Name', ''))
                            name_scores.append(('Last Name', last_score))
                        
                        # Get best name match
                        if name_scores:
                            best_name_match = max(name_scores, key=lambda x: x[1])
                            name_method, name_score = best_name_match
                            
                            if name_score >= 70:  # Name validation threshold
                                combined_score = 95 + (name_score * 0.05)  # Email weight + name bonus
                                if combined_score > best_score:
                                    best_match = candidate_row
                                    best_score = combined_score
                                    best_method = f'Email + {name_method} ({name_score}%)'
                                    break
            
            # Strategy 2: Name-only fuzzy matching (if no email match)
            if best_score < 90 and target_name:
                candidate_names = []
                candidate_indices = []
                
                # Build candidate list based on name type
                for idx_sfdc, row_sfdc in sfdc_df.iterrows():
                    if name_type == 'full':
                        candidate_names.append(row_sfdc.get('Full_Name', ''))
                    elif name_type == 'first':
                        candidate_names.append(row_sfdc.get('First_Name', ''))
                    elif name_type == 'last':
                        candidate_names.append(row_sfdc.get('Last_Name', ''))
                    elif name_type == 'flexible':
                        # For flexible, we'll try full name first
                        candidate_names.append(row_sfdc.get('Full_Name', ''))
                    
                    candidate_indices.append(idx_sfdc)
                
                # Limit to reasonable sample size for performance
                if len(candidate_names) > 5000:
                    sample_indices = np.random.choice(len(candidate_names), 5000, replace=False)
                    candidate_names = [candidate_names[i] for i in sample_indices]
                    candidate_indices = [candidate_indices[i] for i in sample_indices]
                
                # Fuzzy matching
                matches = process.extract(
                    target_name,
                    candidate_names,
                    scorer=fuzz.token_set_ratio,
                    limit=3,
                    score_cutoff=threshold
                )
                
                for match_text, score, list_idx in matches:
                    candidate_idx = candidate_indices[list_idx]
                    candidate_row = sfdc_df.iloc[candidate_idx]
                    
                    if score > best_score:
                        best_match = candidate_row
                        best_score = score
                        best_method = f'Name Only - {name_type.title()} ({score}%)'
                        break
            
            # Add result if found
            if best_match is not None:
                result = {
                    'Input_Email': target_email,
                    'Input_Name': target_name,
                    'Match_SFDC_Email': best_match.get('Clean_Email', ''),
                    'Match_SFDC_Full_Name': best_match.get('Full_Name', ''),
                    'Match_SFDC_First_Name': best_match.get('First_Name', ''),
                    'Match_SFDC_Last_Name': best_match.get('Last_Name', ''),
                    'Match_Contact_ID': best_match.get('Contact_ID', ''),
                    'Match_Account_Name': best_match.get('Account Name', ''),
                    'Match_Confidence': f'{best_score:.1f}%',
                    'Match_Method': best_method
                }
                results.append(result)
                batch_matches += 1
                matches_found += 1
        
        # Update progress
        progress = batch_end / total_rows
        progress_bar.progress(progress)
        status_text.text(f"Processed {batch_end}/{total_rows} contacts...")
        match_counter.text(f"✅ Matches: {matches_found} (Batch: +{batch_matches})")
    
    progress_bar.empty()
    status_text.empty()
    match_counter.empty()
    
    return pd.DataFrame(results)

# Main Streamlit App
def main():
    st.title("📧 Email + Name Contact Matcher")
    st.markdown("**Specialized matching for email and name combinations**")
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📁 Upload Target Contacts")
        input_file = st.file_uploader("Upload CSV with contacts to match", type=['csv'], key="input")
        
    with col2:
        st.subheader("📁 Upload SFDC Contacts")
        sfdc_file = st.file_uploader("Upload SFDC contacts CSV", type=['csv'], key="sfdc")
    
    if input_file and sfdc_file:
        # Load data
        input_df = load_csv_with_encoding(input_file)
        sfdc_df = load_sfdc_contacts(sfdc_file)
        
        if input_df is not None and not sfdc_df.empty:
            st.success(f"✅ Loaded {len(input_df)} target contacts and {len(sfdc_df)} SFDC contacts")
            
            # Configuration section
            st.subheader("📋 Matching Configuration")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                email_col = st.selectbox("📧 Email Column", 
                                       ['-- No Email --'] + list(input_df.columns))
            
            with col2:
                name_col = st.selectbox("👤 Name Column", 
                                      list(input_df.columns))
            
            with col3:
                name_strategy = st.selectbox("🎯 Name Matching Strategy", [
                    'flexible',  # Try all combinations
                    'full',      # Full name to full name
                    'first',     # Name to first name only
                    'last'       # Name to last name only
                ])
            
            with col4:
                threshold = st.slider("📊 Confidence Threshold", 70, 100, 85)
            
            # Strategy explanation
            strategy_info = {
                'flexible': "Tries full name, first name, and last name matching - most accurate",
                'full': "Matches your name field against SFDC full names only",
                'first': "Matches your name field against SFDC first names only", 
                'last': "Matches your name field against SFDC last names only"
            }
            
            st.info(f"**Strategy: {name_strategy.title()}** - {strategy_info[name_strategy]}")
            
            # Show preview
            with st.expander("📊 Data Preview"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Input Data Sample:**")
                    st.dataframe(input_df.head(3))
                with col2:
                    st.write("**SFDC Data Sample:**")
                    st.dataframe(sfdc_df[['Clean_Email', 'Full_Name', 'First_Name', 'Last_Name']].head(3))
            
            # Matching button
            if st.button("🚀 Start Email + Name Matching"):
                start_time = time.time()
                
                # Convert column selections
                email_field = email_col if email_col != '-- No Email --' else None
                
                with st.spinner("Processing email + name matches..."):
                    results_df = email_name_matching(
                        input_df, sfdc_df, email_field, name_col, name_strategy, threshold
                    )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                if not results_df.empty:
                    st.success(f"⚡ Found {len(results_df)} matches in {processing_time:.1f} seconds!")
                    
                    # Results preview
                    st.subheader("📊 Results Preview")
                    st.dataframe(results_df.head(10))
                    
                    # Download button
                    csv = results_df.to_csv(index=False)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    st.download_button(
                        label="📥 Download Email + Name Matches CSV",
                        data=csv,
                        file_name=f"email_name_matches_{timestamp}.csv",
                        mime="text/csv"
                    )
                    
                    # Statistics
                    if 'Match_Method' in results_df.columns:
                        method_counts = results_df['Match_Method'].str.extract(r'^([^(]+)')[0].value_counts()
                        
                        st.subheader("📈 Match Statistics")
                        for method, count in method_counts.items():
                            st.metric(f"{method.strip()}", count)
                
                else:
                    st.warning("⚠️ No matches found. Try lowering the confidence threshold or changing the name strategy.")
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Email + Name Matching Strategies:
        
        **Flexible (Recommended):**
        - Tries full name, first name, and last name matching
        - Best for varied data formats
        - Example: "John Smith" matches "John Smith", "John", or "Smith"
        
        **Full Name:**
        - Matches your name field against complete SFDC names
        - Best when your data has full names
        - Example: "John Smith" matches "John Smith" only
        
        **First Name:**
        - Matches your name field against SFDC first names only
        - Best when your data has first names only
        - Example: "John" matches first name "John"
        
        **Last Name:**
        - Matches your name field against SFDC last names only
        - Best when your data has last names only
        - Example: "Smith" matches last name "Smith"
        
        ### Matching Priority:
        1. **Email Exact + Name Validation** (95-100% confidence)
        2. **Name-Only Fuzzy Matching** (threshold-based)
        
        ### Output:
        - Contact IDs ready for campaign uploads
        - Match methods and confidence scores
        - All name variations for verification
        """)

if __name__ == "__main__":
    main()