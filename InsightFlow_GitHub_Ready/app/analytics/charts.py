import json

def get_dashboard_chart_configs(kpis):
    """
    Returns chart configurations and dataset arrays structured for Chart.js.
    """
    # 1. Revenue Trend Line Chart
    revenue_trend_chart = {
        'type': 'line',
        'data': {
            'labels': kpis['months'],
            'datasets': [
                {
                    'label': f"This year ({kpis.get('current_year', 2025)})",
                    'data': kpis['revenue_trend_current'],
                    'borderColor': '#6C5CE7',
                    'backgroundColor': 'rgba(108, 92, 231, 0.12)',
                    'fill': True,
                    'tension': 0.42,
                    'borderWidth': 3,
                    'pointRadius': 0,
                    'pointHoverRadius': 6,
                    'pointHoverBackgroundColor': '#6C5CE7',
                    'pointHoverBorderColor': '#FFFFFF',
                    'pointHoverBorderWidth': 2
                },
                {
                    'label': f"Last year ({kpis.get('previous_year', 2024)})",
                    'data': kpis['revenue_trend_previous'],
                    'borderColor': '#C4C2FD',
                    'backgroundColor': 'transparent',
                    'borderDash': [5, 5],
                    'fill': False,
                    'tension': 0.42,
                    'borderWidth': 2,
                    'pointRadius': 0
                }
            ]
        }
    }

    # 2. Revenue By Channel Donut Chart
    channel_labels = [c['channel'] for c in kpis['channels']]
    channel_values = [c['revenue'] for c in kpis['channels']]
    channel_colors = ['#6C5CE7', '#00CEC9', '#45AAF2', '#FFA502', '#2ED573']

    channel_donut_chart = {
        'type': 'doughnut',
        'data': {
            'labels': channel_labels,
            'datasets': [{
                'data': channel_values,
                'backgroundColor': channel_colors[:len(channel_labels)],
                'borderWidth': 0,
                'hoverOffset': 6
            }]
        },
        'options': {
            'cutout': '72%',
            'plugins': {
                'legend': {'display': False}
            }
        }
    }

    # 3. Orders By Quarter Grouped Bar Chart
    quarters = kpis.get('quarters', {'labels': ['Q1', 'Q2', 'Q3', 'Q4'], 'current': [1760, 1930, 2240, 2530], 'previous': [1520, 1710, 1950, 2280]})
    orders_bar_chart = {
        'type': 'bar',
        'data': {
            'labels': quarters['labels'],
            'datasets': [
                {
                    'label': f"{kpis.get('current_year', 2025)}",
                    'data': quarters['current'],
                    'backgroundColor': '#6C5CE7',
                    'borderRadius': 6,
                    'barThickness': 18
                },
                {
                    'label': f"{kpis.get('previous_year', 2024)}",
                    'data': quarters['previous'],
                    'backgroundColor': '#D6D4FF',
                    'borderRadius': 6,
                    'barThickness': 18
                }
            ]
        }
    }

    return {
        'revenue_trend': revenue_trend_chart,
        'revenue_channel': channel_donut_chart,
        'orders_quarter': orders_bar_chart
    }
