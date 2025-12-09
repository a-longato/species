import pandas as pd
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = "sim_results_2herb_2carn"

def analyze_species_extinction(target_column, species_label, color_code):
    print(f"\nAnalyzing Extinction for: {species_label} ({target_column})")
    
    file_pattern = os.path.join(RESULTS_DIR, "sim_*.csv")
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"No files found in {RESULTS_DIR}")
        return

    data_points = []

    for filepath in files:
        try:
            df = pd.read_csv(filepath)
            sim_id = os.path.basename(filepath).replace("sim_", "").replace(".csv", "")
            
            total_duration = df['step'].max()

            zero_count_rows = df[df[target_column] == 0]
            
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

    print(f"Total Simulations:          {len(results_df)}")
    print(f"Extinction Events:          {len(extinct_df)} ({len(extinct_df)/len(results_df)*100:.1f}%)")
    
    if not extinct_df.empty:
        avg_step = extinct_df['extinction_step'].mean()
        avg_ratio = extinct_df['lifespan_ratio'].mean()

        print(f"Avg Time to Extinction:     {avg_step:.0f} steps")
        print(f"Avg % of Sim Survived:      {avg_ratio*100:.1f}%")

        plt.figure(figsize=(10, 6))

        plt.scatter(extinct_df['total_duration'], extinct_df['extinction_step'], 
                    color=color_code, alpha=0.6, label=f'Extinct ({species_label})')

        plt.scatter(survived_df['total_duration'], survived_df['extinction_step'], 
                    color='black', marker='^', alpha=0.6, label='Survived')

        max_val = max(results_df['total_duration'].max(), 100)
        plt.plot([0, max_val], [0, max_val], color='black', linestyle='--', alpha=0.5, label='Full Lifespan')

        plt.title(f"{species_label}: Extinction Time vs. Duration", fontsize=14)
        plt.xlabel("Total Simulation Duration (Steps)", fontsize=12)
        plt.ylabel("Extinction Step", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        filename_safe = species_label.replace(" ", "_").lower()
        scatter_filename = f"extinction_scatter_{filename_safe}.png"
        plt.savefig(scatter_filename)
        print(f"Scatter plot saved as: {scatter_filename}")
        plt.close()

def main():
    print("--- EXTINCTION ANALYSIS (2 Herb / 2 Carn) ---")

    analyze_species_extinction(
        target_column='herb_fast_count', 
        species_label='Herbivore Fast', 
        color_code='green'
    )
    
    print("-" * 40)

    analyze_species_extinction(
        target_column='carn_fast_count', 
        species_label='Carnivore Fast', 
        color_code='orange'
    )

if __name__ == "__main__":
    main()