import csv
import os
import numpy as np
import source_2herb

NUM_SIMULATIONS = 100
MAX_STEPS = 3000
OUTPUT_DIR = "sim_results_2herb"

HERB_ARMOR_GENES = ['speed', 'vision', 'sociability', 'armor', 'w_plant', 'w_threat']
HERB_NO_ARMOR_GENES = ['speed', 'vision', 'sociability', 'w_plant', 'w_threat']
CARN_GENES = ['speed', 'vision', 'sociability', 'strength', 'w_prey', 'w_competition']

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_gene_stats(entities, gene_name):
    """Calculates mean and std for a specific attribute in a list of entities."""
    if not entities:
        return 0.0, 0.0

    values = [getattr(e, gene_name) for e in entities]
    return np.mean(values), np.std(values)

def run_single_simulation(sim_id):
    world = source_2herb.World()
    world.init_population()
    
    sim_data = []
    
    for step in range(MAX_STEPS):
        world.step()

        all_living = [e for e in world.all_entities if not e.is_dead]
        
        herbs_armor = [e for e in all_living if isinstance(e, source_2herb.Herbivore_armor)]
        herbs_no_armor = [e for e in all_living if isinstance(e, source_2herb.Herbivore_no_armor)]
        carns = [e for e in all_living if isinstance(e, source_2herb.Carnivore)]
        
        total_herbs = len(herbs_armor) + len(herbs_no_armor)

        if total_herbs == 0 or len(carns) == 0:
            break

        row = {
            'step': step,
            'herb_armor_count': len(herbs_armor),
            'herb_no_armor_count': len(herbs_no_armor),
            'carn_count': len(carns)
        }

        for gene in HERB_ARMOR_GENES:
            mean, std = get_gene_stats(herbs_armor, gene)
            row[f'herb_armor_{gene}_mean'] = mean
            row[f'herb_armor_{gene}_std'] = std

        for gene in HERB_NO_ARMOR_GENES:
            mean, std = get_gene_stats(herbs_no_armor, gene)
            row[f'herb_no_armor_{gene}_mean'] = mean
            row[f'herb_no_armor_{gene}_std'] = std

        for gene in CARN_GENES:
            mean, std = get_gene_stats(carns, gene)
            row[f'carn_{gene}_mean'] = mean
            row[f'carn_{gene}_std'] = std
            
        sim_data.append(row)

    filename = os.path.join(OUTPUT_DIR, f"sim_{sim_id}.csv")
    if sim_data:
        keys = sim_data[0].keys()
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(sim_data)
            
    return step, len(herbs_armor), len(herbs_no_armor), len(carns)

def main():
    ensure_dir(OUTPUT_DIR)
    
    print(f"--- STARTING {NUM_SIMULATIONS} SIMULATIONS (2 Herbivore Species) ---")
    print(f"Output Directory: ./{OUTPUT_DIR}/")
    
    summary_file = os.path.join(OUTPUT_DIR, "summary.csv")
    
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['sim_id', 'duration_steps', 'final_herb_armor_count', 'final_herb_no_armor_count', 'final_carn_count'])
        
        for i in range(NUM_SIMULATIONS):
            print(f"Running Simulation {i+1}/{NUM_SIMULATIONS}...", end="\r")
            
            duration, h_a_end, h_na_end, c_end = run_single_simulation(i)
            
            writer.writerow([i, duration, h_a_end, h_na_end, c_end])
            f.flush()

    print(f"\n--- DONE. Data saved to {OUTPUT_DIR} ---")

if __name__ == "__main__":
    main()