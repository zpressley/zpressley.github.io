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
