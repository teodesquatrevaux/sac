import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components
from datetime import datetime
import base64
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import plotly.io as pio
from PIL import Image as PILImage
import re

# --- Configuration de la page Streamlit ---
st.set_page_config(layout="wide", page_title="Analyse des Ventes")

# --- Navigation entre les pages ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à:", ["📊 Dashboard", "🆚 Comparaison", "📚 Documentation"])

# --- Initialisation des sessions states ---
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'df_complet' not in st.session_state:
    st.session_state.df_complet = None

# --- Page Documentation ---
if page == "📚 Documentation":
    st.title("📚 Documentation - Mapping des Catégories")
    
    st.markdown("""
    ## Guide d'utilisation du Dashboard
    
    Cette documentation explique le système de catégorisation automatique des articles 
    et comment utiliser le dashboard d'analyse des ventes.
    """)
    
    # Mapping détaillé des catégories
    st.header("🗂️ Mapping des Catégories")
    
    st.subheader("🍹 Boissons Non-Alcoolisées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### ☕ Boissons Chaudes
        - **Café/Chocolat** : café, espresso, latte, déca, chocolat viennois, hot chocolat, tisane, verveine, cappucino, glass of milk
        - **Thé** : tea, thé, earl grey, green tea, mariage, mint tea, fruits rouges
        
        #### 🥤 Boissons Froides
        - **Soda/Jus** : coke, cola, sprite, schweppes, diabolo, orangina, powerade, syrop, ice tea, ginger beer, choose, pint choose
        - **Jus de Fruit** : jus, juice, orange, pomme, apple, tomato, apricot, cranberry, pamplemousse
        - **Eau** : cristaline, badoit, perrier, evian
        """)
    
    with col2:
        st.markdown("""
        #### 🍷 Boissons Alcoolisées
        - **Spiritueux** : whiskey, rhum, cognac, porto, pastis, gin, martini, whisky, ricard
        - **Vin** : wine, saumur, bourgueil, pinot noir, merlot, rosé, mâcon, viognier, sancerre, château, champigny, gris blanc, vezelay, chardonnay, marquis de mores, sauvignon
        - **Bière** : bière, beer, pint, lager, adnams, theakston, brooklyn, guinness, brewdog, 1664, pils, la folie douce
        - **Effervescent** : champagne, prosecco, vin petillant
        - **Cocktail** : cocktail
        """)
    
    st.subheader("🍽️ Nourriture")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("""
        #### 🍬 Sucré
        - **Pâtisserie/Sucré** : cookie, muffin, cake, brownie, pie, crumble, viennoiserie, biscuit, croissant, pain d'epice, frangipane, cupcake, lemon bars, lemon poppyseed loaf
        - **Glace/Confiserie** : mars, twix, kinder bueno, kit kat, lolly pops, magnum, cornetto, twister, haribo, lion king, rocket, marshmallow
        """)
    
    with col4:
        st.markdown("""
        #### 🧂 Salé
        - **Plat/Snack Salé** : quiche, gnocchi, lasagna, chili, nuggets, lil'fries, crisps, terrîne, hot dog, gaspacho
        - **Plat du Jour** : plat à, plat 11, plat 13
        - **Bocaux** : terrine, vrai & bon pot
        """)
    
    st.subheader("⚙️ Autres Catégories")
    
    st.markdown("""
    - **Service / Frais / Activité** : entree, fee, vigik, corkage, tennis, squash, social, member, adult, bridge, snooker, remboursement, mini viennoiserie, cuff links, polo, bbq, cutlery
    - **Matériel** : balle, balls
    - **Hors Catégorie** : not used
    - **Autre** : Tout article qui ne correspond à aucune des catégories ci-dessus
    """)
    
    # Guide d'utilisation
    st.header("🎯 Guide d'utilisation")
    
    st.markdown("""
    ### Comment utiliser le Dashboard
    
    1. **Chargement des données** : Utilisez le fichier CSV exporté depuis votre système de caisse
    2. **Filtrage** : 
       - Sélectionnez la période d'analyse
       - Choisissez les catégories et articles à inclure
       - Utilisez les boutons "Toutes/Aucune" pour une sélection rapide
    3. **Analyse** : 
       - Consultez les indicateurs clés (KPIs)
       - Explorez l'évolution temporelle des ventes
       - Découvrez les tops articles et catégories
       - Analysez la répartition par catégorie
    4. **Export** : Téléchargez un rapport PDF complet
    
    ### Format des données attendu
    Le fichier CSV doit contenir les colonnes suivantes :
    - `Date` (format JJ/MM/AAAA)
    - `Libellé` (nom de l'article)
    - `Quantité` 
    - `Total HT`
    - `TVA`
    - `Total TTC`
    - `Code établissement`
    
    **Encodage** : latin1  
    **Séparateur** : point-virgule (;)
    """)
    
    # Exemple de structure
    st.header("📋 Exemple de structure de données")
    
    example_data = {
        'Date': ['01/01/2024', '01/01/2024', '02/01/2024'],
        'Libellé': ['Café espresso', 'Cookie chocolat', 'Bière 1664'],
        'Quantité': [2, 1, 3],
        'Total HT': [4.00, 2.50, 12.00],
        'TVA': [0.80, 0.50, 2.40],
        'Total TTC': [4.80, 3.00, 14.40],
        'Code établissement': ['BAR01', 'BAR01', 'BAR01']
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    st.info("💡 **Astuce** : La catégorisation est automatique basée sur les mots-clés dans le libellé des articles.")
    
    # Footer de la documentation
    st.markdown("---")
    st.markdown("*Documentation mise à jour le {}*".format(datetime.now().strftime("%d/%m/%Y")))

    # Stop l'exécution pour ne pas afficher le dashboard
    st.stop()

# --- Fonction de nettoyage des articles ---
def nettoyer_article(libelle):
    """
    Nettoie le libellé de l'article en enlevant les dates et les (a):/(A):
    """
    if pd.isna(libelle):
        return libelle
    
    libelle_str = str(libelle)
    
    # Enlever les dates (format JJ/MM/AAAA ou JJ-MM-AAAA)
    libelle_sans_dates = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', '', libelle_str)
    
    # Enlever les (a): et (A):
    libelle_sans_a = re.sub(r'\([aA]\):', '', libelle_sans_dates)
    
    # Nettoyer les espaces multiples et les espaces en début/fin
    libelle_propre = re.sub(r'\s+', ' ', libelle_sans_a).strip()
    
    return libelle_propre

# --- Chargement et Préparation des Données (mis en cache pour la performance) ---
@st.cache_data
def load_data(uploaded_file):
    """
    Charge, nettoie et catégorise les données de ventes à partir d'un fichier chargé.
    """
    
    # Charger le fichier depuis l'objet uploadé
    try:
        df = pd.read_csv(uploaded_file, sep=";", encoding='latin1')
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
        st.error("Veuillez vérifier que le fichier est un CSV valide, avec le séparateur ';' et l'encodage 'latin1'.")
        st.stop()
        
    # Supprimer les colonnes inutiles
    df.drop(columns=['AQTE1', 'ATTC1', 'AHT1', 'AQTE2', 'ATTC2', 'AHT2'], inplace=True, errors='ignore')

    # Nettoyage des données
    try:
        df['Total HT'] = df['Total HT'].str.replace(',', '.', regex=False)
        df['TVA'] = df['TVA'].str.replace(',', '.', regex=False)
        df['Total TTC'] = df['Total TTC'].str.replace(',', '.', regex=False)
        
        df['Total HT'] = pd.to_numeric(df['Total HT'])
        df['TVA'] = pd.to_numeric(df['TVA'])
        df['Total TTC'] = pd.to_numeric(df['Total TTC'])
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        
        df = df.rename(columns={
            'Total HT': 'Total_HT',
            'Total TTC': 'Total_TTC',
            'Code établissement': 'Code_établissement'
        })
        
        df['Quantité'] = pd.to_numeric(df['Quantité'], errors='coerce').fillna(0)

    except KeyError as e:
        st.error(f"Erreur : Colonne manquante dans le fichier chargé : {e}.")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du nettoyage des données : {e}")
        st.stop()
    
    # Appliquer le nettoyage des articles
    df['Libellé_Original'] = df['Libellé'].copy()  # Garder une copie originale
    df['Libellé_Nettoyé'] = df['Libellé'].apply(nettoyer_article)

    # Fonction de Catégorisation
    def categoriser_article(libelle):
        libelle = str(libelle).lower()
        
        # Catégories existantes...
        if any(keyword in libelle for keyword in ['café', 'coffee', 'espresso', 'latte', 'dèca', 'chocolat viennois', 'hot chocolat', 'tisane', 'verveine', 'déca', 'cappucino', 'glass of milk']):
            return 'Boisson Chaude - Café/Chocolat'
        if any(keyword in libelle for keyword in ['tea', 'thé', 'earl grey', 'green tea', 'mariage', 'mint tea', 'fruits rouges']):
            return 'Boisson Chaude - Thé'
        if any(keyword in libelle for keyword in ['coke', 'cola', 'sprite', 'schweppes', 'diabolo', 'orangina', 'powerade', 'syrop', 'ice tea', 'ginger beer', 'choose', 'pint choose']):
            return 'Boisson Froide - Soda/Jus'
        if any(keyword in libelle for keyword in ['jus', 'juice', 'orange', 'pomme', 'apple', 'tomato', 'apricot', 'cranberry', 'pamplemousse']):
            return 'Boisson Froide - Jus de Fruit'
        if any(keyword in libelle for keyword in ['cristaline', 'badoit', 'perrier', 'evian']):
            return 'Boisson Froide - Eau'

        if any(keyword in libelle for keyword in ['whiskey', 'rhum', 'cognac', 'porto', 'pastis', 'gin', 'martini', 'whisky', 'ricard']):
            return 'Alcool - Spiritueux'
        if any(keyword in libelle for keyword in ['wine', 'saumur', 'bourgueil', 'pinot noir', 'merlot', 'rosé', 'mâcon', 'viognier', 'sancerre', 'château', 'champigny', 'gris blanc', 'vezelay', 'chardonnay', 'marquis de mores', 'sauvignon']):
            return 'Alcool - Vin'
        if any(keyword in libelle for keyword in ['bière', 'beer', 'pint', 'lager', 'adnams', 'theakston', 'brooklyn', 'guinness', 'brewdog', '1664', 'pils', 'la folie douce']):
            return 'Alcool - Bière'
        if any(keyword in libelle for keyword in ['champagne', 'prosecco', 'vin petillant']):
            return 'Alcool - Effervescent'
        if any(keyword in libelle for keyword in ['cocktail']):
            return 'Alcool - Cocktail'
            
        if any(keyword in libelle for keyword in ['cookie', 'muffin', 'cake', 'brownie', 'pie', 'crumble', 'viennoiserie', 'biscuit', 'croissant', 'pain d epice', 'frangipane', 'cupcake', 'lemon bars', 'lemon poppyseed loaf']):
            return 'Pâtisserie/Sucré'
        if any(keyword in libelle for keyword in ['mars', 'twix', 'kinder bueno', 'kit kat', 'lolly pops', 'magnum', 'cornetto', 'twister', 'haribo', 'lion king', 'rocket', 'marshmallow']):
            return 'Glace/Confiserie'
            
        if any(keyword in libelle for keyword in ['quiche', 'gnocchi', 'lasagna', 'chili', 'nuggets', 'lil\'fries', 'crisps', 'terrîne', 'hot dog', 'gaspacho']):
            return 'Plat/Snack Salé'
        
        if any(keyword in libelle for keyword in ['plat à', 'plat 11', 'plat 13']):
            return 'Plat du Jour'
        if any(keyword in libelle for keyword in ['terrine', 'vrai & bon pot']):
            return 'Bocaux'

        if any(keyword in libelle for keyword in ['entree', 'fee', 'vigik', 'corkage', 'tennis', 'squash', 'social', 'member', 'adult', 'bridge', 'snooker', 'remboursement', 'mini viennoiserie', 'cuff links', 'polo', 'bbq', 'cutlery']):
            return 'Service / Frais / Activité'
        if any(keyword in libelle for keyword in ['balle', 'balls']):
            return 'Matériel'
        if any(keyword in libelle for keyword in ['not used']):
            return 'Hors Catégorie' 

        return 'Autre'

    # Appliquer la catégorisation sur les libellés nettoyés
    try:
        df['Catégorie'] = df['Libellé_Nettoyé'].apply(categoriser_article)
    except KeyError:
        st.error("Erreur : La colonne 'Libellé' est manquante dans le fichier chargé.")
        st.stop()
    
    # --- REGROUPEMENT DES ARTICLES IDENTIQUES APRES NETTOYAGE ---
    # Agrégation des données par libellé nettoyé et catégorie
    df_aggregated = df.groupby(['Libellé_Nettoyé', 'Catégorie', 'Date', 'Code_établissement']).agg({
        'Quantité': 'sum',
        'Total_HT': 'sum',
        'TVA': 'sum',
        'Total_TTC': 'sum',
        'Libellé_Original': 'first'  # Garder le premier libellé original pour référence
    }).reset_index()
    
    # Renommer la colonne Libellé_Nettoyé en Libellé pour l'utilisation dans le dashboard
    df_aggregated = df_aggregated.rename(columns={'Libellé_Nettoyé': 'Libellé'})
    
    return df_aggregated

# --- Fonctions pour la page de comparaison ---
def create_comparison_kpis(df1, df2, nom_periode1, nom_periode2):
    """Crée un tableau comparatif des KPIs entre deux périodes"""
    
    def calculate_kpis(df):
        if df.empty:
            return {
                'CA_TTC': 0, 'CA_HT': 0, 'Quantite': 0, 
                'Prix_Moyen': 0, 'Nb_Articles': 0, 'Nb_Categories': 0
            }
        
        total_ttc = df['Total_TTC'].sum()
        total_ht = df['Total_HT'].sum()
        total_quantite = df['Quantité'].sum()
        prix_moyen = total_ttc / total_quantite if total_quantite > 0 else 0
        nb_articles = df['Libellé'].nunique()
        nb_categories = df['Catégorie'].nunique()
        
        return {
            'CA_TTC': total_ttc,
            'CA_HT': total_ht,
            'Quantite': total_quantite,
            'Prix_Moyen': prix_moyen,
            'Nb_Articles': nb_articles,
            'Nb_Categories': nb_categories
        }
    
    kpis1 = calculate_kpis(df1)
    kpis2 = calculate_kpis(df2)
    
    # Calcul des écarts
    ecarts = {}
    for key in kpis1.keys():
        if kpis1[key] != 0:
            ecart_pourcentage = ((kpis2[key] - kpis1[key]) / kpis1[key]) * 100
        else:
            ecart_pourcentage = 0
        ecarts[key] = ecart_pourcentage
    
    # Création du tableau comparatif
    comparison_data = {
        'Indicateur': [
            "Chiffre d'Affaires TTC (€)",
            "Chiffre d'Affaires HT (€)", 
            "Volume d'Articles Vendus",
            "Prix Moyen par Article (€)",
            "Nombre d'Articles Différents",
            "Nombre de Catégories"
        ],
        nom_periode1: [
            f"{kpis1['CA_TTC']:,.2f}",
            f"{kpis1['CA_HT']:,.2f}",
            f"{kpis1['Quantite']:,.0f}",
            f"{kpis1['Prix_Moyen']:,.2f}",
            f"{kpis1['Nb_Articles']:,.0f}",
            f"{kpis1['Nb_Categories']:,.0f}"
        ],
        nom_periode2: [
            f"{kpis2['CA_TTC']:,.2f}",
            f"{kpis2['CA_HT']:,.2f}",
            f"{kpis2['Quantite']:,.0f}",
            f"{kpis2['Prix_Moyen']:,.2f}",
            f"{kpis2['Nb_Articles']:,.0f}",
            f"{kpis2['Nb_Categories']:,.0f}"
        ],
        'Évolution (%)': [
            f"{ecarts['CA_TTC']:+.1f}%",
            f"{ecarts['CA_HT']:+.1f}%", 
            f"{ecarts['Quantite']:+.1f}%",
            f"{ecarts['Prix_Moyen']:+.1f}%",
            f"{ecarts['Nb_Articles']:+.1f}%",
            f"{ecarts['Nb_Categories']:+.1f}%"
        ]
    }
    
    return pd.DataFrame(comparison_data)

def create_comparison_chart(df1, df2, nom_periode1, nom_periode2, chart_type='top_categories'):
    """Crée un graphique comparatif"""
    
    if chart_type == 'top_categories':
        # Top 10 catégories comparées
        cat1 = df1.groupby('Catégorie')['Total_TTC'].sum().nlargest(10)
        cat2 = df2.groupby('Catégorie')['Total_TTC'].sum().nlargest(10)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name=nom_periode1,
            x=cat1.values,
            y=cat1.index,
            orientation='h',
            marker_color='blue'
        ))
        
        fig.add_trace(go.Bar(
            name=nom_periode2,
            x=cat2.values,
            y=cat2.index,
            orientation='h',
            marker_color='red'
        ))
        
        fig.update_layout(
            title="Top 10 Catégories - Comparaison",
            barmode='group',
            height=400
        )
        
    elif chart_type == 'repartition':
        # Répartition par catégorie
        repart1 = df1.groupby('Catégorie')['Total_TTC'].sum()
        repart2 = df2.groupby('Catégorie')['Total_TTC'].sum()
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[nom_periode1, nom_periode2],
            specs=[[{'type':'pie'}, {'type':'pie'}]]
        )
        
        fig.add_trace(go.Pie(
            labels=repart1.index,
            values=repart1.values,
            name=nom_periode1
        ), 1, 1)
        
        fig.add_trace(go.Pie(
            labels=repart2.index,
            values=repart2.values,
            name=nom_periode2
        ), 1, 2)
        
        fig.update_layout(height=400)
        
    return fig

def filter_data(df_complet, date_debut, date_fin, selected_categories, selected_articles):
    """Filtre les données selon les critères"""
    return df_complet[
        (df_complet['Date'] >= pd.to_datetime(date_debut)) &
        (df_complet['Date'] <= pd.to_datetime(date_fin)) &
        (df_complet['Catégorie'].isin(selected_categories)) &
        (df_complet['Libellé'].isin(selected_articles))
    ]

def get_valid_default_articles(default_articles, available_articles):
    """Retourne uniquement les articles par défaut qui existent dans la liste disponible"""
    return [article for article in default_articles if article in available_articles]

# --- Fonction pour créer un PDF de comparaison ---
def create_comparison_pdf(df_periode1, df_periode2, nom_periode1, nom_periode2, 
                         date_debut1, date_fin1, date_debut2, date_fin2,
                         selected_categories1, selected_articles1,
                         selected_categories2, selected_articles2,
                         comparison_df, fig_comp_cat, fig_comp_rep):
    """Crée un rapport PDF complet pour l'analyse comparative"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                          topMargin=0.5*inch, bottomMargin=0.5*inch,
                          leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2E86AB'),
        spaceAfter=20,
        alignment=1  # Centré
    )
    
    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2E86AB'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Style pour le texte normal
    normal_style = styles['Normal']
    
    # En-tête du rapport
    title = Paragraph("🆚 RAPPORT COMPARATIF DES VENTES", title_style)
    story.append(title)
    
    # Périodes comparées
    period_text = f"Comparaison : {nom_periode1} vs {nom_periode2}"
    period = Paragraph(period_text, normal_style)
    story.append(period)
    
    date_generation = f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    generation = Paragraph(date_generation, normal_style)
    story.append(generation)
    
    story.append(Spacer(1, 20))
    
    # --- Section 1: Périodes comparées ---
    story.append(Paragraph("📅 PÉRIODES COMPARÉES", subtitle_style))
    
    period_data = [
        ['Paramètre', nom_periode1, nom_periode2],
        ['Date de début', date_debut1.strftime('%d/%m/%Y'), date_debut2.strftime('%d/%m/%Y')],
        ['Date de fin', date_fin1.strftime('%d/%m/%Y'), date_fin2.strftime('%d/%m/%Y')],
        ['Catégories sélectionnées', str(len(selected_categories1)), str(len(selected_categories2))],
        ['Articles sélectionnés', str(len(selected_articles1)), str(len(selected_articles2))]
    ]
    
    period_table = Table(period_data, colWidths=[200, 150, 150])
    period_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(period_table)
    story.append(Spacer(1, 20))
    
    # --- Section 2: Comparaison des Indicateurs Clés ---
    story.append(Paragraph("📈 COMPARAISON DES INDICATEURS CLÉS", subtitle_style))
    
    # Convertir le DataFrame de comparaison en tableau PDF
    if not comparison_df.empty:
        kpi_data = [comparison_df.columns.tolist()] + comparison_df.values.tolist()
        kpi_table = Table(kpi_data, colWidths=[200, 120, 120, 100])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('TEXTCOLOR', (-1, 1), (-1, -1), colors.red)  # Couleur pour les évolutions
        ]))
        story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # --- Section 3: Graphiques comparatifs ---
    story.append(Paragraph("🆚 GRAPHIQUES COMPARATIFS", subtitle_style))
    
    # Graphique des top catégories
    if fig_comp_cat:
        try:
            story.append(Paragraph("Top 10 Catégories Comparées", subtitle_style))
            img_buffer = plotly_fig_to_image(fig_comp_cat, width=700, height=350)
            img = Image(img_buffer, width=6.5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique Top Catégories: {e}", normal_style)
            story.append(error_msg)
    
    story.append(Spacer(1, 15))
    
    # Graphique de répartition
    if fig_comp_rep:
        try:
            story.append(Paragraph("Répartition par Catégorie", subtitle_style))
            img_buffer = plotly_fig_to_image(fig_comp_rep, width=700, height=350)
            img = Image(img_buffer, width=6.5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique de répartition: {e}", normal_style)
            story.append(error_msg)
    
    story.append(Spacer(1, 15))
    
    # --- Section 4: Top Articles ---
    story.append(Paragraph("🏆 TOP 10 ARTICLES PAR PÉRIODE", subtitle_style))
    
    # Top articles période 1
    top_art1 = df_periode1.groupby('Libellé')['Total_TTC'].sum().nlargest(10)
    top_art2 = df_periode2.groupby('Libellé')['Total_TTC'].sum().nlargest(10)
    
    # Préparer les données pour le tableau
    max_rows = max(len(top_art1), len(top_art2))
    articles_data = [['Classement', nom_periode1, 'CA (€)', nom_periode2, 'CA (€)']]
    
    for i in range(max_rows):
        row = [str(i+1)]
        
        # Période 1
        if i < len(top_art1):
            article1 = list(top_art1.items())[i]
            row.extend([article1[0], f"{article1[1]:,.2f}"])
        else:
            row.extend(['', ''])
        
        # Période 2
        if i < len(top_art2):
            article2 = list(top_art2.items())[i]
            row.extend([article2[0], f"{article2[1]:,.2f}"])
        else:
            row.extend(['', ''])
        
        articles_data.append(row)
    
    articles_table = Table(articles_data, colWidths=[60, 180, 80, 180, 80])
    articles_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(articles_table)
    
    # Pied de page
    story.append(Spacer(1, 20))
    footer = Paragraph("Rapport comparatif généré automatiquement par le Dashboard d'Analyse des Ventes - © 2024", normal_style)
    story.append(footer)
    
    # Génération du PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Fonction pour convertir un graphique Plotly en image ---
def plotly_fig_to_image(fig, width=800, height=400):
    """Convertit un graphique Plotly en image PNG"""
    img_bytes = pio.to_image(fig, format='png', width=width, height=height)
    return BytesIO(img_bytes)

# --- Page Comparaison ---
if page == "🆚 Comparaison":
    st.title("🆚 Comparaison des Périodes")
    
    # Afficher le fichier actuellement chargé
    if st.session_state.uploaded_file is not None:
        st.success(f"📁 Fichier chargé : {st.session_state.uploaded_file.name}")
        
        # Bouton pour supprimer le fichier chargé
        if st.button("🗑️ Supprimer le fichier chargé"):
            st.session_state.uploaded_file = None
            st.session_state.df_complet = None
            st.rerun()
    
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre journal des ventes (CSV) ici",
        type=["csv"],
        help="Le fichier doit être un CSV avec un séparateur ';' et un encodage 'latin1'.",
        key="comparison_upload"
    )
    
    # Gérer le chargement du fichier
    if uploaded_file is not None:
        # Si un nouveau fichier est chargé, mettre à jour le session_state
        if uploaded_file != st.session_state.uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.df_complet = load_data(uploaded_file)
            st.rerun()
    
    # Utiliser les données du session_state si disponibles
    if st.session_state.df_complet is not None:
        df_complet = st.session_state.df_complet
        
        st.markdown("---")
        
        # Configuration des deux colonnes de comparaison
        col1, col2 = st.columns(2)
        
        # Initialisation des sessions states pour les filtres de comparaison
        if 'periode1_filters' not in st.session_state:
            st.session_state.periode1_filters = {
                'date_debut': df_complet['Date'].min().date(),
                'date_fin': df_complet['Date'].max().date(),
                'categories': list(df_complet['Catégorie'].unique()),
                'articles': list(df_complet['Libellé'].unique())
            }
        
        if 'periode2_filters' not in st.session_state:
            st.session_state.periode2_filters = {
                'date_debut': df_complet['Date'].min().date(),
                'date_fin': df_complet['Date'].max().date(),
                'categories': list(df_complet['Catégorie'].unique()),
                'articles': list(df_complet['Libellé'].unique())
            }
        
        # Variables pour stocker les graphiques comparatifs
        fig_comp_cat = None
        fig_comp_rep = None
        comparison_df = pd.DataFrame()
        
        # Colonne 1 - Période 1
        with col1:
            st.header("🟦 Période 1")
            
            # Dates Période 1
            min_date = df_complet['Date'].min().date()
            max_date = df_complet['Date'].max().date()
            
            st.subheader("📅 Période temporelle")
            date_debut1 = st.date_input(
                "Date de début Période 1",
                value=st.session_state.periode1_filters['date_debut'],
                min_value=min_date,
                max_value=max_date,
                key="date_debut1"
            )
            date_fin1 = st.date_input(
                "Date de fin Période 1", 
                value=st.session_state.periode1_filters['date_fin'],
                min_value=date_debut1,
                max_value=max_date,
                key="date_fin1"
            )
            
            # Filtres Période 1
            st.subheader("🎯 Filtres")
            
            # Catégories Période 1
            all_categories = sorted(df_complet['Catégorie'].unique())
            cat_col1, cat_col2 = st.columns(2)
            with cat_col1:
                if st.button("✅ Toutes P1", key="all_cat_p1"):
                    st.session_state.periode1_filters['categories'] = all_categories
                    st.rerun()
            with cat_col2:
                if st.button("❌ Aucune P1", key="no_cat_p1"):
                    st.session_state.periode1_filters['categories'] = []
                    st.rerun()
            
            selected_categories1 = st.multiselect(
                "Catégories Période 1",
                all_categories,
                default=st.session_state.periode1_filters['categories'],
                key="cat_p1"
            )
            
            # Articles Période 1
            if selected_categories1:
                articles_filtres1 = sorted(df_complet[df_complet['Catégorie'].isin(selected_categories1)]['Libellé'].unique())
            else:
                articles_filtres1 = sorted(df_complet['Libellé'].unique())
            
            # Obtenir les articles valides pour la sélection par défaut
            default_articles1 = st.session_state.periode1_filters.get('articles', [])
            valid_default_articles1 = get_valid_default_articles(default_articles1, articles_filtres1)
            
            art_col1, art_col2 = st.columns(2)
            with art_col1:
                if st.button("✅ Tous P1", key="all_art_p1"):
                    st.session_state.periode1_filters['articles'] = articles_filtres1
                    st.rerun()
            with art_col2:
                if st.button("❌ Aucun P1", key="no_art_p1"):
                    st.session_state.periode1_filters['articles'] = []
                    st.rerun()
            
            selected_articles1 = st.multiselect(
                "Articles Période 1",
                articles_filtres1,
                default=valid_default_articles1,
                key="art_p1"
            )
            
            # Mise à jour des filtres dans session_state
            st.session_state.periode1_filters.update({
                'date_debut': date_debut1,
                'date_fin': date_fin1,
                'categories': selected_categories1,
                'articles': selected_articles1
            })
            
            # Application des filtres Période 1
            df_periode1 = filter_data(df_complet, date_debut1, date_fin1, selected_categories1, selected_articles1)
            
            if not df_periode1.empty:
                # KPIs Période 1
                st.subheader("📈 Indicateurs Période 1")
                total_ttc1 = df_periode1['Total_TTC'].sum()
                total_ht1 = df_periode1['Total_HT'].sum()
                total_quantite1 = df_periode1['Quantité'].sum()
                prix_moyen1 = total_ttc1 / total_quantite1 if total_quantite1 > 0 else 0
                
                st.metric("CA TTC", f"{total_ttc1:,.2f} €")
                st.metric("CA HT", f"{total_ht1:,.2f} €")
                st.metric("Volume Vendu", f"{total_quantite1:,.0f}")
                st.metric("Prix Moyen", f"{prix_moyen1:,.2f} €")
                st.metric("Nb Articles", f"{df_periode1['Libellé'].nunique():,.0f}")
                st.metric("Nb Catégories", f"{df_periode1['Catégorie'].nunique():,.0f}")
                
            else:
                st.warning("Aucune donnée pour la période 1 avec les filtres sélectionnés")
        
        # Colonne 2 - Période 2
        with col2:
            st.header("🟥 Période 2")
            
            # Dates Période 2
            st.subheader("📅 Période temporelle")
            date_debut2 = st.date_input(
                "Date de début Période 2",
                value=st.session_state.periode2_filters['date_debut'],
                min_value=min_date,
                max_value=max_date,
                key="date_debut2"
            )
            date_fin2 = st.date_input(
                "Date de fin Période 2",
                value=st.session_state.periode2_filters['date_fin'],
                min_value=date_debut2,
                max_value=max_date,
                key="date_fin2"
            )
            
            # Filtres Période 2
            st.subheader("🎯 Filtres")
            
            # Catégories Période 2
            cat_col1, cat_col2 = st.columns(2)
            with cat_col1:
                if st.button("✅ Toutes P2", key="all_cat_p2"):
                    st.session_state.periode2_filters['categories'] = all_categories
                    st.rerun()
            with cat_col2:
                if st.button("❌ Aucune P2", key="no_cat_p2"):
                    st.session_state.periode2_filters['categories'] = []
                    st.rerun()
            
            selected_categories2 = st.multiselect(
                "Catégories Période 2",
                all_categories,
                default=st.session_state.periode2_filters['categories'],
                key="cat_p2"
            )
            
            # Articles Période 2
            if selected_categories2:
                articles_filtres2 = sorted(df_complet[df_complet['Catégorie'].isin(selected_categories2)]['Libellé'].unique())
            else:
                articles_filtres2 = sorted(df_complet['Libellé'].unique())
            
            # Obtenir les articles valides pour la sélection par défaut
            default_articles2 = st.session_state.periode2_filters.get('articles', [])
            valid_default_articles2 = get_valid_default_articles(default_articles2, articles_filtres2)
            
            art_col1, art_col2 = st.columns(2)
            with art_col1:
                if st.button("✅ Tous P2", key="all_art_p2"):
                    st.session_state.periode2_filters['articles'] = articles_filtres2
                    st.rerun()
            with art_col2:
                if st.button("❌ Aucun P2", key="no_art_p2"):
                    st.session_state.periode2_filters['articles'] = []
                    st.rerun()
            
            selected_articles2 = st.multiselect(
                "Articles Période 2",
                articles_filtres2,
                default=valid_default_articles2,
                key="art_p2"
            )
            
            # Mise à jour des filtres dans session_state
            st.session_state.periode2_filters.update({
                'date_debut': date_debut2,
                'date_fin': date_fin2,
                'categories': selected_categories2,
                'articles': selected_articles2
            })
            
            # Application des filtres Période 2
            df_periode2 = filter_data(df_complet, date_debut2, date_fin2, selected_categories2, selected_articles2)
            
            if not df_periode2.empty:
                # KPIs Période 2
                st.subheader("📈 Indicateurs Période 2")
                total_ttc2 = df_periode2['Total_TTC'].sum()
                total_ht2 = df_periode2['Total_HT'].sum()
                total_quantite2 = df_periode2['Quantité'].sum()
                prix_moyen2 = total_ttc2 / total_quantite2 if total_quantite2 > 0 else 0
                
                st.metric("CA TTC", f"{total_ttc2:,.2f} €")
                st.metric("CA HT", f"{total_ht2:,.2f} €")
                st.metric("Volume Vendu", f"{total_quantite2:,.0f}")
                st.metric("Prix Moyen", f"{prix_moyen2:,.2f} €")
                st.metric("Nb Articles", f"{df_periode2['Libellé'].nunique():,.0f}")
                st.metric("Nb Catégories", f"{df_periode2['Catégorie'].nunique():,.0f}")
                
            else:
                st.warning("Aucune donnée pour la période 2 avec les filtres sélectionnés")
        
        # Section de comparaison (en dessous des deux colonnes)
        st.markdown("---")
        st.header("📊 Analyse Comparative")
        
        if not df_periode1.empty and not df_periode2.empty:
            # Noms des périodes
            nom_periode1 = st.text_input("Nom de la Période 1", value="Période 1", key="nom_p1")
            nom_periode2 = st.text_input("Nom de la Période 2", value="Période 2", key="nom_p2")
            
            # Tableau comparatif des KPIs
            st.subheader("📋 Comparaison des Indicateurs Clés")
            comparison_df = create_comparison_kpis(df_periode1, df_periode2, nom_periode1, nom_periode2)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Graphiques comparatifs
            col_comp1, col_comp2 = st.columns(2)
            
            with col_comp1:
                st.subheader("🏆 Top Catégories Comparées")
                fig_comp_cat = create_comparison_chart(
                    df_periode1, df_periode2, nom_periode1, nom_periode2, 'top_categories'
                )
                st.plotly_chart(fig_comp_cat, use_container_width=True)
            
            with col_comp2:
                st.subheader("💰 Répartition par Catégorie")
                fig_comp_rep = create_comparison_chart(
                    df_periode1, df_periode2, nom_periode1, nom_periode2, 'repartition'
                )
                st.plotly_chart(fig_comp_rep, use_container_width=True)
            
            # Top articles comparés
            st.subheader("📦 Top 10 Articles Comparés")
            top_art1 = df_periode1.groupby('Libellé')['Total_TTC'].sum().nlargest(10)
            top_art2 = df_periode2.groupby('Libellé')['Total_TTC'].sum().nlargest(10)
            
            col_art1, col_art2 = st.columns(2)
            with col_art1:
                st.write(f"**{nom_periode1}**")
                for i, (article, ca) in enumerate(top_art1.items(), 1):
                    st.write(f"{i}. {article}: {ca:,.2f} €")
            
            with col_art2:
                st.write(f"**{nom_periode2}**")
                for i, (article, ca) in enumerate(top_art2.items(), 1):
                    st.write(f"{i}. {article}: {ca:,.2f} €")
            
            # --- Section Téléchargement PDF pour la comparaison ---
            st.markdown("---")
            st.header("📥 Téléchargement du Rapport Comparatif")
            
            # Bouton pour générer et télécharger le PDF comparatif
            if st.button("📊 Générer le Rapport Comparatif PDF", use_container_width=True):
                with st.spinner("Génération du rapport PDF en cours..."):
                    try:
                        pdf_buffer = create_comparison_pdf(
                            df_periode1, df_periode2, nom_periode1, nom_periode2,
                            date_debut1, date_fin1, date_debut2, date_fin2,
                            selected_categories1, selected_articles1,
                            selected_categories2, selected_articles2,
                            comparison_df, fig_comp_cat, fig_comp_rep
                        )
                        
                        st.download_button(
                            label="📥 Télécharger le Rapport Comparatif (PDF)",
                            data=pdf_buffer,
                            file_name=f"rapport_comparatif_{nom_periode1}_vs_{nom_periode2}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                            mime="application/pdf",
                            help="Téléchargez un rapport PDF complet de l'analyse comparative",
                            use_container_width=True
                        )
                        
                        st.success("Rapport PDF généré avec succès ! Cliquez sur le bouton de téléchargement.")
                        
                    except Exception as e:
                        st.error(f"Erreur lors de la génération du PDF : {e}")
        
        elif df_periode1.empty or df_periode2.empty:
            st.warning("Veuillez sélectionner des filtres valides pour les deux périodes pour voir la comparaison")
    
    else:
        if st.session_state.uploaded_file is None:
            st.info("Veuillez charger un fichier CSV pour démarrer l'analyse comparative.")

# --- Le reste du code pour le dashboard principal reste inchangé ---
# [Les fonctions pour le dashboard principal et la génération PDF restent identiques...]

# --- Fonction pour créer un PDF avec les graphiques (pour le dashboard principal) ---
def create_pdf_with_charts(df, date_debut, date_fin, frequence_choix, critere_articles, critere_categories, critere_pie, 
                          fig_evol, fig_top_art, fig_top_cat, fig_pie):
    """Crée un rapport PDF complet avec les graphiques"""
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                          topMargin=0.5*inch, bottomMargin=0.5*inch,
                          leftMargin=0.5*inch, rightMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2E86AB'),
        spaceAfter=20,
        alignment=1  # Centré
    )
    
    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2E86AB'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Style pour le texte normal
    normal_style = styles['Normal']
    
    # En-tête du rapport
    title = Paragraph("📊 RAPPORT D'ANALYSE DES VENTES", title_style)
    story.append(title)
    
    # Période d'analyse
    period_text = f"Période analysée : {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"
    period = Paragraph(period_text, normal_style)
    story.append(period)
    
    date_generation = f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}"
    generation = Paragraph(date_generation, normal_style)
    story.append(generation)
    
    story.append(Spacer(1, 20))
    
    # --- Section 1: Indicateurs Clés ---
    story.append(Paragraph("📈 INDICATEURS CLÉS DE PERFORMANCE", subtitle_style))
    
    # Calcul des KPIs
    total_ttc = df['Total_TTC'].sum()
    total_ht = df['Total_HT'].sum()
    total_quantite = df['Quantité'].sum()
    prix_moyen = total_ttc / total_quantite if total_quantite > 0 else 0
    
    # Tableau des KPIs
    kpi_data = [
        ['Indicateur', 'Valeur'],
        ["Chiffre d'Affaires TTC", f"{total_ttc:,.2f} €"],
        ["Chiffre d'Affaires HT", f"{total_ht:,.2f} €"],
        ["Volume d'Articles Vendus", f"{total_quantite:,.0f}"],
        ["Prix Moyen par Article", f"{prix_moyen:,.2f} €"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[200, 150])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # --- Section 2: Évolution Temporelle ---
    story.append(Paragraph("📈 ÉVOLUTION DU CHIFFRE D'AFFAIRES", subtitle_style))
    
    # Ajouter le graphique d'évolution
    if fig_evol:
        try:
            # Convertir le graphique Plotly en image
            img_buffer = plotly_fig_to_image(fig_evol, width=700, height=350)
            img = Image(img_buffer, width=6.5*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique d'évolution: {e}", normal_style)
            story.append(error_msg)
    
    story.append(Spacer(1, 15))
    
    # --- Section 3: Top 10 ---
    story.append(Paragraph("🏆 ANALYSE DES PERFORMERS", subtitle_style))
    
    # Top 10 Articles
    story.append(Paragraph(f"Top 10 Articles - {critere_articles}", subtitle_style))
    if fig_top_art:
        try:
            img_buffer = plotly_fig_to_image(fig_top_art, width=600, height=400)
            img = Image(img_buffer, width=6*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique Top Articles: {e}", normal_style)
            story.append(error_msg)
    
    story.append(Spacer(1, 10))
    
    # Top 10 Catégories
    story.append(Paragraph(f"Top 10 Catégories - {critere_categories}", subtitle_style))
    if fig_top_cat:
        try:
            img_buffer = plotly_fig_to_image(fig_top_cat, width=600, height=400)
            img = Image(img_buffer, width=6*inch, height=3.5*inch)
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique Top Catégories: {e}", normal_style)
            story.append(error_msg)
    
    story.append(Spacer(1, 15))
    
    # --- Section 4: Répartition par Catégorie ---
    story.append(Paragraph("💰 RÉPARTITION PAR CATÉGORIE", subtitle_style))
    story.append(Paragraph(f"Répartition par {critere_pie}", subtitle_style))
    
    if fig_pie:
        try:
            img_buffer = plotly_fig_to_image(fig_pie, width=500, height=400)
            img = Image(img_buffer, width=5*inch, height=3.5*inch)
            story.append(img)
        except Exception as e:
            error_msg = Paragraph(f"Erreur lors de la génération du graphique de répartition: {e}", normal_style)
            story.append(error_msg)
    
    # --- Section 5: Paramètres utilisés ---
    story.append(Spacer(1, 20))
    story.append(Paragraph("⚙️ PARAMÈTRES DE L'ANALYSE", subtitle_style))
    
    param_data = [
        ['Paramètre', 'Valeur'],
        ['Période', f"{date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}"],
        ['Fréquence d\'agrégation', frequence_choix],
        ['Critère Top Articles', critere_articles],
        ['Critère Top Catégories', critere_categories],
        ['Critère Répartition', critere_pie],
        ['Nombre de catégories sélectionnées', str(len(df['Catégorie'].unique()))],
        ['Nombre d\'articles sélectionnés', str(len(df['Libellé'].unique()))]
    ]
    
    param_table = Table(param_data, colWidths=[200, 200])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(param_table)
    
    # Pied de page
    story.append(Spacer(1, 20))
    footer = Paragraph("Rapport généré automatiquement par le Dashboard d'Analyse des Ventes - © 2024", normal_style)
    story.append(footer)
    
    # Génération du PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Interface Streamlit principale (Dashboard) ---
if page == "📊 Dashboard":
    st.title("Dashboard Interactif des Ventes")

    # Afficher le fichier actuellement chargé
    if st.session_state.uploaded_file is not None:
        st.success(f"📁 Fichier chargé : {st.session_state.uploaded_file.name}")
        
        # Bouton pour supprimer le fichier chargé
        if st.button("🗑️ Supprimer le fichier chargé"):
            st.session_state.uploaded_file = None
            st.session_state.df_complet = None
            st.rerun()

    uploaded_file = st.file_uploader(
        "Glissez-déposez votre journal des ventes (CSV) ici",
        type=["csv"],
        help="Le fichier doit être un CSV avec un séparateur ';' et un encodage 'latin1'.",
        key="dashboard_upload"
    )

    # Gérer le chargement du fichier
    if uploaded_file is not None:
        # Si un nouveau fichier est chargé, mettre à jour le session_state
        if uploaded_file != st.session_state.uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.session_state.df_complet = load_data(uploaded_file)
            st.rerun()

    # Utiliser les données du session_state si disponibles
    if st.session_state.df_complet is not None:
        df_complet = st.session_state.df_complet

        # --- Barre Latérale des Filtres ---
        st.sidebar.header("Filtres")

        min_date = df_complet['Date'].min().date()
        max_date = df_complet['Date'].max().date()
        
        # Bouton de réinitialisation uniquement
        if st.sidebar.button("🗑️ Réinitialiser les filtres", use_container_width=True):
            if 'selected_categories' in st.session_state:
                del st.session_state.selected_categories
            if 'selected_articles' in st.session_state:
                del st.session_state.selected_articles

        # Dates
        date_debut = st.sidebar.date_input(
            "Date de début", 
            min_date, 
            min_value=min_date, 
            max_value=max_date
        )
        date_fin = st.sidebar.date_input(
            "Date de fin", 
            max_date, 
            min_value=date_debut, 
            max_value=max_date
        )

        all_categories = sorted(df_complet['Catégorie'].unique())
        
        # Boutons pour les catégories
        st.sidebar.markdown("**Catégories**")
        cat_col1, cat_col2 = st.sidebar.columns(2)
        with cat_col1:
            if st.button("✅ Toutes", key="all_categories", use_container_width=True):
                st.session_state.selected_categories = all_categories
        with cat_col2:
            if st.button("❌ Aucune", key="no_categories", use_container_width=True):
                st.session_state.selected_categories = []

        selected_categories = st.sidebar.multiselect(
            "Sélection des catégories",
            all_categories,
            default=st.session_state.get('selected_categories', all_categories),
            label_visibility="collapsed"
        )
        
        # Stocker les catégories sélectionnées
        st.session_state.selected_categories = selected_categories

        # Filtrer les articles en fonction des catégories sélectionnées
        if selected_categories:
            # Obtenir les articles qui appartiennent aux catégories sélectionnées
            articles_filtres = sorted(df_complet[df_complet['Catégorie'].isin(selected_categories)]['Libellé'].unique())
        else:
            # Si aucune catégorie n'est sélectionnée, montrer tous les articles
            articles_filtres = sorted(df_complet['Libellé'].unique())

        # Boutons pour les articles
        st.sidebar.markdown("**Articles**")
        art_col1, art_col2 = st.sidebar.columns(2)
        with art_col1:
            if st.button("✅ Tous", key="all_articles", use_container_width=True):
                st.session_state.selected_articles = articles_filtres
        with art_col2:
            if st.button("❌ Aucun", key="no_articles", use_container_width=True):
                st.session_state.selected_articles = []

        # Fonction pour filtrer les articles sélectionnés qui existent dans la liste filtrée
        def get_valid_default_articles(default_articles, available_articles):
            """Retourne uniquement les articles par défaut qui existent dans la liste disponible"""
            return [article for article in default_articles if article in available_articles]

        # Obtenir les articles sélectionnés par défaut (valides)
        default_articles = st.session_state.get('selected_articles', articles_filtres)
        valid_default_articles = get_valid_default_articles(default_articles, articles_filtres)

        selected_articles = st.sidebar.multiselect(
            "Sélection des articles",
            articles_filtres,
            default=valid_default_articles,
            label_visibility="collapsed"
        )
        
        # Stocker les articles sélectionnés
        st.session_state.selected_articles = selected_articles

        # Application des filtres
        df = df_complet[
            (df_complet['Date'] >= pd.to_datetime(date_debut)) &
            (df_complet['Date'] <= pd.to_datetime(date_fin)) &
            (df_complet['Catégorie'].isin(selected_categories)) &
            (df_complet['Libellé'].isin(selected_articles))
        ]

        if df.empty:
            st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
            st.stop()

        # --- AFFICHAGE COMPLET DU DASHBOARD ---
        st.markdown(f"Analyse de la période du **{date_debut.strftime('%d/%m/%Y')}** au **{date_fin.strftime('%d/%m/%Y')}**")

        # Section 1: Indicateurs Clés (KPIs)
        st.header("Indicateurs Clés (KPIs)")

        total_ttc = df['Total_TTC'].sum()
        total_ht = df['Total_HT'].sum()
        total_quantite = df['Quantité'].sum()
        prix_moyen = total_ttc / total_quantite if total_quantite > 0 else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Chiffre d'Affaires Total (TTC)", f"{total_ttc:,.2f} €")
        kpi2.metric("Chiffre d'Affaires Total (HT)", f"{total_ht:,.2f} €")
        kpi3.metric("Volume d'Articles Vendus", f"{total_quantite:,.0f}")
        kpi4.metric("Prix Moyen par Article (TTC)", f"{prix_moyen:,.2f} €")

        st.markdown("---")

        # --- Section 2: Évolution Temporelle ---
        st.header("📈 Évolution du Chiffre d'Affaires (TTC)")

        # Widget pour choisir la fréquence
        frequence_choix = st.selectbox(
            "Agréger par :",
            options=['Mois', 'Semaine', 'Jour'],
            index=0  # 'Mois' par défaut
        )

        # Préparation des données pour le graphique d'évolution
        freq_map = {'Jour': 'D', 'Semaine': 'W', 'Mois': 'M'}
        freq_code = freq_map[frequence_choix]

        df_temp = df.set_index('Date')
        df_evolution = df_temp['Total_TTC'].resample(freq_code).sum().reset_index()

        # Renommer les colonnes pour le graphique
        df_evolution.columns = [frequence_choix, 'Total TTC (€)']

        # Création du graphique
        fig_evol = px.line(
            df_evolution,
            x=frequence_choix,
            y='Total TTC (€)',
            title=f"Évolution du Total TTC par {frequence_choix.lower()}"
        )
        st.plotly_chart(fig_evol, use_container_width=True)

        st.markdown("---")

        # --- Section 3: Top 10 ---
        st.header("🏆 Analyse des Performers")
        col1, col2 = st.columns(2)

        # Variables pour stocker les graphiques
        fig_top_art = None
        fig_top_cat = None

        # Colonne 1: Top 10 Articles
        with col1:
            st.subheader("Top 10 Articles")
            
            # Sélecteur pour le critère de classement
            critere_articles = st.selectbox(
                "Classer les articles par :",
                options=["Chiffre d'Affaires (TTC)", "Volume des Ventes (Quantité)"],
                key='critere_articles'
            )
            
            # Logique de classement
            if critere_articles == "Chiffre d'Affaires (TTC)":
                col_a_sommer = 'Total_TTC'
                axe_x_label = "Chiffre d'Affaires Total (TTC)"
            else:
                col_a_sommer = 'Quantité'
                axe_x_label = "Volume Total Vendu (Quantité)"

            # Calcul du Top 10
            df_groupe_art = df.groupby('Libellé')[col_a_sommer].sum().reset_index()
            df_top10_art = df_groupe_art.sort_values(by=col_a_sommer, ascending=False).head(10)

            # Graphique Top 10 Articles
            fig_top_art = px.bar(
                df_top10_art,
                y='Libellé',
                x=col_a_sommer,
                title=f"Top 10 des articles par {critere_articles}",
                labels={'Libellé': 'Article', col_a_sommer: axe_x_label}
            )
            fig_top_art.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top_art, use_container_width=True)

        # Colonne 2: Top 10 Catégories
        with col2:
            st.subheader("Top 10 Catégories")
            
            # Sélecteur pour le critère de classement
            critere_categories = st.selectbox(
                "Classer les catégories par :",
                options=["Chiffre d'Affaires (TTC)", "Volume des Ventes (Quantité)"],
                key='critere_categories'
            )
            
            # Logique de classement
            if critere_categories == "Chiffre d'Affaires (TTC)":
                col_a_sommer_cat = 'Total_TTC'
                axe_x_label_cat = "Chiffre d'Affaires Total (TTC)"
            else:
                col_a_sommer_cat = 'Quantité'
                axe_x_label_cat = "Volume Total Vendu (Quantité)"

            # Calcul du Top 10
            df_groupe_cat = df.groupby('Catégorie')[col_a_sommer_cat].sum().reset_index()
            df_top10_cat = df_groupe_cat.sort_values(by=col_a_sommer_cat, ascending=False).head(10)

            # Graphique Top 10 Catégories
            fig_top_cat = px.bar(
                df_top10_cat,
                y='Catégorie',
                x=col_a_sommer_cat,
                title=f"Top 10 des catégories par {critere_categories}",
                labels={'Catégorie': 'Catégorie', col_a_sommer_cat: axe_x_label_cat}
            )
            fig_top_cat.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_top_cat, use_container_width=True)

        st.markdown("---")

        # --- Section 4: Répartition par Catégorie ---
        st.header("💰 Répartition par Catégorie")

        # Sélecteur pour le camembert
        critere_pie = st.radio(
            "Voir la répartition par :",
            options=["Chiffre d'Affaires (TTC)", "Volume des Ventes (Quantité)"],
            key='critere_pie'
        )

        if critere_pie == "Chiffre d'Affaires (TTC)":
            col_pie = 'Total_TTC'
            title_pie = "Répartition du Chiffre d'Affaires (TTC) par Catégorie"
        else:
            col_pie = 'Quantité'
            title_pie = "Répartition du Volume des Ventes par Catégorie"

        # Calcul de la répartition
        df_repartition = df.groupby('Catégorie')[col_pie].sum().reset_index()

        # Graphique Camembert
        fig_pie = px.pie(
            df_repartition,
            names='Catégorie',
            values=col_pie,
            title=title_pie
        )
        fig_pie.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- Section 5: Téléchargement PDF ---
        st.sidebar.markdown("---")
        st.sidebar.header("Téléchargement")

        # Créer le rapport PDF avec les graphiques actuels
        pdf_buffer = create_pdf_with_charts(
            df, pd.to_datetime(date_debut), pd.to_datetime(date_fin), frequence_choix, 
            critere_articles, critere_categories, critere_pie,
            fig_evol, fig_top_art, fig_top_cat, fig_pie
        )
        
        # Bouton de téléchargement PDF
        st.sidebar.download_button(
            label="📥 Télécharger le Rapport (PDF)",
            data=pdf_buffer,
            file_name=f"rapport_ventes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            help="Téléchargez un rapport PDF avec les graphiques actuels"
        )

        st.sidebar.markdown("""
        **Le PDF inclut :**
        • Les indicateurs clés
        • Tous les graphiques affichés
        • Les paramètres sélectionnés
        """)

        # --- Section 6: Données Brutes ---
        with st.expander("Afficher les données filtrées"):
            st.dataframe(df)

    else:
        if st.session_state.uploaded_file is None:
            st.info("Veuillez charger un fichier CSV pour démarrer l'analyse.")
