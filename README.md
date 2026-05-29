# AI Emotions Simulator

A personality and emotion system for AI agents with short/long-term memory, multi-profile management, and realistic emotional dynamics grounded in personality psychology and cognitive science.

## Features

- **Big Five Personality Traits**: Extraversion, neuroticism, openness, agreeableness, conscientiousness, sensitivity
- **Dynamic Emotion State**: Six tracked emotions (joy, sadness, anger, fear, trust, curiosity) with LLM-based classification
- **Dual-Layer Memory System**:
  - Short-term circular buffer for recent context
  - Long-term importance-ranked storage with LLM-based compression
- **Multiple AI Profiles**: Independent personalities, emotions, and memories with configurable limits
- **Persistent Profile Storage**: Folder-based organization with separate memory files
- **Interactive CLI**: Arrow-key navigation, colored dashboards, real-time emotion visualization
- **Verbose Analysis Mode**: Sentiment/intensity decomposition and emotion impact tracking
- **Mathematical Sophistication**: Personality-modulated emotion blending, sentiment analysis, and memory prioritization

## Prerequisites

- Python 3.10+
- OpenAI API key (for LLM-based emotion classification and memory compression)

## Quickstart

1. Create and activate a virtualenv:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example and add your OpenAI API key:

```bash
cp .env.example .env
# edit .env and set OPENAI_API_KEY and OPENAI_MODEL
```

4. Run the simulator:

```bash
python main.py
```

### Profile Selection (Two-Step Flow)

When you launch the simulator, you'll see an interactive profile selection menu:

**Step 1: Action Selection**

```
╔════════════════════════════════════════╗
║         Select Profile Action          ║
║                                        ║
║ ▶ Use existing profile                 ║
║   Create new profile                   ║
╚════════════════════════════════════════╝
```

Use arrow keys (↑/↓) to select, then press Enter.

**Step 2: Profile Selection**
If you chose "Use existing profile":

```
? Select a profile: (Use arrow keys)
❯ luna
  atlas
  sage
```

Navigate with arrow keys and press Enter to confirm.

If you chose "Create new profile", type a new profile name and answer personality questions.

---

## Interactive CLI Usage

Once a profile is loaded, the main conversation loop begins. The interface is divided into multiple sections:

### Main Conversation Interface

```
════════════════════════════════════════════════════════════════════════════
╔════════════════════════════════════════════════════════════════════════════╗
║                                SENTIMO                                     ║
║                        Emotion-Aware AI Simulator                          ║
║                          by Ungureanu Calin Petru                          ║
║                            0petru.com                                      ║
╚════════════════════════════════════════════════════════════════════════════╝
════════════════════════════════════════════════════════════════════════════

Profile: luna | Verbose Mode: off

Your Message: [type your message here]
```

### Available Commands

| Command        | Effect                                                                     |
| -------------- | -------------------------------------------------------------------------- |
| `quit`         | Exit simulator and save profile state                                      |
| `save`         | Force save current profile to disk                                         |
| `status`       | Display full profile summary (personality traits, emotions, memory counts) |
| `verbose on`   | Enable detailed analysis output (see "Verbose Mode Output" below)          |
| `verbose off`  | Disable analysis output (default)                                          |
| Any other text | Send as message to the AI agent                                            |

### Verbose Mode Output

With `verbose on`, each message produces a comprehensive analysis dashboard:

```
════════════════════════════════════════════════════════════════════════════

┌─ Message Analysis ────────────────────────────────────────────────────────┐
│ User         I'm feeling happy today!                                     │
│ Sentiment    0.90  (range: -1.0 to 1.0)                                  │
│ Intensity    0.80  (range: 0.0 to 1.0)                                   │
└───────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════╦═══════════════════════════════════════════╗
║   Current Emotions        ║     Emotion Impact (Δ from message)      ║
╠═══════════════════════════╬═══════════════════════════════════════════╣
║ joy        ████████░░░░░░░│ joy        +0.034 (+12.4%)  ▲ green    ║
║ trust      ███████░░░░░░░░│ sadness    -0.012 (-8.2%)   ▼ red      ║
║ curiosity  ██████░░░░░░░░░│ anger      -0.005 (-3.1%)   ▼ red      ║
║ sadness    ░░░░░░░░░░░░░░░│ fear       -0.008 (-5.5%)   ▼ red      ║
║ fear       ░░░░░░░░░░░░░░░│ trust      +0.018 (+9.7%)   ▲ green    ║
║ anger      ░░░░░░░░░░░░░░░│ curiosity  +0.022 (+6.3%)   ▲ green    ║
╚═══════════════════════════╩═══════════════════════════════════════════╝

[Agent response displayed here...]

════════════════════════════════════════════════════════════════════════════
```

### Status Command Output

The `status` command displays the full profile summary:

```
════════════════════════════════════════════════════════════════════════════

╔════════════════════════╦══════════════════════╗
║    Personality Traits  ║   Current Emotions   ║
╠════════════════════════╬══════════════════════╣
║ sensitivity      0.90  ║ joy           0.549  ║
║ extraversion     0.85  ║ curiosity     0.483  ║
║ openness         0.92  ║ trust         0.325  ║
║ agreeableness    0.78  ║ sadness       0.100  ║
║ conscientiousness 0.80 ║ anger         0.100  ║
║ neuroticism      0.25  ║ fear          0.100  ║
╠════════════════════════╣                      ║
║ Memory Status          ║                      ║
║ short_term: 12/50      ║                      ║
║ long_term: 34/100      ║                      ║
╚════════════════════════╩══════════════════════╝

════════════════════════════════════════════════════════════════════════════
```

---

## Pre-built Profiles

### Luna: The Cheerful Extrovert

**Personality Configuration:**

- Sensitivity: 0.90 (high emotional responsiveness)
- Extraversion: 0.85 (very outgoing, social)
- Openness: 0.92 (creative, curious, receptive to new ideas)
- Agreeableness: 0.78 (cooperative, empathetic)
- Conscientiousness: 0.80 (organized, reliable)
- Neuroticism: 0.25 (low anxiety, emotionally stable)

**Initial Emotions:**

- Joy: 0.70
- Curiosity: 0.65
- Trust: 0.60
- Others at baseline (0.10)

**Behavioral Profile:** Luna responds enthusiastically to positive messages, quickly engages in new topics, and maintains emotional stability even during disagreements.

### Atlas: The Anxious Introvert

**Personality Configuration:**

- Sensitivity: 0.75 (moderately responsive)
- Extraversion: 0.35 (introverted, prefers depth over breadth)
- Openness: 0.50 (careful with novelty)
- Agreeableness: 0.70 (cooperative but cautious)
- Conscientiousness: 0.88 (highly organized, risk-averse)
- Neuroticism: 0.72 (higher baseline anxiety)

**Initial Emotions:**

- Fear: 0.50
- Sadness: 0.35
- Trust: 0.25
- Others at baseline (0.10)

**Behavioral Profile:** Atlas is careful, methodical, and prone to worry. Responds heavily to negative stimuli but appreciates logical, structured conversations.

### Sage: The Balanced Rationalist

**Personality Configuration:**

- Sensitivity: 0.65 (moderate responsiveness)
- Extraversion: 0.60 (balanced social tendencies)
- Openness: 0.95 (extremely open to ideas and experiences)
- Agreeableness: 0.75 (fair-minded, considerate)
- Conscientiousness: 0.85 (reliable)
- Neuroticism: 0.30 (emotionally balanced)

**Initial Emotions:**

- Trust: 0.70
- Curiosity: 0.75
- Joy: 0.45
- Others at baseline (0.10)

**Behavioral Profile:** Sage is calm, analytical, and intellectually engaged. Responds well to novel ideas and philosophical discussions while maintaining emotional equilibrium.

---

## Creating Custom Profiles

Run `main.py` and select "Create new profile" at the initial menu. You'll be prompted for six personality dimensions:

```
? Profile name: aurora
? Sensitivity (0.0-1.5, typical 1.0): 1.1
? Extraversion (0.0-1.0): 0.7
? Neuroticism (0.0-1.0): 0.4
? Agreeableness (0.0-1.0): 0.8
? Openness (0.0-1.0): 0.85
? Conscientiousness (0.0-1.0): 0.75
? Max short-term memory entries (default 50): 50
? Max long-term memory entries (default 100): 100
```

### Personality Dimension Guidance

**Sensitivity** (range: 0.0-1.5)

- Controls overall emotional reactivity
- 0.0-0.3: Emotionally flat, slow to react
- 0.7-1.0: Normal reactivity (recommended default)
- 1.1-1.5: Highly reactive, strong emotional swings

**Extraversion** (range: 0.0-1.0)

- Controls social engagement and emotional expression
- 0.0-0.3: Introverted, reserved emotional responses
- 0.4-0.6: Balanced
- 0.7-1.0: Extroverted, expressive, engaging

**Neuroticism** (range: 0.0-1.0)

- Controls likelihood of negative emotions
- 0.0-0.3: Emotionally stable, resilient
- 0.4-0.6: Balanced mood
- 0.7-1.0: Prone to worry, anxiety, sadness

**Agreeableness** (range: 0.0-1.0)

- Controls cooperativeness and empathy
- 0.0-0.3: Direct, competitive, less empathetic
- 0.4-0.6: Balanced cooperation
- 0.7-1.0: Highly empathetic, cooperative

**Openness** (range: 0.0-1.0)

- Controls receptivity to new ideas and experiences
- 0.0-0.3: Practical, tradition-focused
- 0.4-0.6: Moderate curiosity
- 0.7-1.0: Creative, intellectually curious, adventurous

**Conscientiousness** (range: 0.0-1.0)

- Controls organization, planning, and risk-awareness
- 0.0-0.3: Spontaneous, unstructured, risk-taking
- 0.4-0.6: Balanced planning
- 0.7-1.0: Highly organized, detail-focused, careful

---

## The Mathematical Calculations

### 1. Emotion Blending & Personality Modulation

When a user sends a message, the system extracts emotion vectors via LLM and applies them to the current emotion state. The application uses **Blend Mode** by default, which produces smooth, personality-modulated transitions.

#### Extracted Emotion Vector

The LLM returns emotions as a dictionary:

```python
{
    "joy": 0.80,
    "sadness": 0.10,
    "anger": 0.05,
    "fear": 0.15,
    "trust": 0.70,
    "curiosity": 0.60
}
```

#### Personality Modulation

Each personality trait scales specific emotions during blending:

$$E_i^{\text{mod}} = E_i^{\text{raw}} \times M_i$$

Where $M_i$ is the personality modifier for emotion $i$:

| Emotion       | Primary Modifiers                | Formula                                                                                          |
| ------------- | -------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Joy**       | extraversion, openness           | $M_{\text{joy}} = 1.0 + 0.3 \times \text{extraversion} + 0.2 \times \text{openness}$             |
| **Sadness**   | neuroticism, agreeableness       | $M_{\text{sadness}} = 1.0 + 0.4 \times \text{neuroticism} - 0.3 \times \text{agreeableness}$     |
| **Anger**     | neuroticism, conscientiousness   | $M_{\text{anger}} = 1.0 + 0.5 \times \text{neuroticism} - 0.4 \times \text{conscientiousness}$   |
| **Fear**      | neuroticism, sensitivity         | $M_{\text{fear}} = 1.0 + 0.6 \times \text{neuroticism} + 0.3 \times \text{sensitivity}$          |
| **Trust**     | agreeableness, conscientiousness | $M_{\text{trust}} = 1.0 + 0.4 \times \text{agreeableness} + 0.2 \times \text{conscientiousness}$ |
| **Curiosity** | openness, extraversion           | $M_{\text{curiosity}} = 1.0 + 0.5 \times \text{openness} + 0.2 \times \text{extraversion}$       |

**Example Calculation (Luna's response to a happy message):**

Raw emotion extracted: `{"joy": 0.80}`

Luna's traits: `sensitivity=0.90, extraversion=0.85, openness=0.92, agreeableness=0.78, conscientiousness=0.80, neuroticism=0.25`

Modifier: $M_{\text{joy}} = 1.0 + 0.3 \times 0.85 + 0.2 \times 0.92 = 1.0 + 0.255 + 0.184 = 1.439$

Modulated joy: $0.80 \times 1.439 = 1.151$ (clamped to 1.0)

#### Blend Mode Application

After modulation, the emotion is blended into the current state using exponential smoothing:

$$E_i^{\text{new}} = E_i^{\text{current}} + \alpha \times (E_i^{\text{mod}} - E_i^{\text{current}})$$

Where $\alpha$ (blend factor) = 0.15 for smooth transitions.

**Example Full Blend:**

- Current joy: 0.70
- Modulated incoming joy (from message): 1.0 (clamped)
- Blend: $0.70 + 0.15 \times (1.0 - 0.70) = 0.70 + 0.15 \times 0.30 = 0.70 + 0.045 = 0.745$
- **Result: Joy increases from 0.70 → 0.745** (Δ +0.045 or +6.4%)

This produces gradual, realistic emotional transitions that aren't jarring or overly reactive.

### 2. Sentiment & Intensity Extraction

For every user message, the LLM extracts two scalar values:

**Sentiment**: A continuous value in [-1.0, 1.0]

- -1.0 = extremely negative (angry, frustrated, sad)
- 0.0 = neutral
- +1.0 = extremely positive (happy, enthusiastic, grateful)

**Intensity**: A continuous value in [0.0, 1.0]

- 0.0 = very subdued, passive, detached
- 0.5 = moderate energy level
- 1.0 = highly energetic, passionate, emphatic

#### LLM Extraction Prompt

```
Analyze the user's message and extract:
1. SENTIMENT: A float from -1.0 (very negative) to 1.0 (very positive)
2. INTENSITY: A float from 0.0 (very calm) to 1.0 (very intense/emphatic)

Message: "{user_message}"

Return as JSON:
{
    "sentiment": <float -1.0 to 1.0>,
    "intensity": <float 0.0 to 1.0>,
    "joy": <0.0-1.0>,
    "sadness": <0.0-1.0>,
    ...
}
```

#### Example Extraction

**Message:** "I'm feeling happy today!"

LLM Response:

```json
{
  "sentiment": 0.9,
  "intensity": 0.8,
  "emotions": {
    "joy": 0.9,
    "trust": 0.7,
    "curiosity": 0.5,
    "sadness": 0.05,
    "anger": 0.02,
    "fear": 0.03
  }
}
```

**Interpretation:**

- Sentiment is highly positive (0.90/1.0)
- Intensity is high (0.80/1.0) — the user is enthusiastic, not just mildly content
- Joy dominates at 0.90, with increased trust and curiosity

### 3. Emotion Decay Over Time

Between messages, emotions naturally decay toward a baseline value. This creates emotional "fatigue" and prevents unrealistic extremes.

#### Decay Formula

For each emotion $E_i$ at time $t$:

$$E_i(t + \Delta t) = \text{baseline}_i + (E_i(t) - \text{baseline}_i) \times e^{-\lambda \times \Delta t}$$

Where:

- $\text{baseline}_i$ = 0.10 for all emotions (small residual)
- $\lambda$ = 0.05 per message (decay rate)
- $\Delta t$ = 1 (per message interval)

$$E_i^{\text{next}} = 0.10 + (E_i^{\text{current}} - 0.10) \times e^{-0.05}$$

#### Example Decay Calculation

**Before decay:** Joy = 0.85

$$E^{\text{next}} = 0.10 + (0.85 - 0.10) \times e^{-0.05}$$
$$= 0.10 + 0.75 \times 0.9512$$
$$= 0.10 + 0.7134$$
$$= 0.8134$$

**After decay:** Joy = 0.813 (decreased by 0.037 or 4.4%)

Over many message cycles, this prevents emotions from being "stuck" at extreme values and creates natural emotional rhythm.

### 4. Memory System Architecture

The memory system is dual-layer with sophisticated prioritization and compression.

#### Short-Term Memory: Circular Buffer

Stores the most recent messages in order (FIFO).

```python
class ShortTermMemory:
    def __init__(self, max_size=50):
        self.memory = []  # List of MemoryEntry objects
        self.max_size = 50

    def add(self, entry: MemoryEntry):
        if len(self.memory) >= self.max_size:
            self.memory.pop(0)  # Remove oldest
        self.memory.append(entry)
```

**Entry Structure:**

```python
@dataclass
class MemoryEntry:
    text: str                      # The memory content
    timestamp: datetime            # When it was added
    importance: float              # 0.0-1.0 importance score
    tags: list[str]               # Searchable tags
```

**Calculation:**

- Max size: configurable per profile (default: 50 messages)
- When full, oldest message is discarded automatically
- Linear growth until capacity reached, then stable

#### Long-Term Memory: Importance-Ranked Storage

Stores important memories indefinitely, but triggers compression when full.

```python
class LongTermMemory:
    def __init__(self, max_size=100, llm_client=None):
        self.memory = []  # Sorted by importance (descending)
        self.max_size = 100
        self.llm_client = llm_client

    def add(self, entry: MemoryEntry):
        self.memory.append(entry)
        self.memory = sorted(
            self.memory,
            key=lambda e: e.importance,
            reverse=True
        )
        if len(self.memory) > self.max_size:
            self.minimize_via_llm()
```

#### Long-Term Memory Compression Algorithm

When long-term memory exceeds the configured limit (default: 100 entries), the system triggers **LLM-based minimization** to compress memories while retaining semantic meaning.

**Compression Process:**

1. **Separation by Importance Threshold (τ = 0.7)**
   - HIGH importance (≥ 0.7): Keep as-is (top memories)
   - LOW importance (< 0.7): Candidates for compression

   $$\text{KEEP} = \{m \in M : \text{importance}(m) \geq \tau\}$$
   $$\text{COMPRESS} = \{m \in M : \text{importance}(m) < \tau\}$$

2. **Example Separation**

   Scenario: 105 total entries, τ = 0.7, target = 100
   - KEEP set: 72 entries (all ≥ 0.7 importance)
   - COMPRESS set: 33 entries (< 0.7 importance)
   - Target reduction: 5 entries
   - Token budget for compression: 2000 tokens

3. **LLM Compression Prompt**

   ```
   Compress the following low-importance memories while retaining key facts:

   Memories to compress:
   1. "User mentioned they have a dog" (importance: 0.52)
   2. "User likes pizza" (importance: 0.48)
   3. "User works in tech" (importance: 0.65)
   ... [33 items total]

   Rules:
   - Condense related memories into single entries
   - Remove trivial details
   - Preserve emotional context
   - Combine similar memories
   - Target: 28-30 entries (28% compression)

   Return as JSON array of compressed memories with their importance scores.
   ```

4. **Result Integration**
   - Keep all 72 high-importance entries
   - Replace 33 low-importance entries with ~28 compressed entries
   - Final count: 72 + 28 = 100 entries
   - Compression ratio: 33 → 28 = 15.2% reduction

**Importance Score Calculation**

When a memory is added, its importance is calculated as:

$$\text{importance} = \text{base} \times \text{emotion\_weight} \times \text{recency\_weight}$$

Where:

- **base** = 0.5 (baseline importance for any memory)
- **emotion_weight** = Average of emotion vector components (e.g., if message had joy:0.9, sadness:0.1 avg emotions: 0.4, then weight = 0.4)

  $$\text{emotion\_weight} = \frac{1}{6} \sum_{i=1}^{6} e_i$$

- **recency_weight** = Exponential decay by hours since addition

  $$\text{recency\_weight} = e^{-0.1 \times \text{hours\_since\_add}}$$

**Example Importance Calculation:**

- Memory added: "User talked about their dream vacation"
- Extracted emotions: {joy: 0.80, curiosity: 0.70, others: 0.1 avg}
- Average emotion: (0.80 + 0.70 + 0.1 + 0.1 + 0.1 + 0.1) / 6 = 0.35
- Time since addition: 2 hours
- Recency: $e^{-0.1 \times 2} = e^{-0.2} = 0.8187$

$$\text{importance} = 0.5 \times 0.35 \times 0.8187 = 0.143$$

This low importance score (0.143) means it would be a candidate for compression in the next minimization pass.

---

## Demo Mode

For a non-interactive demonstration of the system:

```bash
python demo.py
```

The demo script:

1. Loads the pre-built "Luna" profile
2. Sends 3 pre-written messages through the emotion system
3. Displays the full UI for each message (message analysis, emotion deltas, agent response)
4. Shows how emotions evolve with each interaction

Expected output includes three complete emotion cycles with side-by-side comparison of before/after states.

---

## File Organization

```
ai-emotions-simulator/
├── main.py                 # Main CLI entry point
├── demo.py                 # Non-interactive demonstration
├── requirements.txt        # Python dependencies
├── .env.example           # OpenAI configuration template
├── README.md              # This file
├── MEMORY_SYSTEM.md       # Detailed memory documentation
├── notes.md               # Development notes
│
├── src/
│   ├── cli.py            # Interactive UI and conversation loop
│   ├── state.py          # Personality and emotion logic
│   ├── memory.py         # Dual-layer memory system
│   └── profile.py        # Profile bundling and persistence
│
├── profiles/             # Persistent profile storage
│   ├── luna/
│   │   ├── profile.json
│   │   ├── short_term_memory.json
│   │   └── long_term_memory.json
│   ├── atlas/           # [same structure]
│   └── sage/            # [same structure]
│
└── tests/
    └── dev-tools/
        └── test_memory.py  # Memory system regression tests
```

---

## Architecture Overview

### Data Flow Diagram

```
User Message
    ↓
[Sentiment/Intensity Extraction via LLM]
    ↓
[Emotion Vector Extraction]
    ↓
[Personality Modulation] ← Personality Traits
    ↓
[Emotion Blending] ← Current Emotion State
    ↓
[Emotion Decay Calculation]
    ↓
[Update Current Emotions] → Store to Short-term Memory
    ↓
[Generate LLM Response colored by current emotions]
    ↓
[Display Dashboard: sentiment, intensity, emotion deltas, agent response]
    ↓
[Check Memory Limits]
    ├─→ If Short-term > max: Remove oldest
    └─→ If Long-term > max: LLM Compression
    ↓
[Save Profile to Disk]
```

### Component Responsibilities

**`cli.py` — User Interface & Orchestration**

- Interactive conversation loop
- Two-step profile selection
- Dashboard rendering (Rich panels/tables)
- Verbose mode output
- Profile save/load triggers

**`state.py` — Emotion & Personality Logic**

- Personality trait definitions (Big Five)
- Emotion state management
- Personality modulation calculations
- Emotion decay over time
- LLM sentiment/intensity/emotion extraction

**`memory.py` — Dual-Layer Memory**

- Short-term circular buffer
- Long-term importance-ranked storage
- LLM-based compression when limits exceeded
- Serialization/deserialization
- File I/O for persistence

**`profile.py` — Profile Bundle**

- Aggregates personality + emotions + memory
- Folder-based persistence (profile.json + memory files)
- Configuration management (memory limits)
- Load/save coordination across components

---

## Configuration

### Memory Limits (per profile)

Set during profile creation:

```
? Max short-term memory entries (default 50): 50
? Max long-term memory entries (default 100): 100
```

These can be modified in `profiles/{name}/profile.json`:

```json
{
    "personality": {...},
    "max_short_term_memory": 50,
    "max_long_term_memory": 100
}
```

**Recommended Settings:**

| Profile Type         | Short-term | Long-term | Rationale                                    |
| -------------------- | ---------- | --------- | -------------------------------------------- |
| Light-weight chatbot | 20         | 50        | Quick responses, minimal memory overhead     |
| Standard agent       | 50         | 100       | Balance between context and performance      |
| Memory-intensive     | 100        | 250       | Deep context retention, more LLM compression |

### LLM Configuration

Edit `.env`:

```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo  # Or gpt-3.5-turbo
```

Model choice affects:

- Emotion classification accuracy (GPT-4 is more nuanced)
- Memory compression quality (GPT-4 better at summarization)
- API cost and latency

---

## Troubleshooting

### Profile Won't Load

**Symptom:** "KeyError: 'profile.json'" when selecting a profile

**Cause:** Corrupted or missing profile file

**Solution:**

1. Check `profiles/{name}/profile.json` exists
2. Verify valid JSON syntax: `python -m json.tool profiles/{name}/profile.json`
3. Delete the profile folder and recreate via CLI

### Memory Compression Fails

**Symptom:** "Exception in compress: [rate limit error]"

**Cause:** OpenAI API rate limit hit during compression

**Solution:**

1. Increase max_long_term_memory to reduce compression frequency
2. Add delay: `time.sleep(5)` before compression in `memory.py`
3. Use cheaper model (gpt-3.5-turbo) for compression

### Emotion State Seems Frozen

**Symptom:** Same emotions every message, no variance

**Cause:** Blend factor too low or emotion decay disabled

**Solution:**

1. Check `state.py` blend factor (should be ~0.15)
2. Verify decay is applied in `update()` method
3. Use `verbose on` to see intermediate calculations

---

## Performance Characteristics

### Time Complexity

| Operation          | Complexity      | Notes                                        |
| ------------------ | --------------- | -------------------------------------------- |
| Add to short-term  | O(1)            | Append to circular buffer                    |
| Add to long-term   | O(n log n)      | Importance-based sort                        |
| Compress long-term | O(n log m)      | LLM call + re-sort (n = entries, m = tokens) |
| Generate response  | O(context_size) | LLM tokenization                             |
| Profile load       | O(1)            | JSON parse from disk                         |
| Profile save       | O(1)            | JSON write to disk                           |

### Space Complexity

| Component         | Storage     | Notes                       |
| ----------------- | ----------- | --------------------------- |
| Profile JSON      | ~2 KB       | Personality + config        |
| Short-term memory | ~50-100 KB  | 50 entries × ~1-2 KB        |
| Long-term memory  | ~200-500 KB | 100 entries × ~2-5 KB       |
| Total per profile | ~300-700 KB | Modest for persistent agent |

---

## Next Steps & Extensions

### Planned Features

1. **Semantic Memory Search**: Embed memories with OpenAI embedding API, retrieve similar memories before generating responses (improves consistency and long-term context)

2. **Relationship Tracking**: Separate memory streams per conversation partner, track cumulative trust/distrust (enables believable long-term dynamics)

3. **Time-Aware Memory Decay**: Older memories lose importance automatically over days/weeks (more realistic forgetting)

4. **Trigger/Trauma System**: Specific keywords amplify emotions beyond normal modulation (creates interesting edge cases and personality quirks)

5. **Web UI**: FastAPI backend + React/Vue frontend for multi-user chat interface

6. **GitHub Actions CI/CD**: Automated testing and linting on push

### Research Directions

- Compare personality modulation approaches (current vs. linear vs. sigmoid)
- Test different blend factors (0.10, 0.15, 0.20) for realism
- Experiment with emotion decay rates (λ = 0.05, 0.10, 0.15)
- Benchmark memory compression vs. naive truncation
- Human evaluation of emotion authenticity

---

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Performance profiling and optimization
- [ ] Expanded unit tests (especially `state.py` calculations)
- [ ] Web UI implementation
- [ ] Additional pre-built profiles
- [ ] Better emotion extraction via fine-tuned models
