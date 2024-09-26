# Role-Filler Binding
# Agreement Report
"""
  Aggregates document level agreement into 
  human-readable metrics.
"""

# ====================================|
# Imports
import argparse
from collections import defaultdict
import csv
import os
import json 
# ====================================|

def read_in_results(fname):
    """Read results in as a dictionary"""
    out= {}
    with open(fname, 'r', encoding='utf8') as f:
        reader = csv.reader(f)
        fields = next(reader)[1:]
        for row in reader:
            out[row[0]] = dict(zip(fields, row[1:]))
    return out

def get_metrics(results_dict):
    """Calculate the aggregation metrics

    ## Metrics
    - Zero Agreement    : number of documents which have 0.0 agreement
    - Perfect Agreement : number of documents which have 1.0 agreement
    - Averages          : average agreement for each locus of comparison
        - k_total : key agreement average
        - v_total : value agreement average
        - p_total : pair agreement average
        - t_total : total agreement average
    """

    output_dict={}

    num_docs = len(results_dict)
    values = defaultdict(float)

    for guid, results in results_dict.items():
        if float(results["total"]) == 0:
            values["zeros"] += 1

        if float(results["total"]) == 1:
            values["perfect"] += 1

        values["k_total"] += float(results["keys"])
        values["v_total"] += float(results["vals"])
        values["p_total"] += float(results["pairs"])
        values["t_total"] += float(results["total"])
    
    output_dict.update({"zero_agreement": values["zeros"] / num_docs,
                        "perfect_agreement": values["perfect"] / num_docs,
                        "averages": {"keys": values["k_total"] / num_docs,
                                     "vals": values["v_total"] / num_docs,
                                     "pairs": values["p_total"] / num_docs,
                                     "total": values["t_total"] / num_docs}})
    return output_dict


def process_file(fname):
    """Process a single file into metrics"""
    results = get_metrics(read_in_results(f"./results/noskips/{fname}"))
    print(results)
    fname = os.path.basename(fname)
    with open(f"{fname}_agreement_report.json", 'w', encoding='utf8') as f:
        json.dump(results, f, indent=2)


def main(args):
    results_dir = args.in_dir
    for name in os.listdir(results_dir):
        process_file(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_dir",
                        help="directory containing results",
                        default="./results/")
    runtime_args = parser.parse_args()
    main(runtime_args)