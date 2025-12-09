import csv
import os
import numpy as np
import source_2herb_2carn

NUM_SIMULATIONS = 100       
MAX_STEPS = 3000           
OUTPUT_DIR = "sim_results_2herb_2carn" 

HERB_GENES = ['speed', 'vision', 'sociability', 'armor', 'w_plant', 'w_threat']
CARN_GENES = ['speed', 'vision', 'sociability', 'strength', 'w_prey', 'w_competition']

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_gene_stats(entities, gene_name):
    """Calculates mean and std for a specific attribute."""
    if not entities:
        return 0.0, 0.0
    values = [getattr(e, gene_name) for e in entities]
    return np.mean(values), np.std(values)

def run_single_simulation(sim_id):
    world = source_2herb_2carn.World()
    world.init_population()
    
    sim_data = []
    
    for step in range(MAX_STEPS):
        world.step()

        all_living = [e for e in world.all_entities if not e.is_dead]
        
        h_armored = [e for e in all_living if isinstance(e, source_2herb_2carn.Herbivore_Armored)]
        h_fast    = [e for e in all_living if isinstance(e, source_2herb_2carn.Herbivore_Fast)]
        c_strong  = [e for e in all_living if isinstance(e, source_2herb_2carn.Carnivore_Strong)]
        c_fast    = [e for e in all_living if isinstance(e, source_2herb_2carn.Carnivore_Fast)]
        
        total_herbs = len(h_armored) + len(h_fast)
        total_carns = len(c_strong) + len(c_fast)

        if total_herbs == 0 or total_carns == 0:
            break

        row = {
            'step': step,
            'herb_armored_count': len(h_armored),
            'herb_fast_count': len(h_fast),
            'carn_strong_count': len(c_strong),
            'carn_fast_count': len(c_fast)
        }

        for gene in HERB_GENES:
            mean, std = get_gene_stats(h_armored, gene)
            row[f'herb_armored_{gene}_mean'] = mean
            row[f'herb_armored_{gene}_std'] = std

        for gene in HERB_GENES:
            mean, std = get_gene_stats(h_fast, gene)
            row[f'herb_fast_{gene}_mean'] = mean
            row[f'herb_fast_{gene}_std'] = std

        for gene in CARN_GENES:
            mean, std = get_gene_stats(c_strong, gene)
            row[f'carn_strong_{gene}_mean'] = mean
            row[f'carn_strong_{gene}_std'] = std

        for gene in CARN_GENES:
            mean, std = get_gene_stats(c_fast, gene)
            row[f'carn_fast_{gene}_mean'] = mean
            row[f'carn_fast_{gene}_std'] = std
            
        sim_data.append(row)

    filename = os.path.join(OUTPUT_DIR, f"sim_{sim_id}.csv")
    if sim_data:
        keys = sim_data[0].keys()
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(sim_data)
            
    return step, len(h_armored), len(h_fast), len(c_strong), len(c_fast)

def main():
    ensure_dir(OUTPUT_DIR)
    
    print(f"--- STARTING {NUM_SIMULATIONS} SIMULATIONS (4 Species) ---")
    print(f"Output Directory: ./{OUTPUT_DIR}/")
    
    summary_file = os.path.join(OUTPUT_DIR, "summary.csv")
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sim_id', 'duration_steps', 'final_h_armored', 'final_h_fast', 'final_c_strong', 'final_c_fast'])
        
        for i in range(NUM_SIMULATIONS):
            print(f"Running Simulation {i+1}/{NUM_SIMULATIONS}...", end="\r")
            
            duration, ha, hf, cs, cf = run_single_simulation(i)
            
            writer.writerow([i, duration, ha, hf, cs, cf])
            f.flush()

    print(f"\n--- DONE. Data saved to {OUTPUT_DIR} ---")

if __name__ == "__main__":
    main()