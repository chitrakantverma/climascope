import streamlit as st
from modules.analysis import compute_climate_insights
from modules.variable_adapter import get_variable_info, normalize_values
import numpy as np

def render_insights_panel(ds, selected_var):
    """Renders formatted summary statistics for the selected climate variable."""
    st.subheader("Dataset summary")
    st.caption("Statistics over the supplied dataset. Mean uses latitude-area weights on regular grids and equal weight per time step.")
    with st.spinner("Computing statistics…"):
        insights = compute_climate_insights(ds, selected_var)
        
    if insights is None:
        st.warning("Could not compute insights for this variable.")
        return
        
    info = get_variable_info(ds, selected_var)
    units = info['display_units'] or 'native units'
    avg, maximum, minimum = normalize_values(np.array([insights['global_avg'], insights['max_value'], insights['min_value']]), info)
    st.markdown(f"""
- **Area-weighted mean**: `{avg:.2f} {units}`
- **Maximum**: `{maximum:.2f} {units}` at **{insights['max_location']}**
- **Minimum**: `{minimum:.2f} {units}` at **{insights['min_location']}**
""")
    
    if insights.get('largest_change') is not None:
        change = insights['largest_change'] / (100.0 if info.get('needs_pa_to_hpa') else 1.0)
        direction = "increase" if change > 0 else "decrease"
        st.markdown(f"- **Largest step change**: `{change:+.2f} {units}` ({direction}) between **{insights['largest_change_times']}**")
    else:
        st.markdown("- **Largest step change**: _At least two valid time steps are required_")
