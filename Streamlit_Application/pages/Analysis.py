import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import pickle
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import seaborn as sns
import random

st.set_page_config(page_title="Plotting Demo")

st.title('Analytics')

new_df = pd.read_csv('datasets/data_viz1.csv')
feature_text = pickle.load(open('datasets/feature_text.pkl','rb'))

group_df = new_df.groupby('sector')[[
    'price',
    'price_per_sqft',
    'built_up_area',
    'latitude',
    'longitude'
]].mean().reset_index()

st.header('Sector Price per Sqft Geomap')

fig = px.scatter_map(
    group_df,
    lat="latitude",
    lon="longitude",
    color="price_per_sqft",
    size="built_up_area",
    hover_name="sector",
    hover_data={
        "price": ":,.2f",
        "price_per_sqft": ":,.2f",
        "built_up_area": ":,.0f",
        "latitude": False,
        "longitude": False
    },
    color_continuous_scale=px.colors.cyclical.IceFire,
    size_max=25,
    zoom=10,
    map_style="open-street-map",
    width=1200,
    height=700
)

fig.update_layout(
    title="Gurgaon Real Estate Price Distribution",
    margin={"r": 0, "t": 50, "l": 0, "b": 0},
    coloraxis_colorbar=dict(title="Price per Sqft")
)

fig.update_traces(marker=dict(opacity=0.8))

st.plotly_chart(fig, width="stretch")

# word cloud
st.header('Property Features Word Cloud')

width, height = 1200, 800

# Create house-shaped mask
mask_image = Image.new("L", (width, height), 255)
draw = ImageDraw.Draw(mask_image)

draw.polygon(
    [(600, 30), (1150, 350), (50, 350)],
    fill=0
)

draw.rectangle(
    [(150, 300), (1050, 780)],
    fill=0
)

house_mask = np.array(mask_image)

# Custom Violet-Purple color palette
purple_colors = [
    '#efbbff',
    '#d896ff',
    '#be29ec',
    '#800080',
    '#660066'
]

def purple_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return random.choice(purple_colors)

# Generate WordCloud
wordcloud = WordCloud(
    width=width,
    height=height,
    background_color='#0E0B16',
    mask=house_mask,
    stopwords=STOPWORDS.union({'s'}),
    min_font_size=10,
    max_font_size=150,
    max_words=200,
    color_func=purple_color_func,
    contour_width=2,
    contour_color='#d896ff',
    prefer_horizontal=0.9,
    relative_scaling=0.5,
    collocations=False
).generate(feature_text)

# Display
fig, ax = plt.subplots(figsize=(12, 8))

fig.patch.set_facecolor('#0E0B16')
ax.set_facecolor('#0E0B16')

ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')

plt.tight_layout(pad=0)

st.pyplot(fig)
plt.close(fig)

st.header('Area Vs Price')

property_type = st.selectbox('Select Property Type', ['flat','house'])

# if property_type == 'house':
#     fig1 = px.scatter(new_df[new_df['property_type'] == 'house'], x="built_up_area", y="price", color="bedRoom", title="Area Vs Price")
#
#     st.plotly_chart(fig1, use_container_width=True)
# else:
#     fig1 = px.scatter(new_df[new_df['property_type'] == 'flat'], x="built_up_area", y="price", color="bedRoom",
#                       title="Area Vs Price")
#
#     st.plotly_chart(fig1, use_container_width=True)

plot_df = new_df[new_df['property_type'] == property_type]

fig1 = px.scatter(
    plot_df,
    x="built_up_area",
    y="price",
    color="bedRoom",
    size="price",
    hover_data={
        "sector": True,
        "bathroom": True,
        "balcony": True,
        "price_per_sqft": True,
        "built_up_area": ":,.0f",
        "price": ":,.2f"
    },
    color_continuous_scale="Turbo",
    size_max=15,
    opacity=0.75,
    title=f"{property_type.title()} - Built-up Area vs Price",
    labels={
        "built_up_area": "Built-up Area (sq.ft.)",
        "price": "Property Price",
        "bedRoom": "Bedrooms"
    },
    trendline="ols"
)

fig1.update_layout(
    height=600,
    template="plotly_white",
    title_x=0.5,
    font=dict(family="Arial", size=13),
    margin=dict(l=40, r=30, t=70, b=40),
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    yaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    coloraxis_colorbar=dict(title="Bedrooms")
)

fig1.update_traces(
    marker=dict(
        line=dict(width=0.5, color="white")
    )
)

st.plotly_chart(fig1, width="stretch")

st.header('BHK Distribution')

sector_options = ['overall'] + sorted(new_df['sector'].dropna().unique().tolist())

selected_sector = st.selectbox('Select Sector', sector_options)

if selected_sector == 'overall':
    plot_df = new_df.copy()
else:
    plot_df = new_df[new_df['sector'] == selected_sector].copy()

# Count properties in each BHK category
bhk_counts = (
    plot_df['bedRoom']
    .value_counts()
    .sort_index()
    .reset_index()
)

bhk_counts.columns = ['BHK', 'Count']

# Donut chart
fig2 = px.pie(
    bhk_counts,
    names='BHK',
    values='Count',
    hole=0.5,
    color='BHK',
    color_discrete_sequence=px.colors.qualitative.Set2,
    title=f'BHK Distribution - {selected_sector.title()}',
)

fig2.update_traces(
    textposition='outside',
    textinfo='label+percent',
    hovertemplate='<b>%{label} BHK</b><br>Properties: %{value}<br>Share: %{percent}<extra></extra>'
)

fig2.update_layout(
    template='plotly_white',
    showlegend=True,
    legend_title='BHK Type',
    title_x=0.5,
    height=500
)

st.plotly_chart(fig2, width='stretch')

st.header('BHK-wise Property Price Distribution')

plot_df = new_df[
    (new_df['bedRoom'] >= 1) &
    (new_df['bedRoom'] <= 4)
].copy()

fig3 = px.violin(
    plot_df,
    x='bedRoom',
    y='price',
    color='bedRoom',
    box=True,
    points=False,
    color_discrete_sequence=px.colors.qualitative.Set2,
    title='BHK-wise Property Price Distribution'
)

fig3.update_layout(
    template='plotly_white',
    showlegend=False,
    title_x=0.5,
    height=550,
    xaxis_title='BHK Type',
    yaxis_title='Price (Crores)'
)

fig3.update_traces(
    meanline_visible=True,
    hovertemplate='<b>%{x} BHK</b><br>Price: %{y:.2f} Crores<extra></extra>'
)

st.plotly_chart(fig3, width='stretch')

st.header('Property Type-wise Price Analysis')

plot_df = new_df[
    new_df['property_type'].isin(['house', 'flat']) &
    new_df['price'].notna() &
    (new_df['price'] > 0)
].copy()

# Dark theme
plt.style.use('dark_background')

fig, ax = plt.subplots(figsize=(12, 5))

fig.patch.set_facecolor('#0E1117')
ax.set_facecolor('#0E1117')

# Histogram
sns.histplot(
    data=plot_df,
    x='price',
    hue='property_type',
    palette={'house': '#00E5A8', 'flat': '#FF6B8A'},
    bins=40,
    stat='density',
    common_norm=False,
    element='step',
    fill=True,
    alpha=0.18,
    linewidth=1.8,
    kde=True,
    ax=ax
)

# Styling
ax.set_title(
    'House vs Flat Price Distribution',
    fontsize=17,
    fontweight='bold',
    color='white',
    pad=20
)

ax.set_xlabel('Price (Crores)', fontsize=12, color='white', labelpad=10)
ax.set_ylabel('Density', fontsize=12, color='white', labelpad=10)

ax.grid(axis='y', linestyle='--', alpha=0.15)
ax.grid(axis='x', visible=False)

ax.tick_params(colors='#CCCCCC')

for spine in ax.spines.values():
    spine.set_visible(False)

plt.tight_layout()

st.pyplot(fig)
plt.close(fig)