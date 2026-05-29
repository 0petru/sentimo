"""Interactive CLI for emotion-aware AI conversations."""
import os
import json
from typing import Optional
import questionary
from openai import OpenAI
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from state import Personality, EmotionState, classify_emotions
from profile import Profile
from memory import Memory


class ConversationUI:
    """Interactive conversation interface with emotion analysis."""

    def __init__(self, client: OpenAI, model: str, profiles_dir: str = "profiles"):
        self.client = client
        self.model = model
        self.profiles_dir = profiles_dir
        self.profile: Optional[Profile] = None
        self.verbose = True
        self.console = Console()

    def list_profiles(self) -> list:
        """List all available profiles (folders with profile.json)."""
        if not os.path.exists(self.profiles_dir):
            return []
        profiles = []
        for item in os.listdir(self.profiles_dir):
            item_path = os.path.join(self.profiles_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "profile.json")):
                profiles.append(item)
        return sorted(profiles)

    def print_welcome_banner(self) -> None:
        """Print startup ASCII banner and author attribution."""
        banner = r"""
 ____  _____ _   _ _____ ___ __  __  ___
/ ___|| ____| \ | |_   _|_ _|  \/  |/ _ \
\___ \|  _| |  \| | | |  | || |\/| | | | |
 ___) | |___| |\  | | |  | || |  | | |_| |
|____/|_____|_| \_| |_| |___|_|  |_|\___/
"""
        self.console.print(banner, style="bold cyan")
        self.console.print(
            "Emotion-aware AI chat simulator with personality, memory, and adaptive state.",
            style="italic bright_white",
        )
        self.console.print(
            "by Ungureanu Calin Petru (0petru) 0petru.com",
            style="bold green",
        )
        self.console.print()

    def select_or_create_profile(self) -> None:
        """Prompt user to pick create/load flow, then choose profile with arrow keys."""
        self.print_welcome_banner()

        action = questionary.select(
            "Choose an option:",
            choices=[
                "Use an existing profile",
                "Create a new profile",
            ],
            qmark="[AI]",
        ).ask()

        if action == "Use an existing profile":
            self._select_existing_profile()
        else:
            self._create_profile_flow()

        print("\nProfile Summary:")
        print(self.profile.summary())

    def _select_existing_profile(self) -> None:
        """Select an existing profile via arrow-key menu."""
        profiles = self.list_profiles()
        if not profiles:
            print("\nNo existing profiles found. Let's create one.")
            self._create_profile_flow()
            return

        selected = questionary.select(
            "Select a profile:",
            choices=profiles,
            qmark="[AI]",
        ).ask()

        if not selected:
            raise SystemExit("Profile selection cancelled")

        profile_dir = os.path.join(self.profiles_dir, selected)
        self.profile = Profile.load(profile_dir)
        print(f"Loaded profile: {self.profile.name}")

    def _create_profile_flow(self) -> None:
        """Ask for a name and create a new profile."""
        name = questionary.text(
            "Enter new profile name:",
            qmark="[AI]",
            validate=lambda text: len(text.strip()) > 0 or "Name is required",
        ).ask()

        if not name:
            raise SystemExit("Profile creation cancelled")

        self.profile = self._create_new_profile(name.strip())

    def _create_new_profile(self, name: str) -> Profile:
        """Create a new profile with user input."""
        print(f"\nCreating new profile: {name}")
        
        def ask_int(label: str, default: int) -> int:
            value = questionary.text(
                f"{label} (default {default}):",
                default=str(default),
                qmark="[AI]",
            ).ask()
            return int(value.strip() or str(default))

        def ask_float(label: str, default: float) -> float:
            value = questionary.text(
                f"{label} (default {default}):",
                default=str(default),
                qmark="[AI]",
            ).ask()
            return float(value.strip() or str(default))

        # Get memory size preferences
        max_short_term = ask_int("Max short-term memory size", 10)
        max_long_term = ask_int("Max long-term memory size", 100)
        
        # Get personality traits
        sensitivity = ask_float("Sensitivity 0.0-1.5", 1.0)
        extraversion = ask_float("Extraversion 0.0-1.0", 0.5)
        neuroticism = ask_float("Neuroticism 0.0-1.0", 0.5)
        agreeableness = ask_float("Agreeableness 0.0-1.0", 0.5)
        openness = ask_float("Openness 0.0-1.0", 0.5)
        conscientiousness = ask_float("Conscientiousness 0.0-1.0", 0.5)
        
        personality = Personality(
            sensitivity=sensitivity,
            extraversion=extraversion,
            neuroticism=neuroticism,
            agreeableness=agreeableness,
            openness=openness,
            conscientiousness=conscientiousness,
        )
        
        emotions = EmotionState()
        memory = Memory(short_term_size=max_short_term, long_term_size=max_long_term)
        profile = Profile(
            name=name,
            personality=personality,
            emotions=emotions,
            memory=memory,
            max_short_term_memory=max_short_term,
            max_long_term_memory=max_long_term,
        )
        
        # Save profile to folder
        os.makedirs(self.profiles_dir, exist_ok=True)
        profile_dir = os.path.join(self.profiles_dir, name)
        profile.save(profile_dir)
        print(f"Profile saved to {profile_dir}")
        
        return profile

    def generate_emotional_response(self, user_message: str) -> str:
        """Generate a response colored by the profile's current emotional state."""
        emotions = self.profile.emotions.as_dict()
        
        # Build emotion context
        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        emotion_str = ", ".join([f"{e}: {v:.2f}" for e, v in top_emotions])
        
        system_prompt = (
            f"You are {self.profile.name}. Current emotional state: {emotion_str}. "
            f"Personality traits: extraversion={self.profile.personality.extraversion:.1f}, "
            f"neuroticism={self.profile.personality.neuroticism:.1f}. "
            f"Respond authentically reflecting these emotions. Keep responses concise (1-3 sentences)."
        )
        
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"[Error generating response: {e}]"

    def print_analysis(self, user_message: str, sentiment: float, intensity: float, emotions_dict: dict) -> None:
        """Render a full-width boxed message analysis panel."""
        analysis_table = Table(show_header=False, box=None, pad_edge=False)
        analysis_table.add_column("Key", style="bold cyan", no_wrap=True)
        analysis_table.add_column("Value")

        sentiment_style = "green" if sentiment > 0 else "red" if sentiment < 0 else "yellow"

        analysis_table.add_row("User", user_message)
        analysis_table.add_row(
            "Sentiment",
            Text(f"{sentiment:.2f}", style=sentiment_style) + Text("  (range: -1.0 to 1.0)")
        )
        intensity_text = Text(f"{intensity:.2f}", style="bold" if intensity >= 0.7 else "")
        analysis_table.add_row("Intensity", intensity_text)

        breakdown_lines = []
        for e, v in sorted(emotions_dict.items(), key=lambda x: x[1], reverse=True):
            tone = "green" if v >= 0.5 else "yellow" if v >= 0.25 else "red"
            breakdown_lines.append(f"[{tone}]{e}: {v:.3f}[/{tone}]")
        analysis_table.add_row("Emotion Breakdown", "\n".join(breakdown_lines))

        self.console.print()
        self.console.print(
            Panel(
                analysis_table,
                title="Message Analysis",
                border_style="blue",
                expand=True,
            )
        )

    def print_emotion_dashboard(self, before: dict, after: dict) -> None:
        """Render side-by-side boxed panels: current emotions (left) and impact (right)."""
        current_table = Table(show_header=True, header_style="bold cyan")
        current_table.add_column("Emotion", style="bold")
        current_table.add_column("Level", justify="right")
        current_table.add_column("Bar")

        for emotion, value in sorted(after.items(), key=lambda x: x[1], reverse=True):
            if value >= 0.6:
                value_style = "green"
            elif value >= 0.3:
                value_style = "yellow"
            else:
                value_style = "red"
            bar_fill = int(value * 20)
            bar = "█" * bar_fill + "░" * (20 - bar_fill)
            current_table.add_row(emotion, f"[{value_style}]{value:.3f}[/{value_style}]", bar)

        impact_table = Table(show_header=True, header_style="bold magenta")
        impact_table.add_column("Emotion", style="bold")
        impact_table.add_column("Delta", justify="right")
        impact_table.add_column("% Change", justify="right")

        impacts = []
        for emotion in after.keys():
            old_val = before.get(emotion, 0.0)
            new_val = after.get(emotion, 0.0)
            delta = new_val - old_val
            pct_change = 0.0 if abs(old_val) < 1e-9 else (delta / old_val) * 100.0
            impacts.append((emotion, delta, pct_change))

        for emotion, delta, pct_change in sorted(impacts, key=lambda x: abs(x[1]), reverse=True):
            if delta > 0:
                delta_text = Text(f"+{delta:.3f}", style="bold green")
                pct_text = Text(f"+{pct_change:.1f}%", style="green")
            elif delta < 0:
                delta_text = Text(f"{delta:.3f}", style="bold red")
                pct_text = Text(f"{pct_change:.1f}%", style="red")
            else:
                delta_text = Text(f"{delta:.3f}", style="dim")
                pct_text = Text(f"{pct_change:.1f}%", style="dim")
            impact_table.add_row(emotion, delta_text, pct_text)

        self.console.print()
        self.console.print(
            Columns(
                [
                    Panel(current_table, title="Current Emotions", border_style="cyan", expand=True),
                    Panel(impact_table, title="Emotion Impact", border_style="magenta", expand=True),
                ],
                equal=True,
                expand=True,
            )
        )

    def print_status_dashboard(self) -> None:
        """Render a styled status dashboard with personality/emotions and memory counts."""
        personality_table = Table(show_header=True, header_style="bold cyan")
        personality_table.add_column("Trait", style="bold")
        personality_table.add_column("Value", justify="right")

        personality_table.add_row("sensitivity", f"{self.profile.personality.sensitivity:.2f}")
        personality_table.add_row("extraversion", f"{self.profile.personality.extraversion:.2f}")
        personality_table.add_row("neuroticism", f"{self.profile.personality.neuroticism:.2f}")
        personality_table.add_row("agreeableness", f"{self.profile.personality.agreeableness:.2f}")
        personality_table.add_row("openness", f"{self.profile.personality.openness:.2f}")
        personality_table.add_row("conscientiousness", f"{self.profile.personality.conscientiousness:.2f}")

        emotions_table = Table(show_header=True, header_style="bold magenta")
        emotions_table.add_column("Emotion", style="bold")
        emotions_table.add_column("Level", justify="right")
        emotions_table.add_column("Bar")

        for emotion, value in sorted(self.profile.emotions.as_dict().items(), key=lambda x: x[1], reverse=True):
            if value >= 0.6:
                value_style = "green"
            elif value >= 0.3:
                value_style = "yellow"
            else:
                value_style = "red"
            bar_fill = int(value * 20)
            bar = "█" * bar_fill + "░" * (20 - bar_fill)
            emotions_table.add_row(emotion, f"[{value_style}]{value:.3f}[/{value_style}]", bar)

        self.console.print()
        self.console.print(
            Columns(
                [
                    Panel(personality_table, title="Personality", border_style="cyan", expand=True),
                    Panel(emotions_table, title="Emotions", border_style="magenta", expand=True),
                ],
                equal=True,
                expand=True,
            )
        )

        recent_count = len(self.profile.memory.short_term.get_all())
        long_term_count = len(self.profile.memory.long_term.get_all())
        self.console.print(
            Panel(
                f"Recent memories: [bold]{recent_count}[/bold]    |    Long-term memories: [bold]{long_term_count}[/bold]",
                title="Memory",
                border_style="green",
                expand=True,
            )
        )

    def conversation_loop(self) -> None:
        """Main conversation loop."""
        print("\n=== Starting Conversation ===")
        print("Commands: 'quit' to exit, 'save' to save profile, 'status' for profile summary, 'verbose on/off'")
        
        while True:
            user_input = input("\nYour Message: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye!")
                profile_dir = os.path.join(self.profiles_dir, self.profile.name)
                self.profile.save(profile_dir)
                break
            
            if user_input.lower() == "save":
                profile_dir = os.path.join(self.profiles_dir, self.profile.name)
                self.profile.save(profile_dir)
                print(f"Profile saved to {profile_dir}")
                continue
            
            if user_input.lower() == "status":
                self.print_status_dashboard()
                continue
            
            if user_input.lower().startswith("verbose"):
                mode = user_input.split()[1].lower() if len(user_input.split()) > 1 else "on"
                self.verbose = mode == "on"
                print(f"Verbose mode: {'ON' if self.verbose else 'OFF'}")
                continue
            
            # Process message through emotion system
            sent, intensity, emotions = classify_emotions(user_input, client=self.client, model=self.model)
            
            if self.verbose:
                self.print_analysis(user_input, sent, intensity, emotions)
            
            # Apply emotion update
            before_emotions = self.profile.emotions.as_dict().copy()
            self.profile.emotions.apply_emotion_vector(
                emotions=emotions,
                base_strength=intensity,
                sentiment=sent,
                personality=self.profile.personality,
                blend=0.2,
            )
            self.profile.emotions.decay(0.03)
            after_emotions = self.profile.emotions.as_dict().copy()
            self.profile.memory.record_message(user_input, importance=intensity, tags=["user_message"])
            
            # Check if long-term memory exceeds limit and minimize if needed
            if len(self.profile.memory.long_term.memories) > self.profile.max_long_term_memory:
                if self.verbose:
                    print(f"\n[Minimizing long-term memory ({len(self.profile.memory.long_term.memories)} entries)...]")
                self.profile.memory.long_term.minimize_via_llm(
                    client=self.client,
                    model=self.model,
                    target_count=int(self.profile.max_long_term_memory * 0.8)
                )
            
            if self.verbose:
                self.print_emotion_dashboard(before_emotions, after_emotions)
            
            # Generate response
            ai_response = self.generate_emotional_response(user_input)
            print(f"\n{self.profile.name}: {ai_response}")
