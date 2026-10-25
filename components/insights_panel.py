import streamlit as st
from modules.analysis import compute_climate_insights

def render_insights_panel(ds, selected_var):
    """Renders formatted summary statistics for the selected climate variable."""
    st.markdown('<div class="section-header">📊 Summary Statistics</div>', unsafe_allow_html=True)
    st.caption("Statistics over the supplied dataset. Mean uses latitude-area weights on regular grids and equal weight per time step.")
    with st.spinner("Computing statistics…"):
        insights = compute_climate_insights(ds, selected_var)
        
    if insights is None:
        st.warning("Could not compute insights for this variable.")
        return
        
    st.markdown(f"""
- **Area-weighted Dataset Mean**: `{insights['global_avg']:.4f}`
- **Maximum Value**: `{insights['max_value']:.4f}` at **{insights['max_location']}**
- **Minimum Value**: `{insights['min_value']:.4f}` at **{insights['min_location']}**
""")
    
    if insights.get('largest_change') is not None:
        change = insights['largest_change']
        direction = "increase" if change > 0 else "decrease"
        st.markdown(f"- **Largest Step Change**: `{change:+.4f}` ({direction}) between **{insights['largest_change_times']}**")
    else:
        st.markdown("- **Largest Step Change**: _At least two valid time steps are required_")
