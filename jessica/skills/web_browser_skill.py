"""Web browsing skill for fetching and extracting content from websites.

Allows Jessica to:
- Open websites in Chrome browser
- Search the web (DuckDuckGo)
- Fetch and read website content
- Extract information from pages
"""
from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import Optional
import subprocess
import os
import shutil


def can_handle(intent: dict) -> bool:
    """Check if this is a web browsing request."""
    # Check if intent parser already identified this as web_browser
    if intent.get("intent") == "web_browser":
        return True
    
    # Otherwise check keywords in text as fallback
    text = intent.get("text", "").lower()
    
    # Skip if file attachments present
    if "[user attached files" in text or "[attached files" in text:
        return False
    
    web_keywords = [
        "search for", "search online", "search the web", "look up online",
        "browse to", "go to website", "open website", "visit website",
        "what's on", "check website", "find online", "google",
        "look it up", "search it", "web search", "find on the internet",
        "open chrome"
    ]
    
    return any(kw in text for kw in web_keywords)


def _open_in_chrome(url: str) -> str:
    """Open a URL in Chrome browser."""
    try:
        # Ensure URL has protocol
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
        
        # Common Chrome locations on Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe")
        ]
        
        chrome_exe = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_exe = path
                break
        
        # If not found in common locations, try PATH
        if not chrome_exe:
            chrome_exe = shutil.which("chrome")
        
        if chrome_exe:
            # Open Chrome with the URL in a new window
            subprocess.Popen([chrome_exe, "--new-window", url], 
                           shell=False, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return f"🌐 **Opened in Chrome**\n\n{url}"
        
        # Try Edge as fallback
        edge_exe = shutil.which("msedge")
        if edge_exe:
            subprocess.Popen([edge_exe, url], 
                           shell=False,
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return f"🌐 **Opened in Microsoft Edge**\n\n{url}"
        
        # Last resort - use Windows start command
        subprocess.Popen(["cmd", "/c", "start", "", url], 
                       shell=False,
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        return f"🌐 **Opened in default browser**\n\n{url}"
        
    except Exception as e:
        return f"⚠️ Could not open browser: {str(e)}"


def _open_chrome_search(query: str) -> str:
    """Open a Google search in Chrome."""
    search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
    return _open_in_chrome(search_url)


def _fetch_url(url: str) -> str:
    """Fetch content from a URL."""
    try:
        # Use more complete browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Create a session for cookie support
        session = requests.Session()
        session.headers.update(headers)
        
        response = session.get(url, timeout=15, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to extract main content areas first
        main_content = None
        for selector in ['main', 'article', '[role="main"]', '.content', '#content']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup
        
        # Remove script, style, nav, footer elements
        for element in main_content(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
        
        # Get text
        text = main_content.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Get title if available
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""
        
        # Limit to first 2000 characters
        content = text[:2000] + "..." if len(text) > 2000 else text
        
        if title_text:
            return f"**{title_text}**\n\n{content}"
        return content
        
    except requests.RequestException as e:
        error_msg = str(e)
        if "403" in error_msg or "Forbidden" in error_msg:
            return f"⚠️ Website blocked our request (403 Forbidden)\n\nThis usually means the site requires JavaScript or blocks automated access. Try searching for information about this site instead."
        elif "404" in error_msg:
            return "⚠️ Page not found (404)"
        else:
            return f"⚠️ Error accessing site: {error_msg}"


def _search_duckduckgo(query: str) -> str:
    """Search DuckDuckGo and return top results."""
    try:
        # Use DuckDuckGo HTML (no JavaScript required)
        search_url = f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract search results
        results = []
        for result in soup.find_all('div', class_='result')[:5]:  # Top 5 results
            title_elem = result.find('a', class_='result__a')
            snippet_elem = result.find('a', class_='result__snippet')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                url = title_elem.get('href', '')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                
                results.append(f"**{title}**\n{snippet}\n🔗 {url}\n")
        
        if results:
            return "🔍 **Search Results:**\n\n" + "\n".join(results)
        else:
            return "No results found."
            
    except Exception as e:
        return f"Search error: {str(e)}"


def run(intent: dict, context: dict, relevant: list, manager) -> dict:
    """Execute web browsing task."""
    text = intent.get("text", "")
    text_lower = text.lower()
    
    # Check if user wants to OPEN a browser window (not just fetch content)
    wants_visual = any(word in text_lower for word in ["open chrome", "open browser", "launch chrome", "show me", "open in"])
    
    # Check if it's a direct URL request
    if "what's on" in text_lower or "check website" in text_lower or "visit" in text_lower or "open" in text_lower:
        # Try to extract URL
        words = text.split()
        url = None
        for word in words:
            if word.startswith('http://') or word.startswith('https://') or '.' in word:
                url = word.strip('.,;:!?')
                if not url.startswith('http'):
                    url = 'https://' + url
                break
        
        # Common site detection
        if not url:
            if 'openai' in text_lower:
                url = 'https://openai.com'
            elif 'github' in text_lower:
                url = 'https://github.com'
            elif 'python' in text_lower:
                url = 'https://python.org'
        
        if url:
            # If user wants to see it in browser, open Chrome
            if wants_visual or "open chrome" in text_lower:
                print(f"[Web Browser] Opening in Chrome: {url}")
                result = _open_in_chrome(url)
                return {"reply": result}
            
            # Otherwise fetch content
            print(f"[Web Browser] Fetching: {url}")
            content = _fetch_url(url)
            
            # If direct fetch failed with 403, try opening in browser instead
            if "403" in content or "blocked our request" in content:
                print(f"[Web Browser] Direct fetch failed, opening in Chrome instead")
                result = _open_in_chrome(url)
                return {
                    "reply": f"🌐 **Website blocks automated access**\n\nOpening in Chrome instead...\n\n{result}"
                }
            
            return {"reply": f"🌐 **Content from {url}:**\n\n{content}"}
    
    # Check if it's a search request with "open chrome"
    if wants_visual or "search" in text_lower:
        # If they want to open Chrome for search
        if wants_visual:
            query = text
            for prefix in ["open chrome search ", "open chrome ", "search for ", "search online for ", "look up ", "find ", "google ", "search "]:
                if query.lower().startswith(prefix):
                    query = query[len(prefix):]
                    break
            
            print(f"[Web Browser] Opening Chrome search: {query}")
            result = _open_chrome_search(query)
            return {"reply": result}
    
    # Otherwise, it's a DuckDuckGo search (show results in chat)
    query = text
    for prefix in ["search for ", "search online for ", "look up ", "find ", "google ", "search "]:
        if query.lower().startswith(prefix):
            query = query[len(prefix):]
            break
    
    print(f"[Web Browser] Searching: {query}")
    results = _search_duckduckgo(query)
    
    return {"reply": results}

