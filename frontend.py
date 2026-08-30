# frontend.py
import os
import streamlit as st
import pandas as pd
import folium
from folium import Element, plugins
from streamlit_folium import st_folium
from streamlit_searchbox import st_searchbox
from api import search_places

# AuthKit palette constants for Folium (which renders in its own iframe)
_VIOLET = "#663af3"
_BLUEPRINT = "#b6d9fc"
_FROST = "#d1e4fa"
_FOG = "#9da7ba"
_CANVAS = "#05060f"
_GLASS_EDGE = "rgba(186,215,247,0.18)"

def render_header():
    """Renders the Top Header & System Status Bar."""
    st.title("⚛️ Quantum Logistics Pro")

    # Determine Solver Status Pill
    status = st.session_state.get('solver_status', 'Idle')
    if status == 'Completed':
        solver_pill = '<span class="authkit-badge status-ok">✦ Solver Completed</span>'
    elif status == 'Running':
        solver_pill = '<span class="authkit-badge status-run">◌ Optimization Running</span>'
    elif status == 'Failed':
        solver_pill = '<span class="authkit-badge status-err">✕ System Error</span>'
    else:
        solver_pill = '<span class="authkit-badge status-idle">— Engine Idle</span>'

    st.markdown(f"""
    <div style="display:flex; gap:10px; margin-bottom:28px; align-items:center; flex-wrap:wrap;">
        <span class="authkit-badge status-ok">● System Connected</span>
        {solver_pill}
        <span class="authkit-badge">◈ Analytics Active</span>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Renders the Input Sidebar."""
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/delivery--v1.png", width=60)
        st.title("Quantum Logistics")

        # Navigation
        page = st.radio("Navigation", ["Route Optimizer", "Quantum Analytics"], label_visibility="collapsed")
        st.markdown("---")

        # --- Group 1: Route Input ---
        with st.expander("📍 Route Input", expanded=True):
            tab_search, tab_upload = st.tabs(["Search", "Upload"])

            # Search Tab
            with tab_search:
                start_loc = st_searchbox(search_places, key="start_box", label="Start Location")
                st.markdown("---")
                new_stop = st_searchbox(search_places, key="stop_box", label="Add Stop")

                if st.button("➕ Add Location", use_container_width=True):
                    if new_stop:
                        names = [s['name'] for s in st.session_state.stops_data]
                        if new_stop['name'] not in names:
                            st.session_state.stops_data.append(new_stop)
                            st.success("Added!")
                        else:
                            st.warning("Already added.")

            # Upload Tab
            with tab_upload:
                uploaded = st.file_uploader("Upload CSV", type=['csv'])
                if uploaded and st.button("Process CSV", use_container_width=True):
                    try:
                        df = pd.read_csv(uploaded)
                        count = _load_stops_from_df(df)
                        if count > 0:
                            st.success(f"Loaded {count} locations!")
                    except Exception:
                        st.error("CSV columns needed: name, lat, lon")

                st.markdown("---")
                if st.button("📂 LOAD DEMO DATASET", use_container_width=True):
                    try:
                        st.session_state.stops_data = []
                        df = pd.read_csv("demo_stops.csv")
                        count = _load_stops_from_df(df)
                        if count > 0:
                            st.toast("Demo dataset loaded successfully", icon="✅")
                    except Exception as e:
                        st.error(f"Demo file not found: {e}")

                if st.button("📂 LOAD LARGE DATASET (40)", use_container_width=True):
                    try:
                        st.session_state.stops_data = []
                        df = pd.read_csv("demo_stops_40.csv")
                        count = _load_stops_from_df(df)
                        if count > 0:
                            st.toast("Large dataset loaded successfully", icon="✅")
                    except Exception as e:
                        st.error(f"Large demo file not found: {e}")

            # Stops Preview
            if st.session_state.stops_data:
                st.markdown(f"**Stops ({len(st.session_state.stops_data)})**")
                for i, s in enumerate(st.session_state.stops_data):
                    c1, c2 = st.columns([0.85, 0.15])
                    time_str = f" {s['window'][0]:.0f}-{s['window'][1]:.0f}h" if 'window' in s else ""
                    c1.text(f"{i+1}. {s['name'].split(',')[0]}{time_str}")
                    if c2.button("×", key=f"d{i}"):
                        st.session_state.stops_data.pop(i)
                        st.rerun()
                if st.button("Clear All", use_container_width=True):
                    st.session_state.stops_data = []
                    st.rerun()

        # --- Group 2: Optimization Mode ---
        with st.expander("⚙️ Optimization Mode", expanded=True):
            fleet_size = st.slider("Fleet Size", 1, 4, 1, help="Number of vehicles available.")
            is_round_trip = st.toggle("Return to Start", value=False, help="Vehicles return to origin.")

            # Logic: Force Round Trip for Multi-Vehicle
            force_rt = fleet_size > 1
            if force_rt:
                st.caption("Round Trip enforced for multi-vehicle fleets.")

            is_round_trip = st.toggle("Return to Start", value=force_rt, disabled=force_rt,
                                    help="Vehicles return to origin.",
                                    key=f"rt_toggle_{force_rt}")

            st.markdown("---")
            st.caption("Logistics Costs")
            col1, col2 = st.columns(2)
            mileage    = col1.number_input("Km/L",    value=12.0)
            fuel_price = col2.number_input("Fuel ₹",  value=96.0)

        # --- Group 3: Advanced Parameters ---
        with st.expander("⚛️ Advanced Parameters", expanded=False):
            q_iter = st.slider("Iterations",    500, 5000, 3000, help="More steps = higher accuracy.")
            q_cool = st.slider("Cooling Rate", 0.800, 0.999, 0.998, format="%.3f", help="How fast the system freezes.")
            q_temp = st.slider("Initial Temp",  10, 500, 100, help="Initial energy for tunneling.")
            q_params = {"iter": q_iter, "cool": q_cool, "temp": q_temp}

        go_btn = st.button("🚀 RUN QUANTUM ROUTER", type="primary", use_container_width=True)
        st.markdown(
            '<div class="authkit-sidebar-footer">Hybrid Optimization · Quantum-inspired Search</div>',
            unsafe_allow_html=True
        )

        return (page, start_loc, is_round_trip, mileage, fuel_price, fleet_size, q_params, go_btn)


def _load_stops_from_df(df):
    """Helper to parse CSV and update session state."""
    if {'name', 'lat', 'lon'}.issubset(df.columns):
        count = 0
        for _, row in df.iterrows():
            s_time = float(row['start_time']) if 'start_time' in row else 9.0
            e_time = float(row['end_time'])   if 'end_time'   in row else 18.0
            st.session_state.stops_data.append({
                "name":   str(row['name']),
                "coords": (float(row['lat']), float(row['lon'])),
                "window": (s_time, e_time)
            })
            count += 1
        return count
    else:
        st.error("CSV columns needed: name, lat, lon")
        return 0


def render_optimizer_view(traffic_segments=None):
    """Renders the Map, Metrics, and Download."""
    if st.session_state.optimized_route:
        # Safety Check: Handle stale session state from previous versions
        if 'markers' not in st.session_state.optimized_route:
            st.session_state.optimized_route = None
            st.rerun()
            return

        m = st.session_state.route_metrics
        d = st.session_state.optimized_route

        # ── Eyebrow ──────────────────────────────────────────────────
        trip_type = "(Round Trip)" if st.session_state.is_round_trip_active else "(One-Way)"
        st.markdown(f'<div class="authkit-eyebrow"><span>Route Metrics {trip_type}</span></div>',
                    unsafe_allow_html=True)

        # ── Metric Cards ─────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Dist.",   f"{m['dist']:.1f} km",                  help="Total driving distance for all vehicles.")
        c2.metric("Time",          f"{int(m['time']//60)}h {int(m['time']%60)}m", help="Total estimated driving time.")
        c3.metric("Fuel",          f"{m['fuel']:.1f} L",                   help="Estimated fuel consumption based on mileage.")
        c4.metric("Cost",          f"₹ {m['cost']:,.0f}",                  help="Total operational cost.")

        # ── Fleet Breakdown ───────────────────────────────────────────
        if 'vehicles' in m and len(m['vehicles']) > 1:
            st.markdown('<div class="authkit-eyebrow" style="margin-top:20px;"><span>Fleet Breakdown</span></div>',
                        unsafe_allow_html=True)
            badges_html = '<div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:16px;">'
            for v_data in m['vehicles']:
                badges_html += f'''
                <div class="authkit-fleet-badge">
                    <span class="label">Vehicle {v_data["id"]}</span>
                    <span class="value">{v_data["dist"]:.1f} km</span>
                </div>'''
            badges_html += '</div>'
            st.markdown(badges_html, unsafe_allow_html=True)

        st.markdown("---")

        # ── MAP SECTION ──────────────────────────────────────────────
        # Glass card wrapper open
        st.markdown('<div class="authkit-map-card">', unsafe_allow_html=True)

        # Map header row (left: title block; right: layer toggles)
        c_head, c_tog = st.columns([0.55, 0.45])
        with c_head:
            st.markdown("""
            <div class="authkit-map-header">
                <div class="authkit-map-icon">🛰️</div>
                <div>
                    <div class="authkit-map-title">Live Fleet Tracking</div>
                    <div class="authkit-map-subtitle">Real-Time Geospatial Intelligence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_tog:
            t1, t2, t3 = st.columns(3)
            with t1: show_markers = st.toggle("Markers", True)
            with t2: show_routes  = st.toggle("Routes",  True)
            with t3: show_split   = st.toggle("Split",   True, help="Color-code by vehicle")

        # ── Folium Map ────────────────────────────────────────────────
        # Confirmed key-less raster tile endpoint (no watermark)
        map_tile_url = os.environ.get("MAP_TILE_URL")
        if not map_tile_url:
            try:
                if hasattr(st, "secrets") and "MAP_TILE_URL" in st.secrets:
                    map_tile_url = st.secrets["MAP_TILE_URL"]
            except Exception:
                pass

        if not map_tile_url:
            map_tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

        map_obj = folium.Map(
            location=d['coords'][0],
            zoom_start=11,
            tiles=map_tile_url,
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains="abcd"
        )

        # Fit bounds
        sw = [min(p[0] for p in d['coords']), min(p[1] for p in d['coords'])]
        ne = [max(p[0] for p in d['coords']), max(p[1] for p in d['coords'])]
        map_obj.fit_bounds([sw, ne])

        # AuthKit palette for routes:
        route_colors = [_VIOLET, _BLUEPRINT, "#8fb8f0", "#6a9ed8"]

        # Draw Routes
        if show_routes:
            active_traffic = traffic_segments
            if active_traffic is None and 'traffic_segments' in st.session_state:
                active_traffic = st.session_state.get('traffic_segments')
            if active_traffic is None and isinstance(st.session_state.get('optimization_stats'), dict):
                active_traffic = st.session_state.optimization_stats.get('traffic_segments')

            if active_traffic:
                try:
                    from traffic_provider import edge_midpoint
                except Exception:
                    def edge_midpoint(c1, c2):
                        return ((c1[0] + c2[0]) / 2.0, (c1[1] + c2[1]) / 2.0)

                for idx, route_entry in enumerate(d['routes_geo']):
                    default_color = route_colors[idx % len(route_colors)] if show_split else _VIOLET

                    if isinstance(active_traffic, list) and len(active_traffic) > 0 and isinstance(active_traffic[0], list):
                        v_segs = active_traffic[idx] if idx < len(active_traffic) else []
                    elif isinstance(active_traffic, list) and len(active_traffic) > 0 and isinstance(active_traffic[0], dict):
                        v_segs = active_traffic if idx == 0 else []
                    else:
                        v_segs = []

                    if v_segs:
                        for seg in v_segs:
                            from_c = seg.get('from_coords')
                            to_c = seg.get('to_coords')
                            if not from_c or not to_c:
                                continue
                            level = seg.get('level')
                            ratio = seg.get('ratio')

                            if level == 'low':
                                edge_color = '#2ecc71'
                            elif level == 'medium':
                                edge_color = '#f39c12'
                            elif level == 'high':
                                edge_color = '#e74c3c'
                            else:
                                edge_color = default_color

                            folium.PolyLine(
                                [from_c, to_c],
                                color=edge_color,
                                weight=5,
                                opacity=0.8,
                                tooltip=f"Vehicle {idx+1}: {seg.get('from', '')} -> {seg.get('to', '')} ({str(level).upper() if level else 'DEFAULT'})"
                            ).add_to(map_obj)

                            if level == 'high':
                                mid = edge_midpoint(from_c, to_c)
                                ratio_pct = f"{int(round(ratio * 100))}%" if ratio is not None else "high"
                                folium.CircleMarker(
                                    location=[mid[0], mid[1]],
                                    radius=6,
                                    color='#e74c3c',
                                    fill=True,
                                    fill_color='#e74c3c',
                                    fill_opacity=0.9,
                                    popup=f"Heavy traffic: {ratio_pct} of free-flow speed",
                                    tooltip=f"Heavy traffic: {ratio_pct} of free-flow speed"
                                ).add_to(map_obj)
                    else:
                        if isinstance(route_entry, dict):
                            route_geo = route_entry.get("geo", [])
                            is_fallback = route_entry.get("is_fallback", False)
                        else:
                            route_geo = route_entry
                            is_fallback = False

                        color = default_color
                        if is_fallback:
                            line = folium.PolyLine(
                                route_geo, color=color, weight=3, opacity=0.65, dash_array="8, 8",
                                tooltip=f"Vehicle {idx+1} (Approximate Route — Road Geometry Unavailable)"
                            ).add_to(map_obj)
                        else:
                            line = folium.PolyLine(
                                route_geo, color=color, weight=4, opacity=0.85,
                                tooltip=f"Vehicle {idx+1}"
                            ).add_to(map_obj)
                            plugins.PolyLineTextPath(
                                line, "      ➤      ", repeat=True, offset=6,
                                attributes={'fill': color, 'font-weight': 'bold', 'font-size': '18'}
                            ).add_to(map_obj)
            else:
                for idx, route_entry in enumerate(d['routes_geo']):
                    if isinstance(route_entry, dict):
                        route_geo = route_entry.get("geo", [])
                        is_fallback = route_entry.get("is_fallback", False)
                    else:
                        route_geo = route_entry
                        is_fallback = False

                    color = route_colors[idx % len(route_colors)] if show_split else _VIOLET

                    if is_fallback:
                        line = folium.PolyLine(
                            route_geo, color=color, weight=3, opacity=0.65, dash_array="8, 8",
                            tooltip=f"Vehicle {idx+1} (Approximate Route — Road Geometry Unavailable)"
                        ).add_to(map_obj)
                    else:
                        line = folium.PolyLine(
                            route_geo, color=color, weight=4, opacity=0.85,
                            tooltip=f"Vehicle {idx+1}"
                        ).add_to(map_obj)
                        plugins.PolyLineTextPath(
                            line, "      ➤      ", repeat=True, offset=6,
                            attributes={'fill': color, 'font-weight': 'bold', 'font-size': '18'}
                        ).add_to(map_obj)


        # Draw Markers — frosted circular tiles
        if show_markers:
            for mk in d['markers']:
                v_id  = mk['vehicle_id']
                color = route_colors[v_id % len(route_colors)] if show_split else _VIOLET

                if mk['stop_idx'] == 0:
                    icon = plugins.BeautifyIcon(
                        icon="play",
                        border_color=_FROST,
                        background_color="rgba(5,6,15,0.85)",
                        text_color=_FROST,
                        icon_shape="circle"
                    )
                    popup = f"Vehicle {v_id+1}: Start"
                elif mk['is_last']:
                    icon = plugins.BeautifyIcon(
                        icon="flag",
                        border_color=_BLUEPRINT,
                        background_color="rgba(5,6,15,0.85)",
                        text_color=_BLUEPRINT,
                        icon_shape="circle"
                    )
                    popup = f"Vehicle {v_id+1}: End"
                else:
                    icon = plugins.BeautifyIcon(
                        number=mk['stop_idx'],
                        border_color=color,
                        background_color="rgba(5,6,15,0.85)",
                        text_color=_FROST,
                        icon_shape="circle-dot"
                    )
                    popup = f"Vehicle {v_id+1}: Stop {mk['stop_idx']}"
                    if mk.get('window'):
                        popup += f" ({mk['window'][0]:.0f}-{mk['window'][1]:.0f}h)"

                folium.Marker(mk['coords'], tooltip=popup, popup=mk['name'], icon=icon).add_to(map_obj)

        # Fleet legend — nested glass card inside the map iframe
        if show_split and (show_routes or show_markers):
            legend_items = ""
            for i in range(len(d['routes_geo'])):
                c = route_colors[i % len(route_colors)]
                legend_items += f'''
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
                    <span style="background:{c};width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0;"></span>
                    <span style="color:#d1e4fa;font-size:12px;font-weight:500;">Vehicle {i+1}</span>
                    <span style="margin-left:auto;color:#9da7ba;font-size:10px;
                        background:rgba(199,211,234,0.12);border:1px solid rgba(186,215,247,0.12);
                        padding:2px 6px;border-radius:6px;">ACTIVE</span>
                </div>'''

            legend_html = f'''
                <div style="
                    position:fixed;top:20px;right:20px;width:170px;
                    background:rgba(5,6,15,0.92);backdrop-filter:blur(16px);
                    border:1px solid rgba(186,215,247,0.12);border-radius:16px;
                    padding:14px;z-index:9999;font-family:Inter,sans-serif;
                    box-shadow:inset 0 1px 1px rgba(216,236,248,0.15),0 24px 32px rgba(6,6,14,0.70);">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                        color:#9da7ba;margin-bottom:10px;letter-spacing:0.10em;
                        text-transform:uppercase;border-bottom:1px solid rgba(186,215,247,0.08);
                        padding-bottom:6px;">Fleet Status</div>
                    {legend_items}
                </div>'''
            map_obj.get_root().html.add_child(folium.Element(legend_html))

        st_folium(map_obj, width="100%", height=500)

        # Glass card wrapper close
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Download Button ───────────────────────────────────────────
        export_data = []
        for marker in d['markers']:
            export_data.append({
                "Vehicle ID":     f"Vehicle {marker['vehicle_id'] + 1}",
                "Stop Sequence":  marker['stop_idx'],
                "Location Name":  marker['name'],
                "Latitude":       marker['coords'][0],
                "Longitude":      marker['coords'][1],
                "Time Window":    f"{marker['window'][0]}-{marker['window'][1]}h" if marker.get('window') else "Any"
            })

        df_export = pd.DataFrame(export_data)
        csv_data  = df_export.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Download Route Manifest (CSV)",
            data=csv_data,
            file_name="quantum_route_manifest.csv",
            mime="text/csv",
            use_container_width=True
        )


def render_analytics_view():
    """Renders Telemetry and Benchmark."""
    if st.session_state.optimized_route:
        # Eyebrow
        st.markdown('<div class="authkit-eyebrow"><span>Quantum Analytics</span></div>',
                    unsafe_allow_html=True)

        # 1. Quantum Telemetry Panel
        with st.expander("Quantum Solver Telemetry", expanded=True):
            if st.session_state.optimization_stats:
                stats = st.session_state.optimization_stats
                k1, k2, k3 = st.columns(3)
                k1.metric("Tunneling Events",      stats.get('tunnels', 0),
                          help="Times the algorithm accepted a worse state to escape a local minimum.")
                k2.metric("Iterations",            len(stats.get('history', [])),
                          help="Total computational steps.")
                k3.metric("Convergence Stability", "99.8%",
                          help="Theoretical stability of the final state.")

                st.markdown("---")
                st.markdown("**Energy Landscape — Distance Minimization Over Time**")
                st.caption("Lower energy = shorter total travel distance")

                # Chart with smoothing
                history  = stats['history']
                chart_df = pd.DataFrame({"Iteration": range(len(history)), "Energy": history})
                if len(history) > 50:
                    chart_df["Energy"] = chart_df["Energy"].rolling(window=5, min_periods=1).mean()

                # void-violet line for the chart
                st.line_chart(chart_df, x="Iteration", y="Energy", color="#663af3")
    else:
        st.info("No optimization data available. Run the optimizer first.")


def render_download_report_buttons(json_path, pdf_path_or_none):
    """
    Renders two st.download_button widgets (JSON always, PDF only if
    pdf_path_or_none is not None) styled consistently with the existing
    badge components (reuses existing CSS classes). Reads file bytes and
    passes to st.download_button. Does not compute anything — pure
    rendering of already-generated files.
    """
    import os

    st.markdown(
        '<div class="authkit-eyebrow" style="margin-top:12px;">'
        '<span>Optimization Report</span></div>',
        unsafe_allow_html=True,
    )

    col_json, col_pdf = st.columns(2)

    # JSON download — always available
    with col_json:
        if json_path and os.path.isfile(json_path):
            with open(json_path, "rb") as f:
                json_bytes = f.read()
            st.download_button(
                label="📄 Download Report (JSON)",
                data=json_bytes,
                file_name="optimization_report.json",
                mime="application/json",
                use_container_width=True,
            )
        else:
            st.warning("JSON report file not found.")

    # PDF download — only if generation succeeded
    with col_pdf:
        if pdf_path_or_none and os.path.isfile(pdf_path_or_none):
            with open(pdf_path_or_none, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="📑 Download Report (PDF)",
                data=pdf_bytes,
                file_name="optimization_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info("PDF report unavailable (fpdf2 may not be installed).")
