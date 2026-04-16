# Pentad Pilot Node (PPN-1) — At-Home DIY Build Guide

**Folder:** `Unitary Pentad/`
**Version:** 1.0 — April 2026
**For:** Complete beginners — no electronics experience required
**Budget:** Phase 0 is FREE.  Full hardware build ≈ $8–12 USD

---

## What You Are Building

The **Pentad Pilot Node (PPN-1)** is a physical Human-in-the-Loop interface
for the Unitary Pentad simulation.

The five Pentad bodies run as mathematics inside your computer:

| LED Color | Body | What it represents |
|-----------|------|--------------------|
| 🔵 Blue  | UNIV  | The physical universe (cosmological manifold) |
| 🟢 Green | BRAIN | Your biology — the neural manifold |
| 🟡 Yellow| **HUMAN** | **You** — the intent layer.  This is the one you steer. |
| ⚪ White | AI    | The precision / execution body |
| 🔴 Red   | TRUST | The coupling field.  If this goes dark, everything collapses. |

**Two physical knobs connect you to the simulation:**

- **Trust Field knob** — controls φ_trust (the red LED + all couplings)
- **Human Intent knob** — steers φ_human (the yellow LED = you)

When you turn the Trust knob down below 10%, all five LEDs dim and chaos
breaks out — that is **TRUST EROSION collapse**, live in your hands.
Turn it back up; watch the system recover.

When all five LEDs hold steady and bright, you have achieved the
**Harmonic State**: five manifolds sharing a single fixed point.

---

## Four Phases — Build Only What You Need

| Phase | What you add | Cost | Skill |
|-------|-------------|------|-------|
| **0** | Software only (terminal display) | $0 | None — just Python |
| **1** | 5-LED visual panel on cardboard | ~$5 | Plug wires into holes |
| **2** | Two physical knobs (Trust + Human Intent) | +$2 | Same — just plug wires |
| **3** | Biometric skin probe (Brain body) | +$1 | Tape coins to fingers |

Do Phase 0 first.  Everything else is optional.

---

---

# PHASE 0 — SOFTWARE ONLY (FREE)

*You only need a computer and Python.  Nothing to build.*

---

## Step 0.1 — Install Python

1. Go to **https://python.org/downloads**
2. Click the big yellow "Download Python 3.x.x" button
3. Run the installer
4. ✅ **Important:** Check the box that says **"Add Python to PATH"** before clicking Install

Test it: open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:
```
python --version
```
You should see something like `Python 3.11.2`.  If you see "not recognized", restart your computer and try again.

---

## Step 0.2 — Get the Repository

If you have Git installed:
```
git clone https://github.com/wuzbak/Unitary-Manifold-.git
cd "Unitary-Manifold-"
```

If you do NOT have Git:
1. Go to https://github.com/wuzbak/Unitary-Manifold-
2. Click the green **Code** button → **Download ZIP**
3. Extract the ZIP to your Desktop
4. Open a terminal and type: `cd Desktop/Unitary-Manifold-`

---

## Step 0.3 — Install Dependencies

In your terminal, inside the repository folder:
```
pip install numpy scipy
```
(Takes about 30 seconds.)

---

## Step 0.4 — Run the Pilot

```
python "Unitary Pentad/pentad_pilot.py"
```

You should see a live display like this:

```
════════════════════════════════════════════════════════════════════════
  PENTAD PILOT NODE (PPN-1)   Step     42   converging...
════════════════════════════════════════════════════════════════════════

  BODY                    φ       BAR                   STATUS
  ──────────────────────  ──────  ────────────────────  ──────────
  ◉ UNIV  (Universe)      1.012  ████████████████░░░░  STABLE
  ◎ BRAIN (Biology)       0.703  ████████████░░░░░░░░  STABLE
  ★ HUMAN (You)           0.601  ██████████░░░░░░░░░░  ← YOU
  ◆ AI    (Precision)     0.812  █████████████░░░░░░░  STABLE
  ♥ TRUST (Coupling)      0.904  ██████████████░░░░░░  OK

  DEFECT:       0.082341   (< 1e-6 = fixed point)
  MAX GAP:      0.641234   (→ 0 at Harmonic State)
  MAX PHASE:    1.2341 rad (π/2 = 1.5708 = reversal threshold)
  TRUST φ:      0.9040     (floor = 0.1)

  Trust  : [████████████████████████░░░░]  0.900
  Human φ: [████████████████░░░░░░░░░░░░]  0.601

  ──────────────────────────────────────────────────────────────────────
  [↑/+] Trust UP   [↓/-] Trust DOWN   [→/]] Human UP   [←/[] Human DOWN
  [SPACE] Reset    [R] Adversarial intent    [Q/ESC] Quit
════════════════════════════════════════════════════════════════════════
```

---

## Step 0.5 — Try These Experiments

**Experiment A — Watch convergence:**
Just wait.  The DEFECT number should fall toward zero.  When it reaches 1e-6
the display shows `✓ HARMONIC STATE`.

**Experiment B — Trust Erosion collapse:**
Press the **DOWN arrow** (or `-`) repeatedly.  Watch the Trust φ drop.
When it falls below **0.10**, all bodies decouple and you see:
```
  ⚠  COLLAPSE: TRUST_EROSION   [▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░] 0.82
```
Press UP to recover.

**Experiment C — Adversarial intent:**
Press **R**.  This injects a large φ_human offset — "malicious intent".
Even with trust intact, `MALICIOUS_PRECISION` fires.
Press SPACE to reset.

**Experiment D — Phase Collision:**
Press `]` rapidly many times, pushing Human Intent above 1.0 while trust
is low.  The Human–AI Moiré phase exceeds π/2 and coupling reverses:
`PHASE_COLLISION` (the "scream" state).

That is Phase 0 — the full simulation, running live, in your terminal.

---

---

# PHASE 1 — THE LED PENTAD PANEL (~$5)

*Build a physical light panel — 5 LEDs, one per body.*

---

## Parts List — Phase 1

| Part | How many | Where to get | Cost |
|------|----------|--------------|------|
| Arduino Nano (or clone) | 1 | Amazon, eBay, AliExpress | ~$3–4 |
| LED — Blue | 1 | Amazon 100-pack (~$2) | ~$0.02 |
| LED — Green | 1 | (same pack) | ~$0.02 |
| LED — Yellow | 1 | (same pack) | ~$0.02 |
| LED — White | 1 | (same pack) | ~$0.02 |
| LED — Red | 1 | (same pack) | ~$0.02 |
| 220Ω resistor (red-red-brown) | 5 | Amazon 300-pack (~$2) | ~$0.10 |
| Breadboard (mini, 400-point) | 1 | Amazon / local electronics | ~$2 |
| Jumper wires (male-male, 10 cm) | 10 | Amazon 40-pack (~$2) | ~$0.50 |
| USB-A to mini-USB or micro-USB cable | 1 | You probably have one | free |
| Cereal box or shoebox | 1 | Your recycling bin | free |
| Scissors | 1 | Your kitchen | free |
| Tape | — | Your kitchen | free |
| Permanent marker | 1 | Your desk | free |

**Total hardware cost: ≈ $5–9 USD** (less if ordering from AliExpress)

**Alternative to breadboard:** Twist wires together and tape with electrical tape.
No soldering needed at any phase.

---

## Tools — Phase 1

- Scissors (or craft knife)
- Nothing else.

---

## Step 1.1 — Understand an LED (2 minutes)

An LED has two legs:
- **Long leg (+)** = positive = anode = connect to resistor then Arduino pin
- **Short leg (−)** = negative = cathode = connect to GND (ground)

```
Arduino pin ──[220Ω]──|►|── GND
                  RESISTOR  LED
```

The resistor protects the LED from burning out.  The 220Ω value works
for every color LED at 5V.

To identify a 220Ω resistor, look at the colored bands:
```
[RED][RED][BROWN][GOLD]
  2    2     0     ±5%   →  220Ω
```

---

## Step 1.2 — Identify Arduino Pins

Your Arduino Nano looks like this (top view, USB port facing up):

```
     ┌─────[USB]─────┐
 D13 ┤               ├ D12
 3V3 ┤               ├ D11  ← TRUST LED (Red)
 REF ┤               ├ D10
  A0 ┤               ├ D9   ← AI LED (White)
  A1 ┤               ├ D8
  A2 ┤               ├ D7
  A3 ┤               ├ D6   ← HUMAN LED (Yellow)
  A4 ┤               ├ D5   ← BRAIN LED (Green)
  A5 ┤               ├ D4
  A6 ┤  [RESET BTN]  ├ D3   ← UNIV LED (Blue)
  A7 ┤               ├ D2
 5V  ┤               ├ GND  ← connect negative legs here
 RST ┤               ├ RST
 GND ┤               ├ RX0
 VIN ┤               ├ TX1
     └───────────────┘
```

Pins used: **D3** (Blue), **D5** (Green), **D6** (Yellow), **D9** (White),
**D11** (Red), and any **GND** pin.

---

## Step 1.3 — Place Components on Breadboard

A breadboard has numbered rows.  Each row of 5 holes on the same side
is internally connected.  The two long rails on the edges (marked + and −)
run the full length.

```
  ┌─────────────────────────────────────┐
  │ + ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● + │  ← power rail (connect to 5V or GND)
  │ − ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● − │  ← ground rail
  │   a b c d e   f g h i j             │
  │ 1 ● ● ● ● ●   ● ● ● ● ●            │  ← row 1 (a-e connected, f-j connected)
  │ 2 ● ● ● ● ●   ● ● ● ● ●            │
  │ ...                                  │
  └─────────────────────────────────────┘
```

**Place each LED:**
1. Push LED into breadboard.  Long leg (+) in column **e**, short leg in column **f** — this straddles the center gap, which means the two legs are NOT connected.
2. Place the **220Ω resistor** with one leg in column **d** (same row as long LED leg) and the other leg 4 rows up.

Repeat for all 5 LEDs, each in its own row section.

---

## Step 1.4 — Wiring (One LED Shown; Repeat for All Five)

For the **Blue LED (UNIV, Pin D3):**

```
Arduino D3 → jumper wire → resistor leg A (row 5, col a)
                           resistor leg B (row 5, col c) → LED long leg (+) (row 5, col e)
                                                           LED short leg (−) (row 5, col f) → GND rail
```

**Simplified:** 
1. Connect one jumper from Arduino **D3** to breadboard row 5, column a
2. Plug 220Ω resistor across columns a–d in row 5
3. Insert Blue LED: long leg in row 5 column e, short leg in row 6 column f
4. Connect GND rail with a jumper from breadboard GND rail to Arduino **GND**

---

## Step 1.5 — Complete Wiring Table

| Arduino Pin | Wire goes to | Component | Then to |
|-------------|-------------|-----------|---------|
| D3  | Resistor leg 1 (Blue)   | 220Ω → Blue LED (+)  | Blue LED (−) → GND |
| D5  | Resistor leg 1 (Green)  | 220Ω → Green LED (+) | Green LED (−) → GND |
| D6  | Resistor leg 1 (Yellow) | 220Ω → Yellow LED (+)| Yellow LED (−) → GND |
| D9  | Resistor leg 1 (White)  | 220Ω → White LED (+) | White LED (−) → GND |
| D11 | Resistor leg 1 (Red)    | 220Ω → Red LED (+)   | Red LED (−) → GND |
| GND | — | — | GND rail (short leg side of all LEDs) |

---

## Step 1.6 — Full Wiring Diagram (ASCII)

```
Arduino Nano                    Breadboard
─────────────                   ───────────────────────────────────

D3  ─────────────────────────── [220Ω] ──── Blue LED  (+) ──┐
D5  ─────────────────────────── [220Ω] ──── Green LED (+) ──┤
D6  ─────────────────────────── [220Ω] ──── Yellow LED(+) ──┤
D9  ─────────────────────────── [220Ω] ──── White LED (+) ──┤  All (−) legs
D11 ─────────────────────────── [220Ω] ──── Red LED   (+) ──┘  to GND rail
GND ───────────────────────────────────────────────────────────── GND rail
```

---

## Step 1.7 — Upload the Arduino Sketch

1. Download **Arduino IDE** (free): https://www.arduino.cc/en/software
2. Open Arduino IDE
3. Plug Arduino Nano into your computer with the USB cable
4. In Arduino IDE: **Tools → Board → Arduino Nano**
5. **Tools → Port → COMx** (Windows) or **/dev/ttyUSBx** (Linux/Mac)
6. Copy and paste the sketch below into the editor
7. Click the **→ Upload** button (right-pointing arrow)

### Arduino Sketch — Phase 1

```cpp
// Pentad Pilot Node — Phase 1 LED Display
// Receives brightness commands from Python via serial.
// Command format:  "B <index> <brightness>\n"
// Example:         "B 2 128\n"  sets LED index 2 to half brightness.

const int LED_PINS[5] = {3, 5, 6, 9, 11};  // UNIV, BRAIN, HUMAN, AI, TRUST
int brightness[5] = {255, 178, 153, 204, 229};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }
}

void loop() {
  // Read one LED brightness command from Python
  if (Serial.available() >= 1) {
    char cmd = Serial.read();
    if (cmd == 'B') {
      int idx = Serial.parseInt();
      int val = Serial.parseInt();
      if (idx >= 0 && idx < 5 && val >= 0 && val <= 255) {
        brightness[idx] = val;
      }
    }
  }

  // Update all LEDs
  for (int i = 0; i < 5; i++) {
    analogWrite(LED_PINS[i], brightness[i]);
  }
}
```

---

## Step 1.8 — Run with Hardware

Install pyserial (one time only):
```
pip install pyserial
```

Run the pilot with your serial port:
```
# Linux / Mac (find your port with: ls /dev/tty*)
python "Unitary Pentad/pentad_pilot.py" --port /dev/ttyUSB0

# Windows (find your port in Device Manager → Ports → COMx)
python "Unitary Pentad/pentad_pilot.py" --port COM3

# Let the script find it automatically:
python "Unitary Pentad/pentad_pilot.py" --port auto
```

You should see `● Hardware connected (LED panel active)` in the display.

**What to look for:**
- All 5 LEDs should glow at different brightnesses matching the φ values
- Press DOWN to drop Trust — the Red LED dims and all others flicker
- Press SPACE to reset — LEDs stabilise again

---

## Step 1.9 — Build the Housing (Optional but Satisfying)

**Materials:** Any cardboard box (cereal box works perfectly)

1. Place the five LEDs in a **pentagon pattern** on the top of the box:
   - One LED at each corner of an imaginary pentagon (about 3 cm apart)
   - UNIV at top, BRAIN upper-right, AI lower-right, TRUST lower-left, HUMAN upper-left

2. Mark the positions with a pencil, then poke 5 holes with a pencil tip

3. Push each LED through from the inside (legs inside the box)

4. Tape the LED legs to the inside of the box lid so they can't pull back through

5. The breadboard and Arduino sit inside the box

6. Cut a small notch in the back of the box for the USB cable

7. Label each LED with a marker: UNIV, BRAIN, HUMAN, AI, TRUST

```
                ╭────────────────────────────────────╮
                │      PENTAD PILOT NODE v1.0         │
                │                                     │
                │          ●  UNIV (Blue)              │
                │       ●           ●                  │
                │    HUMAN          BRAIN              │
                │    (Yellow)       (Green)            │
                │       ●           ●                  │
                │    TRUST          AI                 │
                │    (Red)          (White)            │
                │                                     │
                ╰────────────────────────────────────╯
                             [USB cable out back]
```

---

---

# PHASE 2 — TRUST FIELD CONTROLLER (+~$2)

*Add two physical knobs — you become truly in-the-loop.*

---

## Additional Parts for Phase 2

| Part | How many | Where to get | Cost |
|------|----------|--------------|------|
| 10kΩ potentiometer (B10K) | 2 | Amazon 10-pack (~$2) | ~$0.40 |
| 3 jumper wires per pot (6 total) | 6 | (already have from Phase 1) | free |

A potentiometer (pot) is a variable resistor with a knob.  It has 3 legs:
- Left leg → GND
- Middle leg → Analog pin (reads the voltage)
- Right leg → 5V

As you turn the knob, the middle leg voltage slides from 0V to 5V, which
the Arduino reads as a number from 0 to 1023.

---

## Step 2.1 — Wiring the Potentiometers

**Trust Field potentiometer (Pot 1):**
```
Pot 1 left leg  → GND
Pot 1 middle leg → Arduino A5
Pot 1 right leg → Arduino 5V
```

**Human Intent potentiometer (Pot 2):**
```
Pot 2 left leg  → GND
Pot 2 middle leg → Arduino A4
Pot 2 right leg → Arduino 5V
```

**Full wiring addition:**
```
Arduino A5 ───── Pot 1 middle (wiper) ─── Trust knob
Arduino A4 ───── Pot 2 middle (wiper) ─── Human Intent knob
5V         ───── Pot 1 right, Pot 2 right
GND        ───── Pot 1 left, Pot 2 left   (can share GND rail)
```

---

## Step 2.2 — Update the Arduino Sketch for Phase 2

Delete the Phase 1 sketch and replace with this one:

```cpp
// Pentad Pilot Node — Phase 2: LED Display + Potentiometer Controllers
// Receives:  "B <index> <brightness>\n"
// Sends:     "P <trust_float> <human_float>\n"  every 50 ms

const int LED_PINS[5] = {3, 5, 6, 9, 11};
const int POT_TRUST   = A5;
const int POT_HUMAN   = A4;

int brightness[5] = {255, 178, 153, 204, 229};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }
}

void loop() {
  // Process LED commands from Python
  while (Serial.available() >= 1) {
    char cmd = Serial.read();
    if (cmd == 'B') {
      int idx = Serial.parseInt();
      int val = Serial.parseInt();
      if (idx >= 0 && idx < 5) {
        brightness[idx] = constrain(val, 0, 255);
      }
    }
  }

  // Update LEDs
  for (int i = 0; i < 5; i++) {
    analogWrite(LED_PINS[i], brightness[i]);
  }

  // Send pot readings to Python every 50 ms
  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 50) {
    float trust_v = analogRead(POT_TRUST) / 1023.0;
    float human_v = analogRead(POT_HUMAN) / 1023.0;
    Serial.print("P ");
    Serial.print(trust_v, 3);
    Serial.print(" ");
    Serial.println(human_v, 3);
    lastSend = millis();
  }
}
```

Upload the new sketch using the same process as Step 1.7.

---

## Step 2.3 — Physical Pot Placement on Panel

Cut two holes in the box (or panel) for the potentiometer shafts:

```
╭────────────────────────────────────────────────────────╮
│                 PENTAD PILOT NODE v1.0                 │
│                                                        │
│        ●UNIV    ●BRAIN    ●HUMAN    ●AI    ●TRUST      │
│                                                        │
│    ╭──────╮                         ╭──────╮          │
│    │TRUST │                         │HUMAN │          │
│    │FIELD │                         │INTENT│          │
│    ╰──────╯                         ╰──────╯          │
│                                                        │
│    [turn left = collapse]           [turn = you steer] │
╰────────────────────────────────────────────────────────╯
```

Push the pot shaft through the hole, hold it with a nut (usually included)
or a dab of hot glue.

**To run:** same command as Phase 1 (the Python script detects the pots
automatically via the serial "P" messages).

---

## Step 2.4 — What to Feel

- **Turn Trust knob fully left (CCW)** → φ_trust → 0 → TRUST EROSION
  All LEDs dim.  Bodies decouple.  The system "screams".
- **Turn Trust knob slowly up** → system rebuilds coupling, LEDs stabilise
- **Turn Human Intent knob right** → φ_human increases → you push harder
- **Turn both knobs to center** → near-harmonic conditions → wait for ✓

The asymmetry of trust (easy to lose, slow to rebuild) is now literally
in your hands.

---

---

# PHASE 3 — BIOMETRIC COUPLING (+~$1, OPTIONAL)

*Connect your biology to Body 2 (Brain) — become part of the circuit.*

---

## What This Does

Your skin's electrical resistance changes with your physiological state:
- Calm, focused: higher resistance (lower conductance)
- Startled, stressed: lower resistance (higher conductance)

This is **Galvanic Skin Response (GSR)** — the same signal used in
polygraph (lie detector) machines.

We use a **simple voltage divider** with a 10kΩ resistor and your skin
as the second resistor.  The Arduino reads the voltage between them and
maps it to φ_brain in the simulation.

**You become Body 2 — the Biological Observer.**

---

## Additional Parts for Phase 3

| Part | How many | Where to get | Cost |
|------|----------|--------------|------|
| Copper coins (pennies) OR copper foil strips | 2 | Pocket change | $0.02 |
| 10kΩ resistor (same type as Phase 2 pots) | 1 | (already have) | free |
| Alligator clip leads OR twist-and-tape | 2 | Amazon ~$2 for 10 / household | ~$0.40 |
| 3 jumper wires | 3 | (already have) | free |

---

## Step 3.1 — Wiring the Skin Probe

```
                     10kΩ
Arduino 5V ─────────[■■■]──── Arduino A3 ──── Coin 1 (right hand)
                                              (skin resistance)
Arduino GND ─────────────────────────────── Coin 2 (left hand)
```

This is a **voltage divider**:
- 5V drives current through the 10kΩ resistor and then through your skin
- Arduino A3 reads the voltage between them
- High skin resistance → voltage closer to 5V → high reading → calm → high φ_brain
- Low skin resistance → voltage pulled toward GND → low reading → stressed → low φ_brain

---

## Step 3.2 — Making the Probes

**Option A — Copper coins:**
1. Sand two pennies with fine sandpaper to clean the surface
2. Attach an alligator clip to each coin
3. Run the other end of each alligator clip to jumper wires
4. Connect Coin 1 (alligator wire) → Arduino A3
5. Connect Coin 2 (alligator wire) → Arduino GND

**Option B — Copper foil tape:**
1. Cut two 3 cm × 3 cm pieces of copper foil tape (from hardware store / Amazon)
2. Attach jumper wires by folding the foil around the wire tip and taping
3. Same connections as above

**Wearing the probes:**
- Place Coin 1 on the palm of your right hand, index finger
- Place Coin 2 on the palm of your right hand, ring finger
- Hold them gently — do not squeeze hard (that saturates the sensor)
- Let your skin make light contact

---

## Step 3.3 — Update the Arduino Sketch for Phase 3

Add the biometric reading to the Phase 2 sketch:

```cpp
// Pentad Pilot Node — Phase 3: LED + Pots + Biometric Skin Probe
// Sends:  "P <trust_float> <human_float> <brain_float>\n"

const int LED_PINS[5] = {3, 5, 6, 9, 11};
const int POT_TRUST   = A5;
const int POT_HUMAN   = A4;
const int SKIN_PIN    = A3;

int brightness[5] = {255, 178, 153, 204, 229};

// Simple moving-average filter for skin sensor (reduces noise)
float skin_avg = 0.5;
const float SKIN_ALPHA = 0.05;  // low-pass smoothing factor

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 5; i++) {
    pinMode(LED_PINS[i], OUTPUT);
  }
}

void loop() {
  while (Serial.available() >= 1) {
    char cmd = Serial.read();
    if (cmd == 'B') {
      int idx = Serial.parseInt();
      int val = Serial.parseInt();
      if (idx >= 0 && idx < 5) {
        brightness[idx] = constrain(val, 0, 255);
      }
    }
  }

  for (int i = 0; i < 5; i++) {
    analogWrite(LED_PINS[i], brightness[i]);
  }

  static unsigned long lastSend = 0;
  if (millis() - lastSend >= 50) {
    float trust_v = analogRead(POT_TRUST) / 1023.0;
    float human_v = analogRead(POT_HUMAN) / 1023.0;
    float skin_raw = analogRead(SKIN_PIN) / 1023.0;
    // Low-pass filter: prevents jumpy readings from affecting the simulation
    skin_avg = SKIN_ALPHA * skin_raw + (1.0 - SKIN_ALPHA) * skin_avg;

    Serial.print("P ");
    Serial.print(trust_v, 3);
    Serial.print(" ");
    Serial.print(human_v, 3);
    Serial.print(" ");
    Serial.println(skin_avg, 3);
    lastSend = millis();
  }
}
```

---

## Step 3.4 — Update pentad_pilot.py for Phase 3 (Skin)

The Python script needs to receive the third value from the Arduino and
apply it to Body 2 (BRAIN).  Add this to `_arduino_thread` in
`pentad_pilot.py` (in the `if len(parts) == 3:` block, change to
`if len(parts) >= 3:` and add):

```python
# Phase 3: also read brain/skin value if present
if len(parts) == 4:
    brain_pot = float(parts[3])
    brain_phi = PHI_MIN + brain_pot * (PHI_MAX - PHI_MIN)
    _set_body_phi(state, PentadLabel.BRAIN, brain_phi)
```

*(The `_arduino_thread` function already handles 2-value "P" messages;
this is a one-line addition for when a third value arrives.)*

---

## Step 3.5 — What to Experience with Phase 3

1. Attach the skin probes loosely to your fingertips
2. Run the pilot: `python "Unitary Pentad/pentad_pilot.py" --port auto`
3. Breathe slowly.  Watch the GREEN (Brain) LED — it should hold steady.
4. Think of something stressful.  The GREEN LED should dim or flicker.
5. Take a slow deep breath.  GREEN LED recovers.
6. Notice how Brain flickering affects all other bodies through the
   coupling matrix — even UNIV (blue) will shimmer when you're stressed,
   because φ_brain is part of the trust-modulated orbit.
7. Now try to consciously bring the system to Harmonic State:
   - Breathe evenly (keeps Brain φ stable)
   - Hold Trust knob at center (keeps Trust φ ≈ 0.9)
   - Hold Human Intent knob at center (keeps Human φ ≈ 0.6)
   
   When all five LEDs hold steady and bright → **✓ HARMONIC STATE**.

You are now Body 2, Body 3, and Body 5 simultaneously.

---

---

# CALIBRATION AND OPERATION

---

## First Power-On Checklist

☐ USB cable connected from Arduino to computer
☐ Python pilot running (`python "Unitary Pentad/pentad_pilot.py" --port auto`)
☐ Terminal shows `● Hardware connected` (if hardware attached)
☐ All 5 LEDs light up (they may be at different brightnesses — that is correct)
☐ DEFECT value is decreasing each second
☐ Knobs respond (turn Trust knob — LEDs should change)

---

## Normal Startup Behaviour

| Time | What you see | What is happening |
|------|-------------|-------------------|
| 0–5s | DEFECT ≈ 0.5–1.0, MAX GAP ≈ 0.5 | Bodies starting far from shared fixed point |
| 5–30s | DEFECT falling, LEDs stabilising | Pentagonal coupling pulling bodies together |
| 30–120s | DEFECT < 0.01, gaps shrinking | Approaching Harmonic State |
| Variable | `✓ HARMONIC STATE` | All 10 pairwise gaps < tolerance |

The time to Harmonic State depends on your initial knob positions.
If Trust knob is fully left (low φ), the system never converges — there
is not enough coupling energy.  Move Trust knob to center first.

---

## Using the System Daily

The PPN-1 is designed to be a **practice instrument** — not a one-time demo.

**Daily calibration sequence (5 minutes):**

1. Plug in, run the pilot
2. Set Trust knob to center (φ ≈ 0.75)
3. Set Human Intent knob to center (φ ≈ 0.75)
4. (Phase 3) Attach skin probes, breathe normally for 30 seconds
5. Wait for HARMONIC STATE
6. Now explore:
   - Slowly decrease Trust — feel the collapse threshold
   - Slowly increase Human Intent past 1.0 — watch for MALICIOUS PRECISION
   - Bring everything back to center — practice recovery

**What you are training:**
The same dynamics that govern the Pentad simulation are the dynamics
described in `IMPLICATIONS.md`: trust as energy, coupling as obligation,
collapse as cascade.  Operating the physical panel builds an embodied
intuition for these dynamics that reading about them cannot provide.

---

---

# TROUBLESHOOTING

---

## Hardware

| Problem | Most likely cause | Fix |
|---------|------------------|-----|
| LED doesn't light at all | LED inserted backwards | Flip the LED around (swap long and short legs) |
| LED always full brightness regardless of simulation | Wrong pin / resistor missing | Check wiring against the table in Step 1.5 |
| LED flickers rapidly | Loose wire | Press jumper wires firmly into breadboard holes |
| All LEDs off | Arduino not powered | Check USB connection; try a different USB port |
| Serial "connection refused" error | Wrong port name | Check Device Manager (Windows) or `ls /dev/tty*` (Linux/Mac) |
| Arduino upload fails | Wrong board type | Tools → Board → Arduino Nano; try "Old Bootloader" under Processor |
| Pots not responding | A4/A5 wired to wrong pins | Swap pot middle-leg wires to A4 and A5 |
| Skin sensor always 0.01 | Probes not touching skin | Press coins gently against two different fingers |
| Skin sensor always 1.0 | Probes shorted together | Make sure the two coins are on different fingers, not touching each other |

---

## Software

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: numpy` | numpy not installed | `pip install numpy scipy` |
| `ModuleNotFoundError: serial` | pyserial not installed | `pip install pyserial` |
| `ModuleNotFoundError: pentad_scenarios` | Running from wrong folder | `cd` into the repository root first, then run the command |
| Display looks like random characters | Terminal too small | Make terminal window larger (at least 80 columns × 40 rows) |
| Display doesn't update live on Windows | curses issue | Add `--no-curses` flag to the run command |
| `PermissionError` on serial port (Linux) | USB permission | Run: `sudo usermod -a -G dialout $USER` then log out and back in |

---

---

# QUICK REFERENCE CARD

Cut out and tape to your panel.

```
┌─────────────────────────────────────────────────────────┐
│           PENTAD PILOT NODE (PPN-1)                     │
│               QUICK REFERENCE                           │
├─────────────────────────────────────────────────────────┤
│ BODIES       φ        LED      WHAT IT MEANS            │
│ UNIV         1.0      Blue     Universe — cosmological   │
│ BRAIN        0.7      Green    Biology — your body      │
│ HUMAN        0.6      Yellow   YOU — intent layer       │
│ AI           0.8      White    Precision / execution    │
│ TRUST        0.9      Red      Coupling — THE GLUE      │
├─────────────────────────────────────────────────────────┤
│ TRUST FLOOR = 0.10                                      │
│ Below this → ALL bodies decouple → COLLAPSE             │
├─────────────────────────────────────────────────────────┤
│ KEYBOARD CONTROLS                                       │
│ ↑ / +     Trust UP       ↓ / -     Trust DOWN          │
│ → / ]     Human UP       ← / [     Human DOWN          │
│ SPACE     Reset          R         Adversarial intent  │
│ Q / ESC   Quit                                         │
├─────────────────────────────────────────────────────────┤
│ COLLAPSE MODES                                         │
│ TRUST_EROSION     → Turn Trust knob UP                 │
│ AI_DECOUPLING     → Press SPACE (reset)                │
│ PHASE_COLLISION   → Press SPACE (reset)                │
│ MALICIOUS_PREC.   → Press SPACE (reset)                │
├─────────────────────────────────────────────────────────┤
│ RUN COMMAND                                             │
│ python "Unitary Pentad/pentad_pilot.py" --port auto    │
└─────────────────────────────────────────────────────────┘
```

---

---

# GOING FURTHER

---

## Upgrade Ideas (All Still Cheap)

**A — RGB LEDs (~$3 extra):**
Replace the 5 single-color LEDs with common-cathode RGB LEDs.
Use 3 PWM pins per LED (15 pins total — use a second Arduino Nano or
an I²C expander like PCA9685).
Map color to both φ value (brightness) and collapse status (hue):
- Green glow = healthy / converging
- Yellow glow = mild warning
- Red glow = collapse mode active

**B — OLED display (~$4 extra):**
A tiny 128×64 I²C OLED screen (SSD1306) can show the full
defect/gap/phase numbers without needing a computer screen.
Library: `Adafruit_SSD1306` (install via Arduino Library Manager).

**C — Buzzer alarm (~$1 extra):**
A passive piezo buzzer on pin D8, triggered by the Arduino when the
Python pilot sends a "COLLAPSE" flag, provides an auditory collapse
warning.  Short triple beep = TRUST_EROSION.  Long tone = PHASE_COLLISION.

**D — Second skin probe on a second person:**
Run a second GSR circuit on another person (use Arduino A2).
Map Person 1 → φ_brain, Person 2 → φ_human.
Two people, each affecting the simulation via their body.
Two bodies in the Pentad loop simultaneously.

---

## Theory Connection

Everything you feel turning the Trust knob is formally described in:

- `IMPLICATIONS.md` — The Good (Harmonic State), The Bad (Collapse), The Wildcard
- `STABILITY_ANALYSIS.md` — Why the trust floor exists and what happens below it
- `unitary_pentad.py` — The exact equations your hands are operating
- `pentad_scenarios.py` — The collapse-detection logic you are triggering live

The Pentad is not a metaphor.  The hardware panel is not a toy.
You are operating the actual fixed-point iteration with your hands.

---

*DIY Prototype Guide version 1.0 — April 2026*
*Theory: ThomasCory Walker-Pearson*
*Implementation & synthesis: GitHub Copilot (AI)*
*Part of the `Unitary Pentad/` folder — see `README.md` for the full module index.*
