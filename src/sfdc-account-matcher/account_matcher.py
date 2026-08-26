import streamlit as st
import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process
from sentence_transformers import SentenceTransformer
import torch
from datetime import datetime
import re
import time
import chardet

# Set page config
st.set_page_config(
    page_title="SFDC Account & Contact Matcher",
    page_icon="🔍",
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

# Cache the model loading
@st.cache_resource
def load_model():
    """Load sentence transformer model for semantic matching"""
    return SentenceTransformer('all-MiniLM-L6-v2')

# Pre-compute embeddings for SFDC data
@st.cache_data
def precompute_account_embeddings(_model, account_names):
    """Pre-compute embeddings for all SFDC accounts"""
    with st.spinner("🧠 Pre-computing AI embeddings for accounts..."):
        embeddings = _model.encode(account_names.tolist(), batch_size=32, show_progress_bar=False)
    return embeddings

@st.cache_data
def precompute_contact_indices(contacts_df):
    """Pre-compute search indices for fast contact lookup"""
    indices = {}
    
    # Email index
    if 'Email' in contacts_df.columns:
        email_mask = contacts_df['Email'].notna() & (contacts_df['Email'] != '')
        indices['email'] = dict(zip(contacts_df.loc[email_mask, 'Email'], 
                                   contacts_df.loc[email_mask].index))
    
    # Domain index - fix the pandas warning
    if 'EmailDomain' in contacts_df.columns:
        domain_mask = contacts_df['EmailDomain'].notna() & (contacts_df['EmailDomain'] != '')
        domain_groups = contacts_df.loc[domain_mask].groupby('EmailDomain', group_keys=False).apply(lambda x: x.index.tolist())
        indices['domain'] = domain_groups.to_dict()
    
    return indices

@st.cache_data
def load_sfdc_accounts(file):
    """Load and preprocess SFDC accounts data with encoding handling"""
    df = load_csv_with_encoding(file)
    if df is None:
        return pd.DataFrame()
    
    # Clean account names
    if 'Name' in df.columns:
        df['Clean_Name'] = df['Name'].apply(clean_company_name)
    else:
        name_cols = [col for col in df.columns if 'name' in col.lower()]
        if name_cols:
            df['Clean_Name'] = df[name_cols[0]].apply(clean_company_name)
            st.info(f"Using column '{name_cols[0]}' as account name")
        else:
            df['Clean_Name'] = df.iloc[:, 0].apply(clean_company_name)
            st.warning("⚠️ No 'Name' column found, using first column as account name")
    
    # Handle website/domain
    if 'Website' in df.columns:
        df['Domain'] = df['Website'].fillna('').str.replace('https://', '').str.replace('http://', '').str.replace('www.', '').str.split('/').str[0]
    else:
        df['Domain'] = ''
    
    return df

@st.cache_data
def load_sfdc_contacts(file):
    """Load and preprocess SFDC contacts data with encoding handling"""
    df = load_csv_with_encoding(file)
    if df is None:
        return pd.DataFrame()
    
    # Handle the exact SFDC export format you showed
    # Expected columns: CASE SAFE ID - CNT, Contact Full Name, First Name, Last Name, Email, Account Name, Title, etc.
    
    # Email handling
    if 'Email' in df.columns:
        df['Email'] = df['Email'].fillna('').str.lower().str.strip()
    else:
        df['Email'] = ''
        st.warning("⚠️ No Email column found")
    
    # Name handling - prioritize Contact Full Name, then build from First+Last
    if 'Contact Full Name' in df.columns:
        df['FullName'] = df['Contact Full Name'].fillna('').str.strip()
        st.info("✅ Using 'Contact Full Name' column for matching")
    elif 'First Name' in df.columns and 'Last Name' in df.columns:
        df['FullName'] = (df['First Name'].fillna('') + ' ' + df['Last Name'].fillna('')).str.strip()
        st.info("✅ Building full name from 'First Name' + 'Last Name'")
    else:
        # Fallback to other name columns
        name_cols = [col for col in df.columns if 'name' in col.lower()]
        if name_cols:
            df['FullName'] = df[name_cols[0]].fillna('').str.strip()
            st.info(f"Using column '{name_cols[0]}' as contact name")
        else:
            df['FullName'] = ''
            st.warning("⚠️ No name column found")
    
    # Extract email domain safely
    try:
        df['EmailDomain'] = df['Email'].str.split('@').str[1].fillna('')
    except:
        df['EmailDomain'] = ''
    
    # Account name handling
    if 'Account Name' in df.columns:
        df['Clean_Account_Name'] = df['Account Name'].fillna('').apply(clean_company_name)
        st.info("✅ Using 'Account Name' column for company matching")
    else:
        # Try other variations
        account_name_cols = [col for col in df.columns if any(term in col.lower() for term in ['account', 'company'])]
        if account_name_cols:
            df['Clean_Account_Name'] = df[account_name_cols[0]].fillna('').apply(clean_company_name)
            st.info(f"Using column '{account_name_cols[0]}' as account name")
        else:
            df['Clean_Account_Name'] = ''
            st.warning("⚠️ No account/company column found")
    
    # Store the Contact ID for results
    if 'CASE SAFE ID - CNT' in df.columns:
        df['Contact_ID'] = df['CASE SAFE ID - CNT']
        st.info("✅ Found 'CASE SAFE ID - CNT' for Contact IDs")
    elif 'Id' in df.columns:
        df['Contact_ID'] = df['Id']
        st.info("✅ Using 'Id' column for Contact IDs")
    else:
        df['Contact_ID'] = ''
        st.warning("⚠️ No Contact ID column found")
    
    return df

def clean_company_name(name):
    """Clean company name by removing common suffixes and standardizing"""
    if pd.isna(name) or name == '':
        return ''
    
    name = str(name).strip()
    
    # Common company suffixes to remove for matching
    suffixes = [
        r'\b(inc\.?|incorporated)\b', r'\b(corp\.?|corporation)\b', 
        r'\b(llc\.?|l\.l\.c\.?)\b', r'\b(ltd\.?|limited)\b',
        r'\b(co\.?|company)\b', r'\b(plc\.?)\b', r'\b(gmbh)\b',
        r'\b(sa)\b', r'\b(bv)\b', r'\b(ag)\b', r'\b(spa)\b',
        r'\b(srl)\b', r'\b(pvt\.?)\b', r'\b(pte\.?)\b'
    ]
    
    for suffix in suffixes:
        name = re.sub(suffix, '', name, flags=re.IGNORECASE)
    
    name = re.sub(r'[^\w\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def vectorized_semantic_match(target_names, reference_df, model, embeddings, threshold=85, input_indices=None):
    """Vectorized semantic matching - MUCH faster

    input_indices: optional list mapping each position in target_names back to its
    row in the caller's original input. Needed when this is called with a filtered
    subset (see Hybrid mode) so Input_Index stays meaningful after a concat.
    """
    if len(target_names) == 0:
        return pd.DataFrame()

    if input_indices is None:
        input_indices = list(range(len(target_names)))
    
    # Clean target names
    clean_targets = [clean_company_name(name) for name in target_names]
    
    # Filter out very short names (exact match only)
    valid_targets = [(i, name) for i, name in enumerate(clean_targets) if len(name.strip()) >= 3]
    
    if not valid_targets:
        return pd.DataFrame()
    
    # Get embeddings for valid targets
    valid_indices, valid_names = zip(*valid_targets)
    target_embeddings = model.encode(list(valid_names), batch_size=32, show_progress_bar=False)
    
    # Calculate similarity matrix
    similarities = torch.nn.functional.cosine_similarity(
        torch.tensor(target_embeddings).unsqueeze(1),
        torch.tensor(embeddings).unsqueeze(0),
        dim=2
    ) * 100
    
    results = []
    for i, target_idx in enumerate(valid_indices):
        # Get top 3 matches above threshold
        target_sims = similarities[i]
        top_indices = torch.where(target_sims >= threshold)[0]
        
        if len(top_indices) > 0:
            # Sort by similarity and take top 3
            sorted_indices = top_indices[torch.argsort(target_sims[top_indices], descending=True)][:3]
            
            for rank, ref_idx in enumerate(sorted_indices, 1):
                matched_row = reference_df.iloc[ref_idx]
                score = float(target_sims[ref_idx])
                
                result = {
                    'Input_Index': input_indices[target_idx],
                    'Input_Name': target_names[target_idx],
                    'Clean_Input_Name': clean_targets[target_idx],
                    f'Match_{rank}_SFDC_Name': matched_row['Name'] if 'Name' in matched_row else matched_row.iloc[0],
                    f'Match_{rank}_Account_ID': matched_row.get('Id', matched_row.get('CASE SAFE ID - ACCT', '')),
                    f'Match_{rank}_Confidence': f"{score:.1f}%",
                    f'Match_{rank}_Method': 'Semantic Match'
                }
                
                if 'Website' in matched_row:
                    result[f'Match_{rank}_Website'] = matched_row['Website']
                if 'BillingCity' in matched_row:
                    result[f'Match_{rank}_City'] = matched_row['BillingCity']
                if 'BillingState' in matched_row:
                    result[f'Match_{rank}_State'] = matched_row['BillingState']
                
                results.append(result)
                break  # Only first match per target
    
    return pd.DataFrame(results)

def vectorized_fuzzy_match(target_names, reference_names, reference_df, threshold=85, input_indices=None):
    """Vectorized fuzzy matching using RapidFuzz process.extract

    input_indices: optional list mapping each position in target_names back to its
    row in the caller's original input. Needed when this is called with a filtered
    subset (see Hybrid mode) so Input_Index stays meaningful after a concat.
    """
    if len(target_names) == 0:
        return pd.DataFrame()

    if input_indices is None:
        input_indices = list(range(len(target_names)))
    
    clean_targets = [clean_company_name(name) for name in target_names]
    reference_list = reference_names.tolist()
    
    results = []
    
    # Process in batches for memory efficiency
    batch_size = 100
    for batch_start in range(0, len(clean_targets), batch_size):
        batch_end = min(batch_start + batch_size, len(clean_targets))
        batch_targets = clean_targets[batch_start:batch_end]
        
        for i, target_name in enumerate(batch_targets):
            target_idx = batch_start + i
            
            if len(target_name.strip()) < 3:
                continue
            
            # Use RapidFuzz process.extract for fast matching
            matches = process.extract(
                target_name,
                reference_list,
                scorer=fuzz.token_set_ratio,
                limit=3,
                score_cutoff=threshold
            )
            
            for rank, (match_text, score, ref_idx) in enumerate(matches, 1):
                matched_row = reference_df.iloc[ref_idx]
                
                result = {
                    'Input_Index': input_indices[target_idx],
                    'Input_Name': target_names[target_idx],
                    'Clean_Input_Name': target_name,
                    f'Match_{rank}_SFDC_Name': matched_row['Name'] if 'Name' in matched_row else matched_row.iloc[0],
                    f'Match_{rank}_Account_ID': matched_row.get('Id', matched_row.get('CASE SAFE ID - ACCT', '')),
                    f'Match_{rank}_Confidence': f"{score:.1f}%",
                    f'Match_{rank}_Method': 'Fuzzy Match'
                }
                
                if 'Website' in matched_row:
                    result[f'Match_{rank}_Website'] = matched_row['Website']
                if 'BillingCity' in matched_row:
                    result[f'Match_{rank}_City'] = matched_row['BillingCity']
                if 'BillingState' in matched_row:
                    result[f'Match_{rank}_State'] = matched_row['BillingState']
                
                results.append(result)
                break  # Only first match per target
    
    return pd.DataFrame(results)

def lightning_fast_contact_matching(input_df, sfdc_contacts_df, email_col, name_col, company_col, threshold=85):
    """Lightning fast contact matching using exact lookups and smart sampling"""
    results = []
    
    st.write("⚡ **Lightning Fast Mode - Building lookup indices...**")
    
    # Build super-fast lookup dictionaries
    progress_bar = st.progress(0)
    
    # 1. Exact name lookup (instant)
    progress_bar.progress(0.2)
    name_lookup = {}
    email_lookup = {}
    
    for idx, row in sfdc_contacts_df.iterrows():
        full_name = str(row.get('Contact Full Name', '')).strip().lower()
        email = str(row.get('Email', '')).strip().lower()
        
        if full_name:
            name_lookup[full_name] = idx
        if email and '@' in email:
            email_lookup[email] = idx
    
    # 2. Build word-based indices for fast fuzzy matching
    progress_bar.progress(0.5)
    word_indices = {}
    
    for idx, row in sfdc_contacts_df.iterrows():
        full_name = str(row.get('Contact Full Name', '')).strip().lower()
        words = full_name.split()
        
        for word in words:
            if len(word) >= 3:  # Only index meaningful words
                if word not in word_indices:
                    word_indices[word] = []
                word_indices[word].append(idx)
    
    progress_bar.progress(1.0)
    st.success(f"✅ Built indices: {len(name_lookup)} names, {len(email_lookup)} emails, {len(word_indices)} words")
    
    # Process input data super fast
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
            target_name = str(row.get(name_col, '')).strip()
            target_email = str(row.get(email_col, '')).strip().lower() if email_col else ''
            target_company = str(row.get(company_col, '')).strip() if company_col else ''
            
            if not target_name:
                continue
            
            best_match = None
            best_score = 0
            best_method = ''
            
            # Method 1: Exact email match (instant)
            if target_email and target_email in email_lookup:
                contact_idx = email_lookup[target_email]
                matched_row = sfdc_contacts_df.iloc[contact_idx]
                best_match = matched_row
                best_score = 100
                best_method = 'Email Exact'
            
            # Method 2: Exact name match (instant)
            elif target_name.lower() in name_lookup:
                contact_idx = name_lookup[target_name.lower()]
                matched_row = sfdc_contacts_df.iloc[contact_idx]
                best_match = matched_row
                best_score = 100
                best_method = 'Name Exact'
            
            # Method 3: Smart word-based fuzzy matching (fast)
            else:
                candidates = set()
                words = target_name.lower().split()
                
                # Find candidates based on shared words
                for word in words:
                    if word in word_indices:
                        candidates.update(word_indices[word][:50])  # Limit candidates per word
                
                # Only do fuzzy matching on a small candidate set
                if candidates and len(candidates) < 200:  # Only if manageable number
                    candidate_names = []
                    candidate_indices = []
                    
                    for candidate_idx in list(candidates)[:100]:  # Max 100 candidates
                        candidate_row = sfdc_contacts_df.iloc[candidate_idx]
                        candidate_names.append(candidate_row['Contact Full Name'])
                        candidate_indices.append(candidate_idx)
                    
                    # Fast fuzzy matching on small candidate set
                    if candidate_names:
                        matches = process.extract(
                            target_name,
                            candidate_names,
                            scorer=fuzz.token_set_ratio,
                            limit=1,
                            score_cutoff=threshold
                        )
                        
                        if matches:
                            match_text, score, list_idx = matches[0]
                            contact_idx = candidate_indices[list_idx]
                            matched_row = sfdc_contacts_df.iloc[contact_idx]
                            best_match = matched_row
                            best_score = score
                            best_method = f'Smart Fuzzy ({score}%)'
            
            # Add result if found
            if best_match is not None:
                result = {
                    'Input_Name': target_name,
                    'Input_Email': target_email if email_col else 'N/A',
                    'Input_Company': target_company if company_col else 'N/A',
                    'Match_1_SFDC_Name': best_match['Contact Full Name'],
                    'Match_1_SFDC_Email': best_match.get('Email', ''),
                    'Match_1_Contact_ID': best_match['CASE SAFE ID - CNT'],
                    'Match_1_Account_Name': best_match.get('Account Name', ''),
                    'Match_1_Title': best_match.get('Title', ''),
                    'Match_1_Confidence': f'{best_score:.1f}%',
                    'Match_1_Method': best_method
                }
                results.append(result)
                batch_matches += 1
                matches_found += 1
        
        # Update progress
        progress = batch_end / total_rows
        progress_bar.progress(progress)
        status_text.text(f"⚡ Processed {batch_end}/{total_rows} contacts...")
        match_counter.text(f"✅ Matches: {matches_found} (Batch: +{batch_matches})")
    
    progress_bar.empty()
    status_text.empty()
    match_counter.empty()
    
    st.success(f"🎉 Lightning processing complete! Found {matches_found} matches")
    return pd.DataFrame(results)

# Main Streamlit App
def main():
    st.title("🚀 SFDC Account & Contact Matcher - SPEED OPTIMIZED")
    st.markdown("**Ultra-fast AI-powered matching with pre-computed indices and vectorized operations**")
    
    # Load model
    with st.spinner("Loading AI model..."):
        model = load_model()
    
    # Main tabs
    tab1, tab2 = st.tabs(["🏢 Account Matching", "👤 Contact Matching"])
    
    with tab1:
        st.header("Account Matching")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Upload Target Accounts")
            input_file = st.file_uploader("Upload CSV with accounts to match", type=['csv'], key="account_input")
            
        with col2:
            st.subheader("📁 Upload SFDC Reference")
            sfdc_file = st.file_uploader("Upload SFDC accounts CSV", type=['csv'], key="account_sfdc")
        
        if input_file and sfdc_file:
            # Load data
            input_df = load_csv_with_encoding(input_file)
            sfdc_accounts_df = load_sfdc_accounts(sfdc_file)
            
            if input_df is not None and not sfdc_accounts_df.empty:
                st.success(f"✅ Loaded {len(input_df)} target accounts and {len(sfdc_accounts_df)} SFDC accounts")
                
                # Pre-compute embeddings
                embeddings = precompute_account_embeddings(model, sfdc_accounts_df['Clean_Name'])
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    name_column = st.selectbox("Account Name Column", input_df.columns, key="acc_name_col")
                
                with col2:
                    algorithm = st.selectbox("Matching Algorithm", 
                                           ["Semantic (BERT)", "Fuzzy String", "Hybrid (Semantic + Fuzzy)"],
                                           key="acc_algorithm")
                
                with col3:
                    threshold = st.slider("Confidence Threshold", 50, 100, 85, key="acc_threshold")
                
                if st.button("🚀 Start Account Matching", key="start_account_match"):
                    start_time = time.time()
                    
                    target_names = input_df[name_column].tolist()
                    
                    with st.spinner("Processing account matches..."):
                        if algorithm == "Semantic (BERT)":
                            results_df = vectorized_semantic_match(target_names, sfdc_accounts_df, model, embeddings, threshold)
                        elif algorithm == "Fuzzy String":
                            results_df = vectorized_fuzzy_match(target_names, sfdc_accounts_df['Clean_Name'], sfdc_accounts_df, threshold)
                        else:  # Hybrid
                            semantic_results = vectorized_semantic_match(target_names, sfdc_accounts_df, model, embeddings, threshold)

                            # Find unmatched targets, keeping each one's original row number.
                            # The fuzzy pass sees a filtered list, so without this map its
                            # Input_Index would count positions in that filtered list and
                            # collide with the semantic half after the concat below.
                            matched_indices = set(semantic_results['Input_Index'].tolist()) if not semantic_results.empty else set()
                            unmatched = [(i, name) for i, name in enumerate(target_names) if i not in matched_indices]

                            if unmatched:
                                unmatched_indices = [i for i, _ in unmatched]
                                unmatched_names = [name for _, name in unmatched]
                                fuzzy_results = vectorized_fuzzy_match(
                                    unmatched_names, sfdc_accounts_df['Clean_Name'], sfdc_accounts_df,
                                    threshold, input_indices=unmatched_indices
                                )
                                results_df = pd.concat([semantic_results, fuzzy_results], ignore_index=True)
                            else:
                                results_df = semantic_results
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    if not results_df.empty:
                        st.success(f"⚡ Found {len(results_df)} matches in {processing_time:.1f} seconds!")
                        
                        st.subheader("📊 Results Preview")
                        st.dataframe(results_df.head(10))
                        
                        csv = results_df.to_csv(index=False)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        
                        st.download_button(
                            label="📥 Download Account Matches CSV",
                            data=csv,
                            file_name=f"account_matches_{timestamp}.csv",
                            mime="text/csv",
                            key="download_account_matches"
                        )
                        
                        # Show statistics
                        if 'Match_1_Confidence' in results_df.columns:
                            results_df['Confidence_Numeric'] = results_df['Match_1_Confidence'].str.replace('%', '').astype(float)
                            high_conf = len(results_df[results_df['Confidence_Numeric'] >= 90])
                            med_conf = len(results_df[results_df['Confidence_Numeric'].between(75, 89)])
                            low_conf = len(results_df[results_df['Confidence_Numeric'] < 75])
                            
                            col1, col2, col3 = st.columns(3)
                            col1.metric("High Confidence (90%+)", high_conf)
                            col2.metric("Medium Confidence (75-89%)", med_conf) 
                            col3.metric("Low Confidence (<75%)", low_conf)
                        
                    else:
                        st.warning("⚠️ No matches found. Try lowering the confidence threshold.")
    
    with tab2:
        st.header("Contact Matching")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📁 Upload Target Contacts")
            contact_input_file = st.file_uploader("Upload CSV with contacts to match", type=['csv'], key="contact_input")
            
        with col2:
            st.subheader("📁 Upload SFDC Contacts")
            contact_sfdc_file = st.file_uploader("Upload SFDC contacts CSV", type=['csv'], key="contact_sfdc")
        
        if contact_input_file and contact_sfdc_file:
            input_contacts_df = load_csv_with_encoding(contact_input_file)
            sfdc_contacts_df = load_sfdc_contacts(contact_sfdc_file)
            
            if input_contacts_df is not None and not sfdc_contacts_df.empty:
                st.success(f"✅ Loaded {len(input_contacts_df)} target contacts and {len(sfdc_contacts_df)} SFDC contacts")
                
                # Show available columns for mapping
                st.subheader("📋 Column Mapping")
                st.write("**Your Input File Columns:**", list(input_contacts_df.columns))
                st.write("**SFDC File Columns:**", list(sfdc_contacts_df.columns))
                
                # Column mapping with optional fields
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    name_col = st.selectbox("👤 Full Name Column (Required)", 
                                          input_contacts_df.columns, key="cont_name_col")
                
                with col2:
                    email_col = st.selectbox("📧 Email Column (Optional)", 
                                           ['-- No Email Column --'] + list(input_contacts_df.columns), 
                                           key="cont_email_col")
                
                with col3:
                    company_col = st.selectbox("🏢 Company Column (Optional)", 
                                             ['-- No Company Column --'] + list(input_contacts_df.columns), 
                                             key="cont_company_col")
                
                with col4:
                    matching_threshold = st.slider("🎯 Matching Threshold", 70, 100, 85, key="cont_threshold")
                
                # Show field mapping info
                st.info(f"""
                **Matching Strategy:**
                - Primary: Full Name matching using '{name_col}' → 'Contact Full Name'
                - Email: {'Enabled' if email_col != '-- No Email Column --' else 'Disabled'}
                - Company: {'Enabled' if company_col != '-- No Company Column --' else 'Disabled'}
                - Output: CASE SAFE ID - CNT for Campaign Member uploads
                """)
                
                # Pre-compute contact indices (not needed for lightning version but kept for compatibility)
                indices = {}
                
                if st.button("🚀 Start Contact Matching", key="start_contact_match"):
                    start_time = time.time()
                    
                    # Convert column selections
                    email_field = email_col if email_col != '-- No Email Column --' else None
                    company_field = company_col if company_col != '-- No Company Column --' else None
                    
                    with st.spinner("Processing contact matches..."):
                        contact_results_df = lightning_fast_contact_matching(
                            input_contacts_df, sfdc_contacts_df, email_field, name_col, company_field, matching_threshold
                        )
                    
                    end_time = time.time()
                    processing_time = end_time - start_time
                    
                    if not contact_results_df.empty:
                        st.success(f"⚡ Found {len(contact_results_df)} matches in {processing_time:.1f} seconds!")
                        
                        st.subheader("📊 Results Preview")
                        st.dataframe(contact_results_df.head(10))
                        
                        csv = contact_results_df.to_csv(index=False)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        
                        st.download_button(
                            label="📥 Download Contact Matches CSV",
                            data=csv,
                            file_name=f"contact_matches_{timestamp}.csv",
                            mime="text/csv",
                            key="download_contact_matches"
                        )
                        
                        # Show statistics
                        if 'Match_1_Method' in contact_results_df.columns:
                            email_exact = len(contact_results_df[contact_results_df['Match_1_Method'] == 'Email Exact'])
                            domain_matches = len(contact_results_df[contact_results_df['Match_1_Method'].str.contains('Domain', na=False)])
                            fuzzy_matches = len(contact_results_df[contact_results_df['Match_1_Method'].str.contains('Fuzzy', na=False)])
                            name_matches = len(contact_results_df[contact_results_df['Match_1_Method'].str.contains('Name Match', na=False)])
                            
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Email Exact Matches", email_exact)
                            col2.metric("Domain Matches", domain_matches)
                            col3.metric("Name Matches", name_matches)
                            col4.metric("Fuzzy Matches", fuzzy_matches)
                        
                    else:
                        st.warning("⚠️ No matches found. Try lowering the matching threshold.")
    
    st.markdown("---")
    st.markdown("**Built for RevOps Team • Speed-optimized AI matching with vectorized operations**")

if __name__ == "__main__":
    main()