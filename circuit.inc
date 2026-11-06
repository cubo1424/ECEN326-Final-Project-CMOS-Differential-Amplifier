* PROVISIONAL topology: ALD dual NMOS input, ALD dual PMOS mirror,
* BSS complementary common-source output. Part names below are labels;
* electrical model cards are the explicitly unvalidated PROXY models.
* Supply is 5 V. Input is DC biased at 2.5 V through two 1-Mohm resistors.
VDD vdd 0 5
RBIAS1 vdd vin 1Meg
RBIAS2 vin 0 1Meg
RREF1 vdd ref 1Meg
RREF2 ref 0 1Meg
* NMOS diode-biased tail device; all currents must be checked in OP.
RBTAIL vdd tailgate 10k
MTAIL tailgate tailgate 0 0 ALD1101A_PROXY W=5u L=1u
M5 source tailgate 0 0 ALD1101A_PROXY W=5u L=1u
M1 mirror vin source 0 ALD1101A_PROXY W=5u L=1u
M2 first ref source 0 ALD1101A_PROXY W=5u L=1u
M3 mirror mirror vdd vdd ALD1102A_PROXY W=3u L=1u
M4 first mirror vdd vdd ALD1102A_PROXY W=3u L=1u
* AC coupling permits independent fixed DC gate biases. These bias dividers
* consume supply power and are included in the power check.
CGN first gn 1u
CGP first gp 1u
RNGU vdd gn 330k
RNGL gn 0 110k
RPGU vdd gp 110k
RPGL gp 0 330k
* Complementary common-source stage; only ONE of each selected output part.
* Zero-volt series probes permit unambiguous instantaneous drain currents.
VNPROBE out nd 0
MOUTN nd gn 0 0 BSS214NW_PROXY W=1u L=1u
VPPROBE pd out 0
MOUTP pd gp vdd vdd BSS223PW_PROXY W=1u L=1u
* Datasheet input capacitance at specified bias, approximated as gate-source.
CGSN gn 0 107p
CGSP gp vdd 45p
* A real feedback capacitor across the inverting second stage.
CCOMP first out 10p
* DC centering bleeders; the 8-ohm load sees no DC via output capacitor.
RCENTERU vdd out 1Meg
RCENTERL out 0 1Meg
COUT out load 2200u
RLOAD load 0 8
