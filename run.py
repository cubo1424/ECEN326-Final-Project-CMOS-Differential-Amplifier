import os
import re
import csv
import json
import socket
from pathlib import Path
from dotenv import load_dotenv

from google import genai
from google.genai import types

from ngspice_interface import run_simulation
from analyze import critic_agent 

load_dotenv()
client = genai.Client()


PLANNER_SYSTEM_PROMPT = """
You are the Planner Agent for a CMOS Two-Stage Miller-Compensated Differential Amplifier optimization loop.
Your objective is to adjust the circuit parameters to meet all specifications while minimizing total power.

Specifications to meet:
1. AC Gain >= 25 V/V
2. 3dB Bandwidth > 200,000 Hz
3. THD < 3.16% (-30 dB)

Design variables you can modify:
- Itail: The tail current source (e.g., 200u, 350u, 500u).
- CC: The Miller compensation capacitor (e.g., 0.5p, 0.8p, 1.5p, 2p).
- RF: The feedback resistor (e.g., 5.6MEG, 6.2MEG, 6.8MEG).

Output ONLY a raw JSON object with the new proposed values. Do not include markdown formatting or explanations.
Format: {"Itail": "350u", "CC": "0.8p", "RF": "5.6MEG"}
"""

_heuristic_step = 0

def planner_agent(critic_feedback, current_metrics, current_vars):
    global _heuristic_step
    prompt = f"""
    Current Variables: {current_vars}
    Current Metrics: {current_metrics}
    Critic Feedback: {critic_feedback}
    
    Provide the next {{"Itail": "...", "CC": "...", "RF": "..."}} JSON to try.
    """
    
    # Force a strict 4-second network timeout
    socket.setdefaulttimeout(4.0)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=PLANNER_SYSTEM_PROMPT,
            )
        )
        clean_text = response.text.strip('` \n').replace('json\n', '')
        new_vars = json.loads(clean_text)
        return new_vars
    except Exception as e:
        print(f"Planner API skipped ({type(e).__name__}). Running heuristic step {_heuristic_step}...")


        sweep_grid = [
            {"Itail": "350u", "CC": "1.5p"},
            {"Itail": "400u", "CC": "1.0p"},
            {"Itail": "450u", "CC": "0.8p"},
            {"Itail": "500u", "CC": "0.6p"},
            {"Itail": "300u", "CC": "1.2p"}
        ]
        choice = sweep_grid[_heuristic_step % len(sweep_grid)]
        _heuristic_step += 1
        return choice

def update_netlist(netlist_path, new_vars):
    with open(netlist_path, 'r') as f:
        content = f.read()
    if "Itail" in new_vars:
        content = re.sub(r'(Itail v_tail 0 )\S+', rf'\g<1>{new_vars["Itail"]}', content)
    if "CC" in new_vars:
        content = re.sub(r'(CC v_stage1 v_out )\S+', rf'\g<1>{new_vars["CC"]}', content)
    with open(netlist_path, 'w') as f:
        f.write(content)

def main(max_iterations=15):
    ROOT = Path(__file__).resolve().parent
    os.chdir(ROOT)
    
    netlist_file = "amplifier_baseline.cir"
    current_vars = {"Itail": "350u", "CC": "1.0p"}
    
    with open('iteration_log.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Iteration', 'Itail', 'CC', 'RF', 'Gain', 'f3dB', 'THD', 'Ptot', 'Decision', 'Feedback'])
    
    for i in range(1, max_iterations + 1):
        print(f"\n--- ITERATION {i} ---")
        print(f"Testing Vars: {current_vars}")
        
        print("Running ngspice simulation...")
        metrics = run_simulation(netlist_file) 
        print(f"Metrics: {metrics}")
        
        eval = critic_agent(metrics)
        print(f"Critic Decision: {eval['decision']}")
        print(f"Critic Feedback: {eval['feedback']}")
        
        with open('iteration_log.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([i, current_vars.get('Itail'), current_vars.get('CC'), current_vars.get('RF'),
                             metrics.get('Gain_V_V'), metrics.get('f3dB_Hz'), 
                             metrics.get('THD_percent'), metrics.get('Ptot_mW'), 
                             eval['decision'], eval['feedback']])
        
        if eval['decision'] == 'ACCEPT':
            print("\n>>> Optimization successful! Design specifications satisfied.")
            break
            
        print("Consulting Planner Agent for new variables...")
        current_vars = planner_agent(eval['feedback'], metrics, current_vars)
        update_netlist(netlist_file, current_vars)

if __name__ == '__main__':
    main()