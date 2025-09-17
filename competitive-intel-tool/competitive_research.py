import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import json
import time
import re
from datetime import datetime
import urllib.parse
import pandas as pd

# Configure page
st.set_page_config(
    page_title="🔍 Competitive Research Tool", 
    page_icon="🔍", 
    layout="wide"
)

# Sidebar for API keys
with st.sidebar:
    st.title("🔍 Competitive Research Tool")
    st.caption("Discover and analyze competitors for any company")
    
    # API Key inputs
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    serpapi_key = st.text_input("SerpAPI Key (250 free searches)", type="password")
    google_api_key = st.text_input("Google Search API Key (100/day free)", type="password")
    google_cse_id = st.text_input("Google Custom Search Engine ID", type="password")
    
    # Set API keys
    if openai_api_key:
        openai.api_key = openai_api_key
        st.success("✅ OpenAI API Ready")
    
    if serpapi_key:
        st.success("✅ SerpAPI Ready (250 free searches)")
    
    if google_api_key:
        st.success("✅ Google Search API Ready (100/day free)")

def main():
    st.title("🔍 Competitive Research Tool")
    st.caption("Enter a company URL to discover and analyze its competitors")
    
    # Input section
    company_url = st.text_input(
        "Company Website URL", 
        placeholder="e.g., https://netflix.com, https://sonarsource.com, https://stripe.com"
    )
    
    # Analysis button
    if st.button("🚀 Research Competitors", type="primary"):
        if not company_url:
            st.error("Please enter a company website URL")
            return
        
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar")
            return
        
        # Run competitive research
        with st.spinner("🔍 Researching competitors... This may take 5-7 minutes"):
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Extract company name from URL
                status_text.text("🔍 Extracting company information...")
                progress_bar.progress(10)
                
                company_name = extract_company_name_from_url(company_url)
                st.success(f"Found company: **{company_name}**")
                
                # Step 2: Discover competitors
                status_text.text("🔍 Discovering competitors...")
                progress_bar.progress(20)
                
                competitors = discover_competitors_comprehensive(company_name, company_url)
                st.info(f"Found {len(competitors)} competitors")
                
                # Step 3: Scrape target company data
                status_text.text("📄 Scraping target company...")
                progress_bar.progress(40)
                
                target_company_data = scrape_company_comprehensive(company_url, company_name)
                
                # Step 4: Scrape competitor data
                status_text.text("📊 Scraping competitors...")
                progress_bar.progress(60)
                
                competitor_data = scrape_competitors_comprehensive(competitors)
                
                # Add target company to competitor data for comprehensive comparison
                competitor_data[company_name] = target_company_data
                
                # Step 5: Competitive Analysis
                status_text.text("🤖 Running competitive analysis...")
                progress_bar.progress(80)
                
                competitive_analysis = analyze_competitive_landscape(company_name, target_company_data, competitor_data)
                
                # Step 6: Display results
                status_text.text("📊 Generating competitive report...")
                progress_bar.progress(100)
                
                display_competitive_research_results(company_name, competitive_analysis, competitors, competitor_data)
                
                status_text.text("✅ Competitive research complete!")
                
            except Exception as e:
                st.error(f"Competitive research failed: {str(e)}")
                st.exception(e)

def extract_company_name_from_url(url):
    """Extract company name from URL"""
    try:
        # Parse URL
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove common prefixes
        domain = domain.replace('www.', '').replace('http://', '').replace('https://', '')
        
        # Extract main domain name
        if '.' in domain:
            company_name = domain.split('.')[0]
        else:
            company_name = domain
        
        # Clean up the name
        company_name = company_name.replace('-', ' ').replace('_', ' ')
        company_name = company_name.title()
        
        return company_name
    except:
        return "Unknown Company"

def discover_competitors_comprehensive(company_name, company_url):
    """Discover competitors using multiple search strategies with enhanced queries"""
    competitors = []
    
    # Enhanced search queries for better competitor discovery
    search_queries = [
        f'"{company_name}" competitors alternatives',
        f'"{company_name}" vs competitors comparison',
        f'best alternatives to {company_name}',
        f'companies like {company_name}',
        f'{company_name} competitors list',
        f'{company_name} vs',
        f'{company_name} alternative software',
        f'{company_name} similar companies',
        f'"{company_name}" market competitors',
        f'"{company_name}" industry rivals'
    ]
    
    # Try SerpAPI first (better results)
    if serpapi_key:
        try:
            for query in search_queries[:3]:  # Limit to 3 queries to save API calls
                competitors.extend(discover_with_serpapi(query, company_name))
                if len(competitors) >= 5:  # Stop if we have enough
                    break
        except Exception as e:
            st.warning(f"SerpAPI failed: {e}")
    
    # Try Google Custom Search as backup
    if len(competitors) < 3 and google_api_key and google_cse_id:
        try:
            for query in search_queries[:2]:  # Limit to 2 queries
                competitors.extend(discover_with_google_search(query, company_name, google_api_key, google_cse_id))
                if len(competitors) >= 5:
                    break
        except Exception as e:
            st.warning(f"Google Search failed: {e}")
    
    # Remove duplicates and return top competitors
    unique_competitors = []
    seen_names = set()
    
    for comp in competitors:
        if comp['name'] not in seen_names and len(unique_competitors) < 5:
            unique_competitors.append(comp)
            seen_names.add(comp['name'])
    
    return unique_competitors

def discover_with_serpapi(query, company_name):
    """Discover competitors using SerpAPI"""
    competitors = []
    
    try:
        params = {
            "q": query,
            "api_key": serpapi_key,
            "engine": "google",
            "num": 5
        }
        
        response = requests.get("https://serpapi.com/search", params=params, timeout=10)
        results = response.json()
        
        # Extract from organic results
        if 'organic_results' in results:
            for result in results['organic_results']:
                title = result.get('title', '')
                url = result.get('link', '')
                
                if company_name.lower() not in title.lower() and url:
                    competitor_name = extract_competitor_name_from_title(title, company_name)
                    if competitor_name:
                        competitors.append({
                            "name": competitor_name,
                            "url": url,
                            "source": "serpapi"
                        })
        
        # Extract from People Also Ask
        if 'people_also_ask' in results:
            for paa in results['people_also_ask']:
                question = paa.get('question', '')
                if 'vs' in question.lower() or 'alternative' in question.lower():
                    potential_competitors = extract_competitors_from_question(question, company_name)
                    competitors.extend(potential_competitors)
    
    except Exception as e:
        pass
    
    return competitors

def discover_with_google_search(query, company_name, api_key, cse_id):
    """Discover competitors using Google Custom Search"""
    competitors = []
    
    try:
        params = {
            'key': api_key,
            'cx': cse_id,
            'q': query,
            'num': 5
        }
        
        response = requests.get('https://www.googleapis.com/customsearch/v1', params=params, timeout=10)
        results = response.json()
        
        if 'items' in results:
            for item in results['items']:
                title = item.get('title', '')
                url = item.get('link', '')
                
                if company_name.lower() not in title.lower() and url:
                    competitor_name = extract_competitor_name_from_title(title, company_name)
                    if competitor_name:
                        competitors.append({
                            "name": competitor_name,
                            "url": url,
                            "source": "google_search"
                        })
    
    except Exception as e:
        pass
    
    return competitors

def extract_competitor_name_from_title(title, original_company):
    """Extract competitor name from search result title"""
    # Remove common words and extract company name
    title = title.replace(' - ', ' ').replace(' | ', ' ').replace(' vs ', ' ')
    title = title.replace(' vs ', ' ').replace(' vs. ', ' ')
    
    # Split and look for company names
    words = title.split()
    
    # Look for patterns like "Company A vs Company B"
    if ' vs ' in title.lower():
        parts = title.split(' vs ')
        for part in parts:
            part = part.strip().replace('?', '').replace('"', '')
            if part and part.lower() != original_company.lower():
                return part
    
    # Otherwise take first 2-3 words as company name
    if words:
        company_name = ' '.join(words[:2])
        return company_name.strip()
    
    return ""

def extract_competitors_from_question(question, company_name):
    """Extract competitor names from People Also Ask questions"""
    competitors = []
    
    if ' vs ' in question.lower():
        parts = question.split(' vs ')
        for part in parts:
            competitor_name = part.strip().replace('?', '').replace('"', '')
            if competitor_name and competitor_name.lower() != company_name.lower():
                competitors.append({
                    "name": competitor_name,
                    "url": f"https://www.{competitor_name.lower().replace(' ', '')}.com",
                    "source": "people_also_ask"
                })
    
    return competitors

def scrape_company_comprehensive(url, company_name):
    """Scrape comprehensive company data"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = {
            'homepage': extract_homepage_content(soup),
            'pricing': scrape_pricing_info(url),
            'features': scrape_features_info(url),
            'about': scrape_about_info(url)
        }
        
        return content
        
    except Exception as e:
        return {"error": f"Failed to scrape {url}: {str(e)}"}

def extract_homepage_content(soup):
    """Extract key homepage content"""
    return {
        'title': soup.find('title').text if soup.find('title') else '',
        'headline': extract_text_by_selectors(soup, ['h1', '.hero-title', '.main-headline']),
        'subheadline': extract_text_by_selectors(soup, ['h2', '.hero-subtitle', '.main-subtitle']),
        'description': extract_text_by_selectors(soup, ['p', '.description', '.intro']),
        'features': extract_features_from_homepage(soup)
    }

def scrape_pricing_info(url):
    """Scrape pricing information"""
    pricing_urls = [f"{url}/pricing", f"{url}/plans", f"{url}/price"]
    
    for pricing_url in pricing_urls:
        try:
            response = requests.get(pricing_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pricing_data = extract_pricing_from_page(soup)
            if pricing_data:
                return pricing_data
        except:
            continue
    
    return None

def scrape_features_info(url):
    """Scrape features information"""
    feature_urls = [f"{url}/features", f"{url}/products", f"{url}/solutions"]
    
    for feature_url in feature_urls:
        try:
            response = requests.get(feature_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            features = extract_features_from_page(soup)
            if features:
                return features
        except:
            continue
    
    return None

def scrape_about_info(url):
    """Scrape about page information"""
    about_url = f"{url}/about"
    
    try:
        response = requests.get(about_url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return extract_about_content(soup)
    except:
        return None

def extract_text_by_selectors(soup, selectors):
    """Extract text using multiple selectors"""
    for selector in selectors:
        element = soup.select_one(selector)
        if element and element.get_text(strip=True):
            return element.get_text(strip=True)
    return ""

def extract_features_from_homepage(soup):
    """Extract features from homepage"""
    features = []
    
    feature_elements = soup.find_all(['li', 'div'], class_=re.compile(r'feature|benefit|capability'))
    
    for element in feature_elements[:10]:
        text = element.get_text(strip=True)
        if text and len(text) < 100:
            features.append(text)
    
    return features

def extract_pricing_from_page(soup):
    """Extract pricing information from pricing page"""
    pricing_tiers = []
    
    pricing_elements = soup.find_all(['div', 'tr'], class_=re.compile(r'pricing|plan|tier'))
    
    for element in pricing_elements:
        tier_name = extract_tier_name(element)
        tier_price = extract_tier_price(element)
        
        if tier_name and tier_price:
            pricing_tiers.append({
                'name': tier_name,
                'price': tier_price
            })
    
    return pricing_tiers if pricing_tiers else None

def extract_features_from_page(soup):
    """Extract features from features page"""
    features = []
    
    feature_elements = soup.find_all(['div', 'li'], class_=re.compile(r'feature|capability|benefit'))
    
    for element in feature_elements:
        text = element.get_text(strip=True)
        if text and len(text) < 150:
            features.append(text)
    
    return features[:20] if features else None

def extract_about_content(soup):
    """Extract about page content"""
    return {
        'description': extract_text_by_selectors(soup, ['.about-text', '.company-description', 'p']),
        'mission': extract_text_by_selectors(soup, ['.mission', '.vision']),
        'team_info': extract_text_by_selectors(soup, ['.team', '.leadership'])
    }

def extract_tier_name(element):
    """Extract pricing tier name"""
    name_selectors = ['.tier-name', '.plan-name', 'h3', 'h4']
    for selector in name_selectors:
        name_elem = element.select_one(selector)
        if name_elem:
            return name_elem.get_text(strip=True)
    return ""

def extract_tier_price(element):
    """Extract pricing tier price"""
    price_selectors = ['.price', '.cost', '.amount']
    for selector in price_selectors:
        price_elem = element.select_one(selector)
        if price_elem:
            return price_elem.get_text(strip=True)
    return ""

def scrape_competitors_comprehensive(competitors):
    """Scrape competitor data with enhanced error handling and progress tracking"""
    competitor_data = {}
    
    # Increase limit to get more competitors for better comparison
    for i, competitor in enumerate(competitors[:5]):  # Increased to top 5 competitors
        try:
            with st.spinner(f"Scraping {competitor['name']}..."):
                data = scrape_company_comprehensive(competitor['url'], competitor['name'])
                competitor_data[competitor['name']] = data
                st.success(f"✅ {competitor['name']} data collected")
        except Exception as e:
            st.warning(f"⚠️ Failed to scrape {competitor['name']}: {str(e)}")
            # Add placeholder data so comparison still works
            competitor_data[competitor['name']] = {
                'homepage': {'title': competitor['name'], 'headline': 'Data unavailable', 'description': 'Could not scrape data'},
                'pricing': None,
                'features': None,
                'about': None
            }
            continue
    
    return competitor_data

def analyze_competitive_landscape(company_name, target_data, competitor_data):
    """Analyze competitive landscape with GPT"""
    
    # Prepare content for analysis
    content = prepare_competitive_content(company_name, target_data, competitor_data)
    
    # Get competitor names for structured analysis
    competitor_names = list(competitor_data.keys()) if competitor_data else []
    
    # Competitive Analysis Prompts
    analysis_prompts = {
        'overview': f"""
        Create a comprehensive competitive landscape analysis comparing {company_name} with all competitors:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        CONTENT: {content}
        
        **COMPETITIVE LANDSCAPE OVERVIEW:**
        
        1. **Market Analysis**: What is the overall market these companies operate in?
        2. **Company Profiles**: Brief description of what each company does
        3. **Competitive Positioning**: How does each company position itself differently?
        4. **Key Differentiators**: What makes each company unique?
        5. **Market Share Insights**: Which companies appear to be market leaders?
        6. **Competitive Advantages**: What advantages does each company have?
        7. **Strategic Recommendations**: What should {company_name} focus on to compete better?
        
        **SIDE-BY-SIDE COMPARISON:**
        | Aspect | {company_name} | {', '.join(competitor_names)} |
        |--------|----------------|{'-' * (len(competitor_names) * 15)}|
        | Target Market | [Description] | [Description] |
        | Value Proposition | [Description] | [Description] |
        | Pricing Strategy | [Description] | [Description] |
        | Key Features | [Description] | [Description] |
        | Market Position | [Description] | [Description] |
        """,
        
        'structured_analysis': f"""
        Provide structured competitive analysis for each company:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        
        CONTENT: {content}
        
        For each company ({company_name} and {', '.join(competitor_names)}), provide:
        
        1. Target Persona/Audience: Who is their primary customer base? (2-3 sentences)
        2. Market Positioning: How do they position themselves in the market? (2-3 sentences)
        3. Tone/Messaging: What messaging tone do they use on their homepage? (1-2 sentences)
        4. Differentiation: How are they positioned differently from competitors? (2-3 sentences)
        
        Format as:
        **COMPANY NAME**
        - Target Persona: [analysis]
        - Market Positioning: [analysis]
        - Tone/Messaging: [analysis]
        - Differentiation: [analysis]
        """,
        
        'table_data': f"""
        Create a structured table data for competitive analysis including {company_name} and all competitors:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        
        CONTENT: {content}
        
        For EACH COMPANY (including {company_name} and all competitors), provide a JSON object with these exact fields:
        {{
            "company_name": "Company Name",
            "target_persona": "Brief description of their target audience (1-2 sentences)",
            "market_positioning": "How they position themselves in the market (1-2 sentences)",
            "tone_messaging": "Messaging tone and style they use (1 sentence)",
            "differentiation": "How they differentiate from other companies in this space (1-2 sentences)"
        }}
        
        Return as a JSON array with ALL companies (target + competitors).
        """,
        
        'pricing': f"""
        Create a comprehensive pricing comparison table for this competitive landscape:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        CONTENT: {content}
        
        For each company ({company_name} and {', '.join(competitor_names)}), provide:
        
        **PRICING COMPARISON TABLE:**
        | Company | Pricing Tiers | Price Range | Billing Model | Target Market | Key Features |
        |---------|---------------|-------------|---------------|---------------|--------------|
        | [Company] | [Tier names] | [Price range] | [Monthly/Annual] | [Target audience] | [Key features] |
        
        **ANALYSIS:**
        1. Pricing Strategy Comparison: How do pricing strategies differ?
        2. Value Proposition: Which company offers best value for money?
        3. Market Positioning: How do prices position each company in the market?
        4. Competitive Advantages: What pricing advantages does each have?
        """,
        
        'features': f"""
        Create a comprehensive feature comparison for this competitive landscape:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        CONTENT: {content}
        
        **FEATURE COMPARISON TABLE:**
        | Feature Category | {company_name} | {', '.join(competitor_names)} |
        |------------------|----------------|{'-' * (len(competitor_names) * 15)}|
        | Core Features | [Features] | [Features] |
        | Integration | [Features] | [Features] |
        | Target Market | [Features] | [Features] |
        | Unique Features | [Features] | [Features] |
        
        **ANALYSIS:**
        1. Feature Gaps: What features does each competitor have that others don't?
        2. Common Features: What features are standard across all competitors?
        3. Unique Differentiators: What makes each company unique?
        4. Feature Quality: Which company has the most comprehensive feature set?
        """,
        
        'swot': f"""
        Perform comprehensive competitive SWOT analysis for all companies:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        CONTENT: {content}
        
        **COMPETITIVE SWOT MATRIX:**
        
        For each company ({company_name} and {', '.join(competitor_names)}), provide:
        
        **{company_name}:**
        - **Strengths (1-5)**: [List with ratings and evidence]
        - **Weaknesses (1-5)**: [List with ratings and evidence]
        - **Opportunities (1-5)**: [List with ratings and evidence]
        - **Threats (1-5)**: [List with ratings and evidence]
        
        **COMPETITORS:**
        [Repeat for each competitor]
        
        **COMPARATIVE ANALYSIS:**
        1. **Market Leader**: Which company has the strongest overall position?
        2. **Biggest Threats**: Which company poses the greatest threat to others?
        3. **Growth Potential**: Which company has the best opportunities?
        4. **Vulnerabilities**: Which company has the most weaknesses?
        5. **Strategic Recommendations**: What should each company focus on?
        """
    }
    
    try:
        analyses = {}
        for analysis_type, prompt in analysis_prompts.items():
            analyses[analysis_type] = get_gpt_response(prompt)
        
        return analyses
        
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

def get_gpt_response(prompt):
    """Get response from GPT"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def prepare_competitive_content(company_name, target_data, competitor_data):
    """Prepare content for competitive analysis"""
    content = f"TARGET COMPANY: {company_name}\n\n"
    
    # Add target company data
    if 'homepage' in target_data:
        content += f"TARGET HOMEPAGE: {target_data['homepage']}\n\n"
    
    if 'pricing' in target_data and target_data['pricing']:
        content += f"TARGET PRICING: {target_data['pricing']}\n\n"
    
    if 'features' in target_data and target_data['features']:
        content += f"TARGET FEATURES: {target_data['features']}\n\n"
    
    # Add competitor data
    if competitor_data:
        content += "COMPETITORS:\n"
        for competitor_name, competitor_info in competitor_data.items():
            content += f"{competitor_name}: {competitor_info}\n\n"
    
    return content

def display_competitive_research_results(company_name, analysis_results, competitors, competitor_data):
    """Display competitive research results with full competitor data"""
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Competitive Overview", "💰 Pricing Comparison", "⚡ Feature Comparison", "🎯 SWOT Analysis", "📊 Export"
    ])
    
    with tab1:
        display_competitive_overview(company_name, analysis_results, competitors, competitor_data)
    
    with tab2:
        display_pricing_comparison(analysis_results.get('pricing', ''), competitor_data)
    
    with tab3:
        display_feature_comparison(analysis_results.get('features', ''), competitor_data)
    
    with tab4:
        display_swot_analysis(analysis_results.get('swot', ''), competitor_data)
    
    with tab5:
        display_export_options(company_name, analysis_results)

def display_competitive_overview(company_name, analysis_results, competitors, competitor_data):
    """Display comprehensive competitive analysis with enhanced visualizations"""
    st.subheader(f"🔍 Competitive Analysis: {company_name} vs Competitors")
    
    # Display competitor discovery summary
    st.subheader("🎯 Discovered Competitors & URLs")
    
    # Create a more visual competitor list
    for i, comp in enumerate(competitors, 1):
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.markdown(f"**{i}.**")
        with col2:
            st.markdown(f"**[{comp['name']}]({comp['url']})**")
        with col3:
            st.markdown(f"*{comp['source']}*")
    
    # Add competitor summary metrics
    st.subheader("📈 Competitive Landscape Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Competitors", len(competitors))
    with col2:
        st.metric("Analysis Status", "✅ Complete" if analysis_results else "⏳ Processing")
    with col3:
        st.metric("Data Sources", len(set(comp['source'] for comp in competitors)))
    with col4:
        st.metric("Market Coverage", f"{len(competitors)} companies")
    
    # Create structured table data
    st.subheader("📊 Detailed Competitive Analysis Table")
    
    # Prepare table data
    table_data = []
    
    # Try to parse structured table data from analysis results
    table_analysis = analysis_results.get('table_data', '')
    parsed_data = {}
    
    if table_analysis and 'table_data' in analysis_results:
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', table_analysis, re.DOTALL)
            if json_match:
                import json
                parsed_data = json.loads(json_match.group())
        except:
            pass
    
    # Add target company first, then competitors
    # Add target company
    target_comp_data = None
    if parsed_data:
        target_comp_data = next((item for item in parsed_data if item.get('company_name', '').lower() == company_name.lower()), None)
    
    target_row = {
        "Company": f"**{company_name}** (Target)",
        "URL": "Target Company",
        "Target Persona/Audience": target_comp_data.get('target_persona', 'Analyzing...') if target_comp_data else "Analyzing...",
        "Market Positioning": target_comp_data.get('market_positioning', 'Analyzing...') if target_comp_data else "Analyzing...",
        "Tone/Messaging": target_comp_data.get('tone_messaging', 'Analyzing...') if target_comp_data else "Analyzing...",
        "Differentiation": target_comp_data.get('differentiation', 'Analyzing...') if target_comp_data else "Analyzing..."
    }
    table_data.append(target_row)
    
    # Add competitors
    for comp in competitors:
        comp_data = None
        if parsed_data:
            comp_data = next((item for item in parsed_data if item.get('company_name', '').lower() == comp['name'].lower()), None)
        
        comp_row = {
            "Company": f"**{comp['name']}**",
            "URL": comp['url'],
            "Target Persona/Audience": comp_data.get('target_persona', 'Analyzing...') if comp_data else "Analyzing...",
            "Market Positioning": comp_data.get('market_positioning', 'Analyzing...') if comp_data else "Analyzing...",
            "Tone/Messaging": comp_data.get('tone_messaging', 'Analyzing...') if comp_data else "Analyzing...",
            "Differentiation": comp_data.get('differentiation', 'Analyzing...') if comp_data else "Analyzing..."
        }
        table_data.append(comp_row)
    
    # Create DataFrame and display table
    df = pd.DataFrame(table_data)
    
    # Style the table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "URL": st.column_config.TextColumn("URL", width="medium"),
            "Target Persona/Audience": st.column_config.TextColumn("Target Persona/Audience", width="large"),
            "Market Positioning": st.column_config.TextColumn("Market Positioning", width="large"),
            "Tone/Messaging": st.column_config.TextColumn("Tone/Messaging", width="medium"),
            "Differentiation": st.column_config.TextColumn("Differentiation", width="large")
        }
    )
    
    # Display AI analysis if available
    structured_analysis = analysis_results.get('structured_analysis', '')
    if structured_analysis and structured_analysis != "Analyzing...":
        st.subheader("🧠 AI-Powered Competitive Analysis")
        st.markdown(structured_analysis)
    else:
        st.info("Running competitive analysis... This may take a moment.")
    
    # Add actual competitor data comparison
    if competitor_data:
        st.subheader("📊 Raw Competitor Data Comparison")
        
        # Create a simple comparison table with actual scraped data
        comparison_data = []
        for comp_name, comp_data in competitor_data.items():
            homepage = comp_data.get('homepage', {})
            row = {
                "Company": f"**{comp_name}**",
                "Title": homepage.get('title', 'N/A'),
                "Headline": homepage.get('headline', 'N/A')[:100] + "..." if len(homepage.get('headline', '')) > 100 else homepage.get('headline', 'N/A'),
                "Description": homepage.get('description', 'N/A')[:150] + "..." if len(homepage.get('description', '')) > 150 else homepage.get('description', 'N/A'),
                "Features Count": len(homepage.get('features', [])),
                "Has Pricing": "✅" if comp_data.get('pricing') else "❌",
                "Has About": "✅" if comp_data.get('about') else "❌"
            }
            comparison_data.append(row)
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            st.dataframe(df_comparison, use_container_width=True, hide_index=True)

def display_pricing_comparison(pricing_text, competitor_data):
    """Display comprehensive pricing comparison with visual elements"""
    st.subheader("💰 Competitive Pricing Analysis")
    
    if pricing_text:
        # Display the AI-generated pricing analysis
        st.markdown(pricing_text)
        
        # Add visual elements for better comparison
        st.subheader("📊 Quick Pricing Overview")
        
        # Try to extract pricing data for visual comparison
        if "PRICING COMPARISON TABLE" in pricing_text:
            st.info("💡 Scroll up to see the detailed pricing comparison table above")
        
        # Add pricing insights
        st.subheader("🔍 Key Pricing Insights")
        st.markdown("""
        - **Price Range Analysis**: Compare the pricing tiers across all competitors
        - **Value Proposition**: Identify which company offers the best value for money
        - **Market Positioning**: Understand how pricing positions each company
        - **Competitive Advantages**: Spot pricing strategies that give companies an edge
        """)
    
    # Add actual pricing data comparison
    if competitor_data:
        st.subheader("📊 Actual Pricing Data Comparison")
        
        pricing_comparison = []
        for comp_name, comp_data in competitor_data.items():
            pricing = comp_data.get('pricing', [])
            if pricing:
                for tier in pricing:
                    pricing_comparison.append({
                        "Company": comp_name,
                        "Tier": tier.get('name', 'Unknown'),
                        "Price": tier.get('price', 'N/A')
                    })
            else:
                pricing_comparison.append({
                    "Company": comp_name,
                    "Tier": "No pricing found",
                    "Price": "N/A"
                })
        
        if pricing_comparison:
            df_pricing = pd.DataFrame(pricing_comparison)
            st.dataframe(df_pricing, use_container_width=True, hide_index=True)
        else:
            st.info("No pricing data available for comparison")
        
    else:
        st.info("Pricing analysis not available - this may take a moment to generate")

def display_feature_comparison(features_text, competitor_data):
    """Display comprehensive feature comparison with visual elements"""
    st.subheader("⚡ Competitive Feature Analysis")
    
    if features_text:
        # Display the AI-generated feature analysis
        st.markdown(features_text)
        
        # Add visual elements for better comparison
        st.subheader("🔍 Feature Comparison Insights")
        
        # Try to extract feature data for visual comparison
        if "FEATURE COMPARISON TABLE" in features_text:
            st.info("💡 Scroll up to see the detailed feature comparison table above")
        
        # Add feature analysis insights
        st.subheader("📋 Key Feature Insights")
        st.markdown("""
        - **Feature Gaps**: Identify what features competitors have that others don't
        - **Common Features**: See what features are standard across the industry
        - **Unique Differentiators**: Discover what makes each company special
        - **Feature Quality**: Compare the depth and breadth of feature sets
        """)
        
        # Add feature categories explanation
        st.subheader("📂 Feature Categories Explained")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Core Features:**
            - Essential functionality
            - Primary value propositions
            - Must-have capabilities
            """)
            
        with col2:
            st.markdown("""
            **Integration Features:**
            - Third-party connections
            - API capabilities
            - Platform integrations
            """)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            **Target Market Features:**
            - Industry-specific tools
            - Role-based functionality
            - Market segment focus
            """)
            
        with col4:
            st.markdown("""
            **Unique Features:**
            - Proprietary capabilities
            - Competitive differentiators
            - Innovation highlights
            """)
    
    # Add actual feature data comparison
    if competitor_data:
        st.subheader("📊 Actual Feature Data Comparison")
        
        feature_comparison = []
        for comp_name, comp_data in competitor_data.items():
            homepage = comp_data.get('homepage', {})
            features = homepage.get('features', [])
            additional_features = comp_data.get('features', [])
            
            all_features = features + (additional_features if additional_features else [])
            
            feature_comparison.append({
                "Company": comp_name,
                "Total Features": len(all_features),
                "Homepage Features": len(features),
                "Additional Features": len(additional_features) if additional_features else 0,
                "Sample Features": ", ".join(all_features[:5]) if all_features else "No features found"
            })
        
        if feature_comparison:
            df_features = pd.DataFrame(feature_comparison)
            st.dataframe(df_features, use_container_width=True, hide_index=True)
            
            # Show detailed features for each company
            st.subheader("🔍 Detailed Features by Company")
            for comp_name, comp_data in competitor_data.items():
                with st.expander(f"View all features for {comp_name}"):
                    homepage = comp_data.get('homepage', {})
                    features = homepage.get('features', [])
                    additional_features = comp_data.get('features', [])
                    
                    if features:
                        st.write("**Homepage Features:**")
                        for feature in features:
                            st.write(f"• {feature}")
                    
                    if additional_features:
                        st.write("**Additional Features:**")
                        for feature in additional_features:
                            st.write(f"• {feature}")
                    
                    if not features and not additional_features:
                        st.write("No features found for this company")
        else:
            st.info("No feature data available for comparison")
        
    else:
        st.info("Feature analysis not available - this may take a moment to generate")

def display_swot_analysis(swot_text, competitor_data):
    """Display comprehensive competitive SWOT analysis with visual elements"""
    st.subheader("🎯 Competitive SWOT Analysis")
    
    if swot_text:
        # Display the AI-generated SWOT analysis
        st.markdown(swot_text)
        
        # Add visual elements for better comparison
        st.subheader("📊 SWOT Comparison Matrix")
        
        # Try to extract SWOT data for visual comparison
        if "COMPETITIVE SWOT MATRIX" in swot_text:
            st.info("💡 Scroll up to see the detailed SWOT comparison matrix above")
        
        # Add SWOT insights
        st.subheader("🔍 Key Strategic Insights")
        st.markdown("""
        - **Market Leader Analysis**: Which company has the strongest overall position?
        - **Threat Assessment**: Which company poses the greatest competitive threat?
        - **Growth Opportunities**: Which company has the best growth potential?
        - **Vulnerability Analysis**: Which company has the most weaknesses to address?
        - **Strategic Recommendations**: What should each company focus on for competitive advantage?
        """)
        
        # Add SWOT explanation
        st.subheader("📋 Understanding SWOT Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Strengths (Internal + Positive):**
            - What does the company do well?
            - What unique resources do they have?
            - What advantages do they have over competitors?
            """)
            
        with col2:
            st.markdown("""
            **Weaknesses (Internal + Negative):**
            - What could the company improve?
            - What resources are they lacking?
            - What puts them at a disadvantage?
            """)
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown("""
            **Opportunities (External + Positive):**
            - What trends could benefit the company?
            - What market gaps could they fill?
            - What partnerships could they form?
            """)
            
        with col4:
            st.markdown("""
            **Threats (External + Negative):**
            - What competitors are doing well?
            - What market changes could hurt them?
            - What external factors pose risks?
            """)
    
    # Add actual competitor data for SWOT context
    if competitor_data:
        st.subheader("📊 Competitor Data for SWOT Context")
        
        swot_context = []
        for comp_name, comp_data in competitor_data.items():
            homepage = comp_data.get('homepage', {})
            about = comp_data.get('about', {})
            
            swot_context.append({
                "Company": comp_name,
                "Title": homepage.get('title', 'N/A'),
                "Headline": homepage.get('headline', 'N/A')[:100] + "..." if len(homepage.get('headline', '')) > 100 else homepage.get('headline', 'N/A'),
                "Description": homepage.get('description', 'N/A')[:150] + "..." if len(homepage.get('description', '')) > 150 else homepage.get('description', 'N/A'),
                "Mission": about.get('mission', 'N/A')[:100] + "..." if len(about.get('mission', '')) > 100 else about.get('mission', 'N/A'),
                "Features Count": len(homepage.get('features', [])),
                "Has Pricing": "✅" if comp_data.get('pricing') else "❌"
            })
        
        if swot_context:
            df_swot = pd.DataFrame(swot_context)
            st.dataframe(df_swot, use_container_width=True, hide_index=True)
            
            st.info("💡 Use this data above to understand each company's strengths and weaknesses for SWOT analysis")
        else:
            st.info("No competitor data available for SWOT context")
        
    else:
        st.info("SWOT analysis not available - this may take a moment to generate")

def display_export_options(company_name, analysis_results):
    """Display export options"""
    st.subheader("📊 Export Competitive Research")
    
    # Create export data
    export_data = {
        'company': company_name,
        'timestamp': datetime.now().isoformat(),
        'overview': analysis_results.get('overview', ''),
        'pricing': analysis_results.get('pricing', ''),
        'features': analysis_results.get('features', ''),
        'swot': analysis_results.get('swot', '')
    }
    
    # Export as JSON
    json_data = json.dumps(export_data, indent=2)
    st.download_button(
        "📥 Download as JSON",
        data=json_data,
        file_name=f"{company_name}_competitive_research.json",
        mime="application/json"
    )
    
    # Export as text
    text_data = f"""
# {company_name} - Competitive Research Report

## Competitive Overview
{analysis_results.get('overview', '')}

## Pricing Comparison
{analysis_results.get('pricing', '')}

## Feature Comparison
{analysis_results.get('features', '')}

## SWOT Analysis
{analysis_results.get('swot', '')}

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    st.download_button(
        "📄 Download as Text",
        data=text_data,
        file_name=f"{company_name}_competitive_research.txt",
        mime="text/plain"
    )

if __name__ == "__main__":
    main()
