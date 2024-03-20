import optparse
import pandas as pd
import warnings

# Command line arguments
parser = optparse.OptionParser()
parser.add_option("-f", "--file", dest="filename", help="input file", metavar="FILE")
parser.add_option("-p", "--pct_failed", dest = "pct_failed", help = "lower limit pct failed samples")

(options, args) = parser.parse_args()

# read input file
df = pd.read_csv(options.filename, sep=',')

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

# Raise warning if pct > user defined limit
fail_val = float(options.pct_failed)
if any(table_totals["pct"] > fail_val):
    failed_origins = table_totals.query(f"pct >{fail_val}").index
    fail_origins_str = ', '.join(map(str, failed_origins))
    print(table_totals)
    warnings.warn(f"The following origins have more than {fail_val}% failed samples: {fail_origins_str}")
