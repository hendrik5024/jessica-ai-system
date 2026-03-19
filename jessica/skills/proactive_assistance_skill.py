"""
Proactive Assistance Skill - Handles frustration-based interventions.

Provides research, alternative approaches, and documentation lookup.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional

from jessica.skills.base_skill import BaseSkill

logger = logging.getLogger("jessica.proactive_assistance")


class ProactiveAssistanceSkill(BaseSkill):
    """
    Handles proactive assistance when frustration is detected.
    
    Offers:
    - Documentation research
    - Alternative logic approaches
    - Error explanation
    - Workflow suggestions
    """
    
    def __init__(self):
        super().__init__()
        self.name = "ProactiveAssistance"
    
    def handle(self, query: str, context: Dict) -> Dict:
        """
        Handle proactive assistance request.
        
        Context should include:
        - frustration_context: Type of frustration (file_reopen, undo, error, etc.)
        - details: Specific details (file name, error message, etc.)
        - user_response: User's response to assistance offer
        """
        frustration_context = context.get('frustration_context', '')
        details = context.get('details', '')
        user_response = query.lower()
        
        # User declined help
        if any(word in user_response for word in ['no', 'skip', 'later', 'ignore']):
            return {
                'success': True,
                'message': "No problem! I'm here if you need me.",
                'action': 'declined'
            }
        
        # User accepted help - provide suggestions
        suggestions = self._generate_suggestions(frustration_context, details, user_response)
        
        return {
            'success': True,
            'message': suggestions['message'],
            'suggestions': suggestions['options'],
            'action': 'assistance_provided'
        }
    
    def _generate_suggestions(self, frustration_type: str, details: str, query: str) -> Dict:
        """Generate context-specific assistance suggestions"""
        
        if 'file' in frustration_type:
            return self._file_reopen_assistance(details, query)
        
        elif 'undo' in frustration_type:
            return self._undo_assistance(query)
        
        elif 'error' in frustration_type:
            return self._error_assistance(details, query)
        
        elif 'switch' in frustration_type:
            return self._switching_assistance(query)
        
        else:
            return self._general_assistance(query)
    
    def _file_reopen_assistance(self, file_path: str, query: str) -> Dict:
        """Assistance for repeated file reopening"""
        message = f"I can help with this file. What would you like me to do?"
        
        options = []
        
        # Check if user wants documentation
        if any(word in query for word in ['doc', 'documentation', 'reference', 'api']):
            options.append({
                'type': 'documentation',
                'action': f"Search documentation related to {file_path}",
                'priority': 'high'
            })
        
        # Check if user wants debugging help
        if any(word in query for word in ['debug', 'error', 'fix', 'problem', 'issue']):
            options.append({
                'type': 'debug',
                'action': f"Analyze {file_path} for potential issues",
                'priority': 'high'
            })
        
        # Check if user wants refactoring suggestions
        if any(word in query for word in ['refactor', 'improve', 'better', 'approach']):
            options.append({
                'type': 'refactor',
                'action': f"Suggest alternative approaches for {file_path}",
                'priority': 'medium'
            })
        
        # Default options if no specific intent
        if not options:
            options = [
                {'type': 'documentation', 'action': 'Search related documentation', 'priority': 'high'},
                {'type': 'debug', 'action': 'Analyze code for issues', 'priority': 'high'},
                {'type': 'explain', 'action': 'Explain current code structure', 'priority': 'medium'}
            ]
        
        return {'message': message, 'options': options}
    
    def _undo_assistance(self, query: str) -> Dict:
        """Assistance for rapid undo sequences"""
        message = "It looks like we're iterating on something that's not working. Let me help."
        
        options = [
            {
                'type': 'alternative',
                'action': 'Suggest a different logic approach',
                'priority': 'high'
            },
            {
                'type': 'step_back',
                'action': 'Review the overall goal and break it down',
                'priority': 'high'
            },
            {
                'type': 'research',
                'action': 'Search for examples of this pattern',
                'priority': 'medium'
            }
        ]
        
        return {'message': message, 'options': options}
    
    def _error_assistance(self, error_message: str, query: str) -> Dict:
        """Assistance for repeated errors"""
        message = f"Let's tackle this error together: '{error_message[:80]}...'"
        
        options = [
            {
                'type': 'explain',
                'action': 'Explain what this error means',
                'priority': 'high'
            },
            {
                'type': 'fix',
                'action': 'Suggest specific fixes for this error',
                'priority': 'high'
            },
            {
                'type': 'research',
                'action': 'Search Stack Overflow and docs for solutions',
                'priority': 'medium'
            }
        ]
        
        return {'message': message, 'options': options}
    
    def _switching_assistance(self, query: str) -> Dict:
        """Assistance for rapid window switching"""
        message = "I noticed rapid context switching. Looking for something specific?"
        
        options = [
            {
                'type': 'search',
                'action': 'Help search files or documentation',
                'priority': 'high'
            },
            {
                'type': 'organize',
                'action': 'Suggest workflow organization',
                'priority': 'medium'
            },
            {
                'type': 'focus',
                'action': 'Help prioritize next steps',
                'priority': 'medium'
            }
        ]
        
        return {'message': message, 'options': options}
    
    def _general_assistance(self, query: str) -> Dict:
        """General assistance fallback"""
        message = "How can I help you get unstuck?"
        
        options = [
            {
                'type': 'documentation',
                'action': 'Search documentation',
                'priority': 'high'
            },
            {
                'type': 'alternative',
                'action': 'Suggest alternative approach',
                'priority': 'high'
            },
            {
                'type': 'explain',
                'action': 'Explain current context',
                'priority': 'medium'
            }
        ]
        
        return {'message': message, 'options': options}
    
    def get_frustration_interrupt_message(self, frustration_context: str, details: str = "") -> str:
        """
        Generate voice/notification interrupt message based on context.
        
        This is the initial message Jessica says when frustration is detected.
        """
        messages = {
            'file_reopen': [
                f"I noticed we've been reopening this file multiple times. Would you like me to help troubleshoot or find related documentation?",
                f"Hey, I see you're working on this file repeatedly. Want me to take a look and suggest improvements?"
            ],
            'undo': [
                "I noticed we've been undoing a lot. Would you like me to suggest a different logic approach?",
                "Looks like we're iterating on something tricky. Want me to help think through this differently?"
            ],
            'error': [
                f"This error keeps appearing: '{details[:60]}...' Would you like me to research solutions or explain what's happening?",
                f"I've noticed this error {details}. Let me help find a fix or workaround."
            ],
            'rapid_switch': [
                "I noticed rapid window switching. Are you searching for something? I can help.",
                "You're switching contexts a lot. Looking for something specific? Let me assist."
            ]
        }
        
        # Extract base context type (remove prefixes like 'file:' or 'error:')
        base_context = frustration_context.split(':')[0]
        
        # Get appropriate messages
        context_messages = messages.get(base_context, [
            "I noticed we've been stuck on this for a bit. Would you like me to research the documentation or try a different logic approach?"
        ])
        
        # Return first message (could randomize in future)
        return context_messages[0]


# Singleton instance
_assistance_skill = None


def get_proactive_assistance_skill() -> ProactiveAssistanceSkill:
    """Get or create proactive assistance skill singleton"""
    global _assistance_skill
    if _assistance_skill is None:
        _assistance_skill = ProactiveAssistanceSkill()
    return _assistance_skill
