# TP FINAL

import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Données + nettoyages des données
df = pd.read_csv("datasets/data.csv")
df["Transaction_Date"] = pd.to_datetime(df["Transaction_Date"])
df["Total_price"] = df["Quantity"] * df["Avg_Price"] * (1 - df["Discount_pct"]/100)
df = df.dropna(subset=["Location"])
df["Location"] = df["Location"].astype(str)
# Police d'écriture pour le tableau de bord
FONT_FAMILY = "Arial, sans-serif"

# Couleurs
BLEU_FONCE = "#283580"
BLEU = "#90D6EB"
ROUGE_PALE = "#FF8F8F"
VIOLET_PALE = "#CBB5E4" 
VIOLET_FONCE = "#6F27C2" 
TEXTE = "#2c3e50" 
VERT = "#288f24"
ROUGE ="#f11616"

# Création d'un style commun pour les blocs
BLOCK_STYLE = {
    "border": "2px solid #e0e0e0",
    "borderRadius": "8px",
    "padding": "15px",
    "backgroundColor": "white",
    "marginBottom": "0px", 
    "height": "100%" 
}

# Figures

# Evolution du CA par semaines
def tracer_evolution_ca(donnees):
    ca_hebdo = donnees.groupby(pd.Grouper(key="Transaction_Date", freq="W"))["Total_price"].sum().reset_index()
    fig = px.line(ca_hebdo, x="Transaction_Date", y="Total_price")
    fig.update_traces(line_color=BLEU_FONCE, line_width=3)
    fig.update_layout(
        template="plotly_white",
        height=230, 
        margin=dict(l=40, r=20, t=20, b=30),
        xaxis_title= "Temps", yaxis_title= "Chiffre d'affaires (€)"
    )
    return fig

# Top 10 des catégories de produits les plus vendus
def graph_top_ventes(donnees):
    top_cat = donnees.groupby("Product_Category")["Quantity"].sum().sort_values(ascending=False).head(10).index
    df_top = donnees[donnees["Product_Category"].isin(top_cat)]
    frequence = df_top.groupby(["Product_Category","Gender"])["Quantity"].sum().reset_index()
    ordre = frequence.groupby("Product_Category")["Quantity"].sum().sort_values(ascending=False).index
    
    fig = px.bar(frequence, y="Product_Category", x="Quantity", color="Gender",
                  orientation="h", barmode="group",
                  category_orders={"Product_Category": ordre},
                  color_discrete_map={"M": BLEU ,"F": ROUGE_PALE})
    
    fig.update_layout(
        template="plotly_white",
        height=400, 
        margin=dict(l=10, r=20, t=10, b=40),
        legend=dict(title="Genre", orientation="h", x=0.5, xanchor="center", y=-0.15),
        xaxis_title="Quantité totale vendue", yaxis_title= "Catégories de produits"
    )
    return fig

# KPI du CA de décembre
def kpi_ca(donnees):
    dec = donnees[donnees["Transaction_Date"].dt.month == 12]
    nov = donnees[donnees["Transaction_Date"].dt.month == 11]
    ca_dec = dec["Total_price"].sum()
    ca_nov = nov["Total_price"].sum()
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=ca_dec,
        number={'valueformat': '.3s', 'suffix': '€', 'font': {'size': 40, 'color': TEXTE}},
        delta={
            "reference": ca_nov, 
            "valueformat": ".2s", 
            "increasing": {"color": VERT}, 
            "decreasing": {"color": ROUGE} 
        },
        title={"text": "CA Décembre", "font": {"size": 16}}
    ))
    fig.update_layout(height=100, margin=dict(l=0,r=0,t=30,b=0))
    return fig

# KPI des ventes de décembre
def kpi_volume_ventes(donnees):
    dec = donnees[donnees["Transaction_Date"].dt.month == 12]
    nov = donnees[donnees["Transaction_Date"].dt.month == 11]
    nb_dec = len(dec)
    nb_nov = len(nov)
    fig = go.Figure(go.Indicator(
        mode="number+delta",
        value=nb_dec,
        number={'font': {'size': 40, 'color': TEXTE}},
        delta={
            "reference": nb_nov, 
            "increasing": {"color": VERT},  
            "decreasing": {"color": ROUGE} 
        },
        title={"text": "Ventes Décembre", "font": {"size": 16}}
    ))
    fig.update_layout(height=100, margin=dict(l=0,r=0,t=30,b=0))
    return fig

# App Dash

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([
    # Barre du haut
    dbc.Row([
        dbc.Col(html.H3("ECAP Store", style={"margin": "10px 0 0 20px", "fontWeight":"bold", "color": TEXTE}), md=6),
        dbc.Col(
            # Ajout du filtre
            dcc.Dropdown(
                id="location_filter",
                options=[{"label": loc, "value": loc} for loc in sorted(df["Location"].unique())],
                value=[], 
                multi=True,
                placeholder="Choisissez des zones",
                style={"marginTop":"10px", "width": "90%"}
            ), md=6, className="d-flex justify-content-end"
        ),
    ], style={"backgroundColor": VIOLET_PALE, "height": "60px", "margin": "0", "alignItems": "center"}),

    dbc.Container([
        html.Br(),
        dbc.Row([
            # COLONNE DE GAUCHE
            dbc.Col([
                dbc.Row([
                    dbc.Col(html.Div(dcc.Graph(id="kpi_ca", config={'displayModeBar': False}), style=BLOCK_STYLE), width=6),
                    dbc.Col(html.Div(dcc.Graph(id="kpi_sales", config={'displayModeBar': False}), style=BLOCK_STYLE), width=6),
                ], className="mb-3"),
                
                # Gauche bas : graphique du top 10 des catégories de produits les plus vendus
                html.Div([
                    html.H3("Top 10 des catégories de produits les plus vendus",
                            style={"fontFamily": FONT_FAMILY, "fontSize": "18px", "fontWeight": "bold", "color": TEXTE}),
                    dcc.Graph(id="top_sales", config={'displayModeBar': False})
                ], style=BLOCK_STYLE),
            ], md=5, className="d-flex flex-column"),

            # COLONNE DE DROITE
            dbc.Col([
                # Droite haut : évolution du CA par semaines
                html.Div([
                    html.H3("Évolution du chiffre d'affaires par semaines",
                        style={"fontFamily": FONT_FAMILY, "fontSize": "18px", "fontWeight": "bold", "color": TEXTE}),
                    dcc.Graph(id="ca_graph", config={'displayModeBar': False}),
                ], style={**BLOCK_STYLE, "height": "320px"}, className="mb-3"), 
                
                # Droite bas : table des 100 dernières ventes
                html.Div([
                    html.H3("Table des 100 dernières ventes",
                            style={"fontFamily": FONT_FAMILY, "fontSize": "18px", "fontWeight": "bold", "color": TEXTE}),
                    dash_table.DataTable(
                        id="sales_table",
                        page_size=10,
                        style_table={"height": "345px", "overflowY": "auto"},
                        style_cell={"textAlign": "center", "fontSize": 11, "fontFamily": FONT_FAMILY, "color": TEXTE},
                        style_header={"fontWeight": "bold", "backgroundColor": VIOLET_PALE, "color": VIOLET_FONCE, "border": "1px solid #dee2e6"},
                    )
                ], style=BLOCK_STYLE),
            ], md=7, className="d-flex flex-column"),
        ], className="g-4"), 
    ], fluid=True)
], style={"backgroundColor": "#fafafa", "minHeight": "100vh"})

# Callback
@app.callback(
    Output("kpi_ca","figure"),
    Output("kpi_sales","figure"),
    Output("top_sales","figure"),
    Output("ca_graph","figure"),
    Output("sales_table","data"),
    Output("sales_table","columns"),
    Input("location_filter","value")
)

# Mise à jour du tableau de bord
def maj_dashboard(zones):
    dff = df[df["Location"].isin(zones)] if zones else df.copy()
    table = dff.sort_values("Transaction_Date", ascending=False).head(100)
    table_affichage = table.copy()
    table_affichage["Transaction_Date"] = table_affichage["Transaction_Date"].dt.strftime('%d/%m/%Y') # pour mettre la date au format français
    
    # Traduction des titres des colonnes du tableau
    traductions = {
        "Transaction_Date": "Date",
        "Gender": "Genre",
        "Location": "Localisation",
        "Product_Category": "Catégorie de produit",
        "Quantity": "Quantité",
        "Avg_Price": "Prix moyen",
        "Discount_pct": "Remise (%)"
    }
    
    # Liste des noms de colonnes originaux pour extraire les données du DataFrame
    colonnes_techniques = list(traductions.keys())
    
    return (
        kpi_ca(dff),
        kpi_volume_ventes(dff),
        graph_top_ventes(dff),
        tracer_evolution_ca(dff),
        table_affichage[colonnes_techniques].to_dict("records"),
        [{"name": traductions[i], "id": i} for i in colonnes_techniques]
    )

# Lancement du tableau de bord
if __name__ == '__main__':
    app.run_server(debug=True)