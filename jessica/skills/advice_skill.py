"""
Life Advice Skill: Etiquette, first aid, and home maintenance guidance.
"""

def can_handle(intent):
    i = intent.get("intent", "")
    text = (intent.get("text", "") or "").lower()
    
    # Skip if this is a file attachment analysis request
    if "[user attached files" in text or "[attached files" in text:
        return False
    
    # Etiquette keywords
    etiquette_keywords = ["etiquette", "proper way", "how to handle", "social", "introduce",
                         "invitation", "thank you", "apology", "manners", "tipping"]
    
    # First aid keywords  
    first_aid_keywords = ["first aid", "what to do if", "emergency", "choking", "burn",
                         "sprain", "injury", "bleeding", "sting", "cut"]
    
    # Home maintenance keywords
    home_keywords = ["how to fix", "repair", "leaky", "clogged", "broken", "not working",
                    "faucet", "toilet", "breaker", "disposal", "drain", "heater"]
    
    # Emotional intelligence keywords
    ei_keywords = ["validate", "empathy", "listen", "understand someone", "feel heard",
                   "emotional", "feeling", "support someone"]
    
    # Conflict resolution keywords
    conflict_keywords = ["conflict", "argument", "fight", "disagree", "difficult conversation",
                        "coworker", "boundaries", "feedback"]
    
    # Decision-making keywords
    decision_keywords = ["should i", "decide", "choice", "prioritize", "eisenhower",
                        "pros and cons", "decision"]
    
    # Financial literacy keywords
    financial_keywords = ["budget", "money", "401k", "ira", "invest", "retirement",
                         "debt", "loan", "compound interest", "saving"]
    
    # Travel planning keywords
    travel_keywords = ["trip", "travel", "itinerary", "destination", "visit",
                      "vacation", "plan a trip"]
    
    # Tech support keywords
    tech_keywords = ["shortcut", "keyboard", "code", "programming", "security",
                    "password", "slow computer", "tech support", "how to fix"]
    
    # Creative thinking keywords
    thinking_keywords = ["six thinking hats", "thinking hats", "first principles",
                        "inversion", "scamper", "5 whys", "creative thinking",
                        "problem solving framework"]
    
    # Storytelling keywords
    story_keywords = ["hero's journey", "story structure", "three act", "character archetype",
                     "analyze story", "analyze movie", "writing", "narrative"]
    
    # Logical fallacies keywords
    fallacy_keywords = ["fallacy", "logical error", "ad hominem", "straw man", "sunk cost",
                       "critique my thinking", "socratic", "cognitive bias"]
    
    # Professional communication keywords
    prof_comm_keywords = ["email", "feedback", "difficult conversation", "professional",
                         "de-escalate", "i statement", "boundary", "workplace"]
    
    # Systems thinking keywords
    systems_keywords = ["5 whys", "root cause", "substitute", "substitution",
                       "systems thinking", "feedback loop"]
    
    # Digital wellness keywords
    digital_keywords = ["media literacy", "verify source", "fake news", "phishing",
                       "digital security", "2fa", "misinformation"]
    
    return (i == "advice" or 
            any(kw in text for kw in etiquette_keywords) or
            any(kw in text for kw in first_aid_keywords) or
            any(kw in text for kw in home_keywords) or
            any(kw in text for kw in ei_keywords) or
            any(kw in text for kw in conflict_keywords) or
            any(kw in text for kw in decision_keywords) or
            any(kw in text for kw in financial_keywords) or
            any(kw in text for kw in travel_keywords) or
            any(kw in text for kw in tech_keywords) or
            any(kw in text for kw in thinking_keywords) or
            any(kw in text for kw in story_keywords) or
            any(kw in text for kw in fallacy_keywords) or
            any(kw in text for kw in prof_comm_keywords) or
            any(kw in text for kw in systems_keywords) or
            any(kw in text for kw in digital_keywords))


def run(intent, context, relevant, manager):
    try:
        from jessica.memory.etiquette_store import EtiquetteStore
        from jessica.memory.first_aid_store import FirstAidStore
        from jessica.memory.home_maintenance_store import HomeMaintenanceStore
        from jessica.memory.emotional_intelligence_store import EmotionalIntelligenceStore
        from jessica.memory.conflict_resolution_store import ConflictResolutionStore
        from jessica.memory.decision_making_store import DecisionMakingStore
        from jessica.memory.financial_literacy_store import FinancialLiteracyStore
        from jessica.memory.travel_planning_store import TravelPlanningStore
        from jessica.memory.tech_support_store import TechSupportStore
        from jessica.memory.thinking_frameworks_store import ThinkingFrameworksStore
        from jessica.memory.storytelling_store import StorytellingStore
        from jessica.memory.logical_fallacies_store import LogicalFallaciesStore
        from jessica.memory.professional_communication_store import ProfessionalCommunicationStore
        from jessica.memory.systems_thinking_store import SystemsThinkingStore
        from jessica.memory.digital_wellness_store import DigitalWellnessStore
        
        text = intent.get("text", "").lower()
        
        # Determine category and search
        results = []
        category = None
        
        # Check for first aid (highest priority for safety)
        first_aid_keywords = ["first aid", "emergency", "choking", "burn", "bleed", "sting", 
                             "sprain", "injury", "cut", "what to do if"]
        if any(kw in text for kw in first_aid_keywords):
            fa = FirstAidStore()
            results = fa.search(text)
            category = "first_aid"
        
        # Check for home maintenance
        elif any(kw in text for kw in ["fix", "repair", "leaky", "clogged", "broken", "not working",
                                         "faucet", "toilet", "breaker", "disposal", "drain", "heater"]):
            hm = HomeMaintenanceStore()
            results = hm.search(text)
            category = "home_maintenance"
        
        # Check for emotional intelligence
        elif any(kw in text for kw in ["validate", "empathy", "listen", "understand", "feel", "emotion"]):
            ei = EmotionalIntelligenceStore()
            results = ei.search(text)
            category = "emotional_intelligence"
        
        # Check for conflict resolution
        elif any(kw in text for kw in ["conflict", "argument", "fight", "disagree", "difficult conversation",
                                         "coworker", "boundaries", "feedback"]):
            cr = ConflictResolutionStore()
            results = cr.search(text)
            category = "conflict_resolution"
        
        # Check for decision-making
        elif any(kw in text for kw in ["should i", "decide", "choice", "prioritize", "eisenhower",
                                         "pros", "cons", "decision"]):
            dm = DecisionMakingStore()
            results = dm.search(text)
            category = "decision_making"
        
        # Check for financial literacy
        elif any(kw in text for kw in ["budget", "money", "401k", "ira", "invest", "retirement",
                                         "debt", "loan", "compound", "saving"]):
            fl = FinancialLiteracyStore()
            results = fl.search(text)
            category = "financial_literacy"
        
        # Check for travel planning
        elif any(kw in text for kw in ["trip", "travel", "itinerary", "destination", "visit",
                                         "vacation", "plan"]):
            tp = TravelPlanningStore()
            results = tp.search(text)
            category = "travel_planning"
        
        # Check for tech support
        elif any(kw in text for kw in ["shortcut", "keyboard", "code", "programming", "security",
                                         "password", "slow", "computer", "tech"]):
            ts = TechSupportStore()
            results = ts.search(text)
            category = "tech_support"
        
        # Check for thinking frameworks
        elif any(kw in text for kw in ["thinking hats", "six hats", "first principles", "inversion",
                                         "scamper", "5 whys", "creative thinking", "problem solving"]):
            tf = ThinkingFrameworksStore()
            results = tf.search(text)
            category = "thinking_frameworks"
        
        # Check for storytelling
        elif any(kw in text for kw in ["hero's journey", "story", "three act", "archetype",
                                         "analyze", "writing", "narrative", "movie", "book"]):
            st = StorytellingStore()
            results = st.search(text)
            category = "storytelling"
        
        # Check for logical fallacies
        elif any(kw in text for kw in ["fallacy", "logical", "ad hominem", "straw man",
                                         "sunk cost", "critique", "socratic", "bias"]):
            lf = LogicalFallaciesStore()
            results = lf.search(text)
            category = "logical_fallacies"
        
        # Check for professional communication
        elif any(kw in text for kw in ["email", "feedback", "conversation", "professional",
                                         "de-escalate", "statement", "boundary", "workplace"]):
            pc = ProfessionalCommunicationStore()
            results = pc.search(text)
            category = "professional_communication"
    
        # Check for systems thinking
        elif any(kw in text for kw in ["5 whys", "root cause", "substitute", "substitution",
                                         "systems", "feedback loop"]):
            sys = SystemsThinkingStore()
            results = sys.search(text)
            category = "systems_thinking"
        
        # Check for digital wellness
        elif any(kw in text for kw in ["media", "verify", "fake news", "phishing",
                                         "digital", "2fa", "misinformation", "source"]):
            dw = DigitalWellnessStore()
            results = dw.search(text)
            category = "digital_wellness"
        
        # Check for etiquette
        else:
            et = EtiquetteStore()
            results = et.search(text)
            category = "etiquette"
        
        # Return results
        if not results:
            return {
                "reply": f"I don't have specific guidance for that yet. Try asking about common etiquette situations, first aid emergencies, or home repairs."
            }
        
        if len(results) == 1:
            item = results[0]
            if category == "first_aid":
                fa = FirstAidStore()
                return {"reply": fa.format_guidance(item)}
            elif category == "home_maintenance":
                hm = HomeMaintenanceStore()
                return {"reply": hm.format_guide(item)}
            elif category == "emotional_intelligence":
                ei = EmotionalIntelligenceStore()
                return {"reply": ei.format_response(results)}
            elif category == "conflict_resolution":
                cr = ConflictResolutionStore()
                return {"reply": cr.format_response(results)}
            elif category == "decision_making":
                dm = DecisionMakingStore()
                return {"reply": dm.format_response(results)}
            elif category == "financial_literacy":
                fl = FinancialLiteracyStore()
                return {"reply": fl.format_response(results)}
            elif category == "travel_planning":
                tp = TravelPlanningStore()
                return {"reply": tp.format_response(results)}
            elif category == "tech_support":
                ts = TechSupportStore()
                return {"reply": ts.format_response(results)}
            elif category == "thinking_frameworks":
                tf = ThinkingFrameworksStore()
                return {"reply": tf.format_response(results)}
            elif category == "storytelling":
                st = StorytellingStore()
                return {"reply": st.format_response(results)}
            elif category == "logical_fallacies":
                lf = LogicalFallaciesStore()
                return {"reply": lf.format_response(results)}
            elif category == "professional_communication":
                pc = ProfessionalCommunicationStore()
                return {"reply": pc.format_response(results)}
            elif category == "systems_thinking":
                sys = SystemsThinkingStore()
                return {"reply": sys.format_response(results)}
            elif category == "digital_wellness":
                dw = DigitalWellnessStore()
                return {"reply": dw.format_response(results)}
            else:
                et = EtiquetteStore()
                return {"reply": et.format_advice(item)}
        
        # Multiple matches
        if category == "first_aid":
            topics = [r["emergency"] for r in results]
            return {
                "reply": f"I found {len(results)} first aid guides:\n• " + "\n• ".join(topics) + "\n\nAsk about a specific one for detailed steps. ⚕️ Remember: Always call 911 for serious emergencies!"
            }
        elif category == "home_maintenance":
            topics = [r["problem"] for r in results]
            return {
                "reply": f"I found {len(results)} maintenance guides:\n• " + "\n• ".join(topics) + "\n\nAsk about a specific issue for troubleshooting steps."
            }
        elif category == "emotional_intelligence":
            ei = EmotionalIntelligenceStore()
            return {"reply": ei.format_response(results)}
        elif category == "conflict_resolution":
            cr = ConflictResolutionStore()
            return {"reply": cr.format_response(results)}
        elif category == "decision_making":
            dm = DecisionMakingStore()
            return {"reply": dm.format_response(results)}
        elif category == "financial_literacy":
            fl = FinancialLiteracyStore()
            return {"reply": fl.format_response(results)}
        elif category == "travel_planning":
            tp = TravelPlanningStore()
            return {"reply": tp.format_response(results)}
        elif category == "tech_support":
            ts = TechSupportStore()
            return {"reply": ts.format_response(results)}
        elif category == "thinking_frameworks":
            tf = ThinkingFrameworksStore()
            return {"reply": tf.format_response(results)}
        elif category == "storytelling":
            st = StorytellingStore()
            return {"reply": st.format_response(results)}
        elif category == "logical_fallacies":
            lf = LogicalFallaciesStore()
            return {"reply": lf.format_response(results)}
        elif category == "professional_communication":
            pc = ProfessionalCommunicationStore()
            return {"reply": pc.format_response(results)}
        elif category == "systems_thinking":
            sys = SystemsThinkingStore()
            return {"reply": sys.format_response(results)}
        elif category == "digital_wellness":
            dw = DigitalWellnessStore()
            return {"reply": dw.format_response(results)}
        else:
            topics = [r["situation"] for r in results]
            return {
                "reply": f"I found {len(results)} etiquette situations:\n• " + "\n• ".join(topics) + "\n\nAsk about a specific situation for guidance."
            }
    except Exception as e:
        import traceback
        print(f"[Advice Skill Error]: {e}")
        traceback.print_exc()
        # If this skill fails, let chat skill handle it
        return {"reply": "I can help with that, but let me provide a general response instead.", "fallback_to_chat": True}
