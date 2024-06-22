import anthropic
from dotenv import load_dotenv
import os
import pandas as pd
from tqdm import tqdm
import time
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
client = anthropic.Anthropic()

tqdm.pandas()

def annotate_chyron(cleaned_ocr):

    system_message = """
    INSTRUCTIONS: Your job is to match roles and fillers (names) in the following OCR text, which represents a screenshot taken from a public broadcast video. The frame type is CHYRON, meaning the names will typically -- but not always -- appear before their role. Also, typically -- but not always -- there will only be a single name, though it may be attached to multiple roles. Do NOT correct any misspellings. There may be text in the input that is not explicitly matched with a role or name; in those cases, tag them with O. 
    There should be no roles that aren't co-indexed with a filler, and no fillers that aren't co-indexed with a role. If you try to tag a filler with a role that doesn't appear in a corresponding filler or vice-versa, it should be tagged O instead. Many OCR errors may be present; just do your best to figure out what the underlying structure/meaning of the text.

    Please use the following format based in BIO format with indices:

    Format: Tag the end of each word with @(BIO rfb tag), where BIO rfb tag is one of the following:

    BR:i - meaning "begin role i" where i is an index
    IR:i - meaning "in role i"
    BF:i - meaning "begin filler corresponding with role i"
    IF:i - meaning "continue filler corresponding with role i"
    O - meaning not a role or filler

    EXAMPLES:
    OCR STRING: Stanley Kubrick Writer Director of The Shining
    OUTPUT:
    Stanley@BF:1 Kubrick@IF:1 Director@BR:1

    OCR STRING: - :0Meena BoseU.S Military Academy, West Point
    OUTPUT:
    :0Meena@BF:1 BoseU.S@IF:1 Military@BR:1 Academy,@IR:1 West@IR:1 Point@IR:1

    OCR STRING: Indianapolis CLARENCE PAGE Chitago Tribune
    OUTPUT:
    Indianapolis@O CLARENCE@BF:1 PAGE@IF:1 Chitago@BR:1 Tribune@IR:1

    OCR STRING: REP. WIC COURTER GRD MORRI IS COUNTYL

    OUTPUT: REP.@BF:1 WIC@IF:1 COURTER@IF:1 GRD@BR:1 MORRI@IR:1 IS@IR:1 COUNTYL@IR:1

    The most important thing to remember: THE OUTPUT SHOULD BE IDENTICAL TO THE INPUT, VERBATIM, WITH THE ROLE-FILLER TAGS APPENDED TO THE END OF EACH WORD! Do not alter the input text in any other way.
    """

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        temperature=0.0,
        system=system_message,
            messages=[
            {"role": "user", "content": cleaned_ocr}
        ]
    )

    return message.content[0].text


def annotate_credit(cleaned_ocr):

    system_message = """
    INSTRUCTIONS: Your job is to match roles and fillers (names) in the following OCR text, which represents a screenshot taken from a public broadcast video. The frame type is CREDIT, meaning the names will typically -- but not always -- appear AFTER their role. There may be multiple names corresponding with a given role. Do NOT correct any misspellings. There may be text in the input that is not explicitly matched with a role or name; in those cases, tag them with O. 
    There should be no roles that aren't co-indexed with a filler, and no fillers that aren't co-indexed with a role. If you try to tag a filler with a role that doesn't appear in a corresponding filler or vice-versa, it should be tagged O instead. Many OCR errors may be present; just do your best to figure out what the underlying structure/meaning of the text. When in doubt, tag O! Be conservative i.e. use lots of O's.

    Please use the following format based in BIO format with indices:

    Format: Tag the end of each word with @(BIO rfb tag), where BIO rfb tag is one of the following:

    BR:i - meaning "begin role i" where i is an index
    IR:i - meaning "in role i"
    BF:i - meaning "begin filler corresponding with role i"
    IF:i - meaning "continue filler corresponding with role i"
    O - meaning not a role or filler

    EXAMPLES:
    OCR STRING: Director Stanley Kubrick Actors Jack Nicholson Shelley Duvall
    OUTPUT:
    Director@BR:1 Stanley@BF:1 Kubrick@IF:1 Actors@BR:2 Jack@BF:2 Nicholson@IF:2 Shelley@BF:2 Duvall@IF:2

    OCR STRING: John Doe PRODUCTION ASSISTANT LuAnne Halligan POST PRODUCTION SUPERVISOR Maggi s66ug

    OUTPUT: John@O Doe@O PRODUCTION@BR:1 ASSISTANT@IR:1 LuAnne@BF:1 Halligan@IF:1 POST@BR:2 PRODUCTION@IR:2 SUPERVISOR@IR:2 Maggi@BF:2 s66ug@IF:2

    OCR STRING: ENG Crews RUSSELL MARHULL GARY ALLEN CHARLES IDE ED LEE RIC NELSON DAVID PICKERAL STEVE LEDERER BILL MCMILLIN WIC VAN VRANKEN

    OUTPUT: ENG@BR:1 Crews@IR:1 RUSSELL@BF:1 MARHULL@IF:1 GARY@BF:1 ALLEN@IF:1 CHARLES@BF:1 IDE@IF:1 ED@BF:1 LEE@IF:1 RIC@BF:1 NELSON@IF:1 DAVID@BF:1 PICKERAL@IF:1 STEVE@BF:1 LEDERER@IF:1 BILL@BF:1 MCMILLIN@IF:1 WIC@BF:1 VAN@IF:1 VRANKEN@IF:1

    The most important thing to remember: THE OUTPUT SHOULD BE IDENTICAL TO THE INPUT, VERBATIM, WITH THE ROLE-FILLER TAGS APPENDED TO THE END OF EACH WORD! Do not alter the input text in any other way.    """

    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        temperature=0.0,
        system=system_message,
            messages=[
            {"role": "user", "content": cleaned_ocr}
        ]
    )

    return message.content[0].text


def annotate_row(row):
    if row["ocr_accepted"] == False:
        words = row["cleaned_text"].split()
        return " ".join([f"{word}@O" for word in words])
    while True:
        try:
            if row["scene_label"] == "chyron":
                return annotate_chyron(row["cleaned_text"])
            elif row["scene_label"] == "credit":
                return annotate_credit(row["cleaned_text"])
        except Exception as e:
            print(e)
            time.sleep(30)
            continue    


def annotate_df(df):
    df = df.dropna(subset=["cleaned_text"])
    df["silver_standard_annotation"] = df.progress_apply(annotate_row, axis=1)
    return df
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process data")
    parser.add_argument("--input_file", required=True, help="Input CSV file path")
    args = parser.parse_args()

    output_dir = os.path.join(BASE_DIR, "annotations/3-llm-in-progress")
    output_file = os.path.join(output_dir, os.path.basename(args.input_file))

    annotated_df = annotate_df(pd.read_csv(args.input_file))
    annotated_df.to_csv(output_file, index=False)
    os.remove(args.input_file)