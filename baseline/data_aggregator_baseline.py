import pandas as pd
import glob
import os

RESULTS_DIR = "sim_results_baseline"
OUTPUT_FILE = "gene_stats_baseline.csv"

all_files = glob.glob(os.path.join(RESULTS_DIR, "sim_*.csv"))

if not all_files:
    print("No data found!")
else:
    df_list = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df_list.append(df)

    combined_df = pd.concat(df_list)
    grouped = combined_df.groupby('step')

    mean_df = grouped.mean().add_suffix('_mean')
    std_df = grouped.std().add_suffix('_std')

    final_df = pd.concat([mean_df, std_df], axis=1).reset_index()

    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Created {OUTPUT_FILE}")