import streamlit as st
from source_2herb_2carn import World, Herbivore_Armored, Herbivore_Fast, Carnivore_Strong, Carnivore_Fast
import matplotlib.pyplot as plt
import time
import config_2herb_2carn as config
import pandas as pd

st.set_page_config(layout="wide")
st.title("SPECIES: Niche Partitioning Experiment")

def get_population_stats(entities):
    """
    Calculates average and max stats for a list of animal entities.
    Returns a formatted Pandas DataFrame.
    """
    if not entities:
        return pd.DataFrame()

    genomes = [e.get_genome() for e in entities]
    df = pd.DataFrame(genomes)

    display_cols = [col for col in df.columns if not col.startswith('w_')]

    stats_df = pd.concat([
        df[display_cols].mean().rename('Avg'), 
        df[display_cols].max().rename('Max')
    ], axis=1)
    
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
        
        h_armored = [e for e in all_entities if isinstance(e, Herbivore_Armored)]
        h_fast    = [e for e in all_entities if isinstance(e, Herbivore_Fast)]
        c_strong  = [e for e in all_entities if isinstance(e, Carnivore_Strong)]
        c_fast    = [e for e in all_entities if isinstance(e, Carnivore_Fast)]

        st.session_state.history.append({
            'Tick': st.session_state.tick,
            'Herb (Armor)': len(h_armored),
            'Herb (Fast)': len(h_fast),
            'Carn (Strong)': len(c_strong),
            'Carn (Fast)': len(c_fast)
        })

        ax.clear()
        ax.imshow(st.session_state.world.create_grid_image(), interpolation='nearest')
        ax.axis('off')
        grid_placeholder.pyplot(fig)

        if st.session_state.history:
            history_df = pd.DataFrame(st.session_state.history).set_index('Tick')
            line_chart_placeholder.line_chart(history_df)

        with stats_placeholder.container():
            st.subheader("Population Statistics")

            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                st.markdown("### Standard Herbivores")
                st.metric("Count", len(h_armored))
                st.dataframe(get_population_stats(h_armored), width='stretch')
            
            with row1_col2:
                st.markdown("### Light Herbivores")
                st.metric("Count", len(h_fast))
                st.dataframe(get_population_stats(h_fast), width='stretch')

            st.divider()

            # Row 2: Carnivores
            row2_col1, row2_col2 = st.columns(2)
            with row2_col1:
                st.markdown("### Standard Carnivores")
                st.metric("Count", len(c_strong))
                st.dataframe(get_population_stats(c_strong), width='stretch')
            
            with row2_col2:
                st.markdown("### Light Carnivores")
                st.metric("Count", len(c_fast))
                st.dataframe(get_population_stats(c_fast), width='stretch')

        tick_counter_placeholder.write(f"**Tick:** {st.session_state.tick}")

        total_herbivores = len(h_armored) + len(h_fast)
        total_carnivores = len(c_strong) + len(c_fast)
        
        if total_herbivores == 0:
            st.session_state.running = False
            st.toast("Simulation Stopped: All herbivores are extinct.")
        elif total_carnivores == 0:
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
    st.info("Grid Legend:\n\nBlue: All Herbivores\n\nRed: All Carnivores\n\nGreen: Plants")

col1, col2 = st.columns([1.5, 2])

with col1:
    st.subheader("Simulation Grid")
    fig, ax = plt.subplots(figsize=(8, 8))
    grid_placeholder = st.empty()

with col2:
    st.subheader("Population Trends")
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
        history_df = pd.DataFrame(columns=['Herb (Armor)', 'Herb (Fast)', 'Carn (Strong)', 'Carn (Fast)'])
    
    line_chart_placeholder.line_chart(history_df)

    with stats_placeholder.container():
        all_entities = st.session_state.world.all_entities
        
        h_armored = [e for e in all_entities if isinstance(e, Herbivore_Armored)]
        h_fast    = [e for e in all_entities if isinstance(e, Herbivore_Fast)]
        c_strong  = [e for e in all_entities if isinstance(e, Carnivore_Strong)]
        c_fast    = [e for e in all_entities if isinstance(e, Carnivore_Fast)]
        
        st.subheader("Population Statistics")
        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            st.markdown("### Standard Herbivores")
            st.metric("Count", len(h_armored))
            st.dataframe(get_population_stats(h_armored), width='stretch')
        with row1_col2:
            st.markdown("### Light Herbivores")
            st.metric("Count", len(h_fast))
            st.dataframe(get_population_stats(h_fast), width='stretch')

        st.divider()

        row2_col1, row2_col2 = st.columns(2)
        with row2_col1:
            st.markdown("### Standard Carnivores")
            st.metric("Count", len(c_strong))
            st.dataframe(get_population_stats(c_strong), width='stretch')
        with row2_col2:
            st.markdown("### Light Carnivores")
            st.metric("Count", len(c_fast))
            st.dataframe(get_population_stats(c_fast), width='stretch')