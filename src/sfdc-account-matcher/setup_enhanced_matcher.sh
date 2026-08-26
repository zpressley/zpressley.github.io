#!/bin/bash

# Enhanced Account & Contact Matcher Setup Script
# Run this in your Terminal to set up the complete matching application

echo "🚀 Setting up Enhanced SFDC Account & Contact Matcher..."
echo "=================================================="

# Navigate to project directory
cd "/Users/zpressley/Fuzzy Matching"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

# Install required packages
echo "📚 Installing required packages..."
pip install streamlit==1.28.0
pip install pandas==2.1.0
pip install numpy==1.24.0
pip install rapidfuzz==3.3.0
pip install sentence-transformers==2.2.2
pip install torch==2.0.1
pip install scikit-learn==1.3.0
pip install chardet==5.2.0

# Create requirements.txt for future reference
echo "📝 Creating requirements.txt..."
cat > requirements.txt << EOF
streamlit==1.28.0
pandas==2.1.0
numpy==1.24.0
rapidfuzz==3.3.0
sentence-transformers==2.2.2
torch==2.0.1
scikit-learn==1.3.0
chardet==5.2.0
EOF

# Create launch script
echo "🖥️ Creating launch script..."
cat > launch_matcher.sh << 'EOF'
#!/bin/bash
cd "/Users/zpressley/Fuzzy Matching"
source venv/bin/activate
echo "🔍 Starting Enhanced SFDC Matcher..."
echo "Application will open in your browser automatically"
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo "=================================================="
streamlit run account_matcher.py --server.port=8501 --server.address=localhost
EOF

# Make launch script executable
chmod +x launch_matcher.sh

# Create quick run script for team members
echo "👥 Creating team launcher..."
cat > run_matcher.command << 'EOF'
#!/bin/bash
cd "/Users/zpressley/Fuzzy Matching"
source venv/bin/activate
echo "🚀 Enhanced SFDC Account & Contact Matcher"
echo "==========================================="
echo ""
echo "Starting application..."
echo "Browser will open automatically"
echo ""
echo "Features:"
echo "✅ Account matching with AI semantic analysis"
echo "✅ Contact matching with multi-field validation"
echo "✅ Fuzzy string matching for variations"
echo "✅ CSV export for SFDC upload"
echo ""
echo "Press Ctrl+C to stop"
echo "==========================================="
streamlit run account_matcher.py --server.port=8501 --server.address=0.0.0.0
EOF

# Make team launcher executable and double-clickable
chmod +x run_matcher.command

# Create data directory structure
echo "📁 Creating data directories..."
mkdir -p data/input
mkdir -p data/output
mkdir -p data/reference

# Create sample data templates
echo "📋 Creating sample data templates..."

# Sample account input template
cat > data/input/sample_accounts_template.csv << EOF
Company_Name,Website,Industry
Anaconda Inc,anaconda.com,Software
Microsoft Corporation,microsoft.com,Technology
Salesforce Inc,salesforce.com,CRM Software
EOF

# Sample contact input template  
cat > data/input/sample_contacts_template.csv << EOF
Email,Name,Company
john.doe@anaconda.com,John Doe,Anaconda Inc
jane.smith@microsoft.com,Jane Smith,Microsoft Corporation
bob.johnson@salesforce.com,Bob Johnson,Salesforce Inc
EOF

# Create user guide
echo "📖 Creating user guide..."
cat > USER_GUIDE.md << 'EOF'
# Enhanced SFDC Account & Contact Matcher - User Guide

## 🚀 Quick Start

### For Mac Users:
1. **Double-click** `run_matcher.command` file
2. **Allow terminal access** if prompted
3. **Wait for browser** to open automatically
4. **Upload your files** and start matching!

### For Terminal Users:
```bash
cd "/Users/zpressley/Fuzzy Matching"
./launch_matcher.sh
```

## 📁 File Requirements

### Account Matching:
- **Input CSV**: Must have a column with company names
- **SFDC Reference**: Use `sfdc_accounts.csv` (already included)
- **Supported formats**: .csv files only

### Contact Matching:
- **Input CSV**: Must have Email, Name, and Company columns
- **SFDC Reference**: Use `sfdc_contacts.csv` (already included)
- **Email format**: Standard email addresses (name@domain.com)

## 🔍 Matching Algorithms

### Account Matching:
1. **Semantic (BERT)**: AI-powered understanding of company name variations
2. **Fuzzy String**: Character-by-character similarity matching
3. **Hybrid**: Combines both for best accuracy

### Contact Matching Priority:
1. **Email Exact Match** (100% confidence)
2. **Domain + Name Match** (high confidence)
3. **Fuzzy Name + Company** (medium confidence)

## 📊 Results Interpretation

### Confidence Scores:
- **90%+ (High)**: Very reliable matches, safe to use
- **75-89% (Medium)**: Good matches, review recommended
- **<75% (Low)**: Uncertain matches, manual review required

### Match Methods:
- **Email Exact**: Perfect email address match
- **Semantic Match**: AI detected company name similarity
- **Fuzzy Match**: String similarity algorithm
- **Domain Match**: Same email domain + name similarity

## 📥 Output Files

### Columns Included:
- **Input data**: Your original data
- **Match details**: SFDC Name, ID, confidence score
- **Match method**: How the match was found
- **Additional fields**: Website, location (when available)

### Ready for SFDC:
- **Account IDs**: Use CASE SAFE ID - ACCT column
- **Contact IDs**: Use CASE SAFE ID - CNT column
- **Campaign Members**: Format ready for bulk upload

## ⚠️ Troubleshooting

### Common Issues:
1. **No matches found**: Lower confidence threshold
2. **App won't start**: Check terminal for error messages
3. **Slow performance**: Use smaller test files first
4. **Wrong columns**: Verify column names match your CSV

### Getting Help:
- Check terminal window for error messages
- Ensure CSV files are properly formatted
- Try with sample template files first
- Contact Sales Ops team for technical support

## 🎯 Best Practices

### Data Quality:
- **Clean your data** before upload (remove extra spaces)
- **Use standard formats** for company names
- **Include complete email addresses** for contacts
- **Test with small files** before processing large datasets

### Efficiency Tips:
- **Start with high thresholds** (85%+) for accuracy
- **Review medium confidence** matches manually
- **Use hybrid algorithm** for best results
- **Export results immediately** after processing

---
**Built for RevOps Team • Enhanced AI-powered matching**
EOF

echo ""
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "🎯 What's Ready:"
echo "   ✅ Enhanced matching application installed"
echo "   ✅ All required packages installed"
echo "   ✅ Launch scripts created"
echo "   ✅ Sample templates created"
echo "   ✅ User guide created"
echo ""
echo "🚀 To Start Matching:"
echo "   Option 1: Double-click 'run_matcher.command'"
echo "   Option 2: Run './launch_matcher.sh' in terminal"
echo ""
echo "📁 Files Created:"
echo "   • account_matcher.py (main application)"
echo "   • launch_matcher.sh (terminal launcher)"
echo "   • run_matcher.command (team launcher)"
echo "   • USER_GUIDE.md (complete instructions)"
echo "   • requirements.txt (package list)"
echo ""
echo "📊 Sample Templates:"
echo "   • data/input/sample_accounts_template.csv"
echo "   • data/input/sample_contacts_template.csv"
echo ""
echo "Ready to match accounts and contacts with AI precision! 🎯"