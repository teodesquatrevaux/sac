import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components

# --- Configuration de la page Streamlit ---
st.set_page_config(layout="wide", page_title="Analyse des Ventes")

# --- Chargement et Préparation des Données (mis en cache pour la performance) ---
@st.cache_data
def load_data(uploaded_file):
    """
    Charge, nettoie et catégorise les données de ventes à partir d'un fichier chargé.
    Toute la préparation effectuée dans le notebook est ici.
    """
    
    # Charger le fichier depuis l'objet uploadé
    try:
        # Utilise l'argument 'uploaded_file' au lieu d'un chemin de fichier
        df = pd.read_csv(uploaded_file, sep=";", encoding='latin1')
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier CSV : {e}")
        st.error("Veuillez vérifier que le fichier est un CSV valide, avec le séparateur ';' et l'encodage 'latin1'.")
        st.stop()
        
    # Supprimer les colonnes inutiles
    df.drop(columns=['AQTE1', 'ATTC1', 'AHT1', 'AQTE2', 'ATTC2', 'AHT2'], inplace=True, errors='ignore')

    # --- Nettoyage des données (Cellule 4) ---
    # Gérer les erreurs potentielles si les colonnes n'existent pas
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
        
        # S'assurer que la colonne Quantité est numérique (ajout de sécurité)
        df['Quantité'] = pd.to_numeric(df['Quantité'], errors='coerce').fillna(0)

    except KeyError as e:
        st.error(f"Erreur : Colonne manquante dans le fichier chargé : {e}.")
        st.error("Assurez-vous que le fichier contient les colonnes 'Total HT', 'TVA', 'Total TTC', 'Date', 'Quantité' et 'Code établissement'.")
        st.stop()
    except Exception as e:
        st.error(f"Erreur lors du nettoyage des données : {e}")
        st.stop()


    # --- Fonction de Catégorisation (Cellule 5) ---
    def categoriser_article(libelle):
        libelle = str(libelle).lower()
        
        # --- Boissons : Alcoolisées ---
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
            
        # --- Boissons : Non Alcoolisées ---
        if any(keyword in libelle for keyword in ['café', 'coffee', 'espresso', 'latte', 'dèca', 'chocolat viennois', 'hot chocolat', 'tisane', 'verveine', 'déca', 'cappucino', 'glass of milk']):
            return 'Boisson Chaude - Café/Chocolat'
        if any(keyword in libelle for keyword in ['tea', 'thé', 'earl grey', 'green tea', 'mariage', 'mint tea', 'fruits rouges']):
            return 'Boisson Chaude - Thé'
        if any(keyword in libelle for keyword in ['coke', 'cola', 'sprite', 'schweppes', 'diabolo', 'orangina', 'powerade', 'syrop', 'ice tea', 'ginger beer', 'choose']):
            return 'Boisson Froide - Soda/Jus'
        if any(keyword in libelle for keyword in ['jus', 'juice', 'orange', 'pomme', 'apple', 'tomato', 'apricot', 'cranberry', 'pamplemousse']):
            return 'Boisson Froide - Jus de Fruit'
        if any(keyword in libelle for keyword in ['cristaline', 'badoit', 'perrier', 'evian']):
            return 'Boisson Froide - Eau'
            
        # --- Nourriture : Sucré ---
        if any(keyword in libelle for keyword in ['cookie', 'muffin', 'cake', 'brownie', 'pie', 'crumble', 'viennoiserie', 'biscuit', 'croissant', 'pain d epice', 'frangipane', 'cupcake', 'lemon bars', 'lemon poppyseed loaf']):
            return 'Pâtisserie/Sucré'
        if any(keyword in libelle for keyword in ['mars', 'twix', 'kinder bueno', 'kit kat', 'lolly pops', 'magnum', 'cornetto', 'twister', 'haribo', 'lion king', 'rocket', 'marshmallow']):
            return 'Glace/Confiserie'
            
        # --- Nourriture : Salé ---
        
        # ***** LIGNE CORRIGÉE *****
        if any(keyword in libelle for keyword in ['quiche', 'gnocchi', 'lasagna', 'chili', 'nuggets', 'lil\'fries', 'crisps', 'terrîne', 'hot dog', 'gaspacho']):
            return 'Plat/Snack Salé'
        
        if any(keyword in libelle for keyword in ['plat à', 'plat 11', 'plat 13']):
            return 'Plat du Jour'
        if any(keyword in libelle for keyword in ['terrine', 'vrai & bon pot']):
            return 'Bocaux'

        # --- Autres / Services / Entrées ---
        if any(keyword in libelle for keyword in ['entree', 'fee', 'vigik', 'corkage', 'tennis', 'squash', 'social', 'member', 'adult', 'bridge', 'snooker', 'remboursement', 'mini viennoiserie', 'cuff links', 'polo', 'bbq', 'cutlery']):
            return 'Service / Frais / Activité'
        if any(keyword in libelle for keyword in ['balle', 'balls']):
            return 'Matériel'
        if any(keyword in libelle for keyword in ['not used']):
            return 'Hors Catégorie' 

        return 'Autre'

    # Appliquer la catégorisation
    try:
        df['Catégorie'] = df['Libellé'].apply(categoriser_article)
    except KeyError:
        st.error("Erreur : La colonne 'Libellé' est manquante dans le fichier chargé.")
        st.stop()
    
    return df

# --- Début de la Page Principale ---

# Ajout du logo (visible avant le chargement)
try:
    st.image("Standard_AC.svg.png", width=50)
except Exception as e:
    st.warning(f"Impossible d'afficher le logo 'Standard_AC.svg.png'. Assurez-vous qu'il est dans le bon dossier. Erreur: {e}")

st.title("Dashboard Interactif des Ventes")

# --- MODIFICATION : Zone de Chargement de Fichier ---
uploaded_file = st.file_uploader(
    "Glissez-déposez votre journal des ventes (CSV) ici",
    type=["csv"],
    help="Le fichier doit être un CSV avec un séparateur ';' et un encodage 'latin1'."
)

# --- Le reste de l'application ne s'exécute que si un fichier est chargé ---
if uploaded_file is not None:

    # Charger le DataFrame complet à partir du fichier uploadé
    df_complet = load_data(uploaded_file)

    # --- Barre Latérale des Filtres ---
    st.sidebar.header("Filtres")

    # Filtre par Date
    min_date = df_complet['Date'].min().date()
    max_date = df_complet['Date'].max().date()
    date_debut = st.sidebar.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
    date_fin = st.sidebar.date_input("Date de fin", max_date, min_value=date_debut, max_value=max_date)

    # Conversion des dates pour la comparaison
    date_debut = pd.to_datetime(date_debut)
    date_fin = pd.to_datetime(date_fin)

    # Filtre par Catégorie
    all_categories = sorted(df_complet['Catégorie'].unique())
    selected_categories = st.sidebar.multiselect("Catégories", all_categories, default=all_categories)

    # Filtre par Établissement
    all_etablissements = sorted(df_complet['Code_établissement'].unique())
    selected_etablissements = st.sidebar.multiselect("Établissements", all_etablissements, default=all_etablissements)

    # Filtre par Article (Libellé)
    all_articles = sorted(df_complet['Libellé'].unique())
    selected_articles = st.sidebar.multiselect("Articles (Libellé)", all_articles, default=all_articles)


    # --- Bouton de téléchargement PDF ---
    st.sidebar.markdown("---")
    st.sidebar.header("Téléchargement")

    # ... (Le code CSS reste le même) ...
    print_css = """
    <style>
    @media print {
      /* Cache la barre latérale, le header Streamlit, et les boutons */
      [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], .stButton {
        display: none !important;
      }
      /* Assure que le contenu principal prend toute la largeur */
      [data-testid="stAppViewContainer"] {
        padding-left: 0 !important;
        padding-top: 0 !important;
      }
      /* Ajuste les marges du conteneur principal */
      .block-container {
        padding: 1rem 1rem 0 1rem !important;
      }
      /* Empêche les graphiques Plotly de se redimensionner étrangement */
      .plotly-chart {
        width: 100% !important;
      }
    }
    </style>
    """
    st.markdown(print_css, unsafe_allow_html=True)

    # Bouton Streamlit qui déclenche le script d'impression
    if st.sidebar.button("📥 Télécharger la page en PDF"):
        # JS pour appeler l'impression sur la fenêtre PARENTE (l'onglet du navigateur)
        # et non sur l'iframe vide du composant.
        # Un délai est ajouté pour laisser le temps aux graphiques Plotly de s'afficher
        # dans le rendu d'impression, ce qui est souvent la cause des pages blanches.
        print_js = """
        <script>
            setTimeout(function() {
                window.parent.print();
            }, 500); // Délai de 500ms, vous pouvez ajuster si nécessaire
        </script>
        """
        # Mettre height=1 (au lieu de 0) pour s'assurer que le script s'exécute
        components.html(print_js, height=1) 

    st.sidebar.caption(
        "Utilise la fonction \"Enregistrer en PDF\" de votre navigateur."
    )

    # --- Application des Filtres ---
    df = df_complet[
        (df_complet['Date'] >= date_debut) &
        (df_complet['Date'] <= date_fin) &
        (df_complet['Catégorie'].isin(selected_categories)) &
        (df_complet['Code_établissement'].isin(selected_etablissements)) &
        (df_complet['Libellé'].isin(selected_articles))
    ]

    # Gérer le cas où le DataFrame filtré est vide
    if df.empty:
        st.warning("Aucune donnée disponible pour les filtres sélectionnés.")
        st.stop()


    # --- Suite de la Page Principale ---

    st.markdown(f"Analyse de la période du **{date_debut.strftime('%d/%m/%Y')}** au **{date_fin.strftime('%d/%m/%Y')}**")

    # --- Section 1: Indicateurs Clés (KPIs) ---
    st.header("Indicateurs Clés (KPIs)")

    # Calcul des KPIs sur le dataframe filtré
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

    # --- Section 5: Données Brutes ---
    with st.expander("Afficher les données filtrées"):
        st.dataframe(df)

# --- Message si aucun fichier n'est chargé ---
else:
    st.info("Veuillez charger un fichier CSV pour démarrer l'analyse.")