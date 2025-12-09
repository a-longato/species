import streamlit as st
from source_2herb import World, Herbivore_armor, Herbivore_no_armor, Carnivore
import matplotlib.pyplot as plt
import time
import config_2herb as config
import pandas as pd

st.set_page_config(layout="wide")
st.title("SPECIES: 2 Herbivore Populations")

def get_population_stats(entities):
    """
    Calculates average and max stats for a list of animal entities.
    Returns a formatted Pandas DataFrame.
    """
    genomes = [e.get_genome() for e in entities]
    df = pd.DataFrame(genomes)
    stats_df = pd.concat([df.mean().rename('Average'), df.max().rename('Max')], axis=1)
    return stats_df.round(2)

if 'world' not in st.session_state:
    st.session_state.world = World()
    st.session_state.world.init_population()
    st.session_state.running = False
    st.session_state.tick = 0
    st.session_state.history = []

def run_simulation():
    st.session_state.running = True
    while st.session_state.running:
        st.session_state.world.step()
        st.session_state.tick += 1

        all_entities = st.session_state.world.all_entities
        herb_armor = [e for e in all_entities if isinstance(e, Herbivore_armor)]
        herb_no_armor = [e for e in all_entities if isinstance(e, Herbivore_no_armor)]
        carnivores = [e for e in all_entities if isinstance(e, Carnivore)]

        st.session_state.history.append({
            'Tick': st.session_state.tick,
            'Herbivores (Armor)': len(herb_armor),
            'Herbivores (No Armor)': len(herb_no_armor),
            'Carnivores': len(carnivores)
        })

        ax.clear()
        ax.imshow(st.session_state.world.create_grid_image(), interpolation='nearest')
        ax.axis('off')
        grid_placeholder.pyplot(fig)

        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history).set_index('Tick')
            line_chart_placeholder.line_chart(history_df)

        with stats_placeholder.container():
            st.subheader("Population Stats")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("### Armored Herbivores")
                st.metric("Count", len(herb_armor))
                st.dataframe(get_population_stats(herb_armor), width='stretch')

            with c2:
                st.markdown("### Unarmored Herbivores")
                st.metric("Count", len(herb_no_armor))
                st.dataframe(get_population_stats(herb_no_armor), width='stretch')

            with c3:
                st.markdown("### Carnivores")
                st.metric("Count", len(carnivores))
                st.dataframe(get_population_stats(carnivores), width='stretch')

        tick_counter_placeholder.write(f"**Tick:** {st.session_state.tick}")

        total_herbivores = len(herb_armor) + len(herb_no_armor)
        
        if total_herbivores == 0:
            st.session_state.running = False
            st.toast("Simulation Stopped: All herbivores are extinct.")
        elif len(carnivores) == 0:
            st.session_state.running = False
            st.toast("Simulation Stopped: All carnivores are extinct.")

        time.sleep(1 / config.FPS)

with st.sidebar:
    st.header("Controls")
    if st.button("Start", key="start", width='stretch'):
        st.session_state.running = True
    if st.button("Stop", key="stop", width='stretch'):
        st.session_state.running = False
    if st.button("Reset World", key="reset", width='stretch'):
        st.session_state.world = World()
        st.session_state.world.init_population()
        st.session_state.running = False
        st.session_state.tick = 0
        st.session_state.history = []
        st.rerun()

    st.write("---")
    tick_counter_placeholder = st.empty()
    tick_counter_placeholder.write(f"**Tick:** {st.session_state.tick}")
    st.info("Grid Legend:\n\nBlue: All Herbivores\n\nRed: Carnivores\n\nGreen: Plants")


col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("Simulation Grid")
    fig, ax = plt.subplots(figsize=(8, 8))
    grid_placeholder = st.empty()

with col2:
    st.subheader("Population Over Time")
    line_chart_placeholder = st.empty()

stats_placeholder = st.empty()

if st.session_state.running:
    run_simulation()
else:
    ax.clear()
    ax.imshow(st.session_state.world.create_grid_image(), interpolation='nearest')
    ax.axis('off')
    grid_placeholder.pyplot(fig)

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history).set_index('Tick')
    else:
        history_df = pd.DataFrame(columns=['Armored Herbivores', 'Unarmored Herbivores', 'Carnivores'])
    
    line_chart_placeholder.line_chart(history_df)

    with stats_placeholder.container():
        all_entities = st.session_state.world.all_entities
        herb_armor = [e for e in all_entities if isinstance(e, Herbivore_armor)]
        herb_no_armor = [e for e in all_entities if isinstance(e, Herbivore_no_armor)]
        carnivores = [e for e in all_entities if isinstance(e, Carnivore)]
        
        st.subheader("Population Stats")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### Armored Herbivores")
            st.metric("Count", len(herb_armor))
            st.dataframe(get_population_stats(herb_armor), width='stretch')

        with c2:
            st.markdown("### Unarmored Herbivores")
            st.metric("Count", len(herb_no_armor))
            st.dataframe(get_population_stats(herb_no_armor), width='stretch')

        with c3:
            st.markdown("### Carnivores")
            st.metric("Count", len(carnivores))
            st.dataframe(get_population_stats(carnivores), width='stretch')