"""
Phase 91: Internal Belief System Tests

Tests for Jessica's belief system ensuring identity consistency.
"""

import pytest
import json
import os
import tempfile
from datetime import datetime
from jessica.beliefs.belief_record import BeliefRecord
from jessica.beliefs.belief_store import BeliefStore
from jessica.beliefs.belief_reasoner import BeliefReasoner
from jessica.core.cognitive_kernel import CognitiveKernel


class TestBeliefRecord:
    """Test the BeliefRecord data class."""

    def test_belief_record_creation(self):
        """Test creating a belief record."""
        record = BeliefRecord(
            belief_id="test-1",
            subject="user",
            predicate="name",
            value="Hendrik",
            confidence=1.0,
            source="memory",
            created_at=datetime.now().isoformat()
        )
        assert record.subject == "user"
        assert record.predicate == "name"
        assert record.value == "Hendrik"
        assert record.confidence == 1.0

    def test_belief_record_invalid_confidence(self):
        """Test that invalid confidence raises error."""
        with pytest.raises(ValueError):
            BeliefRecord(
                belief_id="test-1",
                subject="user",
                predicate="name",
                value="Hendrik",
                confidence=1.5,  # Invalid
                source="memory",
                created_at=datetime.now().isoformat()
            )

    def test_belief_record_to_dict(self):
        """Test converting belief to dict."""
        record = BeliefRecord(
            belief_id="test-1",
            subject="user",
            predicate="name",
            value="Hendrik",
            confidence=1.0,
            source="memory",
            created_at="2026-02-18T10:00:00"
        )
        data = record.to_dict()
        assert data["subject"] == "user"
        assert data["value"] == "Hendrik"

    def test_belief_record_from_dict(self):
        """Test creating belief from dict."""
        data = {
            "belief_id": "test-1",
            "subject": "user",
            "predicate": "name",
            "value": "Hendrik",
            "confidence": 1.0,
            "source": "memory",
            "created_at": "2026-02-18T10:00:00"
        }
        record = BeliefRecord.from_dict(data)
        assert record.subject == "user"
        assert record.value == "Hendrik"

    def test_belief_record_immutable(self):
        """Test that belief records are immutable."""
        record = BeliefRecord(
            belief_id="test-1",
            subject="user",
            predicate="name",
            value="Hendrik",
            confidence=1.0,
            source="memory",
            created_at=datetime.now().isoformat()
        )
        # Attempting to modify should raise error
        with pytest.raises(AttributeError):
            record.value = "Alice"


class TestBeliefStore:
    """Test the BeliefStore class."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test files."""
        test_file = "test_beliefs.json"
        if os.path.exists(test_file):
            os.remove(test_file)
        yield
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_belief_store_create_empty(self):
        """Test creating empty belief store."""
        store = BeliefStore("test_beliefs.json")
        assert len(store.get_all()) == 0

    def test_belief_store_add_belief(self):
        """Test adding a belief."""
        store = BeliefStore("test_beliefs.json")
        belief = store.add_belief("user", "name", "Hendrik")
        assert belief["subject"] == "user"
        assert belief["value"] == "Hendrik"
        assert len(store.get_all()) == 1

    def test_belief_store_persistence(self):
        """Test that beliefs persist to disk."""
        store1 = BeliefStore("test_beliefs.json")
        store1.add_belief("user", "name", "Hendrik")
        
        store2 = BeliefStore("test_beliefs.json")
        beliefs = store2.get_all()
        assert len(beliefs) == 1
        assert beliefs[0]["value"] == "Hendrik"

    def test_belief_store_query_subject(self):
        """Test querying beliefs by subject."""
        store = BeliefStore("test_beliefs.json")
        store.add_belief("user", "name", "Hendrik")
        store.add_belief("user", "location", "Amsterdam")
        store.add_belief("system", "creator", "Hendrik")
        
        user_beliefs = store.query(subject="user")
        assert len(user_beliefs) == 2
        
        system_beliefs = store.query(subject="system")
        assert len(system_beliefs) == 1

    def test_belief_store_query_predicate(self):
        """Test querying beliefs by predicate."""
        store = BeliefStore("test_beliefs.json")
        store.add_belief("user", "name", "Hendrik")
        store.add_belief("system", "creator", "Hendrik")
        
        name_beliefs = store.query(predicate="name")
        assert len(name_beliefs) == 1
        assert name_beliefs[0]["subject"] == "user"
        
        creator_beliefs = store.query(predicate="creator")
        assert len(creator_beliefs) == 1
        assert creator_beliefs[0]["subject"] == "system"

    def test_belief_store_get_belief(self):
        """Test getting specific belief."""
        store = BeliefStore("test_beliefs.json")
        store.add_belief("user", "name", "Hendrik")
        
        belief = store.get_belief("user", "name")
        assert belief is not None
        assert belief["value"] == "Hendrik"
        
        missing = store.get_belief("user", "age")
        assert missing is None

    def test_belief_store_update_belief(self):
        """Test updating a belief."""
        store = BeliefStore("test_beliefs.json")
        store.add_belief("user", "name", "Hendrik")
        
        # Update should replace old belief
        store.update_belief("user", "name", "Alice")
        beliefs = store.query(subject="user", predicate="name")
        assert len(beliefs) == 1
        assert beliefs[0]["value"] == "Alice"

    def test_belief_store_remove_belief(self):
        """Test removing a belief."""
        store = BeliefStore("test_beliefs.json")
        belief = store.add_belief("user", "name", "Hendrik")
        
        store.remove_belief(belief["belief_id"])
        assert len(store.get_all()) == 0

    def test_belief_store_clear(self):
        """Test clearing all beliefs."""
        store = BeliefStore("test_beliefs.json")
        store.add_belief("user", "name", "Hendrik")
        store.add_belief("user", "location", "Amsterdam")
        
        store.clear()
        assert len(store.get_all()) == 0


class TestBeliefReasoner:
    """Test the BeliefReasoner class."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test files."""
        test_file = "test_beliefs_reasoner.json"
        if os.path.exists(test_file):
            os.remove(test_file)
        yield
        if os.path.exists(test_file):
            os.remove(test_file)

    def test_belief_reasoner_resolve_user_name(self):
        """Test resolving user name from beliefs."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.add_belief("user", "name", "Hendrik")
        name = reasoner.resolve("user_name")
        assert name == "Hendrik"

    def test_belief_reasoner_resolve_creator(self):
        """Test resolving creator from beliefs."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.add_belief("system", "creator", "Hendrik")
        creator = reasoner.resolve("creator")
        assert creator == "Hendrik"

    def test_belief_reasoner_resolve_missing(self):
        """Test resolving missing belief returns None."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        name = reasoner.resolve("user_name")
        assert name is None

    def test_belief_reasoner_get_confidence(self):
        """Test getting confidence of belief."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.add_belief("user", "name", "Hendrik", confidence=0.9)
        confidence = reasoner.get_confidence("user", "name")
        assert confidence == 0.9

    def test_belief_reasoner_has_belief(self):
        """Test checking if belief exists."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.add_belief("user", "name", "Hendrik")
        assert reasoner.has_belief("user", "name") is True
        assert reasoner.has_belief("user", "age") is False

    def test_belief_reasoner_get_all_about(self):
        """Test getting all beliefs about a subject."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.add_belief("user", "name", "Hendrik")
        store.add_belief("user", "location", "Amsterdam")
        store.add_belief("system", "creator", "Hendrik")
        
        user_beliefs = reasoner.get_all_about("user")
        assert len(user_beliefs) == 2

    def test_belief_reasoner_get_conflicts(self):
        """Test detecting conflicting beliefs."""
        store = BeliefStore("test_beliefs_reasoner.json")
        reasoner = BeliefReasoner(store)
        
        store.beliefs.append({
            "belief_id": "1",
            "subject": "user",
            "predicate": "name",
            "value": "Hendrik",
            "confidence": 1.0,
            "source": "memory",
            "created_at": datetime.now().isoformat()
        })
        store.beliefs.append({
            "belief_id": "2",
            "subject": "user",
            "predicate": "name",
            "value": "Alice",
            "confidence": 1.0,
            "source": "memory",
            "created_at": datetime.now().isoformat()
        })
        
        conflicts = reasoner.get_conflicts()
        assert ("user", "name") in conflicts


class TestCognitiveKernelBeliefs:
    """Test belief integration with CognitiveKernel."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test files."""
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "jessica/data/beliefs.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)
        # Ensure jessica/data exists
        if not os.path.exists("jessica/data"):
            os.makedirs("jessica/data", exist_ok=True)
        if not os.path.exists("jessica/config"):
            os.makedirs("jessica/config", exist_ok=True)
        yield
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "jessica/data/beliefs.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_kernel_stores_name_creates_belief(self):
        """Test that storing name creates belief."""
        kernel = CognitiveKernel()
        kernel.process("My name is Hendrik")
        
        belief = kernel.belief_store.get_belief("user", "name")
        assert belief is not None
        assert belief["value"] == "Hendrik"

    def test_kernel_stores_birth_year_creates_belief(self):
        """Test that storing birth year creates belief."""
        kernel = CognitiveKernel()
        kernel.process("I was born in 1990")
        
        belief = kernel.belief_store.get_belief("user", "birth_year")
        assert belief is not None
        assert belief["value"] == "1990"

    def test_kernel_stores_location_creates_belief(self):
        """Test that storing location creates belief."""
        kernel = CognitiveKernel()
        kernel.process("I live in Amsterdam")
        
        belief = kernel.belief_store.get_belief("user", "location")
        assert belief is not None
        assert belief["value"] == "Amsterdam"

    def test_kernel_stores_creator_creates_belief(self):
        """Test that storing creator creates belief."""
        kernel = CognitiveKernel()
        kernel.process("My name is Hendrik")
        kernel.process("I created you")
        
        belief = kernel.belief_store.get_belief("system", "creator")
        assert belief is not None
        assert belief["value"] == "Hendrik"

    def test_kernel_retrieves_name_from_belief(self):
        """Test that kernel retrieves name from belief."""
        kernel = CognitiveKernel()
        kernel.process("My name is Hendrik")
        
        response = kernel.process("What is my name?")
        assert "Hendrik" in response

    def test_kernel_retrieves_creator_from_belief(self):
        """Test that kernel retrieves creator from belief."""
        kernel = CognitiveKernel()
        kernel.process("My name is Hendrik")
        kernel.process("I created you")
        
        response = kernel.process("Who created you?")
        assert "Hendrik" in response

    def test_kernel_beliefs_persist_across_instances(self):
        """Test that beliefs persist across kernel instances."""
        kernel1 = CognitiveKernel()
        kernel1.process("My name is Hendrik")
        
        kernel2 = CognitiveKernel()
        belief = kernel2.belief_store.get_belief("user", "name")
        assert belief is not None
        assert belief["value"] == "Hendrik"

    def test_kernel_belief_consistency(self):
        """Test that beliefs maintain consistency."""
        kernel = CognitiveKernel()
        kernel.process("My name is Hendrik")
        kernel.process("My name is Alice")  # Update
        
        response = kernel.process("What is my name?")
        assert "Alice" in response
        
        # Check only latest belief exists
        beliefs = kernel.belief_store.query(subject="user", predicate="name")
        assert len(beliefs) == 1


class TestBeliefIntegration:
    """Integration tests for belief system."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Clean up test files."""
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "jessica/data/beliefs.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)
        if not os.path.exists("jessica/data"):
            os.makedirs("jessica/data", exist_ok=True)
        if not os.path.exists("jessica/config"):
            os.makedirs("jessica/config", exist_ok=True)
        yield
        for f in ["jessica_memory.json", "jessica_permissions.json", "jessica_audit.log", "jessica/data/beliefs.json", "jessica/config/permissions.json"]:
            if os.path.exists(f):
                os.remove(f)

    def test_full_identity_workflow(self):
        """Test complete identity workflow."""
        kernel = CognitiveKernel()
        
        # Step 1: Store identity information
        kernel.process("My name is Hendrik")
        kernel.process("I was born in 1990")
        kernel.process("I live in Amsterdam")
        kernel.process("I created you")
        
        # Step 2: Verify beliefs created
        assert kernel.belief_store.get_belief("user", "name") is not None
        assert kernel.belief_store.get_belief("user", "birth_year") is not None
        assert kernel.belief_store.get_belief("user", "location") is not None
        assert kernel.belief_store.get_belief("system", "creator") is not None
        
        # Step 3: Verify can answer questions
        name_response = kernel.process("What is my name?")
        assert "Hendrik" in name_response
        
        creator_response = kernel.process("Who created you?")
        assert "Hendrik" in creator_response
        
        location_response = kernel.process("Where do I live?")
        assert "Amsterdam" in location_response

    def test_belief_consistency_across_restart(self):
        """Test beliefs persist after restart."""
        # First session
        kernel1 = CognitiveKernel()
        kernel1.process("My name is Hendrik")
        
        # Second session (simulated restart)
        kernel2 = CognitiveKernel()
        response = kernel2.process("What is my name?")
        assert "Hendrik" in response

    def test_belief_update_overwrites_old(self):
        """Test that updating belief overwrites old value."""
        kernel = CognitiveKernel()
        
        kernel.process("My name is Hendrik")
        response1 = kernel.process("What is my name?")
        assert "Hendrik" in response1
        
        kernel.process("My name is Alice")
        response2 = kernel.process("What is my name?")
        assert "Alice" in response2
        assert "Hendrik" not in response2
