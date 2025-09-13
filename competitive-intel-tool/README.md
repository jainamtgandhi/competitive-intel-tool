# 🧠 Personal Competitive Intelligence Tool

Your daily competitive intelligence assistant for analyzing companies, understanding competitors, and making informed decisions.

## 🎯 What This Tool Does

**Input**: Company name + URL  
**Output**: Comprehensive competitive analysis including:
- 🏢 Company Overview & Business Model
- 💰 Pricing Analysis & Comparison
- ⚡ Feature Analysis & Capabilities
- 🎯 SWOT Analysis with Ratings
- 📊 Export Options (JSON, Text)

## 🚀 Quick Start

### 1. Setup (5 minutes)
```bash
# Clone or download this folder
cd competitive-intel-tool

# Install dependencies
python setup.py

# Or manually:
pip install -r requirements.txt
```

### 2. Get API Key
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-`)

### 3. Run the Tool
```bash
streamlit run main.py
```

### 4. Use the Tool
1. Open your browser to `http://localhost:8501`
2. Enter your OpenAI API key in the sidebar
3. Enter a company name and URL
4. Click "🚀 Analyze Company"
5. Wait 3-5 minutes for analysis
6. Explore the results in different tabs

## 💰 Cost Breakdown

**Monthly Usage**: Daily use (30 analyses/month)
- **OpenAI GPT-4**: $5-15/month
- **Google Custom Search**: FREE (100 queries/day)
- **Total**: $5-15/month

## 📊 Example Usage

### Input:
- **Company Name**: SonarSource
- **URL**: https://www.sonarsource.com

### Output:
- **Company Overview**: Code quality platform for developers
- **Pricing**: $10-50/user/month with 20% annual discount
- **Features**: Static analysis, security scanning, technical debt tracking
- **SWOT**: Strong in code quality, opportunity in enterprise market
- **Export**: Download as JSON or text file

## 🔧 Technical Details

### Architecture:
- **Frontend**: Streamlit (runs locally)
- **Scraping**: requests + BeautifulSoup
- **Analysis**: OpenAI GPT-4
- **Storage**: Local files (your computer)

### Data Sources:
- Company websites (homepage, pricing, features, about)
- Google search results (competitor discovery)
- AI analysis of scraped content

### Privacy:
- Everything runs on your computer
- No data sent to third parties (except OpenAI for analysis)
- All scraped data stays local

## 🎨 Features

### ✅ Current Features:
- Company overview analysis
- Pricing comparison
- Feature extraction
- SWOT analysis
- Export to JSON/text
- Local data storage
- Progress tracking

### 🔄 Planned Features:
- Competitor auto-discovery
- Historical analysis tracking
- Excel export
- PDF report generation
- Interactive Q&A

## 🛠️ Customization

### Adding More Analysis Types:
Edit `main.py` and add new analysis functions:
```python
def analyze_market_position(content):
    prompt = f"Analyze market position: {content}"
    return get_gpt_response(prompt)
```

### Changing Analysis Depth:
Modify the prompts in `analyze_with_gpt()` function to get more detailed or focused analysis.

## 🔍 Troubleshooting

### Common Issues:

**"OpenAI API Key Error"**
- Make sure you've entered a valid API key
- Check that you have credits in your OpenAI account

**"Scraping Failed"**
- Some websites block automated requests
- Try with a different company URL
- The tool will continue with partial data

**"Analysis Takes Too Long"**
- GPT-4 analysis takes 2-3 minutes
- Large websites take longer to scrape
- Consider using "Quick" analysis mode

### Getting Help:
1. Check the error messages in the Streamlit interface
2. Look at the browser console for detailed errors
3. Make sure all dependencies are installed

## 📈 Usage Tips

### For Best Results:
1. **Use company's main website URL** (not subdomains)
2. **Enter the exact company name** as it appears on their website
3. **Run analysis during off-peak hours** for faster results
4. **Export results immediately** - they're not saved automatically

### Daily Workflow:
1. Morning: Analyze 1-2 companies you're interested in
2. Export results to your preferred format
3. Use insights for job research, investment decisions, or business analysis

## 🔒 Privacy & Security

- **Local Processing**: All scraping happens on your computer
- **API Keys**: Store securely, never commit to version control
- **Data Storage**: All analysis results stay on your machine
- **No Tracking**: Tool doesn't collect or send usage data

## 📝 License

This is a personal tool for individual use. Feel free to modify and customize for your needs.

## 🆘 Support

This is a personal project. For issues:
1. Check the troubleshooting section above
2. Review the code comments for customization
3. Modify the tool to fit your specific needs

---

**Happy analyzing! 🧠✨**
