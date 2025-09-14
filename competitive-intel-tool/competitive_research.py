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
                
                # Step 5: Competitive Analysis
                status_text.text("🤖 Running competitive analysis...")
                progress_bar.progress(80)
                
                competitive_analysis = analyze_competitive_landscape(company_name, target_company_data, competitor_data)
                
                # Step 6: Display results
                status_text.text("📊 Generating competitive report...")
                progress_bar.progress(100)
                
                display_competitive_research_results(company_name, competitive_analysis, competitors)
                
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
    """Discover competitors using multiple search strategies"""
    competitors = []
    
    # Search queries for competitor discovery
    search_queries = [
        f'"{company_name}" competitors alternatives',
        f'"{company_name}" vs competitors comparison',
        f'best alternatives to {company_name}',
        f'companies like {company_name}',
        f'{company_name} competitors list',
        f'{company_name} vs'
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
    """Scrape competitor data"""
    competitor_data = {}
    
    for competitor in competitors[:3]:  # Limit to top 3 competitors
        try:
            data = scrape_company_comprehensive(competitor['url'], competitor['name'])
            competitor_data[competitor['name']] = data
        except:
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
        Analyze the competitive landscape for {company_name}:
        
        CONTENT: {content}
        
        Provide:
        1. What does {company_name} do?
        2. Who are their main competitors?
        3. What are the key differences between them?
        4. What is the market positioning?
        5. What are the competitive advantages/disadvantages?
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
        Create a structured table data for competitive analysis of {company_name}'s competitors:
        
        TARGET COMPANY: {company_name}
        COMPETITORS: {', '.join(competitor_names)}
        
        CONTENT: {content}
        
        For each COMPETITOR only (not the target company), provide a JSON object with these exact fields:
        {{
            "company_name": "Competitor Company Name",
            "target_persona": "Brief description of their target audience (1-2 sentences)",
            "market_positioning": "How they position themselves in the market (1-2 sentences)",
            "tone_messaging": "Messaging tone and style they use (1 sentence)",
            "differentiation": "How they differentiate from {company_name} and other competitors (1-2 sentences)"
        }}
        
        Return as a JSON array with ONLY the competitors, not the target company.
        """,
        
        'pricing': f"""
        Analyze pricing strategies in this competitive landscape:
        
        CONTENT: {content}
        
        Compare pricing models, tiers, and strategies across all companies.
        """,
        
        'features': f"""
        Compare product features and capabilities:
        
        CONTENT: {content}
        
        Identify unique features, common features, and feature gaps.
        """,
        
        'swot': f"""
        Perform competitive SWOT analysis:
        
        CONTENT: {content}
        
        Rate each company's strengths, weaknesses, opportunities, and threats (1-5 scale).
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

def display_competitive_research_results(company_name, analysis_results, competitors):
    """Display competitive research results"""
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Competitive Overview", "💰 Pricing Comparison", "⚡ Feature Comparison", "🎯 SWOT Analysis", "📊 Export"
    ])
    
    with tab1:
        display_competitive_overview(company_name, analysis_results, competitors)
    
    with tab2:
        display_pricing_comparison(analysis_results.get('pricing', ''))
    
    with tab3:
        display_feature_comparison(analysis_results.get('features', ''))
    
    with tab4:
        display_swot_analysis(analysis_results.get('swot', ''))
    
    with tab5:
        display_export_options(company_name, analysis_results)

def display_competitive_overview(company_name, analysis_results, competitors):
    """Display competitive analysis of competitors in structured table format"""
    st.subheader(f"🔍 Competitive Analysis: {company_name}'s Competitors")
    
    # Display basic competitor info first
    st.subheader("🎯 Discovered Competitors & URLs")
    for i, comp in enumerate(competitors, 1):
        st.write(f"{i}. **{comp['name']}** - {comp['url']} (Source: {comp['source']})")
    
    # Create structured table data
    st.subheader("📊 Competitive Analysis Table")
    
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
    
    # Add competitors only (not the target company)
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

def display_pricing_comparison(pricing_text):
    """Display pricing comparison"""
    st.subheader("💰 Competitive Pricing Analysis")
    
    if pricing_text:
        st.markdown(pricing_text)
    else:
        st.info("Pricing analysis not available")

def display_feature_comparison(features_text):
    """Display feature comparison"""
    st.subheader("⚡ Competitive Feature Analysis")
    
    if features_text:
        st.markdown(features_text)
    else:
        st.info("Feature analysis not available")

def display_swot_analysis(swot_text):
    """Display SWOT analysis"""
    st.subheader("🎯 Competitive SWOT Analysis")
    
    if swot_text:
        st.markdown(swot_text)
    else:
        st.info("SWOT analysis not available")

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
