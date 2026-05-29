#!/usr/bin/env python3
"""Demo script showing the CLI UI and emotion system."""
import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
from openai import OpenAI
from rich.panel import Panel
from profile import Profile
from cli import ConversationUI
from state import classify_emotions

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    print("Set OPENAI_API_KEY in environment or .env")
    sys.exit(1)

client = OpenAI(api_key=API_KEY)

def demo():
    ui = ConversationUI(client=client, model=MODEL, profiles_dir="profiles")
    ui.print_welcome_banner()

    # Load Luna profile from folder
    luna = Profile.load("profiles/luna")
    ui.profile = luna
    ui.print_status_dashboard()
    
    # Simulate a conversation
    messages = [
        ("I'm so happy to see you today!", "positive"),
        ("Actually, I'm worried about something.", "mixed"),
        ("But I trust you with this.", "positive"),
    ]
    
    for user_msg, context in messages:
        print(f"\n[Demo context: {context}]\n")

        ui.console.rule("Message Sent to Agent")
        ui.console.print(
            Panel(user_msg, title="Your Message", border_style="yellow", expand=True)
        )

        sent, intensity, emotions = classify_emotions(user_msg, client=client, model=MODEL)

        ui.print_analysis(user_msg, sent, intensity, emotions)
        
        # Apply emotion update
        before_emotions = luna.emotions.as_dict().copy()
        luna.emotions.apply_emotion_vector(
            emotions=emotions,
            base_strength=intensity,
            sentiment=sent,
            personality=luna.personality,
            blend=0.2,
        )
        luna.emotions.decay(0.03)
        after_emotions = luna.emotions.as_dict().copy()
        luna.memory.record_message(user_msg, importance=intensity, tags=["user_message"])
        
        ui.print_emotion_dashboard(before_emotions, after_emotions)

        agent_answer = ui.generate_emotional_response(user_msg)
        ui.console.rule("Agent Answer")
        ui.console.print(
            Panel(agent_answer, title=f"{luna.name}'s Answer", border_style="green", expand=True)
        )

        ui.profile = luna
        ui.print_status_dashboard()
    
    # Final state
    print(f"\nFinal Profile State for {luna.name}:")
    ui.profile = luna
    ui.print_status_dashboard()
    
    # Save profile to folder
    luna.save("profiles/luna")
    print("Profile saved!")

if __name__ == "__main__":
    demo()
