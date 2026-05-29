"""Profile/Agent: a bundle of personality, emotions, and memory."""
from dataclasses import dataclass, asdict
from state import Personality, EmotionState
from memory import Memory
import json
import os


@dataclass
class Profile:
    """A complete AI profile with personality, emotions, and memory."""
    name: str
    personality: Personality
    emotions: EmotionState
    memory: Memory
    max_short_term_memory: int = 10
    max_long_term_memory: int = 100

    def __post_init__(self):
        """Ensure we have valid instances."""
        if not isinstance(self.personality, Personality):
            raise TypeError("personality must be a Personality instance")
        if not isinstance(self.emotions, EmotionState):
            raise TypeError("emotions must be an EmotionState instance")
        if not isinstance(self.memory, Memory):
            raise TypeError("memory must be a Memory instance")

    def summary(self) -> str:
        """Get a summary of this profile's current state."""
        return f"""
Profile: {self.name}
Personality:
  - sensitivity: {self.personality.sensitivity}
  - extraversion: {self.personality.extraversion}
  - neuroticism: {self.personality.neuroticism}
  - agreeableness: {self.personality.agreeableness}
  - openness: {self.personality.openness}
  - conscientiousness: {self.personality.conscientiousness}
Emotions: {self.emotions.as_dict()}
Recent memories: {len(self.memory.short_term.get_all())} messages
Long-term memories: {len(self.memory.long_term.get_all())} entries
"""

    def reset(self) -> None:
        """Reset emotions and memory to defaults."""
        self.emotions = EmotionState()
        self.memory.clear_all()

    def to_dict(self) -> dict:
        """Serialize profile to dictionary for JSON storage."""
        return {
            "name": self.name,
            "max_short_term_memory": self.max_short_term_memory,
            "max_long_term_memory": self.max_long_term_memory,
            "personality": {
                "sensitivity": self.personality.sensitivity,
                "extraversion": self.personality.extraversion,
                "neuroticism": self.personality.neuroticism,
                "agreeableness": self.personality.agreeableness,
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
            },
            "emotions": {
                "joy": self.emotions.joy,
                "sadness": self.emotions.sadness,
                "anger": self.emotions.anger,
                "fear": self.emotions.fear,
                "trust": self.emotions.trust,
                "curiosity": self.emotions.curiosity,
                "baseline": self.emotions.baseline,
            },
        }

    @staticmethod
    def from_dict(data: dict) -> "Profile":
        """Recreate profile from dictionary."""
        name = data.get("name", "Unknown")
        max_st = data.get("max_short_term_memory", 10)
        max_lt = data.get("max_long_term_memory", 100)
        
        pers_data = data.get("personality", {})
        personality = Personality(
            sensitivity=pers_data.get("sensitivity", 1.0),
            extraversion=pers_data.get("extraversion", 0.5),
            neuroticism=pers_data.get("neuroticism", 0.5),
            agreeableness=pers_data.get("agreeableness", 0.5),
            openness=pers_data.get("openness", 0.5),
            conscientiousness=pers_data.get("conscientiousness", 0.5),
        )
        
        emo_data = data.get("emotions", {})
        emotions = EmotionState(
            joy=emo_data.get("joy", 0.15),
            sadness=emo_data.get("sadness", 0.15),
            anger=emo_data.get("anger", 0.15),
            fear=emo_data.get("fear", 0.15),
            trust=emo_data.get("trust", 0.15),
            curiosity=emo_data.get("curiosity", 0.15),
            baseline=emo_data.get("baseline", 0.10),
        )
        
        memory = Memory(short_term_size=max_st, long_term_size=max_lt)
        
        return Profile(
            name=name,
            personality=personality,
            emotions=emotions,
            memory=memory,
            max_short_term_memory=max_st,
            max_long_term_memory=max_lt,
        )

    def save(self, profile_dir: str) -> None:
        """Save profile to a folder with separate files for profile metadata and memory."""
        os.makedirs(profile_dir, exist_ok=True)
        
        # Save profile metadata
        profile_path = os.path.join(profile_dir, "profile.json")
        with open(profile_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        
        # Save memory files
        short_term_path = os.path.join(profile_dir, "short_term_memory.json")
        long_term_path = os.path.join(profile_dir, "long_term_memory.json")
        self.memory.save_to_files(short_term_path, long_term_path)

    @staticmethod
    def load(profile_dir: str) -> "Profile":
        """Load profile from a folder containing profile.json and memory files."""
        profile_path = os.path.join(profile_dir, "profile.json")
        with open(profile_path, "r") as f:
            data = json.load(f)
        
        profile = Profile.from_dict(data)
        
        # Load memory from files
        short_term_path = os.path.join(profile_dir, "short_term_memory.json")
        long_term_path = os.path.join(profile_dir, "long_term_memory.json")
        profile.memory = Memory.load_from_files(
            short_term_path,
            long_term_path,
            short_term_size=profile.max_short_term_memory,
            long_term_size=profile.max_long_term_memory,
        )
        
        return profile
