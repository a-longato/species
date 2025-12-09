import random
import config
import numpy as np
import math

class World():
    def __init__(self):
        """
        Initializes the World environment by creating a grid of Cell objects 
        according to the dimensions specified in the config, and prepares 
        an empty registry for all entities.
        """
        self.grid = [[Cell(x, y, self) for x in range(config.DIM)] for y in range(config.DIM)]
        self.all_entities = []
    
    def get_cell(self, x, y):
        """
        Retrieves the Cell object at the specified (x, y) coordinates. 
        Implements toroidal (wrap-around) logic so coordinates that exceed 
        grid boundaries wrap to the opposite side.
        """
        # Toroidal grid (wrap-around) helps stabilize populations by removing "corners" where prey get cornered
        return self.grid[y % config.DIM][x % config.DIM]
    
    def get_neighborhood_cells(self, x, y, radius):
        """
        Returns a list of all Cell objects situated within a square radius 
        around the specified (x, y) center point, utilizing toroidal wrapping.
        """
        cells = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Using toroidal get_cell logic
                cells.append(self.get_cell(x + dx, y + dy))
        return cells

    def init_population(self):
        """
        Populates the world with the initial counts of Herbivores and Carnivores 
        at random empty locations, assigning them randomized starting genetic attributes.
        """
        # Initialize Herbivores
        for _ in range(config.INIT_HERB):
            while True:
                x = random.randint(0, config.DIM - 1)
                y = random.randint(0, config.DIM - 1)
                cell = self.get_cell(x, y)
                if not cell.entities:
                    herb = Herbivore(x, y, config.INIT_ENERGY, 
                                    random.randint(1, config.MAX_INIT_SPEED),
                                    random.randint(1, config.MAX_INIT_VISION),
                                    random.randint(1, config.MAX_INIT_SOCIABILITY),
                                    random.randint(1, config.MAX_INIT_ARMOR),
                                    config.W_HERB_FOOD_DIRECT, config.W_HERB_THREAT)
                    cell.add(herb)
                    self.all_entities.append(herb)
                    break
        
        # Initialize Carnivores
        for _ in range(config.INIT_CARN):
            while True:
                x = random.randint(0, config.DIM - 1)
                y = random.randint(0, config.DIM - 1)
                cell = self.get_cell(x, y)
                if not cell.entities:
                    carn = Carnivore(x, y, config.INIT_ENERGY, 
                                    random.randint(1, config.MAX_INIT_SPEED), 
                                    random.randint(1, config.MAX_INIT_VISION),
                                    random.randint(1, config.MAX_INIT_SOCIABILITY),
                                    random.randint(1, config.MAX_INIT_STRENGTH),
                                    config.W_CARN_PREY, config.W_CARN_COMPETITION)
                    cell.add(carn)
                    self.all_entities.append(carn)
                    break

    def create_grid_image(self):
        """
        Constructs and returns a 3D NumPy array (RGB) representing the current visual 
        state of the grid, coloring cells based on the presence of ground, plants, 
        herbivores, or carnivores.
        """
        grid_image = np.full((config.DIM, config.DIM, 3), [0.6, 0.4, 0.2]) # Brown ground
        for y in range(config.DIM):
            for x in range(config.DIM):
                cell = self.get_cell(x,y)
                if cell.plant:
                    grid_image[y, x] = [0.2, 0.8, 0.2] # Green grass
                
                # Draw entities on top
                if cell.entities:
                    entity = cell.entities[0]
                    if isinstance(entity, Herbivore):
                        grid_image[y, x] = [0, 0, 1] # Blue Herbivore
                    elif isinstance(entity, Carnivore):
                        grid_image[y, x] = [1, 0, 0] # Red Carnivore
        return grid_image
    
    def grow(self, x, y):
        """
        Calculates the probability of plant growth for a specific cell based on 
        logistic-style rules (neighboring plant density) and updates the cell's 
        plant status if successful.
        """
        # Logistic-style growth based on neighbors
        cell = self.get_cell(x, y)
        if cell.plant == 0:
            grow_factor = 0
            neighbor_cells = self.get_neighborhood_cells(x, y, 1)
            for n_cell in neighbor_cells:
                if n_cell.plant:
                    grow_factor += 1
            
            # Probability increases with more plant neighbors
            chance = config.P_PLANT + (config.P_PLANT_NEIGHBOR_FACTOR * grow_factor)
            if random.random() < chance:
                cell.plant = 1

    def step(self):
        """
        Executes a single simulation tick. This includes:
        1. Planning: Entities decide where to move.
        2. Movement: Entities move if they have sufficient energy.
        3. Actions: Metabolism, aging, eating plants, hunting prey, and reproduction.
        4. Cleanup: Removing dead entities and registering newborns.
        5. Regrowth: Updating plant life on the grid.
        """
        random.shuffle(self.all_entities)
        
        # PLANNING PHASE
        planned_moves = []
        for entity in self.all_entities:
            if entity.is_dead: continue
            destination_cell = entity.plan(self)
            planned_moves.append({'entity': entity, 'destination': destination_cell})
        
        # MOVEMENT PHASE
        for move in planned_moves:
            entity = move['entity']
            destination = move['destination']
            current_cell = self.get_cell(entity.x, entity.y)
            
            if current_cell != destination:
                dist = math.sqrt((entity.x - destination.x)**2 + (entity.y - destination.y)**2)
                cost = int(dist * config.ENERGY_MOVE_COST)
                
                if entity.energy > cost:
                    current_cell.remove(entity)
                    destination.add(entity)
                    entity.energy -= cost
                else:
                    # Too tired to move, stay put
                    pass

        # ACTION PHASE
        newborns = []
        
        for entity in self.all_entities:
            if entity.is_dead: continue

            # METABOLISM AND AGING
            entity.age += 1
            entity.energy -= config.ENERGY_IDLE_COST
            
            # Death by old age or starvation
            if entity.energy <= 0 or entity.age >= entity.max_life:
                entity.is_dead = True
                continue 

            # HERBIVORE LOGIC
            if isinstance(entity, Herbivore):
                # Graze
                cell = self.get_cell(entity.x, entity.y)
                if cell.plant > 0:
                    # Don't exceed max energy
                    gained = min(config.ENERGY_PER_PLANT, config.MAX_ENERGY - entity.energy)
                    entity.energy += gained
                    cell.plant = 0
                
                # Reproduce
                if entity.energy >= config.REPRODUCTION_THRESHOLD:
                    if random.random() < config.P_REPRODUCE_HERB:
                        child = entity.reproduce_asexual()
                        if child: newborns.append(child)

            # CARNIVORE LOGIC
            elif isinstance(entity, Carnivore):
                # Hunt
                action_taken = False
                hunt_radius = 1
                neighborhood = self.get_neighborhood_cells(entity.x, entity.y, hunt_radius)
                
                prey_list = []
                for cell in neighborhood:
                    for e in cell.entities:
                        if isinstance(e, Herbivore) and not e.is_dead and e.energy > 0:
                            prey_list.append(e)
                
                if prey_list:
                    prey = random.choice(prey_list)
                    advantage = (entity.strength * entity.energy) 
                    defense = (prey.armor * prey.energy)
                    success_chance = 0.5 + 0.5 * ((advantage - defense) / (advantage + defense))
                    
                    if random.random() < success_chance:
                        # Successful hunt, max energy check
                        gained = min(config.ENERGY_PER_PREY, config.MAX_ENERGY - entity.energy)
                        entity.energy += gained
                        prey.is_dead = True
                        action_taken = True
                    else:
                        # Failed hunt
                        entity.energy -= config.ENERGY_HUNT_COST
                # Reproduce
                if not action_taken and entity.energy >= config.REPRODUCTION_THRESHOLD:
                    if random.random() < config.P_REPRODUCE_CARN:
                        child = entity.reproduce_asexual()
                        if child: newborns.append(child)

        # CLEANUP
        survivors = []
        for entity in self.all_entities:
            if not entity.is_dead:
                survivors.append(entity)
            else:
                self.get_cell(entity.x, entity.y).remove(entity)
        
        self.all_entities = survivors
        # Add newborns
        for child in newborns:
            self.get_cell(child.x, child.y).add(child)
            self.all_entities.append(child)
            
        # REGROWTH
        for y in range(config.DIM):
            for x in range(config.DIM):
                self.grow(x,y)

class Cell():
    def __init__(self, x, y, world):
        """
        Initializes a single grid cell with specific coordinates, a reference to the 
        main world, and an initial random probability of containing a plant.
        """
        self.x = x
        self.y = y
        self.world = world
        self.plant = 1 if random.uniform(0, 1) < config.P_INIT_PLANT else 0
        self.entities = []
        
    def add(self, entity):
        """
        Adds an entity to this cell's internal list and updates the entity's 
        internal coordinate references to match this cell.
        """
        self.entities.append(entity)
        entity.x = self.x
        entity.y = self.y

    def remove(self, entity):
        """
        Removes a specific entity from this cell's internal list of occupants.
        """
        if entity in self.entities:
            self.entities.remove(entity)

class Animal():
    def __init__(self, x, y, energy, speed, vision, sociability):
        """
        Initializes the base attributes shared by all animals, including location, 
        metabolic stats, movement genes, and lifespan parameters.
        """
        self.x = x
        self.y = y
        self.energy = energy
        self.speed = speed
        self.vision = vision
        self.sociability = sociability
        self.is_dead = False
        self.age = 0
        self.max_life = random.randint(config.MIN_LIFESPAN, config.MAX_LIFESPAN)

    def mutate(self):
        """
        Iterates through the animal's genome and randomly increments or decrements 
        gene values based on the mutation probability defined in the config.
        """
        genome = self.get_genome()
        for gene in genome.keys():
            if random.random() < config.P_MUTATION:
                current_value = getattr(self, gene)
                change = random.choice([-1, 1])
                new_val = max(1, current_value + change)
                setattr(self, gene, new_val)

    def reproduce_asexual(self):
        """
        Creates and returns a new offspring instance. The parent transfers half 
        its energy to the child, and the child inherits the parent's genome 
        subject to mutation.
        """
        cost = self.energy // 2
        self.energy -= cost
        child = type(self)(self.x, self.y, cost, **self.get_genome())
        child.mutate()
        return child

class Herbivore(Animal):
    def __init__(self, x, y, energy, speed, vision, sociability, armor, w_plant, w_threat):
        """
        Initializes a Herbivore with specific defensive attributes (armor) and 
        behavioral weights (attraction to plants vs. fear of threats).
        """
        super().__init__(x, y, energy, speed, vision, sociability)
        self.armor = armor
        self.w_plant = w_plant
        self.w_threat = w_threat

    def get_genome(self):
        """
        Returns a dictionary containing the specific genetic attributes 
        (speed, vision, sociability, armor, and behavioral weights) of this Herbivore.
        """
        return {'speed': self.speed, 'vision': self.vision, 'sociability': self.sociability, 'armor': self.armor,
                'w_plant': self.w_plant, 'w_threat': self.w_threat}

    def plan(self, world):
        """
        Evaluates the local neighborhood to determine the best destination cell.
        Scores potential moves based on food proximity, distance from Carnivores 
        (threats), and herd density (sociability).
        """
        possible_moves = world.get_neighborhood_cells(self.x, self.y, int(self.speed))
        
        # Get all visible entities once
        visible_cells = world.get_neighborhood_cells(self.x, self.y, int(self.vision))
        local_plants = [c for c in visible_cells if c.plant]
        local_carns = [e for c in visible_cells for e in c.entities if isinstance(e, Carnivore)]
        
        scores = {}
        
        for move_cell in possible_moves:
            score = 0.0
            
            # FOOD ATTRACTION
            if move_cell.plant:
                score += self.w_plant
            elif local_plants:
                for plant_cell in local_plants:
                    dist_sq = (plant_cell.x - move_cell.x)**2 + (plant_cell.y - move_cell.y)**2
                    if dist_sq == 0: dist_sq = 0.1
                    score += (self.w_plant * 0.5) / dist_sq

            # THREAT AVOIDANCE
            for carn in local_carns:
                dist_sq = (carn.x - move_cell.x)**2 + (carn.y - move_cell.y)**2
                if dist_sq == 0: dist_sq = 0.1
                score -= self.w_threat / dist_sq
            
            # HERDING
            herd_count = sum(1 for e in move_cell.entities if isinstance(e, Herbivore) and e is not self)
            score += herd_count * (self.sociability-1)
            
            # FINAL SCORE
            scores[move_cell] = score

        if not scores:
            return world.get_cell(self.x, self.y)

        max_score = max(scores.values())
        best_cells = [cell for cell, score in scores.items() if score == max_score]
        return random.choice(best_cells) # Avoid going always in the same direction if all cells are equal

class Carnivore(Animal):
    def __init__(self, x, y, energy, speed, vision, sociability, strength, w_prey, w_competition):
        """
        Initializes a Carnivore with specific offensive attributes (strength) and 
        behavioral weights (attraction to prey vs. avoidance of competition).
        """
        super().__init__(x, y, energy, speed, vision, sociability)
        self.strength = strength
        self.w_prey = w_prey
        self.w_competition = w_competition

    def get_genome(self):
        """
        Returns a dictionary containing the specific genetic attributes 
        (speed, vision, sociability, strength, and behavioral weights) of this Carnivore.
        """
        return {'speed': self.speed, 'vision': self.vision, 'sociability': self.sociability,
                'strength': self.strength, 'w_prey': self.w_prey, 'w_competition': self.w_competition}

    def plan(self, world):
        """
        Evaluates the local neighborhood to determine the best destination cell.
        Scores potential moves based on prey proximity and avoidance of other 
        Carnivores (competition).
        """
        possible_moves = world.get_neighborhood_cells(self.x, self.y, int(self.speed))
        
        # Get all visible entities once
        visible_cells = world.get_neighborhood_cells(self.x, self.y, int(self.vision))
        local_herbs = [e for c in visible_cells for e in c.entities if isinstance(e, Herbivore)]
        local_carns = [e for c in visible_cells for e in c.entities if isinstance(e, Carnivore) and e is not self]

        scores = {}

        for move_cell in possible_moves:
            score = 0.0
            
            # PREY ATTRACTION
            if local_herbs:
                for herb in local_herbs:
                    dist_sq = (herb.x - move_cell.x)**2 + (herb.y - move_cell.y)**2
                    if dist_sq == 0: dist_sq = 0.1
                    score += self.w_prey / dist_sq
            
            # COMPETITION AVOIDANCE
            for carn in local_carns:
                dist_sq = (carn.x - move_cell.x)**2 + (carn.y - move_cell.y)**2
                if dist_sq == 0: dist_sq = 0.1
                score -= (self.w_competition * (1/self.sociability)) / dist_sq
            
            scores[move_cell] = score
            
        if not scores:
            return world.get_cell(self.x, self.y)

        max_score = max(scores.values())
        best_cells = [cell for cell, score in scores.items() if score == max_score]
        return random.choice(best_cells)