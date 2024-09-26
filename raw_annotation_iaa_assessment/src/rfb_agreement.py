# Role-Filler Binding
# Inter-Annotator Agreement Calculations
"""
 Binary agreement calculation using fuzzy match to associate kv pairs 
 within frames and various aggregation functions to create an IOU agreement
 metric for the pairings.
 """

# ====================================|
# Imports
import argparse 
from collections import defaultdict
import csv 
from thefuzz import process
import json
import os

# Imports - Typing
from typing import Dict, List, Tuple, Union
from os import PathLike
# ====================================|
def load_data(annotator_a_dir: Union[str, PathLike],
              annotator_b_dir: Union[str, PathLike],
              include_skips  : bool = False) -> Dict[str, Dict[str, Dict]]:
    """Load in data from two annotators
    
    Collates both sets of annotations into a single data structure, 
    so that the data can be accessed for each GUID.

    ## Args
    - annotator_a_dir : file directory of the first set of annotations
    - annotator_b_dir : file_directory of the second set of annotations
    - include_skips   : boolean for whether to include "skipped frames"

    ## Returns
    - nested dict mapping annotations to GUIDs
    """

    a_annotations = []
    b_annotations = []
    for fname in os.listdir(annotator_a_dir):
        filename = os.path.join(annotator_a_dir, fname)
        with open(filename, 'r', encoding='utf8') as f:
            a_annotations.append(json.load(f))

    for fname in os.listdir(annotator_b_dir):
        filename = os.path.join(annotator_b_dir, fname)
        with open(filename, 'r', encoding='utf8') as f:
            b_annotations.append(json.load(f))

    if not include_skips:
        a_annotations = filter(lambda x: "_skip_reason" not in x, a_annotations)
        b_annotations = filter(lambda x: "_skip_reason" not in x, b_annotations)
    
    frames_dict = defaultdict(dict)

    for frame_anno in a_annotations:
        id = frame_anno["_image_id"]
        frames_dict[id].update({"A": {k:v 
                                      for k, v in frame_anno.items() 
                                      if k != "_image_id" and (k != "" and v != [])}})
    for frame_anno in b_annotations:
        id = frame_anno["_image_id"]
        frames_dict[id].update({"B": {k:v 
                                      for k, v in frame_anno.items() 
                                      if k != "_image_id" and (k != "" and v != [])}})   
                     
    return frames_dict
    

def assoc_pairs(anno_one: Dict[str, List[str]],
                anno_two: Dict[str, List[str]]):
    """Associate Pairs 
    
    Generates a set of tuples for each annotation in
    the document, and sorts them by key.

    ## Args 
    - anno_one : dictionary of annotator_A's annotations
    - anno_two : dictionary of annotator_B's annotations
    
    ## Returns
    - tuple of lists, each consisting of tuples representing kv pairs
    """
    a_pairs = []
    b_pairs = []

    for key, vals in anno_one.items():
        if len(vals) == 1:
            a_pairs.append((key, vals[0]))
        else:
            a_pairs.extend((key, v) for v in vals)
    for key, vals in anno_two.items():
        if len(vals) == 1:
            b_pairs.append((key, vals[0]))
        else:
            b_pairs.extend((key, v) for v in vals)
    a_pairs.sort(key = lambda x: x[0])
    b_pairs.sort(key = lambda x: x[0])
    return a_pairs, b_pairs


def pair_iou(seq_one: List[str], 
             seq_two: List[str], 
             threshold: int=90) -> float:
    """Intersection Over Union for the matched pairs
    
    iterates over the first sequence, finding the most similar 
    kv-pair in the second sequence for each value. Uses the
    similarity value in the IOU calculation.

    ## Args 
    - seq_one   : first sequence
    - seq_two   : second sequence 
    - threshold : minimum similarity value for matches

    ## Returns
    - a float value representing document level IOU along KV-pairs
    """
    intersection = 0
    union = 0
    for x in seq_one:
        threshold_avg = 0
        test_pairs = [y for y in seq_two]
        similarity = get_max_similarity(x, test_pairs)
        if similarity[1] > threshold:
            intersection += similarity[1] / 100
        union += 1
        threshold_avg /= len(seq_two)
    return intersection / union


def get_iou(seq_one: List[str], 
            seq_two: List[str]) -> float:
    """Simpler IOU function for key and value calculation
    
    Since the comparison along keys and values is a lot simpler,
    we can just use basic word-level IOU
    
    ## Args
    - seq_one : first sequence
    - seq_two : second sequence 

    ## Returns
    - a float value representing IOU for the two sequences.
    """
    intersection = 0
    union = 0
    for x in seq_one:
        if x in seq_two:
            intersection += 1
        union += 1
    return intersection / union


def get_max_similarity(gold: Tuple[str, str],
                       test_seq: List[Tuple[str, str]]) -> float:
    """Fuzzy-Match similarity calculation

    Given a gold document and a sequence of test docs, 
    finds the most similar pair in the the sequence 
    according to L-Distance from the gold document.

    ## Args
    - gold     : document being compared
    - test_seq : list of documents to compare to gold

    ## Returns
    - the similarity value of the greatest match in the sequence.
    """
    comp_gold = "_".join(gold)
    comp_seq = ["_".join(pair) for pair in test_seq]
    match = process.extractBests(comp_gold, comp_seq, limit=1)
    return match[0]


def get_agreement(annotations, skips=False) -> defaultdict[Dict[str, float]]:
    """Calculate IOU agreement over KV pairs
    
    ## Args
    - annotations: 
    - skips      : whether or not to include "skipped" annotations in agreement

    ## Returns
    - a nested dictionary of agreement for each type within each guid
    (to be serialized as json)
    """
    
    overall_agreement = defaultdict(dict)

    for guid, frame_annos in annotations.items():
        a_annos = frame_annos["A"] if "A" in frame_annos.keys() and frame_annos["A"] != {} else None
        b_annos = frame_annos["B"] if "B" in frame_annos.keys() and frame_annos["B"] != {} else None

        # Check to see if the annotations are empty (skipped frame)
        if b_annos is None or a_annos is None:
            # if both empty, match
            if b_annos is None and a_annos is None:
                overall_agreement[guid] = {"key"  : 1,
                                           "val"  : 1,
                                           "pair" : 1,
                                           "total": 1}
                continue
            # if only one is empty, mismatch
            else:
                overall_agreement[guid] = {"key"  : 0,
                                           "val"  : 0,
                                           "pair" : 0,
                                           "total": 0}
                continue

        # pair up annotations
        pairs = assoc_pairs(a_annos, b_annos)

        # calculate IOU over each locus of comparison
        key_agreement = get_iou(a_annos.keys(), b_annos.keys())
        val_agreement = get_iou(a_annos.values(), b_annos.values())
        pair_agreement = pair_iou(pairs[0], pairs[1])
        total_agreement = aggregate_vals(key_agreement, val_agreement, pair_agreement)

        # populate GUID results
        overall_agreement[guid] = {"key"  : key_agreement,
                                   "val"  : val_agreement,
                                   "pair" : pair_agreement,
                                   "total": total_agreement}
    return overall_agreement


def aggregate_vals(*args) -> float:
    """Aggregation Function
    
    wrapper for combining agreement values 
    in different ways. 

    NOTE: Current aggregation => AVERAGE
    """

    out = args[0] 
    for arg in args[1:]:
        out *= arg
    return out / len(args)


# Main
def main(args):
    in_dir   = args.in_dir
    out_file = args.out_file
    skip     = args.skip
    ANNOTATOR_A = 20019 # 20007
    ANNOTATOR_B = 20017 # 20008
    a_dir = f"{in_dir}/{ANNOTATOR_A}"
    b_dir = f"{in_dir}/{ANNOTATOR_B}"

    # load in frames
    frames = load_data(a_dir,
                       b_dir, 
                       include_skips=skip)
    
    # calculate agreement
    results = get_agreement(frames, skips = skip)
    
    # write to file
    # with open(f"results/skips/{out_file}", 'w', encoding='utf8') as f:
    with open(f"./{out_file}", 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(["guid", "keys","vals","pairs","total"])
        for guid, agreement in results.items():
            writer.writerow([guid, agreement["key"], agreement["val"], agreement["pair"], agreement["total"]])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_dir",
                        help="Directory where annotation json files are stored",
                        default="./adjud-r3_eval")
    parser.add_argument("-s", "--skip",
                        action="store_true",
                        help="whether or not to include skipped files in the agreement calculation")
    parser.add_argument('-o', "--out_file",
                        help="location of the results output file",
                        default="r3-results.csv")
    runtime_args = parser.parse_args() 
    main(args=runtime_args)
