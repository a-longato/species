import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

RESULTS_DIR = "sim_results_2herb"
TARGET_COLUMN = "herb_no_armor_count"

def analyze_extinction():
    file_pattern = os.path.join(RESULTS_DIR, "sim_*.csv")
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"No files found in {RESULTS_DIR}")
        return

    data_points = []
    
    print(f"Analyzing {len(files)} simulation files...")

    for filepath in files:
        try:
            df = pd.read_csv(filepath)
            sim_id = os.path.basename(filepath).replace("sim_", "").replace(".csv", "")

            total_duration = df['step'].max()

            zero_count_rows = df[df[TARGET_COLUMN] == 0]
            
            if not zero_count_rows.empty:
                extinction_step = zero_count_rows.iloc[0]['step']
                survived = False
            else:
                extinction_step = total_duration
                survived = True
            
            data_points.append({
                'sim_id': sim_id,
                'extinction_step': extinction_step,
                'total_duration': total_duration,
                'survived': survived,
                'lifespan_ratio': extinction_step / total_duration if total_duration > 0 else 0
            })
                
        except Exception as e:
            print(f"Error reading {filepath}: {e}")

    results_df = pd.DataFrame(data_points)

    extinct_df = results_df[results_df['survived'] == False]
    survived_df = results_df[results_df['survived'] == True]

    print("\n" + "="*50)
    print("NO-ARMOR HERBIVORE SURVIVAL ANALYSIS")
    print("="*50)
    print(f"Total Simulations:          {len(results_df)}")
    print(f"Extinction Events:          {len(extinct_df)} ({len(extinct_df)/len(results_df)*100:.1f}%)")
    print(f"Survival Events:            {len(survived_df)}")
    print("-" * 50)
    
    if not extinct_df.empty:
        avg_step = extinct_df['extinction_step'].mean()
        avg_duration = results_df['total_duration'].mean()
        avg_ratio = extinct_df['lifespan_ratio'].mean()

        print(f"Avg Duration of Sim:        {avg_duration:.0f} steps")
        print(f"Avg Time to Extinction:     {avg_step:.0f} steps")
        print(f"Avg % of Sim Survived:      {avg_ratio*100:.1f}% (for extinct cases)")
        print(f"Fastest Extinction:         Step {extinct_df['extinction_step'].min()}")
        print("-" * 50)

        plt.figure(figsize=(10, 6))

        plt.scatter(extinct_df['total_duration'], extinct_df['extinction_step'], 
                    color='red', alpha=0.6, label='Extinct (No Armor)')

        plt.scatter(survived_df['total_duration'], survived_df['extinction_step'], 
                    color='green', marker='^', alpha=0.6, label='Survived')

        max_val = results_df['total_duration'].max()
        plt.plot([0, max_val], [0, max_val], color='gray', linestyle='--', alpha=0.5, label='Full Lifespan Line')

        plt.title("Extinction Time vs. Total Simulation Duration", fontsize=14)
        plt.xlabel("Total Simulation Duration (Steps)", fontsize=12)
        plt.ylabel("Step when No-Armor Herbivores Died", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        scatter_filename = "extinction_scatter.png"
        plt.savefig(scatter_filename)
        print(f"Scatter plot saved as: {scatter_filename}")

        plt.figure(figsize=(10, 6))
        plt.hist(extinct_df['extinction_step'], bins=20, color='teal', edgecolor='black', alpha=0.7)
        plt.title(f"Distribution of Extinction Steps (n={len(extinct_df)})", fontsize=14)
        plt.xlabel("Simulation Step", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.axvline(avg_step, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {avg_step:.0f}')
        plt.legend()
        plt.grid(axis='y', alpha=0.5)
        
        hist_filename = "extinction_histogram.png"
        plt.savefig(hist_filename)
        print(f"Histogram saved as: {hist_filename}")

    else:
        print("No extinction events detected.")

if __name__ == "__main__":
    analyze_extinction()