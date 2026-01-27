#######################################################################
# Copyright (c) 2019-present, Blosc Development Team <blosc@blosc.org>
# All rights reserved.
#
# This source code is licensed under a BSD-style license (found in the
# LICENSE file in the root directory of this source tree)
#######################################################################

# Unified roofline plotter for different machines and disk/memory modes.
# The user selects the benchmark via `machine` and `mem_mode` below.

import matplotlib.pyplot as plt
import ast

# ---------------------------------------------------------------------
# User selection
# ---------------------------------------------------------------------
# Valid machines: "Apple-M4-Pro", "AMD-7800X3D"
machine = "Apple-M4-Pro"
#machine = "AMD-7800X3D"
# False -> on-disk benchmark, True -> in-memory benchmark
mem_mode = True
# Whether we want to compare just compressed Blosc2 in-memory vs on-disk
compare_disk_mem = True

FIGSIZE = (4.5, 2.5)

# ---------------------------------------------------------------------
# Benchmark dictionaries (raw string form, as produced by driver script)
# ---------------------------------------------------------------------

BENCH_DATA = {
    "Apple-M4-Pro": {
        "disk": """
{'blosc2': {'low': {'GFLOPS': 5.312497144823653,
                    'Intensity': 5.5,
                    'Time': 13.976478099822998},
            'matmul0': {'GFLOPS': 49.97026305756767,
                        'Intensity': 1000,
                        'Time': 0.04502677917480469},
            'matmul1': {'GFLOPS': 429.4701523836153,
                        'Intensity': 5000,
                        'Time': 0.654876708984375},
            'matmul2': {'GFLOPS': 452.87712695016023,
                        'Intensity': 10000,
                        'Time': 4.968235015869141},
            'medium': {'GFLOPS': 21.23854062899218,
                       'Intensity': 36.75,
                       'Time': 23.35965585708618},
            'very low': {'GFLOPS': 0.94937480674441,
                         'Intensity': 0.5,
                         'Time': 7.109942197799683}},
 'blosc2-nocomp': {'low': {'GFLOPS': 1.1826098733051902,
                           'Intensity': 5.5,
                           'Time': 62.78486394882202},
                   'matmul0': {'GFLOPS': 9.6658192894732,
                               'Intensity': 1000,
                               'Time': 0.23277902603149414},
                   'matmul1': {'GFLOPS': 200.77368589727772,
                               'Intensity': 5000,
                               'Time': 1.4008309841156006},
                   'matmul2': {'GFLOPS': 326.8636580141097,
                               'Intensity': 10000,
                               'Time': 6.883604049682617},
                   'medium': {'GFLOPS': 6.7257766846117,
                              'Intensity': 36.75,
                              'Time': 73.76471495628357},
                   'very low': {'GFLOPS': 0.1215571944559167,
                                'Intensity': 0.5,
                                'Time': 55.52941584587097}},
 'numpy/numexpr': {'low': {'GFLOPS': 0.13805657436327062,
                           'Intensity': 5.5,
                           'Time': 537.8229928016663},
                   'matmul0': {'GFLOPS': 0.3324317306786938,
                               'Intensity': 1000,
                               'Time': 6.7683069705963135},
                   'matmul1': {'GFLOPS': 191.3547694079063,
                               'Intensity': 5000,
                               'Time': 1.469783067703247},
                   'matmul2': {'GFLOPS': 705.5524632735965,
                               'Intensity': 10000,
                               'Time': 3.188990354537964},
                   'medium': {'GFLOPS': 0.7818169637148463,
                              'Intensity': 36.75,
                              'Time': 634.5794770717621},
                   'very low': {'GFLOPS': 0.012041409514438401,
                                'Intensity': 0.5,
                                'Time': 560.5656042098999}}}
""",
        "mem": """
{'blosc2': {'low': {'GFLOPS': 9.236286374725738,
                    'Intensity': 5.5,
                    'Time': 0.26796483993530273},
            'matmul0': {'GFLOPS': 85.43762731198565,
                        'Intensity': 1000,
                        'Time': 0.02633500099182129},
            'matmul1': {'GFLOPS': 447.606620028329,
                        'Intensity': 5000,
                        'Time': 0.6283419132232666},
            'matmul2': {'GFLOPS': 511.4489548180484,
                        'Intensity': 10000,
                        'Time': 4.399266004562378},
            'medium': {'GFLOPS': 26.782324970433116,
                       'Intensity': 36.75,
                       'Time': 0.6174781322479248},
            'very low': {'GFLOPS': 2.306438202494336,
                         'Intensity': 0.5,
                         'Time': 0.09755301475524902}},
 'blosc2-nocomp': {'low': {'GFLOPS': 6.45917131929239,
                           'Intensity': 5.5,
                           'Time': 0.3831760883331299},
                   'matmul0': {'GFLOPS': 31.971163162566313,
                               'Intensity': 1000,
                               'Time': 0.07037591934204102},
                   'matmul1': {'GFLOPS': 277.4774664581358,
                               'Intensity': 5000,
                               'Time': 1.0135958194732666},
                   'matmul2': {'GFLOPS': 473.9706206222168,
                               'Intensity': 10000,
                               'Time': 4.747129678726196},
                   'medium': {'GFLOPS': 14.709582786026902,
                              'Intensity': 36.75,
                              'Time': 1.1242671012878418},
                   'very low': {'GFLOPS': 0.23142173600437088,
                                'Intensity': 0.5,
                                'Time': 0.9722509384155273}},
 'numpy/numexpr': {'low': {'GFLOPS': 5.099328744991377,
                           'Intensity': 5.5,
                           'Time': 0.48535799980163574},
                   'matmul0': {'GFLOPS': 96.96567171846904,
                               'Intensity': 1000,
                               'Time': 0.02320408821105957},
                   'matmul1': {'GFLOPS': 589.7650234976503,
                               'Intensity': 5000,
                               'Time': 0.4768848419189453},
                   'matmul2': {'GFLOPS': 896.6615140751829,
                               'Intensity': 10000,
                               'Time': 2.509308099746704},
                   'medium': {'GFLOPS': 17.066381125126835,
                              'Intensity': 36.75,
                              'Time': 0.9690103530883789},
                   'very low': {'GFLOPS': 0.23416156311767997,
                                'Intensity': 0.5,
                                'Time': 0.9608750343322754}}}
"""
    },
    "AMD-7800X3D": {
        "disk": """
{'blosc2': {'low': {'GFLOPS': 5.579595433872582,
                    'Intensity': 5.5,
                    'Time': 13.307416439056396},
            'matmul0': {'GFLOPS': 20.829279166933365,
                        'Intensity': 1000,
                        'Time': 0.10802102088928223},
            'matmul1': {'GFLOPS': 240.0398015214518,
                        'Intensity': 5000,
                        'Time': 1.1716806888580322},
            'matmul2': {'GFLOPS': 283.616690545362,
                        'Intensity': 10000,
                        'Time': 7.933242559432983},
            'medium': {'GFLOPS': 15.669677243059686,
                       'Intensity': 36.75,
                       'Time': 31.661468982696533},
            'very low': {'GFLOPS': 1.4137488451813156,
                         'Intensity': 0.5,
                         'Time': 4.7745397090911865}},
 'blosc2-nocomp': {'low': {'GFLOPS': 0.7452224588801104,
                           'Intensity': 5.5,
                           'Time': 99.63467836380005},
                   'matmul0': {'GFLOPS': 0.49891902105294655,
                               'Intensity': 1000,
                               'Time': 4.509749889373779},
                   'matmul1': {'GFLOPS': 143.31068470344604,
                               'Intensity': 5000,
                               'Time': 1.9625194072723389},
                   'matmul2': {'GFLOPS': 258.0346688807398,
                               'Intensity': 10000,
                               'Time': 8.7197585105896},
                   'medium': {'GFLOPS': 4.082011145976717,
                              'Intensity': 36.75,
                              'Time': 121.5393545627594},
                   'very low': {'GFLOPS': 0.07451945757462396,
                                'Intensity': 0.5,
                                'Time': 90.58036947250366}},
 'numpy/numexpr': {'low': {'GFLOPS': 1.3505967264615455,
                           'Intensity': 5.5,
                           'Time': 54.97569966316223},
                   'matmul0': {'GFLOPS': 0.39964597062911356,
                               'Intensity': 1000,
                               'Time': 5.629982948303223},
                   'matmul1': {'GFLOPS': 193.39563405316557,
                               'Intensity': 5000,
                               'Time': 1.454272747039795},
                   'matmul2': {'GFLOPS': 312.98258763598614,
                               'Intensity': 10000,
                               'Time': 7.188898324966431},
                   'medium': {'GFLOPS': 7.8469505111061775,
                              'Intensity': 36.75,
                              'Time': 63.2251980304718},
                   'very low': {'GFLOPS': 0.18918152044971867,
                                'Intensity': 0.5,
                                'Time': 35.680017709732056}}}
""",
        "mem": """
{'blosc2': {'low': {'GFLOPS': 6.320064826782569,
                    'Intensity': 5.5,
                    'Time': 0.39160990715026855},
            'matmul0': {'GFLOPS': 78.40146215834511,
                        'Intensity': 1000,
                        'Time': 0.028698444366455078},
            'matmul1': {'GFLOPS': 263.14124684972785,
                        'Intensity': 5000,
                        'Time': 1.0688176155090332},
            'matmul2': {'GFLOPS': 299.04906343411403,
                        'Intensity': 10000,
                        'Time': 7.523849010467529},
            'medium': {'GFLOPS': 16.33476728303771,
                       'Intensity': 36.75,
                       'Time': 1.012411117553711},
            'very low': {'GFLOPS': 1.7041734008223646,
                         'Intensity': 0.5,
                         'Time': 0.13202881813049316}},
 'blosc2-nocomp': {'low': {'GFLOPS': 5.72307488747803,
                           'Intensity': 5.5,
                           'Time': 0.43245983123779297},
                   'matmul0': {'GFLOPS': 73.18823675393969,
                               'Intensity': 1000,
                               'Time': 0.030742645263671875},
                   'matmul1': {'GFLOPS': 270.0345289513033,
                               'Intensity': 5000,
                               'Time': 1.0415334701538086},
                   'matmul2': {'GFLOPS': 303.4751195129057,
                               'Intensity': 10000,
                               'Time': 7.414116859436035},
                   'medium': {'GFLOPS': 15.246568399562406,
                              'Intensity': 36.75,
                              'Time': 1.0846703052520752},
                   'very low': {'GFLOPS': 1.2136155831529727,
                                'Intensity': 0.5,
                                'Time': 0.18539643287658691}},
 'numpy/numexpr': {'low': {'GFLOPS': 4.633985948369028,
                           'Intensity': 5.5,
                           'Time': 0.53409743309021},
                   'matmul0': {'GFLOPS': 273.32765661656094,
                               'Intensity': 1000,
                               'Time': 0.008231878280639648},
                   'matmul1': {'GFLOPS': 365.7361691098209,
                               'Intensity': 5000,
                               'Time': 0.7689969539642334},
                   'matmul2': {'GFLOPS': 372.64242712518626,
                               'Intensity': 10000,
                               'Time': 6.037959814071655},
                   'medium': {'GFLOPS': 19.902467174400265,
                              'Intensity': 36.75,
                              'Time': 0.8309271335601807},
                   'very low': {'GFLOPS': 1.5052146368383612,
                                'Intensity': 0.5,
                                'Time': 0.14948034286499023}}}

"""
    },
}

# ---------------------------------------------------------------------
# Select benchmark
# ---------------------------------------------------------------------
mode_key = "mem" if mem_mode else "disk"
try:
    result_str = BENCH_DATA[machine][mode_key]
except KeyError as e:
    raise SystemExit(f"Unknown selection: machine={machine!r}, mem_mode={mem_mode}") from e

legend = "in-memory" if mem_mode else "on-disk"

# Parse the result string as a dictionary
results = ast.literal_eval(result_str)

# ---------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------

if compare_disk_mem:
    # Comparison plot: Blosc2 disk vs memory for both machines
    fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

    comp_styles = {
        'AMD-7800X3D-mem': {'color': 'blue', 'marker': 'v', 'label': 'AMD 7800X3D (in-memory)', 'offset': 0.87},
        'AMD-7800X3D-disk': {'color': 'red', 'marker': '^', 'label': 'AMD 7800X3D (on-disk)', 'offset': 0.87},
        'Apple-M4-Pro-mem': {'color': 'blue', 'marker': 's', 'label': 'Apple M4 Pro (in-memory)', 'offset': 1.15},
        'Apple-M4-Pro-disk': {'color': 'red', 'marker': 'o', 'label': 'Apple M4 Pro (on-disk)', 'offset': 1.15},
    }

    # Plot Blosc2 results for both machines and both modes (mem first, then disk)
    for machine_name in ['AMD-7800X3D', 'Apple-M4-Pro']:
        for mode_name in ['mem', 'disk']:
            key = f'{machine_name}-{mode_name}'
            data_str = BENCH_DATA[machine_name][mode_name]
            data = ast.literal_eval(data_str)

            # Extract only Blosc2 (compressed) data
            if 'blosc2' in data:
                blosc2_data = data['blosc2']
                intensities = []
                gflops = []

                for workload, metrics in blosc2_data.items():
                    intensities.append(metrics['Intensity'])
                    gflops.append(metrics['GFLOPS'])

                style = comp_styles[key]
                # Apply horizontal offset to separate markers by machine
                offset_intensities = [i * style['offset'] for i in intensities]

                ax.loglog(
                    offset_intensities,
                    gflops,
                    marker=style['marker'],
                    color=style['color'],
                    label=style['label'],
                    markersize=8,
                    linestyle='',
                    alpha=0.7,
                )

    # Add single set of workload labels (from Apple M4 Pro disk data)
    apple_disk = ast.literal_eval(BENCH_DATA['Apple-M4-Pro']['disk'])
    intensity_map_comp = {}
    for workload, metrics in apple_disk['blosc2'].items():
        intensity = metrics['Intensity']
        gflop = metrics['GFLOPS']
        if intensity not in intensity_map_comp:
            intensity_map_comp[intensity] = {'label': workload, 'min_gflops': gflop}
        else:
            intensity_map_comp[intensity]['min_gflops'] = min(intensity_map_comp[intensity]['min_gflops'], gflop)

    ax.set_xlim(0.1, 5e4)
    ax.set_ylim(0.1, 1000.0)

    for intensity, info in sorted(intensity_map_comp.items()):
        safe_ypos = max(info['min_gflops'] * 0.3, 0.002)
        ax.annotate(
            info['label'],
            (intensity, safe_ypos),
            ha='center',
            va='top',
            fontsize=10,
            alpha=0.9,
        )

    ax.set_xlabel('Arithmetic Intensity (FLOPs/element)', fontsize=12)
    ax.set_ylabel('Performance (GFLOPS/sec)', fontsize=12)
    ax.set_title('Roofline Comparison: Compressed Blosc2 Memory vs Disk', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(False)

    plt.savefig('roofline_blosc2_comparison.png', dpi=300)
    plt.show()

else:
    # Original single-mode plot
    fig, ax = plt.subplots(figsize=FIGSIZE, constrained_layout=True)

    styles = {
        'numpy/numexpr': {'color': 'blue', 'marker': 'o', 'label': 'NumPy/NumExpr'},
        'blosc2': {'color': 'red', 'marker': 's', 'label': 'Blosc2 (compressed)'},
        'blosc2-nocomp': {'color': 'green', 'marker': '^', 'label': 'Blosc2 (uncompressed)'},
    }

    # Plot each backend's results
    for backend, backend_results in results.items():
        intensities = []
        gflops = []
        labels = []
        for workload, metrics in backend_results.items():
            intensities.append(metrics['Intensity'])
            gflops.append(metrics['GFLOPS'])
            labels.append(workload)

        style = styles[backend]
        ax.loglog(
            intensities,
            gflops,
            marker=style['marker'],
            color=style['color'],
            label=style['label'],
            markersize=8,
            linestyle='',
            alpha=0.7,
        )

    # Build a single annotation per unique x (Intensity)
    intensity_map = {}
    for backend_results in results.values():
        for workload, metrics in backend_results.items():
            intensity = metrics['Intensity']
            gflop = metrics['GFLOPS']
            if intensity not in intensity_map:
                intensity_map[intensity] = {'label': workload, 'gflops': []}
            intensity_map[intensity]['gflops'].append(gflop)

    # Axes limits
    ax.set_xlim(0.1, 5e4)
    ymin = 0.1 if mem_mode else 0.001
    ax.set_ylim(ymin, 2000.0)

    # Annotate once per intensity, centered under the cluster of points
    for intensity, info in sorted(intensity_map.items()):
        raw_ypos = min(info['gflops']) * 0.6
        ymin_curr, ymax_curr = ax.get_ylim()
        safe_ypos = max(raw_ypos, ymin_curr * 1.5 if ymin_curr > 0 else raw_ypos)
        ax.annotate(
            info['label'],
            (intensity, safe_ypos),
            ha='center',
            va='top',
            fontsize=10,
            alpha=0.9,
        )

    ax.set_xlabel('Arithmetic Intensity (FLOPs/element)', fontsize=12)
    ax.set_ylabel('Performance (GFLOPS/sec)', fontsize=12)
    machine2 = machine.replace("-", " ")
    ax.set_title(f'Roofline Analysis: {machine2} ({legend})', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(False)

    plt.savefig(f'roofline_plot-{machine}-{legend}.png', dpi=300)
    plt.show()
