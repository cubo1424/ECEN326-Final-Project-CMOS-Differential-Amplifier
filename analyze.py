"""Plot the executed generic-model examples and list failed specs.

For debugging and traceability only: these plots cannot certify selected parts.
"""
from pathlib import Path
import json
import math
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'


def messages(name):
    return '\n'.join(json.loads((OUT / (name + '_raw.json')).read_text())['messages'])


def measured(name, key):
    m = re.search(r'\b' + re.escape(key) + r'\s*=\s*([+-]?[\d.eE+-]+)', messages(name))
    if not m:
        raise RuntimeError(f'Missing {key} in {name}')
    return float(m.group(1))


def fft_plot(name, datafile, outputfile):
    data = np.loadtxt(OUT / datafile)
    t, v = data[:, 0], data[:, 9]  # wrdata: (time, value) pairs; fifth value is load
    n = 3000
    x = np.linspace(t[0], t[-1], n, endpoint=False)
    y = np.interp(x, t, v) - np.mean(v)
    rms_spectrum = np.abs(np.fft.rfft(y)) * math.sqrt(2) / n
    f = np.fft.rfftfreq(n, x[1] - x[0])
    fig, ax = plt.subplots(figsize=(7, 3.3))
    ax.plot(f, rms_spectrum, lw=1.1)
    ax.set_xlim(0, 100000); ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Harmonic RMS voltage (V)')
    ax.set_title('PROXY ONLY: output spectrum, ' + name.replace('_', ' '))
    ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(OUT / outputfile, dpi=150); plt.close(fig)


def main():
    ac = np.loadtxt(OUT / 'ac_transfer_proxy.txt')
    f, gain, rin = ac[:, 0], ac[:, 4], ac[:, 6]
    reference = gain[0]
    indices = np.flatnonzero(gain < reference / math.sqrt(2))
    f3db = float(f[indices[0]]) if indices.size else float('nan')
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.semilogx(f, 20*np.log10(gain), label='Open-loop loaded voltage gain')
    ax.axvline(200000, ls='--', color='red', label='200 kHz requirement')
    ax.set(xlabel='Frequency (Hz)', ylabel='Gain (dB)', title='PROXY ONLY: open-loop AC gain')
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout()
    fig.savefig(OUT / 'ac_gain_proxy.png', dpi=150); plt.close(fig)

    tr = np.loadtxt(OUT / 'transient_proxy.txt')
    fig, ax = plt.subplots(figsize=(7, 3.3))
    ax.plot((tr[:, 0] - tr[0, 0]) * 1000, tr[:, 9], label='8 ohm load')
    ax.set_xlim(0, .6); ax.set(xlabel='Time since saved segment (ms)', ylabel='Load voltage (V)',
                              title='PROXY ONLY: 5 mV, 10 kHz transient')
    ax.grid(alpha=.3); fig.tight_layout()
    fig.savefig(OUT / 'transient_5mV_proxy.png', dpi=150); plt.close(fig)
    fft_plot('open_loop_tran', 'transient_proxy.txt', 'spectrum_5mV_proxy.png')
    fft_plot('inverting_500mV', 'inverting_transient_proxy.txt', 'spectrum_inverting_proxy.png')

    gain10k = measured('open_loop_ac', 'gain10k')
    thd_500mV = float(re.search(r'THD: ([\d.]+) %', messages('inverting_500mV')).group(1))
    maxload = measured('open_loop_swing', 'maxload')
    minload = measured('open_loop_swing', 'minload')
    rows = [
        '# Executed proxy-model checks — NOT selected-part results', '',
        'These are actual ngspice results from a provisional circuit using generic MOS models.',
        'They are **not** evidence that the selected ALD/BSS devices meet any specification.', '',
        '| Metric | Proxy-model result | Project target | Status |',
        '|---|---:|---:|---|',
        f'| Open-loop gain at 10 kHz | {gain10k:.2f} V/V | ≥25 | FAIL |',
        f'| Input resistance at 10 kHz | {rin[0]/1000:.0f} kΩ | ≥200 kΩ | Proxy pass only |',
        f'| Open-loop 3 dB upper frequency (from 100 Hz reference) | ~{f3db/1000:.1f} kHz | >200 kHz | FAIL |',
        f'| Unfeedbacked 500 mV large-signal output extrema | {minload:.3f} to {maxload:.3f} V | ±2 V peak | FAIL |',
        f'| Inverting feedback THD at 500 mV, 10 kHz | {thd_500mV:.3f}% | Each harmonic power ratio <−30 dB | FAIL (2nd harmonic) |',
        f'| Average supply power, 500 mV inverting test | {measured("inverting_500mV", "avgpower"):.3f} W | Minimize subject to constraints | Infeasible circuit |',
        '',
        'The Fourier text is in `inverting_500mV_raw.json` and `open_loop_tran_raw.json`.',
        'At 500 mV input the 2nd harmonic amplitude ratio is 0.07348, giving a power ratio of',
        '20 log10(0.07348) = −22.7 dB; the hand design fails the −30 dB requirement.',
        'Any number here may change materially with verified part models and a revised bias design.',
    ]
    (OUT / 'PROXY_results_summary.md').write_text('\n'.join(rows) + '\n')
    print('\n'.join(rows))

# Inside analyze.py

def critic_agent(metrics):
    """
    Evaluates simulation metrics against ECEN 326 Final Project constraints.
    Returns a decision (ACCEPT/REJECT) and a list of feedback reasons.
    """
    reasons = []
    
    if metrics.get('THD_percent', 100) >= 3.16:
        reasons.append(f"REJECT: THD is {metrics.get('THD_percent'):.2f}%, which exceeds 3.16%.")
        
    if metrics.get('Gain_V_V', 0) < 25.0:
        reasons.append(f"REJECT: AC Gain is {metrics.get('Gain_V_V'):.2f} V/V. Must be >= 25 V/V.")
        
    f3db = metrics.get('f3dB_Hz')
    if f3db is None or f3db <= 200000:
        val = f"{f3db:.2f} Hz" if f3db else "Not Found"
        reasons.append(f"REJECT: 3dB Bandwidth is {val}. Must be > 200,000 Hz.")
        
    if metrics.get('Ptot_mW', 100000) > 10000:
        reasons.append(f"REJECT: Total power dissipation is extremely high ({metrics.get('Ptot_mW')} mW).")

    if not reasons:
        return {"decision": "ACCEPT", "feedback": "All constraints passed."}
    else:
        return {"decision": "REJECT", "feedback": " | ".join(reasons)}

if __name__ == '__main__':
    main()
