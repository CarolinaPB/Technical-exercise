import argparse
import pandas as pd
import warnings

# Command line arguments

parser = argparse.ArgumentParser(description="Create simple report of samples that failed QC")
parser.add_argument("-f", "--filename", help="Specify a file name", required=True)
parser.add_argument("-p", "--pct_failed", type=int, default=10, help="Lower limit pct failed samples. Specify a number (default: 10)", required=True)
parser.add_argument("-o", "--outfile", help="Specify an output file name", required=False, default="samples_summary.csv")
args = parser.parse_args()
# create command line arguments with argparse

args = parser.parse_args()

# read input file


def process_input(filename):
    """
    This function takes a filename as input and returns a pandas dataframe.
    The dataframe contains the number of samples that failed QC for each origin,
    as well as the total number of samples for each origin and the percentage of
    total samples that failed QC.

    Parameters
    ----------
    filename: str
        The path to the input file

    Returns
    -------
    pd.DataFrame
        A pandas dataframe containing the number of samples that failed QC for each origin,
        as well as the total number of samples for each origin and the percentage of
        total samples that failed QC.
    """
    df = pd.read_csv(filename, sep=',')
    # extract second letter of "sample" column
    df['origin'] = df.iloc[:,0].apply(lambda x: x[1])

    # How many samples have pct_covered_bases < 95 or qc_pass == false
    fail_qc = pd.DataFrame(df.query("pct_covered_bases < 95 | qc_pass == False").groupby("origin").count()["sample"])

    # count number of samples per origin
    total_samples_origin = pd.DataFrame(df.groupby("origin").count()["sample"])

    # join fail_qc with total_samples_origin by origin to create a table with
    # number of samples that fail qc as well as total number of samples for each origin
    # Also calculates percentage of total samples that fail qc
    table_totals = pd.merge(fail_qc, total_samples_origin, left_index=True, right_index=True).rename(columns={"sample_x": "n_fail_qc", "sample_y": "n_total_samples"})
    table_totals["pct"] = table_totals["n_fail_qc"] / table_totals["n_total_samples"] * 100
    return(table_totals)

processed_data = process_input(args.filename)

# Raise warning if pct > user defined limit
fail_val = float(args.pct_failed)
if any(processed_data["pct"] > fail_val):
    failed_origins = processed_data.query(f"pct >{fail_val}")
    failed_origins_idx = failed_origins.index
    fail_origins_str = ', '.join(map(str, failed_origins_idx))
    print(failed_origins)
    failed_origins.to_csv(args.outfile, sep=',')
    warnings.warn(f"The following origins have more than {fail_val}% failed samples: {fail_origins_str}")
else:
    print("All samples passed QC")
    
# alternatively, one could set up sending an email with the results to specified users
# I would start here for inspiration https://github.com/CarolinaPB/BioinfoCareerFair/blob/master/send_template_email.py