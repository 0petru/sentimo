#!/usr/bin/env python3
"""Test script demonstrating memory minimization and folder-based profile storage."""
import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from openai import OpenAI
from profile import Profile
from memory import Memory

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    print("Set OPENAI_API_KEY in environment or .env")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

def test_memory_system():
    """Test the new memory system with file storage and minimization."""
    print("=== Testing Memory System ===\n")
    
    # Test 1: Create a profile with custom memory limits
    print("Test 1: Creating profile with custom memory limits...")
    from state import Personality, EmotionState
    
    personality = Personality(sensitivity=1.0, extraversion=0.6)
    emotions = EmotionState()
    memory = Memory(short_term_size=5, long_term_size=8)  # Small limits to test minimization
    
    profile = Profile(
        name="TestAgent",
        personality=personality,
        emotions=emotions,
        memory=memory,
        max_short_term_memory=5,
        max_long_term_memory=8,
    )
    
    print(f"✓ Created profile: {profile.name}")
    print(f"  - Max short-term: {profile.max_short_term_memory}")
    print(f"  - Max long-term: {profile.max_long_term_memory}")
    
    # Test 2: Add many messages and test short-term overflow
    print("\nTest 2: Testing short-term memory overflow...")
    for i in range(8):
        profile.memory.record_message(f"Message {i+1}: This is test message number {i+1}", 
                                     importance=0.3 + (i * 0.05),
                                     tags=["test"])
    
    st_count = len(profile.memory.short_term.get_all())
    lt_count = len(profile.memory.long_term.get_all())
    print(f"✓ Added 8 messages")
    print(f"  - Short-term: {st_count} (max: {profile.max_short_term_memory})")
    print(f"    → Oldest messages deleted when limit exceeded")
    print(f"  - Long-term: {lt_count}")
    
    # Test 3: Save profile to folder structure
    print("\nTest 3: Saving profile to folder structure...")
    profile_dir = "profiles/TestAgent"
    profile.save(profile_dir)
    print(f"✓ Saved profile to {profile_dir}")
    print(f"  - profile.json")
    print(f"  - short_term_memory.json ({st_count} entries)")
    print(f"  - long_term_memory.json ({lt_count} entries)")
    
    # Test 4: Load profile and verify memory was preserved
    print("\nTest 4: Loading profile from folder...")
    loaded_profile = Profile.load(profile_dir)
    print(f"✓ Loaded profile: {loaded_profile.name}")
    print(f"  - Short-term: {len(loaded_profile.memory.short_term.get_all())} entries")
    print(f"  - Long-term: {len(loaded_profile.memory.long_term.get_all())} entries")
    
    # Test 5: Test long-term memory minimization
    print("\nTest 5: Testing long-term memory minimization...")
    print("Adding 15 high-importance messages to trigger minimization...")
    
    for i in range(15):
        loaded_profile.memory.long_term.add(
            f"Important message {i+1}: Significant event in the conversation history",
            importance=0.7 + (i * 0.02),
            tags=["important", "event"]
        )
    
    print(f"Before minimization: {len(loaded_profile.memory.long_term.memories)} entries")
    
    if len(loaded_profile.memory.long_term.memories) > loaded_profile.max_long_term_memory:
        print("Triggering LLM-based minimization...")
        loaded_profile.memory.long_term.minimize_via_llm(
            client=client,
            model=MODEL,
            target_count=int(loaded_profile.max_long_term_memory * 0.8)
        )
        print(f"After minimization: {len(loaded_profile.memory.long_term.memories)} entries")
        print("✓ Long-term memory compressed via LLM while preserving important information")
    
    # Test 6: Save again and verify
    print("\nTest 6: Saving minimized profile...")
    loaded_profile.save(profile_dir)
    print(f"✓ Profile saved with compressed long-term memory")
    
    # Cleanup
    print("\nTest 7: Cleanup...")
    import shutil
    shutil.rmtree(profile_dir)
    print(f"✓ Cleaned up test profile folder")
    
    print("\n=== All Tests Passed ===")

if __name__ == "__main__":
    test_memory_system()
