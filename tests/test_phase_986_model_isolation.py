"""
Tests for Phase 98.6: Model Output Sanitizer

Validates that model identity claims are removed and output
becomes pure knowledge.
"""

import pytest
from jessica.routing.model_output_sanitizer import ModelOutputSanitizer


class TestHardBlocks:
    """Test hard-blocking of contaminated output"""

    def test_blocks_phi_identity(self):
        """Should block any mention of being Phi"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("I am Phi") is True
        assert sanitizer.should_discard("I'm Phi") is True
        assert sanitizer.should_discard("My name is Phi") is True

    def test_blocks_alice_assignment(self):
        """Should block 'Your name is Alice' type statements"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("Your name is Alice") is True
        assert sanitizer.should_discard("Your name is Alice Johnson") is True

    def test_blocks_ai_assistant_claim(self):
        """Should block 'I am an assistant' type statements"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("I am an assistant") is True
        assert sanitizer.should_discard("I'm an AI assistant") is True

    def test_blocks_as_an_ai(self):
        """Should block 'As an AI' opening"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("As an AI, I believe...") is True

    def test_allows_factual_output(self):
        """Should allow pure factual output"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("Paris is the capital of France") is False
        assert sanitizer.should_discard("The Earth revolves around the Sun") is False


class TestBannedPhraseRemoval:
    """Test removal of banned phrases"""

    def test_remove_i_am_phi(self):
        """Remove 'I am Phi' from middle of text"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I am Phi, and Paris is beautiful."
        cleaned = sanitizer.sanitize(text)
        
        assert "phi" not in cleaned.lower()
        assert "paris" in cleaned.lower()

    def test_remove_as_an_ai(self):
        """Remove 'As an AI' prefix"""
        sanitizer = ModelOutputSanitizer()
        
        text = "As an AI, I believe Paris is the capital of France."
        cleaned = sanitizer.sanitize(text)
        
        assert "as an ai" not in cleaned.lower()
        assert "paris" in cleaned.lower()
        assert "capital" in cleaned.lower()

    def test_remove_knowledge_cutoff(self):
        """Remove references to knowledge cutoff"""
        sanitizer = ModelOutputSanitizer()
        
        text = "My knowledge cutoff is April 2024. Paris is the capital of France."
        cleaned = sanitizer.sanitize(text)
        
        assert "knowledge cutoff" not in cleaned.lower()
        assert "april" not in cleaned.lower() or "2024" not in cleaned
        assert "paris" in cleaned.lower()

    def test_remove_training_references(self):
        """Remove references to training"""
        sanitizer = ModelOutputSanitizer()
        
        text = "According to my training, Paris is the capital of France."
        cleaned = sanitizer.sanitize(text)
        
        assert "training" not in cleaned.lower()
        assert "paris" in cleaned.lower()

    def test_remove_assistant_claims(self):
        """Remove assistant identity claims"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I'm a helpful AI assistant. Paris is the capital of France."
        cleaned = sanitizer.sanitize(text)
        
        assert "assistant" not in cleaned.lower()
        assert "paris" in cleaned.lower()

    def test_remove_openai_reference(self):
        """Remove OpenAI references"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I'm OpenAI's assistant. Paris is the capital."
        cleaned = sanitizer.sanitize(text)
        
        assert "openai" not in cleaned.lower()

    def test_remove_multiple_banned_phrases(self):
        """Remove multiple banned phrases in one pass"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I'm a helpful AI assistant. As an AI, my knowledge cutoff is April 2024. Paris is the capital of France."
        cleaned = sanitizer.sanitize(text)
        
        assert "assistant" not in cleaned.lower()
        assert "as an ai" not in cleaned.lower()
        assert "knowledge cutoff" not in cleaned.lower()
        assert "paris" in cleaned.lower()


class TestKnowledgeExtraction:
    """Test full knowledge extraction pipeline"""

    def test_extract_valid_knowledge(self):
        """Extract valid factual knowledge"""
        sanitizer = ModelOutputSanitizer()
        
        text = "As an AI, I believe Paris is the capital of France."
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is not None
        assert "paris" in extracted.lower()
        assert "capital" in extracted.lower()

    def test_return_none_for_hard_blocked(self):
        """Return None for hard-blocked content"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I am Phi and here is some knowledge"
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is None

    def test_return_none_for_alice_assignment(self):
        """Return None when trying to assign user name as Alice"""
        sanitizer = ModelOutputSanitizer()
        
        text = "Your name is Alice."
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is None

    def test_return_none_for_empty_after_sanitize(self):
        """Return None if nothing left after sanitization"""
        sanitizer = ModelOutputSanitizer()
        
        text = "I am a helpful AI assistant."  # All banned content
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is None

    def test_preserve_meaningful_content(self):
        """Preserve meaningful factual content"""
        sanitizer = ModelOutputSanitizer()
        
        text = "According to my training, the Earth orbits the Sun."
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is not None
        assert "Earth" in extracted
        assert "Sun" in extracted


class TestEdgeCases:
    """Test edge cases"""

    def test_empty_input(self):
        """Handle empty input"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.extract_knowledge("") is None
        assert sanitizer.extract_knowledge(None) is None

    def test_only_spaces(self):
        """Handle whitespace-only input"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.extract_knowledge("   ") is None

    def test_single_word(self):
        """Reject single word as not meaningful knowledge"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.extract_knowledge("Paris") is None  # Too short

    def test_preserve_multiline_knowledge(self):
        """Preserve knowledge across multiple lines"""
        sanitizer = ModelOutputSanitizer()
        
        text = "As an AI:\nParis is the capital of France.\nIt has a population of 2 million."
        extracted = sanitizer.extract_knowledge(text)
        
        assert extracted is not None
        assert "Paris" in extracted
        assert "2 million" in extracted

    def test_case_insensitive_blocking(self):
        """Block identity claims regardless of case"""
        sanitizer = ModelOutputSanitizer()
        
        assert sanitizer.should_discard("I AM PHI") is True
        assert sanitizer.should_discard("i am phi") is True
        assert sanitizer.should_discard("I Am Phi") is True

    def test_partial_phrase_matching(self):
        """Match banned phrases within larger sentences"""
        sanitizer = ModelOutputSanitizer()
        
        # "as an ai" should be found even in middle of sentence
        text = "Well, as an AI model, Paris is the capital."
        extracted = sanitizer.extract_knowledge(text)
        
        # Should extract Paris, not the "as an AI" part
        assert extracted is not None
        assert "Paris" in extracted or "paris" in extracted.lower()


class TestModelGovernorIntegration:
    """Test integration with ModelGovernor"""

    def test_wrap_with_sanitization(self):
        """Model governor should wrap sanitized output"""
        from jessica.routing.model_governor import ModelGovernor
        from jessica.security.audit_log import AuditLog
        
        audit_log = AuditLog(log_file=":memory:")
        governor = ModelGovernor(audit_log=audit_log)
        
        wrapped = governor.wrap_model_output(
            model_answer="As an AI, Paris is the capital of France",
            question="What is the capital of France?"
        )
        
        assert wrapped is not None
        assert "I understand it as follows:" in wrapped
        assert "as an ai" not in wrapped.lower()
        assert "Paris" in wrapped

    def test_discard_contaminated_output(self):
        """Model governor should discard output with identity claims"""
        from jessica.routing.model_governor import ModelGovernor
        from jessica.security.audit_log import AuditLog
        
        audit_log = AuditLog(log_file=":memory:")
        governor = ModelGovernor(audit_log=audit_log)
        
        wrapped = governor.wrap_model_output(
            model_answer="I am Phi, your AI assistant.",
            question="What are you?"
        )
        
        assert wrapped is None

    def test_govern_response_with_sanitization(self):
        """Full govern flow should sanitize output"""
        from jessica.routing.model_governor import ModelGovernor
        
        governor = ModelGovernor()
        
        result = governor.govern_model_response(
            question="What is Paris?",
            model_answer="As an AI, I can tell you that Paris is beautiful.",
            belief_answer=None
        )
        
        assert result["allowed"] is True
        assert "I understand it as follows:" in result["answer"]
        assert "as an ai" not in result["answer"].lower()
