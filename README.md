# ECEN 326 transistor-level SPICE starter

These are **provisional topology and intentionally generic proxy transistor
models**, not validated simulations of ALD1101APAL, ALD1102APAL, BSS214NW,
or BSS223PW. They cannot be used as the preliminary report's manufacturer-model
simulation results. The deck checks whether the circuit wiring and scripted
analysis execute. Device screening, matching characterization, gain, bandwidth,
THD, swing, and power remain unproven for the physical parts.

## Files

- `circuit.inc`: an explicit two-stage CMOS circuit, 5 V supply, matched-pair
  differential stage with active mirror load, AC-coupled complementary output
  stage, 10 pF Miller capacitor, and AC-coupled 8-ohm load.
- `models/PROXY_ONLY.lib`: rough generic Level-1 models with conspicuous proxy
  names. Replace with verified part models, pin mappings, and actual fitted
  parameters before calling results representative of selected parts.
- `open_loop_ac.cir`: DC operating point and AC gain and input resistance from
  100 Hz to 10 MHz (including the required 100 Hz–100 kHz range and an extension
  beyond the specified 200 kHz cutoff).
- `open_loop_tran.cir`: 5 mV, 10 kHz input, transient output and `fourier` THD.
- `inverting_500mV.cir`: separate 500 mV peak input through standard-value
  220 kOhm input and 910 kOhm feedback resistors; output is fed back to the
  **inverting first-stage gate**. Measures transient supply power, device
  dissipation, and Fourier THD; these resistor values are merely a proposal.
- `open_loop_swing.cir`: 500 mV peak drive into the provisional open-loop
  circuit to expose clipping, output swing, current, and device dissipation.
- `ngspice_interface.py`, `run.py`: run the decks via `libngspice.so.0` and
  record raw text and AC/transient numerical data. `python run.py` from this
  folder. The runner reports failures. Requires Python 3 and libngspice.
- `analyze.py`: regenerates the proxy-only plots and failures table. Requires
  numpy and matplotlib; run `python analyze.py` after `run.py`.

## Important open issues

1. The generic models do not reproduce the output transistors' transfer curves
   or package thermal behavior. Vendor models or measured Vt/K/lambda and a
   validated gate-capacitance model are required. The exact BSS and ALD vendor
   models were not included because they were not obtained and verified here.
2. Check that the lab allows SOT-323 adapters and a series output capacitor.
3. The inverting 500 mV test is scripted, but its proposed feedback factor
   and results cannot be validated until the circuit and part models are
   verified. Failure to reach 2 V peak or the distortion target is a failure,
   and cannot be hidden by the proxy simulation.
4. These files are distinct from `ECEN326_Simulation_Agent_Scaffold.zip`.
   That earlier ZIP runs RC smoke tests for the scripted simulator interface;
   its ten iterations are **not** amplifier results.

The project requires a stable hand design and every analysis before the
optimization loop. Failed constraints must remain visible in the report.

## Run it

From the extracted folder, run `python run.py` then `python analyze.py`.
Open `results/PROXY_results_summary.md` for the actual exploratory failures;
the raw ngspice text and numerical traces are retained under `results/`.
On a system without `libngspice.so.0`, the `.cir` files can be loaded into
an ngspice installation, but the included `run.py` needs that shared library.
