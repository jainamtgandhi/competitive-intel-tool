import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import json
import time
import re
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="🧠 Personal CI Tool", 
    page_icon="🧠", 
    layout="wide"
)

# Sidebar for API keys
with st.sidebar:
    st.title("🧠 Personal CI Tool")
    st.caption("Your daily competitive intelligence assistant")
    
    # API Key inputs
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    serpapi_key = st.text_input("SerpAPI Key (250 free searches)", type="password", 
                                value="ce79da0c5ca2cf7f2502748f3c5c9a3cf1204d920a83638073b81f7d70263028")
    google_api_key = st.text_input("Google Search API Key (100/day free)", type="password",
                                   value="AIzaSyA28027DgQk9f64vNpZrDpGIfwADn6kWoU")
    google_cse_id = st.text_input("Google Custom Search Engine ID", type="password")
    
    # Analysis settings
    st.subheader("⚙️ Settings")
    analysis_depth = st.selectbox("Analysis Depth", ["Quick (2-3 min)", "Comprehensive (5-7 min)"])
    
    # Set API keys
    if openai_api_key:
        openai.api_key = openai_api_key
        st.success("✅ OpenAI API Ready")
    
    if serpapi_key:
        st.success("✅ SerpAPI Ready (250 free searches)")
    
    if google_api_key:
        st.success("✅ Google Search API Ready (100/day free)")
    
    if google_api_key and google_cse_id:
        st.success("✅ Google Custom Search Ready")
        st.caption("Using free tier for competitor discovery")
    
    # Usage tracking
    st.subheader("📊 Usage Tracking")
    st.caption("Monitor your free tier limits")
    
    if st.button("🔄 Check API Usage"):
        check_api_usage(serpapi_key, google_api_key)

def main():
    st.title("🧠 Personal Competitive Intelligence Tool")
    st.caption("Enter a company name and URL to get comprehensive competitive analysis")
    
    # Input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        company_name = st.text_input(
            "Company Name", 
            placeholder="e.g., SonarSource, Datadog, Stripe"
        )
    
    with col2:
        company_url = st.text_input(
            "Company Website URL", 
            placeholder="https://www.example.com"
        )
    
    # Analysis button
    if st.button("🚀 Analyze Company", type="primary"):
        if not company_name or not company_url:
            st.error("Please enter both company name and URL")
            return
        
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar")
            return
        
        # Run analysis
        with st.spinner("🔍 Analyzing company... This may take 3-5 minutes"):
            try:
                # Step 1: Discover competitors and URLs
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔍 Discovering competitors...")
                progress_bar.progress(10)
                
                competitors = discover_competitors(company_name)
                
                # Step 2: Scrape company data
                status_text.text("📄 Scraping company website...")
                progress_bar.progress(30)
                
                company_data = scrape_company_comprehensive(company_url, company_name)
                
                # Step 3: Scrape competitor data
                status_text.text("📊 Analyzing competitors...")
                progress_bar.progress(60)
                
                competitor_data = scrape_competitors(competitors)
                
                # Step 4: AI Analysis
                status_text.text("🤖 Running AI analysis...")
                progress_bar.progress(80)
                
                analysis_results = analyze_with_gpt(company_name, company_data, competitor_data)
                
                # Step 5: Display results
                status_text.text("📊 Generating report...")
                progress_bar.progress(100)
                
                display_comprehensive_results(company_name, analysis_results)
                
                status_text.text("✅ Analysis complete!")
                
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                st.exception(e)

def discover_competitors(company_name):
    """Discover competitors using hybrid approach: Google Custom Search + SerpAPI"""
    competitors = []
    
    # Strategy: Use Google Custom Search first (free), then SerpAPI if needed
    
    # Step 1: Try Google Custom Search API (free tier - 100 queries/day)
    if google_api_key and google_cse_id:
        try:
            competitors.extend(discover_with_google_search(company_name, google_api_key, google_cse_id))
            if len(competitors) >= 3:  # If we found enough with Google, skip SerpAPI
                return competitors[:5]
        except Exception as e:
            st.warning(f"Google Custom Search failed: {e}")
    
    # Step 2: Use SerpAPI for enhanced discovery (250 free searches)
    if serpapi_key and len(competitors) < 3:
        try:
            serpapi_competitors = discover_with_serpapi(company_name, serpapi_key)
            competitors.extend(serpapi_competitors)
        except Exception as e:
            st.warning(f"SerpAPI failed: {e}")
    
    # Step 3: Fallback if both fail
    if not competitors:
        return [
            {"name": "Competitor 1", "url": "https://example1.com", "source": "fallback"},
            {"name": "Competitor 2", "url": "https://example2.com", "source": "fallback"},
            {"name": "Competitor 3", "url": "https://example3.com", "source": "fallback"}
        ]
    
    # Remove duplicates and return top competitors
    unique_competitors = []
    seen_names = set()
    
    for comp in competitors:
        if comp['name'] not in seen_names and len(unique_competitors) < 5:
            unique_competitors.append(comp)
            seen_names.add(comp['name'])
    
    return unique_competitors

def discover_with_google_search(company_name, api_key, cse_id):
    """Discover competitors using Google Custom Search API (free tier)"""
    competitors = []
    
    # Use fewer, more targeted queries to stay within free limits
    search_queries = [
        f'"{company_name}" competitors',
        f'"{company_name}" alternatives',
        f'"{company_name}" vs'
    ]
    
    for query in search_queries:
        try:
            params = {
                'key': api_key,
                'cx': cse_id,
                'q': query,
                'num': 5  # Limit results to stay within free tier
            }
            
            response = requests.get('https://www.googleapis.com/customsearch/v1', params=params, timeout=10)
            results = response.json()
            
            if 'items' in results:
                for item in results['items']:
                    title = item.get('title', '')
                    url = item.get('link', '')
                    
                    # Extract competitor name from title
                    if company_name.lower() not in title.lower() and url:
                        competitor_name = extract_company_name_from_title(title)
                        if competitor_name and competitor_name != company_name:
                            competitors.append({
                                "name": competitor_name,
                                "url": url,
                                "source": "google_search"
                            })
        
        except Exception as e:
            continue
    
    return competitors

def discover_with_serpapi(company_name, api_key):
    """Discover competitors using SerpAPI (250 free searches)"""
    competitors = []
    
    # Use SerpAPI for more comprehensive search (but limit queries)
    search_queries = [
        f'"{company_name}" competitors alternatives',
        f'"{company_name}" vs competitors'
    ]
    
    for query in search_queries:
        try:
            params = {
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "num": 5  # Limit to stay within free tier
            }
            
            response = requests.get("https://serpapi.com/search", params=params, timeout=10)
            results = response.json()
            
            # Extract competitors from organic results
            if 'organic_results' in results:
                for result in results['organic_results'][:3]:  # Top 3 results
                    title = result.get('title', '')
                    url = result.get('link', '')
                    
                    if company_name.lower() not in title.lower() and url:
                        competitor_name = extract_company_name_from_title(title)
                        if competitor_name and competitor_name != company_name:
                            competitors.append({
                                "name": competitor_name,
                                "url": url,
                                "source": "serpapi"
                            })
            
            # Extract from People Also Ask
            if 'people_also_ask' in results:
                for paa in results['people_also_ask'][:2]:  # Limit PAA results
                    question = paa.get('question', '')
                    if 'vs' in question.lower():
                        potential_competitors = extract_competitors_from_question(question, company_name)
                        competitors.extend(potential_competitors)
        
        except Exception as e:
            continue
    
    return competitors

def extract_company_name_from_title(title):
    """Extract company name from search result title"""
    # Remove common words and extract company name
    title = title.replace(' - ', ' ').replace(' | ', ' ').replace(' vs ', ' ')
    
    # Split and take the first meaningful part
    words = title.split()
    if words:
        # Take first 2-3 words as company name
        company_name = ' '.join(words[:2])
        return company_name.strip()
    
    return ""

def extract_competitors_from_question(question, company_name):
    """Extract competitor names from People Also Ask questions"""
    competitors = []
    
    # Look for patterns like "Company A vs Company B"
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
        # Get main page
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract content
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
    
    # Look for feature lists
    feature_elements = soup.find_all(['li', 'div'], class_=re.compile(r'feature|benefit|capability'))
    
    for element in feature_elements[:10]:  # Limit to 10 features
        text = element.get_text(strip=True)
        if text and len(text) < 100:  # Reasonable feature description length
            features.append(text)
    
    return features

def extract_pricing_from_page(soup):
    """Extract pricing information from pricing page"""
    pricing_tiers = []
    
    # Look for pricing tables
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
    
    # Look for feature sections
    feature_elements = soup.find_all(['div', 'li'], class_=re.compile(r'feature|capability|benefit'))
    
    for element in feature_elements:
        text = element.get_text(strip=True)
        if text and len(text) < 150:
            features.append(text)
    
    return features[:20] if features else None  # Limit to 20 features

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

def scrape_competitors(competitors):
    """Scrape competitor data (simplified for MVP)"""
    competitor_data = {}
    
    for competitor in competitors[:3]:  # Limit to top 3 competitors
        try:
            data = scrape_company_comprehensive(competitor['url'], competitor['name'])
            competitor_data[competitor['name']] = data
        except:
            continue
    
    return competitor_data

def analyze_with_gpt(company_name, company_data, competitor_data):
    """Analyze data with GPT-4"""
    
    # Prepare content for analysis
    content = prepare_content_for_analysis(company_name, company_data, competitor_data)
    
    # Company Overview Analysis
    overview_prompt = f"""
    Act as a Competitive Intelligence expert. Analyze the following company content:
    
    COMPANY: {company_name}
    CONTENT: {content}
    
    Provide a comprehensive analysis including:
    
    1. What does this company do?
    2. Who are their target customers?
    3. What are their main value propositions?
    4. What is their messaging tone and style?
    5. What product features do they emphasize?
    6. What is their pricing model?
    7. What go-to-market channels do they use?
    8. Who are their main competitors?
    9. How do they differentiate from competitors?
    
    Format your response as a structured analysis with clear sections.
    """
    
    # Pricing Analysis
    pricing_prompt = f"""
    Extract and analyze pricing information from this content:
    {content}
    
    Structure the pricing analysis with:
    - Pricing tiers and names
    - Price points and billing periods
    - Target market for each tier
    - Pricing strategy insights
    """
    
    # Feature Analysis
    feature_prompt = f"""
    Extract and categorize features from this content:
    {content}
    
    Organize features by categories such as:
    - Core Features
    - Integration Capabilities
    - Target Market Features
    - Unique/Differentiating Features
    """
    
    # SWOT Analysis
    swot_prompt = f"""
    Perform a SWOT analysis based on this content:
    {content}
    
    Rate each factor 1-5 and provide evidence:
    - Strengths (5 = Very Strong)
    - Weaknesses (5 = Major Weakness)  
    - Opportunities (5 = Major Opportunity)
    - Threats (5 = Major Threat)
    """
    
    try:
        # Run GPT analysis
        analyses = {
            'overview': get_gpt_response(overview_prompt),
            'pricing': get_gpt_response(pricing_prompt),
            'features': get_gpt_response(feature_prompt),
            'swot': get_gpt_response(swot_prompt)
        }
        
        return analyses
        
    except Exception as e:
        return {"error": f"GPT analysis failed: {str(e)}"}

def get_gpt_response(prompt):
    """Get response from GPT-4"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {str(e)}"

def prepare_content_for_analysis(company_name, company_data, competitor_data):
    """Prepare content for GPT analysis"""
    content = f"COMPANY: {company_name}\n\n"
    
    # Add company data
    if 'homepage' in company_data:
        content += f"HOMEPAGE: {company_data['homepage']}\n\n"
    
    if 'pricing' in company_data and company_data['pricing']:
        content += f"PRICING: {company_data['pricing']}\n\n"
    
    if 'features' in company_data and company_data['features']:
        content += f"FEATURES: {company_data['features']}\n\n"
    
    if 'about' in company_data and company_data['about']:
        content += f"ABOUT: {company_data['about']}\n\n"
    
    # Add competitor data
    if competitor_data:
        content += "COMPETITORS:\n"
        for competitor_name, competitor_info in competitor_data.items():
            content += f"{competitor_name}: {competitor_info}\n\n"
    
    return content

def display_comprehensive_results(company_name, analysis_results):
    """Display comprehensive analysis results"""
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Overview", "💰 Pricing", "⚡ Features", "🎯 SWOT", "📊 Export"
    ])
    
    with tab1:
        display_overview(company_name, analysis_results.get('overview', ''))
    
    with tab2:
        display_pricing_analysis(analysis_results.get('pricing', ''))
    
    with tab3:
        display_feature_analysis(analysis_results.get('features', ''))
    
    with tab4:
        display_swot_analysis(analysis_results.get('swot', ''))
    
    with tab5:
        display_export_options(company_name, analysis_results)

def display_overview(company_name, overview_text):
    """Display company overview"""
    st.subheader(f"🏢 {company_name} - Company Overview")
    
    if overview_text:
        st.markdown(overview_text)
    else:
        st.info("Overview analysis not available")

def display_pricing_analysis(pricing_text):
    """Display pricing analysis"""
    st.subheader("💰 Pricing Analysis")
    
    if pricing_text:
        st.markdown(pricing_text)
    else:
        st.info("Pricing analysis not available")

def display_feature_analysis(features_text):
    """Display feature analysis"""
    st.subheader("⚡ Feature Analysis")
    
    if features_text:
        st.markdown(features_text)
    else:
        st.info("Feature analysis not available")

def display_swot_analysis(swot_text):
    """Display SWOT analysis"""
    st.subheader("🎯 SWOT Analysis")
    
    if swot_text:
        st.markdown(swot_text)
    else:
        st.info("SWOT analysis not available")

def display_export_options(company_name, analysis_results):
    """Display export options"""
    st.subheader("📊 Export Analysis")
    
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
        file_name=f"{company_name}_analysis.json",
        mime="application/json"
    )
    
    # Export as text
    text_data = f"""
# {company_name} - Competitive Intelligence Analysis

## Overview
{analysis_results.get('overview', '')}

## Pricing Analysis
{analysis_results.get('pricing', '')}

## Feature Analysis
{analysis_results.get('features', '')}

## SWOT Analysis
{analysis_results.get('swot', '')}

---
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    st.download_button(
        "📄 Download as Text",
        data=text_data,
        file_name=f"{company_name}_analysis.txt",
        mime="text/plain"
    )

def check_api_usage(serpapi_key, google_api_key):
    """Check API usage for free tier monitoring"""
    
    # Check SerpAPI usage
    if serpapi_key:
        try:
            params = {
                "api_key": serpapi_key,
                "engine": "google",
                "q": "test"  # Minimal query just to check API
            }
            response = requests.get("https://serpapi.com/account", params={"api_key": serpapi_key}, timeout=5)
            if response.status_code == 200:
                st.success("✅ SerpAPI: Active (check dashboard for usage)")
            else:
                st.error("❌ SerpAPI: Check your API key")
        except Exception as e:
            st.warning(f"⚠️ SerpAPI: Could not check usage - {e}")
    
    # Check Google API usage
    if google_api_key:
        try:
            params = {
                'key': google_api_key,
                'cx': 'test',  # Just to test API key
                'q': 'test'
            }
            response = requests.get('https://www.googleapis.com/customsearch/v1', params=params, timeout=5)
            if response.status_code == 200:
                st.success("✅ Google Search API: Active (100 free queries/day)")
            elif response.status_code == 403:
                st.error("❌ Google Search API: Quota exceeded or invalid key")
            else:
                st.warning(f"⚠️ Google Search API: Status {response.status_code}")
        except Exception as e:
            st.warning(f"⚠️ Google Search API: Could not check - {e}")

if __name__ == "__main__":
    main()
