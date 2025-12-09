import streamlit as st
from source_baseline import World, Herbivore, Carnivore
import matplotlib.pyplot as plt
import time
import config
import pandas as pd

st.set_page_config(layout="wide")
st.title("SPECIES")

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

        herbivores = [e for e in st.session_state.world.all_entities if isinstance(e, Herbivore)]
        carnivores = [e for e in st.session_state.world.all_entities if isinstance(e, Carnivore)]
        
        st.session_state.history.append({
            'Tick': st.session_state.tick,
            'Herbivores': len(herbivores),
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
            st.metric("Herbivores", len(herbivores))
            st.dataframe(get_population_stats(herbivores), width='stretch')
            st.metric("Carnivores", len(carnivores))
            st.dataframe(get_population_stats(carnivores), width='stretch')

        tick_counter_placeholder.write(f"**Tick:** {st.session_state.tick}")
        
        if not herbivores or not carnivores:
            st.session_state.running = False
            st.toast("A population has gone extinct! Simulation stopped.")

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
    st.info("Grid Legend:\n\nBlue: Herbivores\n\nRed: Carnivores\n\nGreen: Plants")


col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Simulation Grid")
    fig, ax = plt.subplots(figsize=(10, 10))
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
        history_df = pd.DataFrame(columns=['Herbivores', 'Carnivores'])
    
    line_chart_placeholder.line_chart(history_df)
    
    with stats_placeholder.container():
        herbivores = [e for e in st.session_state.world.all_entities if isinstance(e, Herbivore)]
        carnivores = [e for e in st.session_state.world.all_entities if isinstance(e, Carnivore)]
        st.subheader("Population Stats")
        st.metric("Herbivores", len(herbivores))
        st.dataframe(get_population_stats(herbivores), width='stretch')
        st.metric("Carnivores", len(carnivores))
        st.dataframe(get_population_stats(carnivores), width='stretch')