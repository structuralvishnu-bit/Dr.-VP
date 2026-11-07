# WPCB Concrete Durability Toolkit

A Python command-line tool for processing capillary absorption and rapid chloride penetration test (RCPT) measurements from concrete specimens. The workflow was motivated by published research on waste printed circuit board (WPCB) fibre-reinforced concrete. It also works with control mixes and other concrete formulations.

## Quick start

Use Python 3.10 or newer. The tool uses only the Python standard library.

```sh
python durability.py sorptivity examples/sorptivity_demo.csv --diameter-mm 100 --start-min 1 --end-min 36
python durability.py rcpt examples/rcpt_demo.csv
```

The demonstration CSVs contain synthetic measurements for one specimen each. The expected sorptivity is approximately **0.01999 mm/√min**. The expected RCPT charge is **2382.3 C**.

## Use your laboratory data

| Command | CSV columns | Calculation |
| --- | --- | --- |
| `sorptivity` | `time_min,mass_g` | Convert mass gain to equivalent absorption depth using exposed circular area and a water density of 0.001 g/mm³. Fit depth against the square root of elapsed time with a free intercept over the specified window. |
| `rcpt` | `time_min,current_ma` | Integrate current over six hours using the trapezoidal rule with current converted to amperes and time converted to seconds. |

Supply one CSV per specimen. Both series start at zero minutes, with strictly increasing observation times. Sorptivity fits use at least three positive-time measurements and the time-zero mass as the baseline. Supply the exposed diameter and the analysis window from your protocol. RCPT series end at 360 minutes. The output is integrated charge before any specimen diameter correction.

The calculations support exploratory analysis. Follow the applicable test procedure for specimen preparation, conditioning, timing, reporting and interpretation. The toolkit does not evaluate test compliance.

## Research reference

M. Vishnu Priyan, R. Annadurai, K. C. Onyelowe, G. U. Alaneme and N. C. Giri (2023). Recycling and sustainable applications of waste printed circuit board in concrete application and validation using response surface methodology. *Scientific Reports*, 13, 16509. [DOI 10.1038/s41598-023-43919-9](https://doi.org/10.1038/s41598-023-43919-9). Figures 16 and 17 provide the research context for the two workflows. The example CSVs do not reproduce those figures or contain study measurements.

## License

MIT for the toolkit code and synthetic examples. The cited article retains its own license.
