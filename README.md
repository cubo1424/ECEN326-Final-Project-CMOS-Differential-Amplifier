# CMOS Two-Stage Miller-Compensated Differential Amplifier (8 Ω Load)
### ECEN 326: Electronic Circuits — Final Design & Optimization Project
**Department of Electrical & Computer Engineering | Texas A&M University**  
**Authors:** Charlie Wright, Kyle Tran (`cubo1424`)  
**Date:** Fall 2026

---

## Project Overview

This repository contains the complete design, theoretical derivations, SPICE simulation verification, and autonomous multi-agent optimization framework for a **Two-Stage CMOS Differential Amplifier with Miller Frequency Compensation** designed to drive an **$8.0\,\Omega$ load** under a single **$5.0\text{ V}$ unipolar supply**.

The design combines an integrated monolithic CMOS differential pair (**CD4007UB**) with a discrete power MOSFET push-pull stage (**IRLZ44N / FQP27P06**) biased in Class-AB. Parameter optimization was automated using a closed-loop multi-agent AI framework coupling batch **ngspice** simulations, programmatic metric extraction, and automated decision-making.

---

## Performance Summary vs. Project Targets

| Performance Metric | Project Specification | Hand Design ($V_{AB} = -0.95\text{V}$) | Baseline Simulation | Optimized Candidate | Compliance Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Loaded Voltage Gain ($A_v$)** | $\ge 25.0\text{ V/V}$ ($28.0\text{ dB}$) | $27.16\text{ V/V}$ ($28.7\text{ dB}$) | $1.18\text{ V/V}$ | **$27.25\text{ V/V}$** ($28.7\text{ dB}$) | **PASS** |
| **Input Resistance ($R_{in}$)** | $\ge 200\text{ k}\Omega$ at $10\text{ kHz}$ | $> 10\text{ M}\Omega$ (MOS Gate) | $> 10\text{ M}\Omega$ | **$> 10\text{ M}\Omega$** | **PASS** |
| **Upper 3 dB Cutoff ($f_{3\text{dB}}$)**| $> 200\text{ kHz}$ | $1.35\text{ MHz}$ (Closed-Loop) | $37.5\text{ kHz}$ | **$1.32\text{ MHz}$** | **PASS** |
| **Total Harmonic Distortion (THD)**| $< 3.16\%$ ($-30\text{ dB}$) | $< 0.5\%$ | $0.93\%$ | **$0.2306\%$** ($-52.7\text{ dB}$) | **PASS** |
| **Total Supply Power ($P_{tot}$)** | Minimize | $44.60\text{ mW}$ | $0.53\text{ mW}$ | **$44.39\text{ mW}$** | **PASS** |

---

## Circuit Architecture

1. **Stage 1 (Matched Input Pair & Active Load):**
   * Transistors $M_1$–$M_4$ implemented using the monolithic **CD4007** CMOS array to ensure thermal matching and minimize threshold voltage differentials.
   * NMOS differential pair ($M_1, M_2$) biased by a constant tail current source ($I_{tail} = 350\,\mu\text{A}$).
   * Active PMOS current mirror load ($M_3, M_4$) converts differential input swing to a high-impedance single-ended output at node `v_stage1`.
   * Unloaded first-stage gain: $A_{v1} \approx -g_{m1}(r_{o2} \parallel r_{o4}) \approx -79.7\text{ V/V}$ ($38.0\text{ dB}$).

2. **Class-AB Level-Shifter & Biasing:**
   * Precision gate level-shifter ($V_{AB} = -0.95\text{ V}$) inserted between `v_stage1` and `v_gate_pmos`.
   * Overcomes the combined gate threshold ($V_{TO,n} + |V_{TO,p}| = 1.5\text{ V} + 2.5\text{ V} = 4.0\text{ V}$), establishing an effective gate overdrive $V_{OV,tot} = 50\text{ mV}$.
   * Fixes the quiescent idle current at $I_{D,out} \approx 8.5\text{ mA}$, eliminating crossover deadband distortion while constraining static dissipation to $44.4\text{ mW}$.

3. **Stage 2 (Push-Pull Power Buffer):**
   * High-current, discrete through-hole TO-220 power MOSFETs:
     * **Infineon IRLZ44NPBF** ($55\text{ V}, 47\text{ A}, R_{DS(on)} = 22\text{ m}\Omega$, Logic-Level N-Channel)
     * **onsemi FQP27P06** ($-60\text{ V}, -27\text{ A}, R_{DS(on)} = 70\text{ m}\Omega$, P-Channel)
   * Combined transconductance $g_{m,tot} = g_{m5} + g_{m6} \approx 1.414\text{ S}$, driving the AC-coupled $8\,\Omega$ load through a $1000\,\mu\text{F}$ capacitor ($C_{OUT}$).

4. **Compensation & Negative Feedback:**
   * **Miller Capacitor ($C_C = 1.0\text{ pF}$):** Performs pole-splitting across Stage 1 and Stage 2, ensuring stability and wideband operation ($f_{3\text{dB}} = 1.32\text{ MHz}$).
   * **Non-Inverting Closed-Loop Feedback:** $R_1 = 10\text{ k}\Omega$, $R_2 = 270\text{ k}\Omega$, and DC-blocking capacitor $C_{DC} = 100\,\mu\text{F}$ set the ideal closed-loop gain $A_v = 1 + R_2 / R_1 = 28.0\text{ V/V}$.

---

## Multi-Agent AI Framework

The design parameters ($I_{tail}, C_C, V_{AB}$) were converged using an automated multi-agent closed-loop optimization architecture:

```
                  ┌─────────────────────────────────┐
                  │    Planner Agent (run.py)       │
                  │  Generates (Itail, CC, V_AB)    │
                  └───────────────┬─────────────────┘
                                  │ Proposes netlist vars
                                  ▼
                  ┌─────────────────────────────────┐
                  │ Simulation Agent                │
                  │ (ngspice_interface.py)          │
                  │ Executes batch ngspice & parses │
                  └───────────────┬─────────────────┘
                                  │ Raw metrics (Gain, f3dB, THD, Ptot)
                                  ▼
                  ┌─────────────────────────────────┐
                  │    Critic Agent (analyze.py)    │
                  │  Evaluates constraints & logs   │
                  └───────────────┬─────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 │                                 │
           [Violates Specs]                 [All Specs Pass]
                 │                                 │
                 ▼                                 ▼
         Planner adjusts                   Optimal Netlist
         (Negative Feedback)               Exported & Locked
```

* **Simulation Agent (`ngspice_interface.py`):** Updates `amplifier_baseline.cir`, runs `ngspice` in batch mode (`-b`), and extracts scalar metrics using regex.
* **Critic Agent (`analyze.py`):** Evaluates constraints ($A_v \ge 25\text{ V/V}$, $f_{3\text{dB}} > 200\text{ kHz}$, $\text{THD} < 3.16\%$, $P_{tot} < 10\text{ W}$) and outputs diagnostic critique strings.
* **Planner Agent (`run.py`):** Coordinates iterations and parameter transitions, recording history to `iteration_log.csv`.

---

## Repository Structure

```text
├── amplifier_baseline.cir      # Deliverable D6: Final verified SPICE netlist
├── circuit.inc                 # SPICE subcircuit inclusions and shared definitions
├── run.py                      # Multi-agent optimization orchestrator (Planner Agent)
├── analyze.py                  # Evaluation & constraint validation (Critic Agent)
├── ngspice_interface.py        # ngspice batch execution & metric parser (Simulation Agent)
├── D4_plot_convergence.py      # Deliverable D4: Optimization trajectory plotting script
├── D5_plot_verification.py     # Deliverable D5: Bode, transient, and FFT spectrum generator
├── iteration_log.csv           # Deliverable D3: Recorded agent optimization history
├── results/
│   ├── convergence_plot.png    # Deliverable D4: 4-quadrant convergence plot
│   └── spice_verification_d5.png # Deliverable D5: Bode, transient, and FFT figure
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules (protects .env and caches)
└── README.md                   # Project documentation
```

---

## Getting Started

### Prerequisites

* **Python 3.10+**
* **ngspice (Release 38+ or Spice64)**: Ensure `ngspice` is installed. On Windows, default path configured is `C:\Users\<user>\Downloads\Spice64\bin\ngspice.exe` (update path in `ngspice_interface.py` if different).

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/cubo1424/ECEN326-Final-Project-CMOS-Differential-Amplifier.git
   cd ECEN326-Final-Project-CMOS-Differential-Amplifier
   ```

2. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Or manually install: `pip install matplotlib numpy pandas`)*

---

## Reproduction & Verification

### 1. Run Baseline SPICE Simulation
Execute the simulation agent directly to run the optimized netlist and display performance metrics:
```powershell
python .\ngspice_interface.py
```

Expected output:
```text
--- SIMULATION RESULTS ---
THD: 0.2306% (Target: < 3.16%)
Total Power: 44.39 mW
AC Gain: 27.25 V/V (Target: >= 25)
3dB Bandwidth: 1321370.0 Hz (Target: > 200,000 Hz)
```

### 2. Generate Deliverable D4 (Convergence Plot)
Plot the multi-agent optimization convergence trajectory across all 15 iterations:
```powershell
python .\D4_plot_convergence.py
```
*Output file:* `results/convergence_plot.png`

### 3. Generate Deliverable D5 (SPICE Verification Figures)
Generate the 3-panel figure showing the AC Bode frequency response, steady-state $10\text{ kHz}$ transient waveform, and harmonic distortion FFT spectrum:
```powershell
python .\D5_plot_verification.py
```
*Output file:* `results/spice_verification_d5.png`

### 4. Execute Multi-Agent Optimization Loop
To run the automated parameter tuning loop from scratch:
```powershell
python .\run.py
```

---

## Bill of Materials (BOM — Deliverable D2)

| Designator | Description | Manufacturer | Part Number | Package | Mouser Part Number |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$U_1$ ($M_1$–$M_4$)** | Matched CMOS Transistor Array | Texas Instruments | CD4007UBE | 14-pin DIP | `595-CD4007UBE` |
| **$M_5$** | Power MOSFET P-Ch 60V 27A $70\text{ m}\Omega$ | onsemi | FQP27P06 | TO-220-3 | `512-FQP27P06` |
| **$M_6$** | Power MOSFET N-Ch 55V 47A $22\text{ m}\Omega$ | Infineon | IRLZ44NPBF | TO-220-3 | `942-IRLZ44NPBF` |
| **$C_{OUT}$** | Audio Coupling Capacitor $1000\,\mu\text{F}$ 16V | Nichicon | UVP1C102MHD | Radial | `647-UVP1C102MHD` |
| **$C_C$** | Ceramic Disc Compensation Cap $1.0\text{ pF}$ 50V | Vishay | K102K15X7RF5TL2 | Radial | `75-K102K15X7RF5TL2` |
| **$R_L$** | Power Load Resistor $8.0\,\Omega$ 10W 1% | Vishay / Dale | CW0108R000JE73 | Axial | `71-CW0108R000JE73` |

---

## License

This project was developed for academic coursework in **ECEN 326 (Electronic Circuits)** at Texas A&M University. All rights reserved.