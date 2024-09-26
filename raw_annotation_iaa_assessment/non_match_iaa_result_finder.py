'''This code filters the result csv so that only the non-agreed/not-"1.0, 1.0, 1.0, 1.0" lines remain.
This lets you do manual adjudication on the ones that have differences between the annotators using the
RFB Visualizer with Adjudication Buttons v2
https://github.com/clamsproject/RFB_annotation_visualizer/tree/v2-adjudicator-buttons
Note, this branch might move (or become PR'ed) in the future.
'''

import csv

def filter_csv(input_file, output_file):
    with open(input_file, 'r', newline='') as csv_in, open(output_file, 'w', newline='') as csv_out:
        reader = csv.reader(csv_in)
        writer = csv.writer(csv_out)
        for row in reader:
            if "1.0,1.0,1.0,1.0" not in ','.join(row):
                writer.writerow(row)

if __name__ == "__main__":
    # input_file = input("Enter the input CSV file path: ")
    input_file = "evaluation/results/noskips/average-nofuzzy-results.csv"
    # output_file = input("Enter the output CSV file path: ")
    output_file = "evaluation/all_non_matches.csv"
    filter_csv(input_file, output_file)
    print("Rows filtered successfully.")
