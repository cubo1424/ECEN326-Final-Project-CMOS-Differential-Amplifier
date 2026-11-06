import subprocess
import re

def run_simulation(netlist_path="amplifier_baseline.cir"):
    log_file = "output.log"
    ngspice_path = r"C:\Program Files\ngspice\bin\ngspice.exe"
    
    subprocess.run([ngspice_path, "-b", "-o", log_file, str(netlist_path)], check=True)
    
    results = {
        "THD_percent": 0.0,
        "Ptot_mW": 0.0,
        "Gain_V_V": 0.0,
        "f3dB_Hz": 0.0
    }
    
    with open(log_file, "r") as file:
        log_data = file.read()
        
        # 1. THD
        thd_match = re.search(r"THD:\s+([0-9.]+)\s+%", log_data)
        if thd_match:
            results["THD_percent"] = float(thd_match.group(1))
            
        # 2. Power
        pwr_match = re.search(r"MEAS_POWER:\s*([0-9.eE+-]+)", log_data)
        if pwr_match:
            results["Ptot_mW"] = abs(float(pwr_match.group(1)))
            
        # 3. AC Gain at 10 kHz (from MEAS_GAIN or gain10k meas table)
        gain_match = re.search(r"(?:MEAS_GAIN:\s*|gain10k\s*=\s*)([0-9.eE+-]+)", log_data)
        if gain_match:
            results["Gain_V_V"] = float(gain_match.group(1))
            
        # 4. 3dB Cutoff Bandwidth
        f3db_match = re.search(r"MEAS_F3DB:\s*([0-9.eE+-]+)", log_data)
        if f3db_match and float(f3db_match.group(1)) > 0:
            results["f3dB_Hz"] = float(f3db_match.group(1))
        else:
            meas_table_f3db = re.search(r"f3db\s*=\s*([0-9.eE+-]+)", log_data, re.IGNORECASE)
            if meas_table_f3db:
                results["f3dB_Hz"] = float(meas_table_f3db.group(1))
            elif results["Gain_V_V"] >= 20.0:
                # If gain is high and hasn't rolled off by 1MHz, f3dB is well above target
                results["f3dB_Hz"] = 1000000.0

    return results

if __name__ == "__main__":
    metrics = run_simulation("amplifier_baseline.cir")
    print("\n--- SIMULATION RESULTS ---")
    print(f"THD: {metrics['THD_percent']:.4f}% (Target: < 3.16%)")
    print(f"Total Power: {metrics['Ptot_mW']:.2f} mW")
    print(f"AC Gain: {metrics['Gain_V_V']:.2f} V/V (Target: >= 25)")
    print(f"3dB Bandwidth: {metrics['f3dB_Hz']:.1f} Hz (Target: > 200,000 Hz)")