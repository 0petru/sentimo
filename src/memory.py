"""Memory system for short-term and long-term storage."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class MemoryEntry:
    """A single memory record."""
    text: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 0.5  # 0..1, higher = more important
    tags: List[str] = field(default_factory=list)  # e.g., ["user_preference", "emotional_event"]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "tags": self.tags,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "MemoryEntry":
        """Create from dictionary."""
        return MemoryEntry(
            text=data.get("text", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            importance=data.get("importance", 0.5),
            tags=data.get("tags", []),
        )


class ShortTermMemory:
    """Buffer of recent messages, keeps last N entries."""
    def __init__(self, max_size: int = 10):
        self.max_size = max_size
        self.messages: List[MemoryEntry] = []

    def add(self, text: str, importance: float = 0.5, tags: Optional[List[str]] = None) -> None:
        """Add a message. If full, remove oldest."""
        entry = MemoryEntry(text=text, importance=importance, tags=tags or [])
        self.messages.append(entry)
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def get_all(self) -> List[MemoryEntry]:
        """Return all messages in order."""
        return self.messages

    def get_recent(self, n: int = 3) -> List[MemoryEntry]:
        """Return the last N messages."""
        return self.messages[-n:]

    def clear(self) -> None:
        """Clear all short-term memory."""
        self.messages.clear()
    
    def to_list(self) -> list:
        """Serialize to list of dicts for JSON."""
        return [m.to_dict() for m in self.messages]
    
    @staticmethod
    def from_list(data: list, max_size: int = 10) -> "ShortTermMemory":
        """Deserialize from list of dicts."""
        stm = ShortTermMemory(max_size=max_size)
        for entry_dict in data:
            stm.messages.append(MemoryEntry.from_dict(entry_dict))
        return stm


class LongTermMemory:
    """Persistent memory of important events, facts, preferences."""
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.memories: List[MemoryEntry] = []

    def add(self, text: str, importance: float = 0.7, tags: Optional[List[str]] = None) -> None:
        """Add a long-term memory. Higher importance = more likely to be retrieved."""
        if importance < 0.3:
            # Too low importance, skip storage
            return
        entry = MemoryEntry(text=text, importance=importance, tags=tags or [])
        self.memories.append(entry)
        # Keep only the highest-importance memories
        if len(self.memories) > self.max_size:
            self.memories.sort(key=lambda x: x.importance, reverse=True)
            self.memories = self.memories[:self.max_size]

    def get_all(self) -> List[MemoryEntry]:
        """Return all memories, sorted by importance."""
        sorted_mems = sorted(self.memories, key=lambda x: x.importance, reverse=True)
        return sorted_mems

    def get_by_tag(self, tag: str) -> List[MemoryEntry]:
        """Retrieve memories with a specific tag."""
        return [m for m in self.memories if tag in m.tags]

    def search(self, keyword: str) -> List[MemoryEntry]:
        """Simple keyword search in memory text."""
        keyword_lower = keyword.lower()
        return [m for m in self.memories if keyword_lower in m.text.lower()]

    def get_top_n(self, n: int = 5) -> List[MemoryEntry]:
        """Get the N most important memories."""
        sorted_mems = sorted(self.memories, key=lambda x: x.importance, reverse=True)
        return sorted_mems[:n]

    def clear(self) -> None:
        """Clear all long-term memory."""
        self.memories.clear()
    
    def to_list(self) -> list:
        """Serialize to list of dicts for JSON."""
        return [m.to_dict() for m in self.memories]
    
    @staticmethod
    def from_list(data: list, max_size: int = 100) -> "LongTermMemory":
        """Deserialize from list of dicts."""
        ltm = LongTermMemory(max_size=max_size)
        for entry_dict in data:
            ltm.memories.append(MemoryEntry.from_dict(entry_dict))
        return ltm
    
    def minimize_via_llm(self, client, model: str, target_count: int = 50) -> None:
        """Compress long-term memory via LLM summarization when exceeding limit.
        
        Keeps the highest-importance memories, then summarizes the rest.
        """
        if len(self.memories) <= target_count:
            return
        
        # Sort by importance
        sorted_mems = sorted(self.memories, key=lambda x: x.importance, reverse=True)
        
        # Keep top 40% as-is (most important)
        keep_count = max(int(target_count * 0.4), 5)
        keep_mems = sorted_mems[:keep_count]
        summarize_mems = sorted_mems[keep_count:]
        
        # Summarize the less-important ones via LLM
        if not summarize_mems:
            return
        
        texts_to_summarize = [m.text for m in summarize_mems]
        
        try:
            prompt = f"""You are a memory compressor. Summarize these {len(texts_to_summarize)} memories into 3-5 concise key points, 
preserving only essential facts and patterns. Format as a simple list.

Memories to compress:
{chr(10).join(f'- {text}' for text in texts_to_summarize)}"""
            
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
            )
            
            summary = resp.choices[0].message.content
            
            # Create a summarized memory entry
            compressed_entry = MemoryEntry(
                text=f"COMPRESSED_SUMMARY: {summary}",
                importance=sum(m.importance for m in summarize_mems) / len(summarize_mems),
                tags=list(set(tag for m in summarize_mems for tag in m.tags)),
            )
            
            # Replace with compressed version
            self.memories = keep_mems + [compressed_entry]
            
        except Exception as e:
            # Fallback: just keep the highest-importance entries
            print(f"LLM minimization failed: {e}, falling back to importance-based trimming")
            self.memories = sorted_mems[:target_count]


class Memory:
    """Combined short and long-term memory system with file persistence."""
    def __init__(self, short_term_size: int = 10, long_term_size: int = 100):
        self.short_term = ShortTermMemory(max_size=short_term_size)
        self.long_term = LongTermMemory(max_size=long_term_size)
        self.max_short_term = short_term_size
        self.max_long_term = long_term_size

    def record_message(self, text: str, importance: float = 0.5, tags: Optional[List[str]] = None) -> None:
        """Record a message in short-term. Optionally promote to long-term."""
        self.short_term.add(text, importance, tags)
        # Auto-promote high-importance or tagged messages
        if importance > 0.6 or (tags and any(t in tags for t in ["important", "preference", "emotional"])):
            self.long_term.add(text, importance, tags)

    def get_context(self, n_recent: int = 3) -> str:
        """Get a summary of recent and important memories for context."""
        recent = self.short_term.get_recent(n_recent)
        top_long = self.long_term.get_top_n(2)
        
        context = "Recent messages:\n"
        for m in recent:
            context += f"  - {m.text}\n"
        
        if top_long:
            context += "Important memories:\n"
            for m in top_long:
                context += f"  - {m.text}\n"
        
        return context

    def clear_all(self) -> None:
        """Clear all memory."""
        self.short_term.clear()
        self.long_term.clear()
    
    def to_dict(self) -> dict:
        """Serialize memory to dictionary for JSON."""
        return {
            "short_term": self.short_term.to_list(),
            "long_term": self.long_term.to_list(),
            "max_short_term": self.max_short_term,
            "max_long_term": self.max_long_term,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Memory":
        """Deserialize memory from dictionary."""
        mem = Memory(
            short_term_size=data.get("max_short_term", 10),
            long_term_size=data.get("max_long_term", 100),
        )
        mem.short_term = ShortTermMemory.from_list(
            data.get("short_term", []),
            max_size=data.get("max_short_term", 10)
        )
        mem.long_term = LongTermMemory.from_list(
            data.get("long_term", []),
            max_size=data.get("max_long_term", 100)
        )
        return mem
    
    def save_to_files(self, short_term_path: str, long_term_path: str) -> None:
        """Save short-term and long-term memory to separate JSON files."""
        with open(short_term_path, "w") as f:
            json.dump(self.short_term.to_list(), f, indent=2)
        with open(long_term_path, "w") as f:
            json.dump(self.long_term.to_list(), f, indent=2)
    
    @staticmethod
    def load_from_files(short_term_path: str, long_term_path: str, 
                       short_term_size: int = 10, long_term_size: int = 100) -> "Memory":
        """Load short-term and long-term memory from separate JSON files."""
        import os
        
        mem = Memory(short_term_size=short_term_size, long_term_size=long_term_size)
        
        if os.path.exists(short_term_path):
            with open(short_term_path, "r") as f:
                st_data = json.load(f)
            mem.short_term = ShortTermMemory.from_list(st_data, max_size=short_term_size)
        
        if os.path.exists(long_term_path):
            with open(long_term_path, "r") as f:
                lt_data = json.load(f)
            mem.long_term = LongTermMemory.from_list(lt_data, max_size=long_term_size)
        
        return mem
