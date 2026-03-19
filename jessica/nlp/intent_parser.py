def parse_intent(text: str) -> dict:
    """
    Small rule-based system.
    Later you can upgrade this to LLM-based classification.
    """
    t = (text or "").lower().strip()

    # System test
    if "system test" in t or t == "test":
        return {"intent": "system_test", "text": text}

    # Reasoning/Analysis/Technical questions - route to chat for intelligent response
    # Keywords that indicate they want analysis/reasoning, not just advice
    reasoning_keywords = ["explain", "reasoning", "step-by-step", "how did you", "why", "walk me through",
                         "break it down", "show your work", "think through", "analyze", "compare",
                         "algorithm", "search", "binary", "linear", "parallel processing", "thread",
                         "optimization", "complexity", "data structure", "time complexity", "space complexity",
                         "programming concept", "programming logic", "programming method"]
    if any(kw in t for kw in reasoning_keywords):
        return {"intent": "chat", "text": text}

    # System monitoring (time, CPU, memory, disk, processes, uptime)
    # But NOT for file attachment analysis
    monitor_keywords = ["what is the time", "what time", "current time", "what's the time", "tell me the time",
                        "cpu", "processor", "memory usage", "ram usage", "disk space", "storage space", 
                        "running processes", "system uptime", "how long has your computer been running"]
    
    # Skip monitor if this is about attached files
    if "[user attached files" not in t and any(kw in t for kw in monitor_keywords):
        return {"intent": "monitor", "text": text}

    # Chess (strict: only if explicitly asking to play or it's clearly a move notation)
    is_explicit_chess_request = (
        "play chess" in t and ("let's" in t or "want to" in t or t.startswith("play chess") or "me" in t and t.index("play chess") > t.index("me")) or  # "play chess with me" style
        t.startswith("new chess") or
        t.startswith("chess game") or
        (t.startswith(("e4", "e2e4", "d4", "d2d4", "nf3", "move ", "castle")) and len(t) < 20)  # Standard move notation
    )
    
    if is_explicit_chess_request:
        return {"intent": "play_chess", "text": text}

    # Recipes
    if ("recipe for" in t or "how to make" in t or "how to cook" in t or
        any(word in t for word in ["breakfast recipe", "dinner recipe", "dessert recipe", "list recipes"])):
        return {"intent": "recipe", "text": text}

    # Web browsing (search online, look up, etc.)
    # Check this BEFORE open_app to catch "open chrome google.com" patterns
    web_keywords = ["search for", "search online", "search the web", "look up online",
                    "browse to", "go to website", "open website", "visit website",
                    "what's on", "check website", "find online", "google",
                    "look it up", "search it", "web search"]
    
    # Also catch "open chrome [url]" or "open chrome and go to [url]" patterns
    if ("open chrome" in t or "launch chrome" in t) and ("go to" in t or "." in t or "search" in t):
        return {"intent": "web_browser", "text": text}
    
    if any(kw in t for kw in web_keywords):
        return {"intent": "web_browser", "text": text}

    # Life advice (etiquette, first aid, home maintenance, emotional intelligence, conflict, decision-making, finance, travel, tech, thinking, storytelling, logical fallacies, professional communication, systems thinking, digital wellness)
    advice_keywords = ["etiquette", "proper way", "introduce", "invitation", "thank you", 
                      "apology", "manners", "tipping", "first aid", "emergency", "choking",
                      "burn", "sprain", "injury", "bleeding", "how to fix", "repair", 
                      "leaky", "clogged", "broken", "not working", "faucet", "toilet",
                      "breaker", "disposal", "drain", "heater", "validate", "empathy",
                      "listen", "understand someone", "emotional", "conflict", "argument",
                      "disagree", "difficult conversation", "should i", "decide", "choice",
                      "prioritize", "eisenhower", "pros and cons", "budget", "money",
                      "401k", "ira", "invest", "retirement", "debt", "compound interest",
                      "trip", "travel", "itinerary", "destination", "vacation",
                      "keyboard shortcut", "security best practice", "password", "tech support",
                      "thinking hats", "first principles", "hero's journey", "story structure",
                      "analyze story", "analyze movie", "writing", "fallacy", "logical error",
                      "ad hominem", "straw man", "sunk cost", "socratic", "cognitive bias",
                      "email template", "feedback framework", "professional phrase", "i statement", "boundary",
                      "workplace etiquette", "5 whys", "root cause analysis", "cooking substitute",
                      "media literacy", "verify source", "news source", "fake news", "phishing email",
                      "digital security", "2fa", "misinformation"]
    # Don't route reasoning/technical questions to advice
    if any(kw in t for kw in advice_keywords) and not any(kw in t for kw in reasoning_keywords):
        return {"intent": "advice", "text": text}

    # Screen monitoring / vision
    if any(kw in t for kw in ["screenshot", "see my screen", "what am i doing", "look at my screen", "capture screen", "show you my screen"]):
        return {"intent": "screen_monitor", "text": text}

    # Webcam / camera
    if any(kw in t for kw in ["camera", "webcam", "take a photo", "take a picture", "show you via camera", "look through camera", "see me"]):
        return {"intent": "webcam", "text": text}

    # Open file/app (check BEFORE spreadsheet detection)
    app_keywords = ["excel", "word", "notepad", "terminal", "calculator", "powershell", "cmd", "outlook", "chrome", "edge", "firefox", "spotify", "slack", "teams", "paint", "mspaint"]
    
    # Check if user is asking to open/launch an app (natural language)
    import os
    if any(trigger in t for trigger in ["open", "launch", "start"]):
        # First check if any known app keyword is mentioned
        for app in app_keywords:
            if app in t:
                # Make sure it's not part of a spreadsheet operation
                if not any(x in t for x in ["edit", "read", "write", "update", "cell", "data", "formula", "active", "current", "file", ".xlsx"]):
                    return {"intent": "open_app", "text": text, "app": app}
        
        # If no known app, try to extract from "open X" or "launch X" pattern
        for trigger in ["open ", "launch ", "start "]:
            if trigger in t:
                idx = t.index(trigger) + len(trigger)
                target = t[idx:].strip()
                # Clean up common words
                for filler in [" for me", " please", " now", " a blank", " a new", " blank", " new", " worksheet", " workbook", " document", " doc", " the", " a ", "a "]:
                    target = target.replace(filler, "")
                target = target.strip().rstrip("?.")
                
                if target:
                    # Extract just the first word if multiple
                    app_name = target.split()[0] if target else target
                    
                    # If it has a path separator or a file extension, treat as file
                    has_ext = "." in os.path.basename(app_name)
                    has_path = ("/" in app_name) or ("\\" in app_name) or (":" in app_name)
                    if not has_ext and not has_path and app_name:
                        return {"intent": "open_app", "text": text, "app": app_name}
                    # Otherwise, treat as file
                    return {"intent": "open_file", "text": text, "target": target}

    # Spreadsheet automation (live Excel or file-based)
    # Only trigger if it's not just opening the app (no "open"/"launch" at start)
    if any(kw in t for kw in ["spreadsheet", "csv", "edit cell", "read csv", "write csv", "update excel", ".xlsx", ".csv", "active excel", "current sheet", "current spreadsheet", "read cell", "get cell", "what's in"]):
        return {"intent": "spreadsheet", "text": text}
    # Advanced excel operations (but not simple "open")
    if "excel" in t and any(x in t for x in ["edit", "read", "write", "update", "cell", "data", "formula", "sheet", "active", "current"]):
        return {"intent": "spreadsheet", "text": text}

    # Email
    if "draft email" in t:
        return {"intent": "draft_email", "text": text}
    if "send email" in t:
        return {"intent": "send_email", "text": text}

    # Programming (enhanced skill with dependency/API management and autonomous model downloading)
    programming_triggers = [
        "write code", "generate code", "create function", "create class",
        "python function", "javascript function", "bug fix", "refactor",
        "install", "dependency", "package", "requirements", "pip install",
        "openai", "anthropic", "api key", "setup api", "api resource",
        "create file", "write file", "generate file", "new file",
        "project structure", "analyze project", "workspace",
        "model", "download model", "huggingface", "transformer", "llm",
        "text generation", "image generation", "sentiment analysis",
        "summarize", "translate", "transcribe", "speech", "audio",
        "```", "function", "class", "module", "script", "app",
    ]
    if any(k in t for k in programming_triggers):
        return {"intent": "programming", "text": text}

    # Chat fallback
    return {"intent": "chat", "text": text}
