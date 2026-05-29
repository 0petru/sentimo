#!/usr/bin/env python3
"""Demo script showing the new CLI functionality."""
import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from openai import OpenAI
from profile import Profile
from state import classify_emotions

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    print("Set OPENAI_API_KEY in environment or .env")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

def demo():
    print("=== AI Emotions Simulator - Demo ===\n")
    
    # Load Luna profile
    luna = Profile.load("profiles/luna.json")
    print(f"Loaded profile: {luna.name}")
    
    # Simulate a conversation
    messages = [
        ("I'm so happy to see you today!", "positive"),
        ("Actually, I'm worried about something.", "mixed"),
        ("But I trust you with this.", "positive"),
    ]
    
    for user_msg, context in messages:
        print(f"\n{'='*60}")
        print(f"User: {user_msg}")
        print(f"Context: {context}")
        
        # Analyze sentiment
        sent, intensity, emotions = classify_emotions(user_msg, client=client, model=MODEL)
        
        print(f"\n--- Sentiment Analysis ---")
        print(f"Sentiment: {sent:.2f} (range: -1.0 to 1.0)")
        print(f"Intensity: {intensity:.2f}")
        print(f"Top emotions detected:")
        for e, v in sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {e}: {v:.3f}")
        
        # Apply emotion update
        luna.emotions.apply_emotion_vector(
            emotions=emotions,
            base_strength=intensity,
            sentiment=sent,
            personality=luna.personality,
            blend=0.2,
        )
        luna.emotions.decay(0.03)
        luna.memory.record_message(user_msg, importance=intensity, tags=["user_message"])
        
        # Show emotion changes
        print(f"\n{luna.name}'s emotions after update:")
        emotions_state = luna.emotions.as_dict()
        for e, v in sorted(emotions_state.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(v * 15) + "░" * (15 - int(v * 15))
            print(f"  {e:10s} {bar} {v:.3f}")
        
        # Show memory
        print(f"\nMemory: {len(luna.memory.short_term.get_all())} short-term, {len(luna.memory.long_term.get_all())} long-term")
    
    # Final state
    print(f"\n{'='*60}")
    print(f"\nFinal Profile State for {luna.name}:")
    print(luna.summary())
    
    # Save profile
    luna.save("profiles/luna.json")
    print("Profile saved!")

if __name__ == "__main__":
    demo()
