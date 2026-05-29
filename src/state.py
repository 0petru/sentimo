from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json
import re

EMOTIONS: List[str] = ["joy", "sadness", "anger", "fear", "trust", "curiosity"]
# Default values used when the caller does not provide explicit emotion settings.
DEFAULT_EMOTION_VALUE = 0.15
DEFAULT_EMOTION_BASELINE = 0.10


def clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


@dataclass
class Personality:
    # Global sensitivity multiplier for emotion changes.
    # Higher values make the AI react more strongly to messages.
    sensitivity: float = 1.0
    # Big Five trait modifiers in [0,1].
    # These are behavioral knobs, not literal human traits.
    extraversion: float = 0.5
    neuroticism: float = 0.5
    agreeableness: float = 0.5
    openness: float = 0.5
    conscientiousness: float = 0.5


@dataclass
class EmotionState:
    # Current emotion levels. Each one is a separate field so it is easy to tune.
    joy: float = DEFAULT_EMOTION_VALUE
    sadness: float = DEFAULT_EMOTION_VALUE
    anger: float = DEFAULT_EMOTION_VALUE
    fear: float = DEFAULT_EMOTION_VALUE
    trust: float = DEFAULT_EMOTION_VALUE
    curiosity: float = DEFAULT_EMOTION_VALUE

    # Shared resting level for every emotion.
    baseline: float = DEFAULT_EMOTION_BASELINE

    def _emotion_fields(self) -> Dict[str, float]:
        # Build a view of the current emotion values.
        return {name: getattr(self, name) for name in EMOTIONS}

    def _baseline_fields(self) -> Dict[str, float]:
        # Return the same baseline for every emotion.
        return {name: self.baseline for name in EMOTIONS}

    def _set_emotion(self, name: str, value: float) -> None:
        # Keep every emotion inside the valid 0..1 range.
        setattr(self, name, clamp01(value))

    def decay(self, amount: float = 0.02) -> None:
        """Move each emotion a little closer to the shared baseline."""
        for name, value in self._emotion_fields().items():
            target = self.baseline
            # Move the emotion a small fraction of the way toward the baseline.
            # If the current value is above baseline, this lowers it.
            # If the current value is below baseline, this raises it.
            # Using a small amount keeps the decay gradual instead of jumping.
            # Linear decay, because is easy to understand and tune.
            self._set_emotion(name, value - (value - target) * amount)

    def apply_message(self, sentiment: float, intensity: float, personality: Personality) -> None:
        """
        Update emotions from a message.

        - sentiment: in [-1, 1] where negative is negative valence.
        - intensity: positive scalar (0..1) representing strength of the message.
        Personality modifies how large and what emotions change.
        """
        # Base reaction strength from message polarity, intensity, and personality sensitivity.
        s = clamp01(abs(sentiment)) * intensity * personality.sensitivity
        # Extraversion makes the agent more socially active and expressive.
        social_drive = 0.5 + personality.extraversion / 2

        if sentiment >= 0:
            # Positive messages raise pleasant emotions and soften negative ones.
            self.joy = clamp01(self.joy + 0.6 * s * social_drive)
            self.trust = clamp01(
                self.trust + 0.4 * s * (0.5 + personality.openness / 2) * social_drive
            )
            self.curiosity = clamp01(
                self.curiosity + 0.3 * s * (0.5 + personality.openness / 2) * social_drive
            )
            # Neuroticism reduces how quickly the agent recovers from negative feelings.
            self.sadness = clamp01(self.sadness - 0.2 * s * (1 - personality.neuroticism))
            self.fear = clamp01(self.fear - 0.15 * s * (1 - personality.neuroticism))
        else:
            # Negative messages increase distress and lower trust.
            neg = s * (0.5 + personality.neuroticism / 2)
            resilience = 1 - 0.25 * personality.extraversion
            # Agreeableness reduces anger spikes.
            self.anger = clamp01(self.anger + 0.5 * neg * (1 - personality.agreeableness))
            # Extraversion softens the emotional drop from negative input.
            self.sadness = clamp01(self.sadness + 0.6 * neg * resilience)
            # Neuroticism makes fear react more strongly.
            self.fear = clamp01(self.fear + 0.5 * neg * personality.neuroticism * resilience)
            # Trust falls on negative messages, but extraversion reduces the drop a little.
            self.trust = clamp01(self.trust - 0.25 * s * resilience)

        # Conscientiousness dampens volatility by nudging emotions back toward baseline.
        for k in EMOTIONS:
            damp = 0.02 * personality.conscientiousness
            current = getattr(self, k)
            target = self.baseline
            self._set_emotion(k, current - (current - target) * damp)

    def apply_emotion_vector(
        self,
        emotions: Dict[str, float],
        base_strength: float,
        sentiment: float,
        personality: Personality,
        blend: Optional[float] = None,
    ) -> None:
        """
        Apply a per-emotion weight vector from a classifier.

        - `emotions`: mapping of emotion -> value in [0,1].
        - `base_strength`: overall strength scalar (0..1).
        - `sentiment`: message sentiment in [-1,1] (used for sign).
        - `blend`: if provided (0..1), blend toward the classifier's suggested
           absolute emotion levels: new = current + blend*(W - current) scaled by personality.
          If `blend` is None, use delta mode: delta = emotion_valence_sign * sign(sentiment) * base_strength * W * multiplier.
        After applying updates, still apply conscientiousness damping as in `apply_message`.
        """
        mult = personality.sensitivity * (1 + 0.5 * personality.extraversion)
        s_sign = 0 if sentiment == 0 else (1 if sentiment > 0 else -1)

        if blend is not None:
            blend_eff = clamp01(blend) * personality.sensitivity * (1 + 0.5 * personality.extraversion)
            for e in EMOTIONS:
                target = clamp01(emotions.get(e, 0.0))
                current = getattr(self, e)
                self._set_emotion(e, current + blend_eff * (target - current))
        else:
            for e in EMOTIONS:
                W = clamp01(emotions.get(e, 0.0))
                val_sign = 1 if e in ("joy", "trust", "curiosity") else -1
                delta = val_sign * s_sign * base_strength * W * mult
                current = getattr(self, e)
                self._set_emotion(e, current + delta)

        # Apply the same conscientiousness damping as usual
        for k in EMOTIONS:
            damp = 0.02 * personality.conscientiousness
            current = getattr(self, k)
            target = self.baseline
            self._set_emotion(k, current - (current - target) * damp)

    def as_dict(self) -> Dict[str, float]:
        return {k: round(v, 3) for k, v in self._emotion_fields().items()}


def _keyword_sentiment(text: str) -> Tuple[float, float]:
    """Fallback keyword heuristic returning (sentiment, intensity)."""
    t = text.lower()
    positives = ["good", "great", "happy", "glad", "love", "thanks", "wonderful", "nice"]
    negatives = ["bad", "sad", "angry", "hate", "terrible", "awful", "upset", "worried", "fear"]
    score = 0
    for p in positives:
        if p in t:
            score += 1
    for n in negatives:
        if n in t:
            score -= 1
    if score == 0:
        return 0.0, 0.0
    norm = max(-1.0, min(1.0, score / max(len(positives), len(negatives))))
    intensity = min(1.0, abs(norm))
    return norm, intensity


def simple_text_sentiment(text: str, client: Optional[object] = None, model: str = "gpt-4o-mini") -> Tuple[float, float]:
    """
    Return (sentiment, intensity) in [-1,1] x [0,1].

    If `client` is provided it will call the LLM to classify sentiment and intensity
    and expect a short JSON output like `{ "sentiment": -0.2, "intensity": 0.45 }`.
    On any error the function falls back to the keyword heuristic.
    """
    if client is None:
        return _keyword_sentiment(text)

    prompt = (
        "Classify the sentiment of the user's message as two numbers in JSON:"
        " `sentiment` (from -1.0 negative to 1.0 positive) and `intensity` (0.0-1.0)."
        " Be concise and return only valid JSON. Examples: {\"sentiment\": 0.5, \"intensity\": 0.7}."
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=60,
            temperature=0.0,
        )
        content = resp.choices[0].message.content.strip()

        # Try to extract JSON object from model output
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            # sometimes model returns plain key:value lines; try to parse numbers
            # fallback to keyword
            return _keyword_sentiment(text)

        obj = json.loads(m.group(0))
        sentiment = float(obj.get("sentiment", 0.0))
        intensity = float(obj.get("intensity", min(1.0, abs(sentiment))))
        # clamp
        sentiment = max(-1.0, min(1.0, sentiment))
        intensity = max(0.0, min(1.0, intensity))
        return sentiment, intensity
    except Exception:
        return _keyword_sentiment(text)


def classify_emotions(text: str, client: Optional[object] = None, model: str = "gpt-4o-mini") -> Tuple[float, float, Dict[str, float]]:
    """
    Return (sentiment, intensity, emotions_dict).

    `emotions_dict` maps each emotion in `EMOTIONS` to a value in [0,1].
    If `client` is provided the LLM is asked to return JSON with keys
    `sentiment`, `intensity`, and `emotions`.
    On error, fall back to a simple heuristic that allocates the intensity
    to positive or negative emotion groups based on sentiment.
    """
    if client is None:
        s, intensity = _keyword_sentiment(text)
        emotions = {e: 0.0 for e in EMOTIONS}
        if s > 0:
            for e in ["joy", "trust", "curiosity"]:
                emotions[e] = intensity
        elif s < 0:
            for e in ["sadness", "anger", "fear"]:
                emotions[e] = intensity
        return s, intensity, emotions

    prompt = (
        "Return a JSON object with keys: `sentiment` (number -1.0..1.0),"
        " `intensity` (0.0..1.0), and `emotions` which maps the following"
        f" emotions {EMOTIONS} to numbers 0.0..1.0. Return ONLY valid JSON."
        "Examples: {\"sentiment\": 0.5, \"intensity\": 0.6, \"emotions\": {\"joy\":0.6,...}}"
    )

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            max_tokens=180,
            temperature=0.0,
        )
        content = resp.choices[0].message.content.strip()
        m = re.search(r"\{.*\}", content, re.S)
        if not m:
            s, intensity = _keyword_sentiment(text)
            emotions = {e: 0.0 for e in EMOTIONS}
            if s > 0:
                for e in ["joy", "trust", "curiosity"]:
                    emotions[e] = intensity
            elif s < 0:
                for e in ["sadness", "anger", "fear"]:
                    emotions[e] = intensity
            return s, intensity, emotions
        obj = json.loads(m.group(0))
        sentiment = float(obj.get("sentiment", 0.0))
        intensity = float(obj.get("intensity", 0.0))
        emotions = obj.get("emotions", {})
        emotions_out = {}
        for e in EMOTIONS:
            emotions_out[e] = clamp01(float(emotions.get(e, 0.0)))
        sentiment = max(-1.0, min(1.0, sentiment))
        intensity = max(0.0, min(1.0, intensity))
        return sentiment, intensity, emotions_out
    except Exception:
        s, intensity = _keyword_sentiment(text)
        emotions = {e: 0.0 for e in EMOTIONS}
        if s > 0:
            for e in ["joy", "trust", "curiosity"]:
                emotions[e] = intensity
        elif s < 0:
            for e in ["sadness", "anger", "fear"]:
                emotions[e] = intensity
        return s, intensity, emotions
