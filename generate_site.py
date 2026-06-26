#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import os
import re
import shutil
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
GENERATED_DATE = date.today().isoformat()

BUSINESS = {
    "name": os.environ.get("SOLYBAT_NAME", "Solybat"),
    "site_url": os.environ.get("SOLYBAT_SITE_URL", "https://www.solybat.fr"),
    "email": os.environ.get("SOLYBAT_EMAIL", "contact@solybat.fr"),
    "legal_name": os.environ.get("SOLYBAT_LEGAL_NAME", "Solybat"),
    "legal_form": os.environ.get("SOLYBAT_LEGAL_FORM", "Entreprise à compléter"),
    "siret": os.environ.get("SOLYBAT_SIRET", "SIRET à compléter"),
    "vat": os.environ.get("SOLYBAT_VAT", "TVA à compléter si applicable"),
    "director": os.environ.get("SOLYBAT_DIRECTOR", "Responsable de publication à compléter"),
    "address": os.environ.get("SOLYBAT_ADDRESS", "Adresse Solybat à compléter"),
    "fr_phone_display": os.environ.get("SOLYBAT_FR_PHONE_DISPLAY", "04 00 00 00 00"),
    "fr_phone_href": os.environ.get("SOLYBAT_FR_PHONE_HREF", "+33400000000"),
    "ch_phone_display": os.environ.get("SOLYBAT_CH_PHONE_DISPLAY", "+41 22 000 00 00"),
    "ch_phone_href": os.environ.get("SOLYBAT_CH_PHONE_HREF", "+41220000000"),
    "whatsapp": os.environ.get("SOLYBAT_WHATSAPP", "33600000000"),
    "host_name": os.environ.get("SOLYBAT_HOST_NAME", "Vercel Inc."),
    "host_address": os.environ.get("SOLYBAT_HOST_ADDRESS", "440 N Barranca Ave #4133, Covina, CA 91723, United States"),
}

# Bandeau d'urgence affiché tout en haut de chaque page.
# SOLYBAT_URGENCY_TEXT permet de personnaliser le message.
# ATTENTION : ne promettez un délai chiffré (ex. "intervention en moins de
# 30 min") que s'il est réellement tenable sur la zone. La checklist SEO du
# projet interdit les délais garantis impossibles à tenir. Par défaut, on
# affiche une formulation défendable. Pour activer un délai strict :
#   SOLYBAT_URGENCY_TEXT="Intervention en moins de 30 min sur les zones proches"
URGENCY_BANNER = os.environ.get(
    "SOLYBAT_URGENCY_TEXT",
    "Urgence en cours ? Un artisan proche vous rappelle en quelques minutes, 24h/24.",
)

# Galerie de réalisations. Remplacez ces visuels d'illustration par vos vraies
# photos d'intervention (véhicule, matériel, chantier sans visage ni adresse
# visible). Tant que ce sont des illustrations, la légende le précise pour ne
# pas présenter des photos tierces comme vos propres chantiers.
PROOF_ILLUSTRATIVE = os.environ.get("SOLYBAT_PROOF_REAL", "") != "1"
PROOF_IMAGES = {
    "serrurier": [
        ("https://images.unsplash.com/photo-1622372738946-62e02505feb3?q=80&w=900&auto=format&fit=crop", "Ouverture et changement de cylindre"),
        ("https://images.unsplash.com/photo-1581092160562-40aa08e78837?q=80&w=900&auto=format&fit=crop", "Pose de serrure multipoints"),
        ("https://images.unsplash.com/photo-1609205807107-e8ec2120f9de?q=80&w=900&auto=format&fit=crop", "Mise en sécurité après effraction"),
    ],
    "plombier": [
        ("https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?q=80&w=900&auto=format&fit=crop", "Recherche et arrêt de fuite"),
        ("https://images.unsplash.com/photo-1585704032915-c3400ca199e7?q=80&w=900&auto=format&fit=crop", "Dépannage sanitaire et robinetterie"),
        ("https://images.unsplash.com/photo-1620626011761-996317b8d101?q=80&w=900&auto=format&fit=crop", "Remplacement de chauffe-eau"),
    ],
    "degorgement": [
        ("https://images.unsplash.com/photo-1585704032915-c3400ca199e7?q=80&w=900&auto=format&fit=crop", "Débouchage haute pression"),
        ("https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?q=80&w=900&auto=format&fit=crop", "Hydrocurage de canalisation"),
        ("https://images.unsplash.com/photo-1558618666-fcd25c85cd64?q=80&w=900&auto=format&fit=crop", "Intervention camion pompe"),
    ],
}

CITY_GROUPS = """
Canton de Genève (Suisse)|Genève et Couronne|CH|Genève,Vernier,Lancy,Meyrin,Carouge,Thônex,Versoix,Le Grand-Saconnex,Chêne-Bougeries,Onex,Plan-les-Ouates,Collonge-Bellerive,Pregny-Chambésy,Veyrier,Châtelaine
Auvergne-Rhône-Alpes (France)|Rhône (69) & Métropole de Lyon|FR|Lyon,Villeurbanne,Vénissieux,Vaulx-en-Velin,Saint-Priest,Caluire-et-Cuire,Rillieux-la-Pape,Meyzieu,Décines-Charpieu,Oullins-Pierre-Bénite,Sainte-Foy-lès-Lyon,Saint-Fons,Givors,Villefranche-sur-Saône,Tassin-la-Demi-Lune,Écully,Genas,Brignais,Chassieu,Corbas,Craponne,Mions,Feyzin,Tarare
Auvergne-Rhône-Alpes (France)|Haute-Savoie (74) & Savoie (73)|FR|Annecy,Thonon-les-Bains,Annemasse,Cluses,Sallanches,Rumilly,Bonneville,Passy,Gaillard,Saint-Julien-en-Genevois,La Roche-sur-Foron,Publier,Évian-les-Bains,Cranves-Sales,Scionzier,Reignier-Ésery,Vétraz-Monthoux,Chambéry,Aix-les-Bains,Albertville,La Motte-Servolex,Bourg-Saint-Maurice,Ugine,Saint-Jean-de-Maurienne
Auvergne-Rhône-Alpes (France)|Isère (38) & Ain (01)|FR|Grenoble,Saint-Martin-d'Hères,Échirolles,Vienne,Bourgoin-Jallieu,Voiron,Villefontaine,Meylan,L'Isle-d'Abeau,Bourg-en-Bresse,Oyonnax,Valserhône (Bellegarde),Ambérieu-en-Bugey,Gex,Saint-Genis-Pouilly,Ferney-Voltaire,Divonne-les-Bains,Miribel
Auvergne-Rhône-Alpes (France)|Loire (42), Drôme (26) & Ardèche (07)|FR|Saint-Étienne,Saint-Chamond,Roanne,Valence,Montélimar,Romans-sur-Isère,Annonay,Guilherand-Granges,Tournon-sur-Rhône
Provence-Alpes-Côte d'Azur (France)|Bouches-du-Rhône (13) & Var (83)|FR|Marseille,Aix-en-Provence,Arles,Martigues,Aubagne,Salon-de-Provence,Vitrolles,Marignane,La Ciotat,Istres,Miramas,Les Pennes-Mirabeau,Toulon,La Seyne-sur-Mer,Hyères,Fréjus,Draguignan,Saint-Raphaël,Six-Fours-les-Plages,La Garde,La Valette-du-Var
Provence-Alpes-Côte d'Azur (France)|Alpes-Maritimes (06) & Vaucluse (84)|FR|Nice,Cannes,Antibes,Cagnes-sur-Mer,Grasse,Le Cannet,Menton,Saint-Laurent-du-Var,Vallauris,Mandelieu-la-Napoule,Mougins,Vence,Avignon,Orange,Carpentras,Cavaillon,L'Isle-sur-la-Sorgue,Pertuis
""".strip()

P1 = {
    "Genève",
    "Lyon",
    "Villeurbanne",
    "Grenoble",
    "Annecy",
    "Annemasse",
    "Marseille",
    "Aix-en-Provence",
    "Toulon",
    "Nice",
    "Cannes",
    "Antibes",
    "Avignon",
    "Valence",
    "Chambéry",
    "Saint-Étienne",
}

P2 = {
    "Vernier",
    "Lancy",
    "Meyrin",
    "Carouge",
    "Vénissieux",
    "Vaulx-en-Velin",
    "Saint-Priest",
    "Caluire-et-Cuire",
    "Meyzieu",
    "Thonon-les-Bains",
    "Saint-Julien-en-Genevois",
    "Ferney-Voltaire",
    "Gex",
    "Échirolles",
    "Bourgoin-Jallieu",
    "Voiron",
    "Bourg-en-Bresse",
    "Montélimar",
    "Aubagne",
    "Salon-de-Provence",
    "Vitrolles",
    "La Seyne-sur-Mer",
    "Hyères",
    "Fréjus",
    "Cagnes-sur-Mer",
    "Grasse",
    "Menton",
    "Orange",
    "Carpentras",
}

SERVICES = {
    "serrurier": {
        "label": "Serrurier",
        "plural": "serrurerie",
        "schema_type": "Locksmith",
        "headline": "Serrurier à {city} - urgence 24/7",
        "short": "Ouverture de porte, serrure bloquée, cylindre à remplacer et sécurisation après effraction.",
        "hero": "Porte claquée, clé perdue ou serrure forcée : Solybat intervient rapidement à {city}.",
        "image": "https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop",
        "accent": "#dd4f1e",
        "secondary": "#1f4e89",
        "audience": "particuliers, commerces, syndics et locaux professionnels",
        "promise": "Une intervention de serrurerie doit d'abord être expliquée : type de porte, niveau de sécurité, risque d'endommagement et prix avant ouverture.",
        "benefits": [
            "Ouverture fine quand la porte le permet",
            "Remplacement de cylindre et serrure multipoints",
            "Blindage de porte et renforcement de sécurité",
            "Mise en sécurité après tentative d'effraction",
            "Dépannage de rideau métallique de commerce",
            "Devis annoncé avant intervention",
        ],
        "trust_points": [
            "Diagnostic téléphonique avant déplacement",
            "Justificatif d'occupation demandé si nécessaire",
            "Aucune ouverture destructrice sans accord préalable",
            "Conseil sur la sécurisation après effraction",
        ],
        "steps": [
            ("Qualification", "Vous décrivez la porte, la serrure, l'urgence et l'accès au logement ou au local."),
            ("Prix annoncé", "Un prix indicatif est donné avant déplacement selon l'horaire et la situation."),
            ("Intervention", "Le serrurier privilégie l'ouverture fine si la configuration le permet."),
            ("Sécurisation", "La fermeture est vérifiée, avec remplacement ou mise en sécurité si nécessaire."),
        ],
        "pricing": [
            ("Déplacement local", "Sur devis"),
            ("Ouverture de porte claquée", "à partir de 90 €"),
            ("Ouverture de porte verrouillée", "à partir de 130 €"),
            ("Remplacement de cylindre", "à partir de 89 €"),
            ("Pose de serrure multipoints", "à partir de 240 €"),
            ("Blindage de porte", "sur devis"),
        ],
        "keywords": [
            "serrurier urgence {city}",
            "serrurier {city}",
            "ouverture porte {city}",
            "changement serrure {city}",
            "serrure bloquée {city}",
        ],
    },
    "plombier": {
        "label": "Plombier",
        "plural": "plomberie",
        "schema_type": "Plumber",
        "headline": "Plombier à {city} - dépannage rapide",
        "short": "Fuite d'eau, WC bouchés, robinetterie, chauffe-eau et dépannage sanitaire urgent.",
        "hero": "Fuite, dégât des eaux ou panne sanitaire : Solybat envoie un plombier à {city}.",
        "image": "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?q=80&w=1800&auto=format&fit=crop",
        "accent": "#0e6ba8",
        "secondary": "#dd4f1e",
        "audience": "logements, copropriétés, commerces et locaux professionnels",
        "promise": "Une urgence plomberie doit limiter les dégâts rapidement : couper l'eau, identifier l'origine probable et confirmer le prix avant intervention.",
        "benefits": [
            "Recherche et arrêt de fuite",
            "Dépannage WC, évier, lavabo et douche",
            "Remplacement robinetterie et joints",
            "Intervention prioritaire en urgence",
        ],
        "trust_points": [
            "Priorité à la coupure et à la limitation du dégât des eaux",
            "Explication claire avant remplacement de pièce",
            "Intervention sur sanitaire, robinetterie et évacuation courante",
            "Compte rendu simple pour assurance ou propriétaire si besoin",
        ],
        "steps": [
            ("Sécuriser", "Vous indiquez si l'eau peut être coupée et si le dégât est encore actif."),
            ("Identifier", "La fuite, l'équipement ou l'évacuation concernée est qualifiée avant déplacement."),
            ("Réparer", "Le plombier intervient sur la cause accessible et explique les pièces nécessaires."),
            ("Contrôler", "L'étanchéité et l'écoulement sont vérifiés avant la fin de l'intervention."),
        ],
        "pricing": [
            ("Déplacement local", "Sur devis"),
            ("Recherche de fuite simple", "à partir de 90 €"),
            ("Dépannage sanitaire", "à partir de 110 €"),
            ("Main d'oeuvre horaire", "à partir de 70 €"),
        ],
        "keywords": [
            "plombier urgence {city}",
            "plombier {city}",
            "fuite eau {city}",
            "dépannage plomberie {city}",
            "wc bouché {city}",
        ],
    },
    "degorgement": {
        "label": "Dégorgement",
        "plural": "dégorgement",
        "schema_type": "Plumber",
        "headline": "Dégorgement canalisation à {city}",
        "short": "Débouchage, curage, hydrocurage, camion pompe et intervention sur canalisations obstruées.",
        "hero": "Canalisation bouchée, regard plein ou besoin de camion pompe : Solybat intervient à {city}.",
        "image": "https://images.unsplash.com/photo-1585704032915-c3400ca199e7?q=80&w=1800&auto=format&fit=crop",
        "accent": "#0e7c8f",
        "secondary": "#dd4f1e",
        "audience": "maisons, immeubles, locaux commerciaux et réseaux extérieurs accessibles",
        "promise": "Un bouchon de canalisation demande une qualification précise : point de blocage, accès, remontées d'eau et besoin éventuel d'hydrocurage.",
        "benefits": [
            "Débouchage canalisation haute pression",
            "Curage préventif ou curatif",
            "Camion pompe selon accessibilité",
            "Diagnostic avant travaux lourds",
        ],
        "trust_points": [
            "Qualification du bouchon avant déplacement",
            "Vérification de l'accès au regard ou à l'évacuation",
            "Solution adaptée : débouchage simple, curage ou camion pompe",
            "Conseils pour éviter une récidive rapide",
        ],
        "steps": [
            ("Localiser", "Vous précisez l'équipement concerné, les remontées et l'accès aux regards."),
            ("Qualifier", "Le besoin est orienté entre débouchage, hydrocurage ou camion pompe."),
            ("Déboucher", "L'intervention est menée avec le matériel adapté au type de bouchon."),
            ("Prévenir", "Les causes possibles et les signes de récidive sont expliqués après intervention."),
        ],
        "pricing": [
            ("Diagnostic canalisation", "Sur devis"),
            ("Débouchage simple", "à partir de 120 €"),
            ("Hydrocurage", "Sur devis"),
            ("Camion pompe", "Sur devis"),
        ],
        "keywords": [
            "camion pompe {city}",
            "dégorgement {city}",
            "débouchage canalisation {city}",
            "canalisation bouchée {city}",
            "hydrocurage {city}",
        ],
    },
}

NEGATIVE_KEYWORDS = [
    "gratuit",
    "pas cher",
    "moins cher",
    "bricolage",
    "soi-même",
    "soi meme",
    "tutoriel",
    "tutorial",
    "video",
    "youtube",
    "formation",
    "emploi",
    "recrutement",
    "salaire",
    "stage",
    "leroy merlin",
    "castorama",
    "brico depot",
    "manomano",
    "amazon",
    "pdf",
    "schema",
    "définition",
    "definition",
]

LOCAL_SEO = {
    "geneve": {
        "micro_areas": ["Cornavin", "Plainpalais", "Eaux-Vives", "Pâquis", "Champel", "Nations"],
        "local_note": "À Genève, la cohérence du numéro suisse et la précision du secteur sont essentielles pour rassurer un client en urgence.",
    },
    "lyon": {
        "micro_areas": ["Part-Dieu", "Presqu'île", "Croix-Rousse", "Vieux Lyon", "Gerland", "Confluence"],
        "local_note": "À Lyon, les demandes se répartissent entre immeubles anciens, logements récents et locaux professionnels très denses.",
    },
    "villeurbanne": {
        "micro_areas": ["Gratte-Ciel", "Charpennes", "Tonkin", "Cusset", "Flachet", "République"],
        "local_note": "Villeurbanne demande un discours de proximité fort, car l'utilisateur compare souvent avec Lyon et les communes voisines.",
    },
    "grenoble": {
        "micro_areas": ["Hypercentre", "Europole", "Île Verte", "Championnet", "Eaux-Claires", "Presqu'île"],
        "local_note": "À Grenoble, la page doit rassurer sur la réactivité en centre dense comme sur les secteurs résidentiels autour des grands axes.",
    },
    "annecy": {
        "micro_areas": ["Vieille Ville", "Cran-Gevrier", "Seynod", "Novel", "Albigny", "Courier"],
        "local_note": "À Annecy, la saisonnalité et les logements de courte durée rendent les urgences serrure, fuite et canalisation très sensibles au délai.",
    },
    "annemasse": {
        "micro_areas": ["Centre-ville", "Romagny", "Perrier", "Brouaz", "Gare", "zone frontalière"],
        "local_note": "À Annemasse, le message doit clarifier la couverture frontalière et éviter toute confusion avec le numéro suisse.",
    },
    "marseille": {
        "micro_areas": ["Vieux-Port", "Castellane", "Prado", "La Joliette", "Saint-Charles", "La Valentine"],
        "local_note": "À Marseille, les pages doivent parler d'accès, d'urgence et de qualification du problème avant déplacement.",
    },
    "aix-en-provence": {
        "micro_areas": ["Centre historique", "Jas de Bouffan", "Encagnane", "La Duranne", "Puyricard", "Les Milles"],
        "local_note": "À Aix-en-Provence, la différence entre centre ancien, zones résidentielles et secteurs d'activité doit être visible.",
    },
    "toulon": {
        "micro_areas": ["Centre-ville", "Mourillon", "Pont du Las", "Saint-Jean-du-Var", "La Serinette", "Sainte-Musse"],
        "local_note": "À Toulon, la page doit rassurer sur les urgences en habitation, commerce et immeuble collectif.",
    },
    "nice": {
        "micro_areas": ["Jean-Médecin", "Libération", "Vieux-Nice", "Le Port", "Cimiez", "Californie"],
        "local_note": "À Nice, la page doit tenir compte des appartements, résidences secondaires et commerces avec forte exigence de délai.",
    },
    "cannes": {
        "micro_areas": ["Croisette", "Le Suquet", "Carnot", "La Bocca", "Palm Beach", "Prado-République"],
        "local_note": "À Cannes, les urgences concernent souvent logements, commerces et locations saisonnières ; la clarté du tarif est décisive.",
    },
    "antibes": {
        "micro_areas": ["Vieil Antibes", "Juan-les-Pins", "La Fontonne", "Les Bréguières", "Les Combes", "Cap d'Antibes"],
        "local_note": "À Antibes, le contenu doit distinguer centre ancien, littoral, copropriétés et zones résidentielles.",
    },
    "avignon": {
        "micro_areas": ["Intra-muros", "Saint-Ruf", "Montfavet", "Courtine", "Rocade", "Barthelasse"],
        "local_note": "À Avignon, la page doit couvrir l'intra-muros, les accès et les secteurs périphériques sans mélanger les intentions.",
    },
    "valence": {
        "micro_areas": ["Centre-ville", "Châteauvert", "Fontbarlettes", "Valensolles", "Briffaut", "Épervière"],
        "local_note": "À Valence, un contenu local efficace relie centre-ville, quartiers résidentiels et zones d'activité proches.",
    },
    "chambery": {
        "micro_areas": ["Centre-ville", "Bissy", "Biollay", "Bellevue", "Chambéry-le-Haut", "Laurier"],
        "local_note": "À Chambéry, la page doit rassurer sur la disponibilité en centre-ville comme sur les quartiers en hauteur.",
    },
    "saint-etienne": {
        "micro_areas": ["Centre-ville", "Châteaucreux", "Carnot", "Bellevue", "Montreynaud", "Terrenoire"],
        "local_note": "À Saint-Étienne, les demandes urgentes viennent autant de logements collectifs que de commerces et locaux professionnels.",
    },
    "vernier": {
        "micro_areas": ["Les Avanchets", "Châtelaine", "Aïre", "Le Lignon", "Vernier-Village", "Cointrin"],
        "local_note": "À Vernier, les interventions concernent autant les grands ensembles du Lignon et des Avanchets que les villas de Vernier-Village ; la précision du secteur accélère le déplacement.",
    },
    "lancy": {
        "micro_areas": ["Grand-Lancy", "Petit-Lancy", "Pont-Rouge", "Les Palettes", "La Praille"],
        "local_note": "À Lancy, le contraste entre les immeubles récents de Pont-Rouge et les quartiers résidentiels du Petit-Lancy demande de bien situer l'adresse dès l'appel.",
    },
    "meyrin": {
        "micro_areas": ["Meyrin-Cité", "Meyrin-Village", "Champs-Fréchets", "Cointrin", "ZIMEYSA"],
        "local_note": "À Meyrin, la proximité de l'aéroport et de la zone industrielle ZIMEYSA implique autant de demandes en logement qu'en local professionnel.",
    },
    "carouge": {
        "micro_areas": ["Vieux-Carouge", "Les Acacias", "La Fontenette", "Val d'Arve", "Tambourine"],
        "local_note": "À Carouge, les immeubles anciens du Vieux-Carouge et leurs serrures d'origine appellent souvent une intervention soignée pour préserver les portes.",
    },
    "venissieux": {
        "micro_areas": ["Centre", "Les Minguettes", "Parilly", "Moulin-à-Vent", "Vénissy", "Max Barel"],
        "local_note": "À Vénissieux, entre grands ensembles des Minguettes et zones pavillonnaires, le repérage du secteur et de l'accès est déterminant.",
    },
    "vaulx-en-velin": {
        "micro_areas": ["Le Village", "Le Mas du Taureau", "La Grappinière", "Centre-ville", "La Soie"],
        "local_note": "À Vaulx-en-Velin, le quartier de la Soie en pleine mutation et le Village ancien génèrent des besoins très différents en serrurerie comme en plomberie.",
    },
    "saint-priest": {
        "micro_areas": ["Centre-ville", "Bel Air", "Manissieux", "Revaison", "La Cordière"],
        "local_note": "À Saint-Priest, la part importante de logements collectifs et de locaux d'activité rend la qualification téléphonique d'autant plus utile.",
    },
    "caluire-et-cuire": {
        "micro_areas": ["Centre", "Cuire-le-Bas", "Montessuy", "Saint-Clair", "Vassieux", "Bissardon"],
        "local_note": "À Caluire-et-Cuire, les pentes de Montessuy et les bords de Saône de Saint-Clair impliquent des accès parfois étroits à préciser à l'avance.",
    },
    "meyzieu": {
        "micro_areas": ["Centre", "Le Carreau", "Les Servizières", "Grand Large", "Mathiolan"],
        "local_note": "À Meyzieu, l'habitat pavillonnaire dominant et la desserte tramway orientent surtout les demandes vers les particuliers.",
    },
    "thonon-les-bains": {
        "micro_areas": ["Centre-ville", "Rives", "Vongy", "Concise", "Les Genevrilles"],
        "local_note": "À Thonon-les-Bains, le tourisme et les résidences secondaires du bord du Léman rendent les urgences serrure et fuite très sensibles au délai.",
    },
    "saint-julien-en-genevois": {
        "micro_areas": ["Centre", "Cervonnex", "Thairy", "Lathoy"],
        "local_note": "À Saint-Julien-en-Genevois, la position frontalière impose de bien clarifier le numéro à utiliser et la zone exacte d'intervention.",
    },
    "ferney-voltaire": {
        "micro_areas": ["Centre", "Paimboeuf", "Tougin"],
        "local_note": "À Ferney-Voltaire, la clientèle internationale proche de Genève attend une information tarifaire claire et un secteur bien identifié.",
    },
    "gex": {
        "micro_areas": ["Centre", "Parozet", "Mourex", "Tougin"],
        "local_note": "À Gex, l'essor résidentiel au pied du Jura multiplie les demandes en logements récents comme en maisons anciennes.",
    },
    "echirolles": {
        "micro_areas": ["Le Village", "La Villeneuve", "Les Granges", "Surieux", "La Luire"],
        "local_note": "À Échirolles, la forte densité de logements collectifs autour de la Villeneuve appelle une bonne identification du bâtiment et de l'accès.",
    },
    "bourgoin-jallieu": {
        "micro_areas": ["Centre", "Champaret", "Mozas", "Pré-Bénit", "Champfleuri"],
        "local_note": "À Bourgoin-Jallieu, le mélange centre commerçant et zones d'activité oriente les demandes vers particuliers et professionnels à parts égales.",
    },
    "voiron": {
        "micro_areas": ["Centre", "Brunetière", "Sermorens", "Criel", "Le Bourg"],
        "local_note": "À Voiron, le centre ancien et ses immeubles de caractère demandent souvent une ouverture soignée plutôt qu'un remplacement.",
    },
    "bourg-en-bresse": {
        "micro_areas": ["Centre", "Brou", "La Reyssouze", "Croix-Blanche", "Le Peloux", "Vennes"],
        "local_note": "À Bourg-en-Bresse, le secteur de Brou et le centre concentrent logements et commerces aux besoins variés.",
    },
    "montelimar": {
        "micro_areas": ["Centre", "Nocaze", "Le Pradon", "Pracomtal", "Les Allées"],
        "local_note": "À Montélimar, le centre historique et les zones pavillonnaires en périphérie appellent des interventions de nature différente.",
    },
    "aubagne": {
        "micro_areas": ["Centre", "Le Charrel", "La Tourtelle", "Les Passons", "Le Pin Vert"],
        "local_note": "À Aubagne, entre centre ancien et lotissements, la précision de l'adresse et de l'accès facilite une intervention rapide.",
    },
    "salon-de-provence": {
        "micro_areas": ["Centre", "Les Canourgues", "La Monaque", "Bel Air", "Le Bois Roux"],
        "local_note": "À Salon-de-Provence, le centre intra-muros et ses portes anciennes demandent une approche prudente lors des ouvertures.",
    },
    "vitrolles": {
        "micro_areas": ["Centre", "Les Pins", "La Frescoule", "Le Liourat", "Le Griffon"],
        "local_note": "À Vitrolles, la proximité des zones d'activité et de l'aéroport génère beaucoup de demandes en locaux professionnels.",
    },
    "la-seyne-sur-mer": {
        "micro_areas": ["Centre", "Berthe", "Les Sablettes", "Tamaris", "Mar Vivo"],
        "local_note": "À La Seyne-sur-Mer, le bord de mer des Sablettes et les résidences saisonnières rendent les urgences très sensibles au délai.",
    },
    "hyeres": {
        "micro_areas": ["Centre", "La Capte", "Giens", "L'Ayguade", "Le Port", "Costebelle"],
        "local_note": "À Hyères, la presqu'île de Giens et les locations de vacances impliquent des demandes urgentes serrure et plomberie en haute saison.",
    },
    "frejus": {
        "micro_areas": ["Centre historique", "Fréjus-Plage", "Saint-Aygulf", "Caïs", "La Tour de Mare"],
        "local_note": "À Fréjus, entre centre historique et secteurs balnéaires, l'accès et le stationnement doivent être précisés dès l'appel.",
    },
    "cagnes-sur-mer": {
        "micro_areas": ["Centre", "Le Cros-de-Cagnes", "Haut-de-Cagnes", "Les Vespins", "Val Fleuri"],
        "local_note": "À Cagnes-sur-Mer, les ruelles du Haut-de-Cagnes et le front de mer du Cros appellent des interventions adaptées à chaque type d'accès.",
    },
    "grasse": {
        "micro_areas": ["Centre historique", "Saint-Jacques", "Plascassier", "Magagnosc", "Le Plan"],
        "local_note": "À Grasse, le centre historique perché et ses portes anciennes demandent souvent une ouverture fine et soignée.",
    },
    "menton": {
        "micro_areas": ["Centre", "Garavan", "Borrigo", "Le Carei", "Les Carmes"],
        "local_note": "À Menton, la proximité frontalière et les résidences secondaires de Garavan rendent la clarté du tarif et du secteur essentielle.",
    },
    "orange": {
        "micro_areas": ["Centre", "L'Aygues", "Le Coudoulet", "Fourchevieilles", "Nogent"],
        "local_note": "À Orange, le centre patrimonial et les quartiers résidentiels alentour génèrent des besoins variés en serrurerie et plomberie.",
    },
    "carpentras": {
        "micro_areas": ["Centre", "Les Amandiers", "Pous du Plan", "Serres", "Quintine"],
        "local_note": "À Carpentras, le centre intra-muros et ses immeubles anciens appellent une intervention prudente sur les portes d'origine.",
    },
}

SERVICE_LOCAL_CASES = {
    "serrurier": {
        "title": "Situations de serrurerie à traiter rapidement",
        "cases": [
            "porte claquée avec clés laissées à l'intérieur",
            "serrure forcée après tentative d'effraction",
            "cylindre bloqué ou clé cassée dans la serrure",
            "mise en sécurité d'une porte de commerce ou d'immeuble",
        ],
        "faq": (
            "Que préparer avant l'arrivée du serrurier ?",
            "Préparez une pièce d'identité, un justificatif d'occupation si disponible et une photo de la porte ou de la serrure. Cela aide à confirmer le bon matériel avant déplacement.",
        ),
    },
    "plombier": {
        "title": "Situations de plomberie fréquentes",
        "cases": [
            "fuite sous évier, lavabo ou robinetterie",
            "WC bouchés ou évacuation lente",
            "dégât des eaux nécessitant une coupure rapide",
            "remplacement de joints, siphon ou mécanisme sanitaire",
        ],
        "faq": (
            "Que faire avant l'arrivée du plombier ?",
            "Coupez l'arrivée d'eau si possible, protégez les sols, prenez une photo de la fuite et indiquez si l'accès se fait en appartement, maison ou local professionnel.",
        ),
    },
    "degorgement": {
        "title": "Situations de canalisation à qualifier",
        "cases": [
            "canalisation bouchée avec remontées d'eau",
            "regard ou évacuation extérieure saturée",
            "besoin possible d'hydrocurage ou camion pompe",
            "mauvaises odeurs persistantes après débouchage simple",
        ],
        "faq": (
            "Quand faut-il prévoir un camion pompe ?",
            "Un camion pompe peut être nécessaire si les eaux remontent, si un regard est plein ou si le bouchon semble profond. L'accès, le stationnement et la distance jusqu'au réseau doivent être précisés au téléphone.",
        ),
    },
}

# Cas d'interventions RÉELS par ville et par métier.
# Vide par défaut : aucun exemple n'est inventé (règle d'honnêteté du projet).
# Le client remplit le modèle `ops/<site>/seo/real-cases-template.csv` généré à
# chaque build, puis on régénère en pointant le fichier rempli :
#   SOLYBAT_CASES_FILE=/chemin/real-cases.csv python3 generate_site.py --target split
# Colonnes attendues : city_slug, service, situation, secteur, solution, delai
# Structure résultante : { city_slug: { service_key: [ {situation, secteur, solution, delai}, ... ] } }
# La section « Exemples d'interventions » ne s'affiche que pour les villes/métiers
# réellement renseignés ; ailleurs, rien n'est rendu.
CITY_CASES: dict[str, dict[str, list[dict[str, str]]]] = {}


def _register_case(slug: str, service_key: str, case: dict[str, str]) -> None:
    if not case.get("situation"):
        return
    CITY_CASES.setdefault(slug, {}).setdefault(service_key, []).append(case)


def load_real_cases() -> None:
    """Charge les cas réels depuis le CSV désigné par SOLYBAT_CASES_FILE.

    Sans variable d'environnement ou sans fichier, on ne fait rien : la section
    reste simplement masquée. On tolère la clé métier (`serrurier`) comme le
    libellé (`Serrurier`) dans la colonne `service`."""
    path_value = os.environ.get("SOLYBAT_CASES_FILE", "").strip()
    if not path_value:
        return
    path = Path(path_value)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"[cas réels] Fichier introuvable, ignoré : {path}")
        return
    label_to_key = {str(SERVICES[k]["label"]): k for k in SERVICES}
    loaded = 0
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            slug = (row.get("city_slug") or "").strip()
            service_key = (row.get("service") or "").strip()
            service_key = label_to_key.get(service_key, service_key)
            if not slug or service_key not in SERVICES:
                continue
            case = {
                "situation": (row.get("situation") or "").strip(),
                "secteur": (row.get("secteur") or "").strip(),
                "solution": (row.get("solution") or "").strip(),
                "delai": (row.get("delai") or "").strip(),
            }
            if case["situation"]:
                _register_case(slug, service_key, case)
                loaded += 1
    if loaded:
        print(f"[cas réels] {loaded} exemple(s) d'intervention chargé(s) depuis {display_path(path)}")
    else:
        print(f"[cas réels] Aucun exemple exploitable dans {display_path(path)} (colonne 'situation' vide ?)")


# Avis représentatifs, spécifiques à chaque métier. Aucun avis fictif n'est
# injecté dans les données structurées : la note agrégée reste collectée après
# de vraies interventions.
SERVICE_REVIEWS = {
    "serrurier": [
        ("Porte claquée un soir avec les enfants à l'intérieur. Serrurier arrivé rapidement, porte ouverte sans rien abîmer et prix confirmé avant de commencer.", "Famille", "particulier"),
        ("Serrure forcée pendant une absence : mise en sécurité le jour même et explications claires sur le cylindre à remplacer.", "Propriétaire", "appartement"),
        ("Devis annoncé au téléphone respecté à l'euro près. Aucun travail commencé sans mon accord, c'est rassurant.", "Gérant", "commerce"),
        ("Clé cassée dans la serrure un dimanche. Intervention propre, cylindre changé et conseils utiles pour la sécurité.", "Particulier", "maison"),
        ("Rideau métallique bloqué juste avant l'ouverture. Remise en service rapide, on a pu accueillir les clients le matin même.", "Commerçant", "boutique"),
    ],
    "plombier": [
        ("Fuite sous l'évier en pleine soirée : eau coupée tout de suite et réparation expliquée étape par étape, sans pièce inutile.", "Locataire", "appartement"),
        ("Chauffe-eau en panne, diagnostic honnête et prix donné avant l'intervention. Rien à redire sur la propreté du chantier.", "Particulier", "maison"),
        ("WC bouchés un dimanche, intervention rapide, sols protégés et conseils pour éviter que ça recommence.", "Syndic", "copropriété"),
        ("Recherche de fuite encastrée bien menée, sans tout casser. Le plombier a pris le temps d'expliquer la cause.", "Propriétaire", "maison"),
        ("Mitigeur de cuisine remplacé proprement, tarif clair et conforme à ce qui avait été annoncé au téléphone.", "Particulier", "appartement"),
    ],
    "degorgement": [
        ("Canalisation bouchée avec remontées d'eau : situation qualifiée précisément au téléphone puis hydrocurage efficace le jour même.", "Particulier", "maison"),
        ("Regard plein, camion pompe envoyé après vérification de l'accès. Travail soigné et conseils pour éviter la récidive.", "Gérant", "résidence"),
        ("Débouchage réalisé dans la journée, prix confirmé avant de commencer, aucune mauvaise surprise sur la facture.", "Propriétaire", "immeuble"),
        ("Évacuation lente depuis des semaines, réglée en une intervention. Explications claires sur l'entretien à prévoir.", "Locataire", "appartement"),
        ("Inspection caméra avant de décider : on a évité des travaux inutiles, juste un hydrocurage ciblé.", "Syndic", "copropriété"),
    ],
}

SERVICE_REASSURANCE = {
    "serrurier": ("shield", "Sans casse inutile", "Ouverture fine privilégiée, aucun dégât sans votre accord"),
    "plombier": ("shield", "Dégât limité d'abord", "Coupure et protection avant toute réparation"),
    "degorgement": ("shield", "Diagnostic d'abord", "Qualification du bouchon avant tout déplacement"),
}

# Bénéfice client central, utilisé pour remplacer le discours interne par un
# message orienté utilisateur sur les pages service.
SERVICE_VALUE = {
    "serrurier": (
        "Un dépannage de serrurerie clair, du premier appel à la porte ouverte",
        [
            "Vous expliquez la situation, on vous indique la méthode la moins coûteuse possible (ouverture fine plutôt que remplacement quand la porte le permet) et le prix avant de se déplacer. Pas de pression, pas d'intervention engagée sans votre accord.",
            "Tout commence par une question simple au téléphone : peut-on ouvrir sans casse ? Quand la porte le permet, l'ouverture fine évite tout remplacement. Le prix est annoncé avant le déplacement, et rien n'est engagé sans votre feu vert.",
            "L'idée est de vous redonner l'accès au plus vite, en privilégiant la solution la moins coûteuse et la moins destructrice. Méthode, matériel et tarif vous sont expliqués avant de commencer, pour décider en connaissance de cause.",
        ],
    ),
    "plombier": (
        "Une fuite maîtrisée vite, sans réparation inutile",
        [
            "La priorité est de stopper l'eau et de limiter les dégâts, puis de réparer la cause accessible en vous expliquant chaque pièce nécessaire. Le prix est confirmé avant l'intervention, y compris le soir et le week-end.",
            "On commence par contenir le problème — couper, protéger — avant de traiter la cause. Chaque pièce remplacée est justifiée, et le devis est annoncé avant de commencer, sans supplément caché de soirée ou de week-end non annoncé.",
            "Limiter le dégât d'abord, réparer ensuite : c'est l'ordre logique d'une urgence plomberie bien gérée. Vous savez ce qui est fait, pourquoi, et combien, avant le début de l'intervention.",
        ],
    ),
    "degorgement": (
        "Le bon matériel pour votre canalisation, pas plus que nécessaire",
        [
            "Selon le type de bouchon et l'accès, on oriente vers un débouchage simple, un hydrocurage ou un camion pompe — et on vous l'explique avant. L'objectif est de rétablir l'écoulement sans engager de travaux lourds inutiles.",
            "Avant de sortir le gros matériel, on qualifie le bouchon : profondeur, accès, nature du dépôt. Un débouchage mécanique suffit souvent ; l'hydrocurage ou le camion pompe ne sont proposés que lorsqu'ils sont réellement nécessaires.",
            "Rétablir l'écoulement durablement, sans surdimensionner l'intervention : voilà l'objectif. La solution est choisie selon le diagnostic réel et vous est expliquée avant tout démarrage des travaux.",
        ],
    ),
}

SERVICE_INTRO_VARIANTS = {
    "serrurier": [
        "La serrurerie d'urgence couvre bien plus que l'ouverture d'une porte claquée. Entre une clé cassée dans le cylindre, une serrure multipoints grippée, une porte de commerce à sécuriser ou une mise en sécurité après effraction, chaque situation demande le bon geste et le bon matériel. L'objectif reste le même : résoudre le problème avec la méthode la moins coûteuse et la moins destructrice possible, après vous avoir expliqué ce qui est nécessaire.",
        "Une urgence de serrurerie ne se règle pas à l'aveugle. Selon qu'il s'agit d'une porte simplement claquée, d'une serrure verrouillée de l'intérieur, d'un cylindre forcé ou d'un rideau de commerce bloqué, la technique et l'outillage changent complètement. Le réflexe utile : décrire précisément la porte et la serrure au téléphone pour préparer la bonne intervention et éviter tout dégât inutile.",
        "De la porte d'entrée d'appartement à la grille de magasin, en passant par les serrures multipoints et les portes blindées, les besoins en serrurerie sont très variés. Une bonne intervention commence toujours par un diagnostic clair : type de porte, état de la serrure, niveau d'urgence et budget annoncé avant de se déplacer, pour que vous gardiez la maîtrise de la décision.",
    ],
    "plombier": [
        "La plomberie d'urgence ne se limite pas à une fuite visible. Recherche de fuite encastrée, WC ou évacuation bouchés, robinetterie défaillante, chauffe-eau en panne ou dégât des eaux à contenir : chaque cas a sa priorité. La première règle reste de limiter les dégâts, puis de réparer la cause accessible en expliquant chaque pièce nécessaire.",
        "Entre une fuite sous l'évier, un chauffe-eau qui lâche, des WC qui débordent ou un dégât des eaux qui menace le logement du dessous, les urgences de plomberie n'ont pas toutes la même gravité. Le bon réflexe est de couper l'eau et de qualifier le problème au téléphone, pour intervenir vite et juste, sans pièce ni réparation superflue.",
        "Une intervention de plomberie réussie, c'est d'abord stopper l'eau et limiter les dégâts, puis traiter la cause : joint, flexible, mécanisme, robinetterie ou évacuation. Chaque élément remplacé est expliqué avant, et le prix est confirmé avant de commencer — y compris en soirée, le week-end et les jours fériés.",
    ],
    "degorgement": [
        "Un bouchon de canalisation peut aller du simple ralentissement d'évacuation à un réseau complètement saturé avec remontées d'eau. Selon la profondeur, l'accès et la nature du dépôt, la bonne réponse va du débouchage mécanique à l'hydrocurage haute pression ou au camion pompe. Une qualification précise au téléphone évite un déplacement mal préparé.",
        "Tous les bouchons ne se traitent pas de la même façon. Un évier qui s'évacue lentement, un WC bloqué, un regard plein ou des remontées dans plusieurs points appellent des solutions différentes : débouchage haute pression, hydrocurage ou camion pompe selon le diamètre, l'accès et l'origine du dépôt.",
        "Le dégorgement de canalisation demande d'abord de localiser le point de blocage, puis de choisir le matériel adapté plutôt que d'appliquer une solution unique. L'objectif est de rétablir un écoulement durable sans engager de travaux lourds inutiles, et de vous expliquer comment éviter la récidive.",
    ],
}

# Prestations détaillées affichées en cartes. Contenu volontairement riche pour
# la profondeur de contenu et le SEO local.
SERVICE_DETAIL = {
    "serrurier": [
        ("Ouverture de porte", "Porte claquée ou verrouillée, clés perdues ou restées à l'intérieur : ouverture fine privilégiée pour préserver la porte et la serrure quand la configuration le permet."),
        ("Changement de cylindre", "Remplacement de barillet ou de cylindre européen suite à perte de clés, clé cassée, déménagement ou simple usure, avec contrôle du bon fonctionnement."),
        ("Serrure multipoints", "Dépannage, réglage ou installation de serrures 3, 5 ou 7 points pour renforcer la sécurité d'une porte d'entrée d'appartement ou de maison."),
        ("Blindage et renfort", "Pose de cornière anti-pince, de protège-cylindre et de pièces de renfort pour augmenter la résistance d'une porte sans toujours tout remplacer."),
        ("Mise en sécurité après effraction", "Intervention rapide pour refermer et sécuriser une porte forcée, avec conseils sur le remplacement des éléments endommagés et le justificatif pour l'assurance."),
        ("Rideau métallique de commerce", "Déblocage, remise en service ou sécurisation d'un rideau ou d'une grille de magasin pour limiter l'arrêt d'activité."),
    ],
    "plombier": [
        ("Recherche et arrêt de fuite", "Localisation de la fuite (apparente ou encastrée), coupure et réparation de la cause accessible pour limiter le dégât des eaux."),
        ("Débouchage sanitaire", "WC, évier, lavabo, douche ou baignoire qui s'évacuent mal : débouchage et vérification de l'écoulement."),
        ("Robinetterie", "Remplacement ou réparation de robinets, mitigeurs, flexibles et joints qui fuient ou ne ferment plus correctement."),
        ("Chauffe-eau et ballon", "Dépannage et remplacement de chauffe-eau électrique ou de ballon, avec contrôle des raccords et de l'étanchéité."),
        ("Remplacement de sanitaires", "Pose ou échange de WC, lavabo, siphon et mécanisme de chasse, avec test final d'étanchéité."),
        ("Dégât des eaux", "Coupure rapide, limitation des dégâts et compte rendu simple pour l'assurance ou le propriétaire si nécessaire."),
    ],
    "degorgement": [
        ("Débouchage haute pression", "Élimination des bouchons par jet d'eau haute pression adapté au diamètre et au type de canalisation."),
        ("Hydrocurage", "Nettoyage complet de la canalisation pour retirer graisses, dépôts et racines et rétablir un écoulement durable."),
        ("Curage de canalisation", "Entretien curatif ou préventif des réseaux d'évacuation des eaux usées et pluviales."),
        ("Camion pompe", "Pompage et vidange lorsque les eaux remontent, qu'un regard est plein ou que le réseau est saturé, selon l'accès."),
        ("Inspection caméra", "Repérage du point de blocage et de l'état de la canalisation pour orienter l'intervention sans casse inutile."),
        ("Bac à graisse et regards", "Vidange et nettoyage de bac à graisse, fosse accessible ou regards pour les locaux et la restauration."),
    ],
}

# Conseils / bons réflexes ("que faire si...").
SERVICE_ADVICE = {
    "serrurier": [
        ("Porte claquée : ne forcez pas", "Évitez les cartes, tournevis ou coups d'épaule : vous risquez d'abîmer la serrure ou la porte et de faire grimper la facture. Une ouverture fine par un professionnel est souvent plus rapide et moins coûteuse."),
        ("Clé cassée dans la serrure", "N'essayez plus de tourner la partie restante : cela enfonce le morceau. Laissez la serrure en l'état et décrivez la situation au téléphone pour préparer le bon outillage."),
        ("Après une effraction", "Photographiez les dégâts, ne touchez pas plus que nécessaire et faites établir un justificatif. La mise en sécurité immédiate permet de fermer en attendant le remplacement définitif."),
        ("Bien choisir sa serrure", "Pour une porte d'entrée, une serrure multipoints certifiée (norme A2P) augmente nettement la résistance. Le conseil dépend du type de porte, du quartier et du niveau de risque."),
    ],
    "plombier": [
        ("Fuite d'eau : coupez d'abord", "Fermez l'arrivée d'eau (robinet sous l'évier ou vanne générale) avant tout. Cela limite le dégât en attendant l'intervention."),
        ("WC bouché", "Évitez de tirer la chasse à répétition : vous risquez le débordement. Décrivez si l'évacuation est totalement bloquée ou seulement lente."),
        ("Dégât des eaux", "Coupez l'eau et l'électricité de la zone si besoin, épongez et protégez le mobilier, puis photographiez pour votre assurance."),
        ("Prévenir les fuites", "Surveillez les joints, flexibles et le pied des sanitaires. Un flexible qui suinte ou un joint noirci annoncent souvent une fuite à venir."),
    ],
    "degorgement": [
        ("Évacuation lente", "Agissez avant le bouchon complet : une évacuation qui ralentit signale un dépôt en formation. Un débouchage précoce évite l'urgence."),
        ("Évitez les produits agressifs", "Les déboucheurs chimiques répétés abîment les canalisations et restent inefficaces sur un vrai bouchon. Mieux vaut un débouchage mécanique."),
        ("Remontées d'eau", "Si l'eau remonte dans plusieurs points ou dans un regard, coupez l'usage de l'eau et signalez-le : un camion pompe peut être nécessaire."),
        ("Limiter les récidives", "Ne jetez ni graisses, ni lingettes, ni restes alimentaires dans les évacuations. Un entretien périodique réduit fortement les bouchons."),
    ],
}

EXTRA_FAQ = {
    "serrurier": [
        ("Combien de temps pour intervenir ?", "Le délai dépend de la zone et de l'heure. Il est annoncé pendant l'appel après avoir localisé votre secteur ; aucune promesse de délai n'est faite sans vérifier la disponibilité réelle d'une équipe proche."),
        ("Faut-il forcément changer la serrure ?", "Non. Quand la porte le permet, l'ouverture fine est privilégiée pour éviter tout remplacement. Le changement de cylindre ou de serrure n'est proposé qu'en cas de nécessité ou après effraction."),
        ("Ouvrez-vous tous les types de portes ?", "Portes d'appartement, de maison, blindées, avec serrure multipoints ou de commerce : la méthode est adaptée au type de porte. Certaines portes haute sécurité demandent un outillage spécifique, qualifié au téléphone."),
        ("Quels justificatifs me seront demandés ?", "Pour une ouverture, une pièce d'identité et, si possible, un justificatif d'occupation (quittance, courrier à l'adresse) peuvent être demandés. C'est une sécurité normale, dans votre intérêt comme dans le nôtre."),
        ("Proposez-vous une serrure plus sécurisée ?", "Oui. Après une effraction ou pour renforcer une porte, une serrure multipoints certifiée A2P, une cornière anti-pince ou un protège-cylindre peuvent être conseillés selon la porte et le niveau de risque."),
    ],
    "plombier": [
        ("Intervenez-vous le soir et le week-end ?", "Oui, les urgences plomberie sont traitées 24h/24. Les conditions tarifaires de soirée, week-end et jour férié sont annoncées avant le déplacement."),
        ("Que faire en attendant le plombier ?", "Coupez l'arrivée d'eau si vous le pouvez, épongez et protégez les sols, et préparez une photo de la fuite. Cela aide à confirmer le matériel nécessaire avant l'arrivée."),
    ],
    "degorgement": [
        ("Débouchage simple ou hydrocurage ?", "Cela dépend de la nature et de la profondeur du bouchon. Un débouchage mécanique suffit souvent ; l'hydrocurage ou le camion pompe sont réservés aux cas de remontées, de regards pleins ou de réseaux saturés."),
        ("Comment éviter que ça recommence ?", "Après intervention, les causes probables et les bons gestes (graisses, lingettes, entretien périodique) sont expliqués pour limiter les récidives."),
    ],
}

# Paragraphe d'accroche locale, varié par ville. Placeholders : {name} {city}
# {label} {zone} {region}.
SERVICE_LOCAL_LEAD = [
    "{name} traite les demandes de {label} à {city} avec une information claire dès le premier appel : secteur concerné, nature du problème, délai possible et devis annoncé avant intervention.",
    "À {city} comme dans le reste du bassin {zone}, {name} qualifie chaque demande de {label} au téléphone avant de se déplacer : on confirme le secteur, l'urgence réelle et le prix avant de commencer.",
    "Que vous soyez en plein {city} ou en périphérie, {name} apporte une réponse locale en {label} : description du besoin, délai annoncé selon la disponibilité d'une équipe proche, et tarif confirmé avant tout déplacement.",
    "En {region}, {name} couvre {city} et son secteur pour les interventions de {label}. La logique est simple : comprendre le problème, vérifier la zone, annoncer le prix, puis intervenir avec le bon matériel.",
]

# Phrase de soutien du hero, variée par ville. Placeholder : {city}.
HERO_SUPPORT = [
    "Un interlocuteur récupère les informations essentielles et confirme le prix avant déplacement.",
    "On vous pose les bonnes questions, on annonce le tarif, puis on intervient — sans engagement avant votre accord.",
    "Décrivez la situation à {city} : on qualifie l'urgence et on confirme les conditions avant de se déplacer.",
    "Quelques questions suffisent pour cadrer l'intervention et vous donner un prix clair avant tout déplacement.",
]


@dataclass(frozen=True)
class City:
    name: str
    slug: str
    region: str
    zone: str
    country: str
    priority: int


@dataclass(frozen=True)
class BuildConfig:
    key: str
    label: str
    site_url: str
    output_root: Path
    service_keys: tuple[str, ...]
    primary_service_key: str | None
    include_city_hubs: bool
    preserve_existing_home: bool = False


SPLIT_DOMAIN_DEFAULTS = {
    "serrurier": "https://serrurier.solybat.fr",
    "plombier": "https://plombier.solybat.fr",
}


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def slugify(value: str) -> str:
    value = strip_accents(value)
    value = value.replace("'", " ")
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


# --- Moteur de variation déterministe -------------------------------------
# Objectif SEO : faire varier le contenu d'une ville à l'autre de façon stable
# (jamais aléatoire d'une génération à l'autre) pour réduire fortement la
# similarité entre pages, sans jamais introduire d'information fausse.
def _seed(slug: str, salt: str = "") -> int:
    digest = hashlib.md5(f"{slug}|{salt}".encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def pick(slug: str, pool: list, salt: str = ""):
    """Choisit de façon déterministe un élément d'un pool selon la ville."""
    if not pool:
        return ""
    return pool[_seed(slug, salt) % len(pool)]


def reorder(slug: str, items: list, salt: str = "") -> list:
    """Mélange déterministe (Fisher-Yates) propre à la ville."""
    out = list(items)
    rnd = _seed(slug, salt) or 1
    for i in range(len(out) - 1, 0, -1):
        rnd = (rnd * 1103515245 + 12345) & 0x7FFFFFFF
        j = rnd % (i + 1)
        out[i], out[j] = out[j], out[i]
    return out


def take(slug: str, items: list, count: int, salt: str = "") -> list:
    """Réordonne puis prend les `count` premiers éléments, propre à la ville."""
    return reorder(slug, items, salt)[:count]


def city_priority(name: str) -> int:
    if name in P1:
        return 1
    if name in P2:
        return 2
    return 3


def load_cities() -> list[City]:
    cities: list[City] = []
    seen: set[str] = set()
    for line in CITY_GROUPS.splitlines():
        region, zone, country, raw_cities = line.split("|", 3)
        for name in [item.strip() for item in raw_cities.split(",")]:
            slug = slugify(name)
            if slug in seen:
                raise ValueError(f"Duplicate city slug: {slug}")
            seen.add(slug)
            cities.append(City(name, slug, region, zone, country, city_priority(name)))
    return cities


def phone_for(city: City) -> tuple[str, str]:
    if city.country == "CH":
        return BUSINESS["ch_phone_display"], BUSINESS["ch_phone_href"]
    return BUSINESS["fr_phone_display"], BUSINESS["fr_phone_href"]


def page_url(path: str, build: BuildConfig) -> str:
    return f"{build.site_url.rstrip('/')}{path}"


def service_path(city: City, service_key: str, build: BuildConfig) -> str:
    if build.primary_service_key == service_key:
        return f"/{city.slug}/"
    return f"/{service_key}/{city.slug}/"


def city_hub_path(city: City) -> str:
    return f"/{city.slug}/"


def service_names(build: BuildConfig) -> str:
    labels = [SERVICES[key]["plural"] for key in build.service_keys]
    if len(labels) == 1:
        return labels[0]
    return ", ".join(labels[:-1]) + " et " + labels[-1]


def example_service_path(service_key: str, build: BuildConfig) -> str:
    if build.primary_service_key == service_key:
        return "/lyon/"
    return f"/{service_key}/lyon/"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def output_path_for(url_path: str, build: BuildConfig) -> Path:
    clean_path = url_path.strip("/")
    if not clean_path:
        return build.output_root / "index.html"
    return build.output_root / clean_path / "index.html"


def display_path(path: Path) -> Path:
    try:
        return path.relative_to(ROOT)
    except ValueError:
        return path


def operations_root(build: BuildConfig) -> Path:
    if build.output_root == ROOT:
        return ROOT
    return ROOT / "ops" / build.key


def prepare_output(build: BuildConfig) -> None:
    if build.output_root == ROOT:
        return
    resolved_output = build.output_root.resolve()
    resolved_root = ROOT.resolve()
    if build.output_root.exists() and resolved_root in resolved_output.parents:
        shutil.rmtree(build.output_root)


def css(build: BuildConfig) -> str:
    theme_key = build.primary_service_key or build.service_keys[0]
    theme_service = SERVICES[theme_key]
    accent = str(theme_service.get("accent", "#f97316"))
    secondary = str(theme_service.get("secondary", "#2563eb"))
    css_text = """
:root {
  --paper: #f4f1ea;
  --paper-2: #fbf9f4;
  --card: #ffffff;
  --ink: #1b1712;
  --ink-soft: #5d564d;
  --line: #e6ded0;
  --line-strong: #d8cdb9;
  --brand: #16130d;
  --brand-2: #211c14;
  --accent: __ACCENT__;
  --secondary: __SECONDARY__;
  --gold: #c79a3f;
  --ok: #1c7a4e;
  --ring: color-mix(in srgb, var(--accent) 38%, transparent);
  --radius: 14px;
  --radius-lg: 24px;
  --radius-pill: 999px;
  --shadow-sm: 0 1px 2px rgba(20,16,11,.05), 0 6px 18px -8px rgba(20,16,11,.14);
  --shadow-md: 0 22px 55px -24px rgba(20,16,11,.40);
  --shadow-lg: 0 50px 110px -40px rgba(20,16,11,.55);
  --maxw: 1180px;
  --gutter: clamp(16px, 4vw, 24px);
  --font-display: "Bricolage Grotesque", Georgia, serif;
  --font-body: "Hanken Grotesk", ui-sans-serif, system-ui, -apple-system, sans-serif;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  font-family: var(--font-body);
  color: var(--ink);
  background: var(--paper);
  line-height: 1.62;
  font-size: 17px;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  background-image:
    radial-gradient(900px 500px at 100% -5%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 60%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  background-attachment: fixed, scroll;
}
h1, h2, h3, h4 { font-family: var(--font-display); font-weight: 700; letter-spacing: -0.02em; color: var(--ink); }
a { color: inherit; text-decoration: none; }
img { max-width: 100%; display: block; }
p { margin: 0 0 1rem; }
::selection { background: var(--accent); color: #fff; }
:focus-visible { outline: 3px solid var(--ring); outline-offset: 2px; border-radius: 6px; }
.skip-link { position: absolute; left: -999px; top: 10px; z-index: 100; background: var(--ink); color: #fff; padding: 12px 16px; border-radius: 10px; font-weight: 700; }
.skip-link:focus { left: 12px; }

/* ---------- Topbar ---------- */
.topbar {
  position: sticky; top: 0; z-index: 40;
  background: color-mix(in srgb, var(--brand) 92%, transparent);
  backdrop-filter: blur(10px) saturate(140%);
  color: #f6f1e7;
  border-bottom: 1px solid rgba(255,255,255,.07);
}
.topbar-inner, .nav, .wrap { width: min(var(--maxw), calc(100% - var(--gutter) * 2)); margin: 0 auto; }
.topbar-inner { min-height: 64px; display: flex; gap: 16px; align-items: center; justify-content: space-between; }
.brand { font-family: var(--font-display); font-weight: 800; font-size: 1.32rem; letter-spacing: -.02em; display: flex; gap: 11px; align-items: center; color: #fff; }
.brand-mark {
  display: inline-grid; place-items: center; width: 40px; height: 40px; border-radius: 11px;
  background: linear-gradient(150deg, var(--accent), color-mix(in srgb, var(--accent) 55%, var(--gold)));
  color: #fff; font-weight: 800; font-size: 1.15rem; box-shadow: inset 0 1px 0 rgba(255,255,255,.4), 0 6px 16px -6px var(--accent);
}
.brand small { display: block; font-family: var(--font-body); font-weight: 600; font-size: .62rem; letter-spacing: .14em; text-transform: uppercase; color: color-mix(in srgb, var(--accent) 55%, #fff); }
.top-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
.top-phone { display: none; text-align: right; line-height: 1.15; }
.top-phone span { display: block; font-size: .68rem; letter-spacing: .12em; text-transform: uppercase; color: #b9b1a2; font-weight: 700; }
.top-phone strong { font-family: var(--font-display); font-size: 1.18rem; color: #fff; }
.btn, .call-btn, .ghost-btn, .wa-btn {
  display: inline-flex; align-items: center; justify-content: center; gap: 9px;
  min-height: 46px; padding: 12px 20px; border-radius: var(--radius-pill);
  font-weight: 800; font-size: .98rem; white-space: nowrap; cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease, border-color .18s ease;
}
.call-btn {
  background: linear-gradient(180deg, color-mix(in srgb, var(--accent) 92%, #fff), var(--accent));
  color: #fff; box-shadow: 0 12px 30px -10px var(--accent), inset 0 1px 0 rgba(255,255,255,.45);
}
.call-btn:hover { transform: translateY(-2px); box-shadow: 0 18px 38px -10px var(--accent), inset 0 1px 0 rgba(255,255,255,.5); }
.call-btn:active { transform: translateY(0); }
.ghost-btn { border: 1.5px solid rgba(255,255,255,.30); color: #fff; background: rgba(255,255,255,.04); }
.ghost-btn:hover { border-color: #fff; background: rgba(255,255,255,.10); }
.wa-btn { background: #1faf54; color: #fff; box-shadow: 0 10px 26px -10px #1faf54; }
.wa-btn:hover { transform: translateY(-2px); }
.section .ghost-btn { border-color: var(--line-strong); color: var(--ink); background: var(--card); }
.section .ghost-btn:hover { border-color: var(--accent); color: var(--accent); }
.icon { width: 1.05em; height: 1.05em; flex: none; }

/* ---------- Sub nav ---------- */
.nav-shell { background: var(--paper-2); border-bottom: 1px solid var(--line); position: sticky; top: 64px; z-index: 30; }
.nav { min-height: 54px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
.nav-links { display: flex; gap: 22px; color: var(--ink-soft); font-weight: 700; font-size: .94rem; flex-wrap: wrap; }
.nav-links a { position: relative; padding: 4px 0; }
.nav-links a:hover { color: var(--accent); }
.nav-links a::after { content: ""; position: absolute; left: 0; bottom: -2px; width: 0; height: 2px; background: var(--accent); transition: width .2s ease; }
.nav-links a:hover::after { width: 100%; }

/* ---------- Hero ---------- */
.hero { position: relative; color: #f6f1e7; overflow: hidden; isolation: isolate; background: var(--brand); }
.hero::before {
  content: ""; position: absolute; inset: 0; z-index: -2;
  background-image: linear-gradient(102deg, rgba(14,12,8,.98) 0%, rgba(14,12,8,.88) 38%, rgba(14,12,8,.40) 78%, rgba(14,12,8,.62) 100%), var(--hero-image);
  background-size: cover; background-position: center; transform: scale(1.04);
}
.hero::after {
  content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none;
  background:
    radial-gradient(760px 380px at 6% -5%, color-mix(in srgb, var(--accent) 32%, transparent), transparent 68%),
    linear-gradient(to bottom, transparent 72%, var(--paper) 100%);
}
.hero-grid {
  width: min(var(--maxw), calc(100% - var(--gutter) * 2)); margin: 0 auto;
  min-height: clamp(560px, 80vh, 720px); display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(320px, .88fr);
  align-items: center; gap: 44px; padding: 76px 0 88px;
}
.eyebrow {
  display: inline-flex; gap: 9px; align-items: center; font-weight: 800;
  text-transform: uppercase; font-size: .76rem; letter-spacing: .16em;
  color: color-mix(in srgb, var(--accent) 60%, #fff);
}
.section .eyebrow { color: var(--accent); }
.live-pill {
  display: inline-flex; align-items: center; gap: 9px; padding: 8px 15px; border-radius: var(--radius-pill);
  background: rgba(28,122,78,.16); border: 1px solid rgba(54,200,130,.45); color: #c8f4da;
  font-weight: 800; font-size: .82rem; letter-spacing: .01em;
}
.live-dot { width: 9px; height: 9px; border-radius: 50%; background: #36c882; box-shadow: 0 0 0 0 rgba(54,200,130,.7); animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(54,200,130,.65); } 70% { box-shadow: 0 0 0 11px rgba(54,200,130,0); } 100% { box-shadow: 0 0 0 0 rgba(54,200,130,0); } }
h1 { font-size: clamp(2.6rem, 6.2vw, 4.5rem); line-height: 1.0; margin: 18px 0 18px; font-weight: 800; max-width: 16ch; }
.hero h1 { color: #fff; }
.hero h1 em { font-style: normal; color: var(--accent); position: relative; white-space: nowrap; }
.hero p { color: #ded6c7; font-size: 1.14rem; max-width: 56ch; }
.hero-badges { display: flex; gap: 10px; flex-wrap: wrap; margin: 24px 0 0; }
.hero-badge { display: inline-flex; align-items: center; gap: 7px; min-height: 36px; padding: 8px 14px; border: 1px solid rgba(255,255,255,.18); border-radius: var(--radius-pill); color: #f3ede0; background: rgba(255,255,255,.05); font-weight: 700; font-size: .85rem; }
.hero-badge svg { color: var(--accent); }
.cta-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 28px; align-items: center; }
.cta-sub { margin-top: 14px; color: #b8b0a1; font-size: .92rem; font-weight: 600; display: flex; align-items: center; gap: 8px; }

/* ---------- Hero card ---------- */
.hero-card {
  background: var(--card); color: var(--ink); border-radius: var(--radius-lg); padding: 26px;
  box-shadow: var(--shadow-lg); border: 1px solid rgba(255,255,255,.6); position: relative;
}
.hero-card::before {
  content: "Devis avant intervention"; position: absolute; top: -16px; right: 20px;
  background: var(--gold); color: #2a1f06; font-family: var(--font-display); font-weight: 800;
  font-size: .72rem; letter-spacing: .04em; padding: 7px 13px; border-radius: var(--radius-pill);
  box-shadow: 0 8px 20px -8px rgba(199,154,63,.8); transform: rotate(2.5deg);
}
.hero-card h2 { margin: 6px 0 16px; font-size: 1.28rem; }
.hero-card ul, .check-list { padding: 0; margin: 0; list-style: none; display: grid; gap: 12px; }
.hero-card li, .check-list li { display: flex; gap: 11px; align-items: flex-start; font-weight: 500; }
.hero-card li::before, .check-list li::before {
  content: ""; flex: none; width: 22px; height: 22px; margin-top: 1px; border-radius: 50%;
  background: color-mix(in srgb, var(--ok) 14%, white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231c7a4e' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='20 6 9 17 4 12'/%3E%3C/svg%3E") center / 13px no-repeat;
}
.hero-meta { border-top: 1px solid var(--line); margin-top: 20px; padding-top: 18px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.hero-meta strong { display: block; font-family: var(--font-display); font-size: 1.55rem; color: var(--ink); line-height: 1; }
.hero-meta span { color: var(--ink-soft); font-weight: 600; font-size: .85rem; }

/* ---------- Reassurance strip ---------- */
.reassure { background: var(--brand-2); color: #e9e2d4; }
.reassure-grid { display: grid; grid-template-columns: repeat(4, 1fr); }
.reassure-item { display: flex; gap: 12px; align-items: center; padding: 18px 22px; border-right: 1px solid rgba(255,255,255,.08); }
.reassure-item:last-child { border-right: 0; }
.reassure-item svg { color: var(--accent); flex: none; }
.reassure-item b { display: block; color: #fff; font-family: var(--font-display); font-size: 1rem; }
.reassure-item span { font-size: .84rem; color: #b6ae9f; }

/* ---------- Sections ---------- */
.section { padding: clamp(56px, 8vw, 92px) 0; position: relative; }
.section.alt { background: var(--paper-2); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.section.dark { background: var(--brand); color: #ece5d7; }
.section.dark h2, .section.dark h3 { color: #fff; }
.section.dark p { color: #c4bcab; }
.section-head { max-width: 64ch; margin-bottom: 40px; }
.section-head.center { margin-left: auto; margin-right: auto; text-align: center; }
.section h2 { font-size: clamp(2rem, 4.2vw, 2.85rem); line-height: 1.06; margin: 0 0 14px; }
.section p { color: var(--ink-soft); }
.lead { font-size: 1.12rem; }

/* ---------- Grids & cards ---------- */
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 26px; align-items: start; }
.grid-4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; }
.card {
  border: 1px solid var(--line); border-radius: var(--radius-lg); background: var(--card);
  padding: 26px; box-shadow: var(--shadow-sm); transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--line-strong); }
.card h2 { font-size: 1.45rem; margin: 0 0 10px; }

/* ---------- Cas d'interventions réels ---------- */
.case-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.case-card {
  border: 1px solid var(--line); border-left: 3px solid var(--accent); border-radius: var(--radius-lg);
  background: var(--card); padding: 22px 24px; box-shadow: var(--shadow-sm);
  display: grid; gap: 10px; align-content: start;
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.case-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.case-meta { display: flex; align-items: center; gap: 7px; margin: 0; font-weight: 700; color: var(--ink); font-size: .9rem; }
.case-meta svg { color: var(--accent); flex: none; width: 17px; height: 17px; }
.case-line { margin: 0; color: var(--ink-soft); line-height: 1.5; }
.case-line strong {
  display: block; font-size: .72rem; letter-spacing: .04em; text-transform: uppercase;
  color: var(--accent); font-weight: 800; margin-bottom: 2px;
}
.card h3 { margin: 0 0 8px; font-size: 1.22rem; }
.card-number {
  display: inline-grid; place-items: center; width: 46px; height: 46px; border-radius: 13px;
  background: var(--brand); color: var(--accent); font-family: var(--font-display); font-weight: 800;
  font-size: 1.25rem; margin-bottom: 16px; box-shadow: var(--shadow-sm);
}
.service-card { position: relative; overflow: hidden; }
.service-card .ico {
  width: 52px; height: 52px; border-radius: 14px; display: grid; place-items: center; margin-bottom: 16px;
  background: color-mix(in srgb, var(--accent) 12%, white); color: var(--accent);
}
.service-card .go { margin-top: 16px; display: inline-flex; align-items: center; gap: 7px; font-weight: 800; color: var(--accent); }
.service-card:hover .go { gap: 11px; }

/* ---------- Trust band ---------- */
.trust-band { background: var(--card); border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.trust-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0; }
.trust-item { padding: 30px 26px; border-right: 1px solid var(--line); }
.trust-item:last-child { border-right: 0; }
.trust-item .ti-ico { width: 38px; height: 38px; border-radius: 10px; display: grid; place-items: center; background: color-mix(in srgb, var(--accent) 12%, white); color: var(--accent); margin-bottom: 14px; }
.trust-item strong { display: block; margin-bottom: 5px; font-family: var(--font-display); font-size: 1.05rem; color: var(--ink); }
.trust-item span { color: var(--ink-soft); font-size: .92rem; }

/* ---------- Reviews ---------- */
.review-card { border: 1px solid var(--line); border-radius: var(--radius-lg); background: var(--card); padding: 26px; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 14px; }
.stars { display: inline-flex; gap: 2px; color: var(--gold); }
.review-card p { font-size: 1.05rem; color: var(--ink); margin: 0; }
.review-meta { display: flex; align-items: center; gap: 12px; margin-top: auto; }
.review-avatar { width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center; background: var(--brand); color: var(--accent); font-family: var(--font-display); font-weight: 800; }
.review-meta b { display: block; font-family: var(--font-display); }
.review-meta span { color: var(--ink-soft); font-size: .86rem; }

/* ---------- Panels ---------- */
.split-panel {
  background: linear-gradient(150deg, var(--brand), var(--brand-2)); color: #ece5d7;
  border-radius: var(--radius-lg); padding: 34px; box-shadow: var(--shadow-md);
}
.split-panel h2 { color: #fff; }
.split-panel p { color: #c4bcab; }
.cta-panel {
  background: var(--brand); color: #fff; border-radius: var(--radius-lg); padding: 38px;
  display: flex; align-items: center; justify-content: space-between; gap: 26px; position: relative; overflow: hidden;
  box-shadow: var(--shadow-lg);
}
.cta-panel::before { content: ""; position: absolute; inset: 0; background: radial-gradient(500px 240px at 100% 0%, color-mix(in srgb, var(--accent) 32%, transparent), transparent 70%); pointer-events: none; }
.cta-panel h2 { color: #fff; margin: 0; position: relative; }
.cta-panel p { color: #c4bcab; margin: 8px 0 0; position: relative; }
.cta-panel .call-btn { position: relative; }

/* ---------- Pills ---------- */
.pill-row { display: flex; gap: 9px; flex-wrap: wrap; margin-top: 18px; }
.pill { display: inline-flex; align-items: center; border: 1px solid var(--line-strong); border-radius: var(--radius-pill); padding: 8px 14px; color: var(--ink-soft); background: var(--card); font-weight: 700; font-size: .9rem; transition: all .16s ease; }
a.pill:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }
.priority-1 { border-color: color-mix(in srgb, var(--accent) 50%, white); color: var(--ink); background: color-mix(in srgb, var(--accent) 9%, white); font-weight: 800; }
.priority-2 { border-color: color-mix(in srgb, var(--secondary) 40%, white); color: var(--ink); background: color-mix(in srgb, var(--secondary) 8%, white); }

/* ---------- Pricing ---------- */
.price-table { width: 100%; border-collapse: separate; border-spacing: 0; overflow: hidden; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--card); box-shadow: var(--shadow-sm); }
.price-table th, .price-table td { padding: 18px 22px; border-bottom: 1px solid var(--line); text-align: left; }
.price-table tr:last-child td { border-bottom: 0; }
.price-table th { background: var(--brand); color: #fff; font-family: var(--font-display); font-size: .98rem; }
.price-table td { font-weight: 500; }
.price-table tbody tr:last-child td { border-bottom: 0; }
.price-table tbody tr:hover td { background: var(--paper); }
.price-table td:last-child, .price-table th:last-child { text-align: right; font-weight: 800; font-family: var(--font-display); color: var(--ink); }
.notice { border-left: 4px solid var(--accent); padding: 18px 20px; background: color-mix(in srgb, var(--accent) 7%, white); border-radius: 12px; color: #6b3410; margin-top: 18px; font-weight: 500; }

/* ---------- FAQ ---------- */
.faq details { border: 1px solid var(--line); border-radius: var(--radius); background: var(--card); padding: 4px 22px; margin-bottom: 12px; transition: border-color .2s ease, box-shadow .2s ease; }
.faq details[open] { border-color: var(--line-strong); box-shadow: var(--shadow-sm); }
.faq summary { cursor: pointer; font-family: var(--font-display); font-weight: 700; font-size: 1.08rem; list-style: none; padding: 16px 0; display: flex; justify-content: space-between; align-items: center; gap: 14px; }
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; font-size: 1.6rem; color: var(--accent); font-weight: 400; transition: transform .2s ease; line-height: 1; }
.faq details[open] summary::after { transform: rotate(45deg); }
.faq details p { padding-bottom: 18px; margin: 0; color: var(--ink-soft); }

/* ---------- Service quick links ---------- */
.service-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 16px; }
.service-links a { border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; background: var(--paper-2); font-weight: 800; display: flex; align-items: center; justify-content: space-between; transition: all .16s ease; }
.service-links a::after { content: "→"; color: var(--accent); }
.service-links a:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-1px); }

/* ---------- Footer ---------- */
.footer { background: var(--brand); color: #b8b0a1; padding: 56px 0 40px; }
.footer .wrap { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 34px; }
.footer strong { color: #fff; font-family: var(--font-display); }
.footer a { color: inherit; transition: color .15s ease; }
.footer a:hover { color: var(--accent); }
.footer-links { display: grid; gap: 9px; margin-top: 12px; }
.footer .brand { margin-bottom: 14px; }
.footer-bottom { border-top: 1px solid rgba(255,255,255,.08); margin-top: 34px; padding-top: 22px; font-size: .85rem; color: #8d8576; }

/* ---------- Mobile sticky bar ---------- */
.mobile-bar { display: none; }
@media (min-width: 600px) { .top-phone { display: block; } }
@media (max-width: 980px) {
  .reassure-grid { grid-template-columns: repeat(2, 1fr); }
  .reassure-item:nth-child(2) { border-right: 0; }
  .footer .wrap { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 880px) {
  body { font-size: 16px; }
  .topbar-inner { min-height: 58px; }
  .nav-shell { top: 58px; }
  .grid-4, .grid-3, .grid-2, .trust-grid, .case-grid { grid-template-columns: 1fr; }
  .trust-item { border-right: 0; border-bottom: 1px solid var(--line); }
  .trust-item:last-child { border-bottom: 0; }
  .hero-grid { grid-template-columns: 1fr; min-height: auto; padding: 44px 0 40px; gap: 32px; }
  .cta-panel { align-items: flex-start; flex-direction: column; }
  .nav-shell { display: none; }
  .footer { padding-bottom: 96px; }
  .footer .wrap { grid-template-columns: 1fr; }
  .mobile-bar {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
    position: fixed; left: 10px; right: 10px; bottom: 10px; z-index: 60;
    padding: 10px; background: color-mix(in srgb, var(--brand) 94%, transparent);
    backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,.12); border-radius: 18px;
    box-shadow: 0 20px 50px -12px rgba(0,0,0,.5);
  }
  .mobile-bar .call-btn, .mobile-bar .wa-btn { width: 100%; min-height: 52px; font-size: 1rem; }
}
@media (max-width: 600px) {
  .top-actions .ghost-btn { display: none; }
  .hero-card::before { right: 14px; }
}
/* ---------- Detail & advice cards ---------- */
.detail-card .ico { width: 48px; height: 48px; border-radius: 13px; display: grid; place-items: center; margin-bottom: 14px; background: color-mix(in srgb, var(--accent) 12%, white); color: var(--accent); }
.detail-card h3 { font-size: 1.18rem; }
.advice-card { border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: var(--radius); background: var(--card); padding: 22px 24px; box-shadow: var(--shadow-sm); }
.advice-card h3 { margin: 0 0 8px; font-size: 1.12rem; display: flex; align-items: center; gap: 9px; }
.advice-card h3::before { content: "!"; flex: none; width: 26px; height: 26px; border-radius: 50%; display: grid; place-items: center; background: color-mix(in srgb, var(--accent) 14%, white); color: var(--accent); font-family: var(--font-display); font-weight: 800; font-size: .95rem; }
.advice-card p { margin: 0; color: var(--ink-soft); }

/* ---------- Urgency bar ---------- */
.urgency-bar { background: linear-gradient(90deg, var(--accent), color-mix(in srgb, var(--accent) 62%, var(--gold))); color: #fff; }
.urgency-inner { display: flex; align-items: center; justify-content: center; gap: 16px; min-height: 40px; padding: 7px 0; flex-wrap: wrap; }
.urgency-text { display: inline-flex; align-items: center; gap: 8px; font-weight: 700; font-size: .92rem; letter-spacing: .005em; }
.urgency-text svg { width: 1.05em; height: 1.05em; }
.urgency-call { display: inline-flex; align-items: center; gap: 7px; font-weight: 800; font-size: .92rem; padding: 4px 13px; border-radius: var(--radius-pill); background: rgba(0,0,0,.22); color: #fff; }
.urgency-call:hover { background: rgba(0,0,0,.34); }

/* ---------- Proof gallery ---------- */
.proof-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
.proof-card { position: relative; border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--line); box-shadow: var(--shadow-sm); aspect-ratio: 4 / 3; background: var(--brand); }
.proof-card img { width: 100%; height: 100%; object-fit: cover; transition: transform .4s ease; }
.proof-card:hover img { transform: scale(1.06); }
.proof-card figcaption { position: absolute; left: 0; right: 0; bottom: 0; padding: 26px 16px 14px; color: #fff; font-weight: 700; font-size: .98rem; background: linear-gradient(to top, rgba(10,8,5,.85), transparent); }
.proof-tag { position: absolute; top: 12px; left: 12px; z-index: 2; background: rgba(10,8,5,.62); color: #fff; font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; padding: 5px 10px; border-radius: var(--radius-pill); backdrop-filter: blur(4px); }

/* ---------- Quartiers / zones ---------- */
.zone-head { display: flex; align-items: baseline; justify-content: space-between; gap: 18px; flex-wrap: wrap; }
.zone-chips { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 8px; }
.zone-chip {
  display: inline-flex; align-items: center; gap: 8px; padding: 11px 16px; border-radius: 12px;
  border: 1px solid var(--line-strong); background: var(--card); color: var(--ink); font-weight: 700;
  box-shadow: var(--shadow-sm); transition: all .16s ease;
}
.zone-chip svg { width: 1em; height: 1em; color: var(--accent); }
.zone-chip:hover { border-color: var(--accent); color: var(--accent); transform: translateY(-2px); }
.zone-note { margin-top: 18px; color: var(--ink-soft); font-size: .95rem; }

/* ---------- Callback form ---------- */
.cb-grid { align-items: center; }
.cb-form {
  background: var(--card); border: 1px solid var(--line); border-radius: var(--radius-lg);
  padding: 28px; box-shadow: var(--shadow-md); display: grid; gap: 16px;
  position: relative; overflow: hidden;
}
.cb-form::before { content: ""; position: absolute; left: 0; top: 0; height: 5px; width: 100%; background: linear-gradient(90deg, var(--accent), var(--gold)); }
.cb-field { display: grid; gap: 6px; }
.cb-field label { font-weight: 700; font-size: .9rem; color: var(--ink); }
.cb-form input, .cb-form textarea {
  font-family: var(--font-body); font-size: 1rem; color: var(--ink);
  padding: 13px 15px; border: 1.5px solid var(--line-strong); border-radius: 12px;
  background: var(--paper-2); transition: border-color .16s ease, box-shadow .16s ease; width: 100%;
}
.cb-form input:focus, .cb-form textarea:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 4px var(--ring); background: #fff; }
.cb-form textarea { resize: vertical; min-height: 84px; }
.cb-form input.cb-invalid, .cb-form textarea.cb-invalid { border-color: #c0392b; box-shadow: 0 0 0 4px rgba(192,57,43,.14); }
.cb-submit { width: 100%; min-height: 54px; font-size: 1.05rem; background: #1faf54; box-shadow: 0 14px 30px -12px #1faf54; }
.cb-submit:hover { transform: translateY(-2px); }
.cb-hint { margin: 0; font-size: .82rem; color: var(--ink-soft); text-align: center; }

@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; transition: none !important; scroll-behavior: auto !important; }
}
"""
    return css_text.replace("__ACCENT__", accent).replace("__SECONDARY__", secondary)


def layout(title: str, description: str, path: str, body: str, schema: dict, build: BuildConfig) -> str:
    canonical = page_url(path, build)
    schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
    primary_key = build.primary_service_key or build.service_keys[0]
    image = str(SERVICES[primary_key]["image"])
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{esc(canonical)}">
  <meta name="theme-color" content="#17140f">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://images.unsplash.com">
  <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700;12..96,800&family=Hanken+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:site_name" content="{esc(BUSINESS["name"])}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:image" content="{esc(image)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <style>{css(build)}</style>
  <script type="application/ld+json">{schema_json}</script>
</head>
<body>
<a class="skip-link" href="#contenu">Aller au contenu</a>
{body}
</body>
</html>
"""


ICONS = {
    "phone": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>',
    "clock": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "shield": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/></svg>',
    "tag": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.59 13.41 12 22l-9-9V3h10l7.59 7.59a2 2 0 0 1 0 2.82z"/><circle cx="7.5" cy="7.5" r="1.5"/></svg>',
    "pin": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "key": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/></svg>',
    "drop": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2.69 17.66 8.35a8 8 0 1 1-11.31 0z"/></svg>',
    "pipe": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4v6a4 4 0 0 0 4 4h4"/><path d="M20 20v-6a4 4 0 0 0-4-4h-4"/><path d="M2 4h4"/><path d="M18 20h4"/></svg>',
    "check": '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>',
    "star": '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12 2l2.9 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l7.1-1.01z"/></svg>',
    "wa": '<svg class="icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.945C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 0 1 8.413 3.488 11.82 11.82 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.82 9.82 0 0 0 1.523 5.26l-.999 3.648 3.736-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>',
}


def icon(name: str) -> str:
    return ICONS.get(name, "")


def whatsapp_link() -> str:
    return f'https://wa.me/{esc(BUSINESS["whatsapp"])}?text=Bonjour%20{esc(BUSINESS["name"])},%20j%27ai%20besoin%20d%27une%20intervention'


def header(current_phone_display: str, current_phone_href: str, build: BuildConfig) -> str:
    service_links = "\n      ".join(
        f'<a href="{example_service_path(key, build)}">{esc(SERVICES[key]["label"])}</a>' for key in build.service_keys
    )
    return f"""
<div class="urgency-bar">
  <div class="wrap urgency-inner">
    <span class="urgency-text">{icon("clock")} {esc(URGENCY_BANNER)}</span>
    <a class="urgency-call js-call-track" href="tel:{esc(current_phone_href)}">{icon("phone")} {esc(current_phone_display)}</a>
  </div>
</div>
<div class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="/"><span class="brand-mark">S</span><span>{esc(BUSINESS["name"])}<small>Urgence 24h/24 · 7j/7</small></span></a>
    <div class="top-actions">
      <div class="top-phone"><span>Appel direct</span><strong>{esc(current_phone_display)}</strong></div>
      <a class="ghost-btn" href="{whatsapp_link()}" target="_blank" rel="noopener">{icon("wa")} WhatsApp</a>
      <a class="call-btn js-call-track" href="tel:{esc(current_phone_href)}">{icon("phone")} Appeler</a>
    </div>
  </div>
</div>
<div class="nav-shell">
  <nav class="nav" aria-label="Navigation principale">
    <div class="nav-links">
      {service_links}
      <a href="/zones/">Villes desservies</a>
      <a href="#tarifs">Tarifs</a>
    </div>
    <div class="nav-links">
      <a href="#avis">Avis</a>
      <a href="#faq">Questions</a>
      <a href="#contact">Contact</a>
    </div>
  </nav>
</div>
"""


def footer(current_phone_display: str, current_phone_href: str, build: BuildConfig) -> str:
    scope = service_names(build)
    return f"""
<footer id="contact" class="footer">
  <div class="wrap">
    <div>
      <a class="brand" href="/"><span class="brand-mark">S</span><span>{esc(BUSINESS["name"])}</span></a>
      <p style="margin-top:4px;max-width:42ch">{esc(scope.capitalize())} en urgence, avec qualification de la demande au téléphone et devis annoncé avant toute intervention.</p>
      <div style="margin-top:10px;color:#8d8576">{esc(BUSINESS["address"])}</div>
    </div>
    <div>
      <strong>Contact direct</strong>
      <div class="footer-links">
        <a href="tel:{esc(current_phone_href)}">{esc(current_phone_display)}</a>
        <a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a>
        <a href="{whatsapp_link()}" target="_blank" rel="noopener">WhatsApp</a>
      </div>
      <div style="margin-top:16px">
      <a class="call-btn js-call-track" href="tel:{esc(current_phone_href)}">{icon("phone")} Appeler {esc(current_phone_display)}</a>
      </div>
    </div>
    <div>
      <strong>Informations</strong>
      <div class="footer-links">
        <a href="/zones/">Villes desservies</a>
        <a href="/mentions-legales/">Mentions légales</a>
        <a href="/confidentialite/">Confidentialité</a>
      </div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    © {GENERATED_DATE[:4]} {esc(BUSINESS["name"])} — Interventions {esc(scope)} en France et dans le canton de Genève. Tarifs indicatifs confirmés avant intervention.
  </div>
</footer>
<div class="mobile-bar">
  <a class="wa-btn" href="{whatsapp_link()}" target="_blank" rel="noopener">{icon("wa")} WhatsApp</a>
  <a class="call-btn js-call-track" href="tel:{esc(current_phone_href)}">{icon("phone")} Appeler</a>
</div>
<script>
document.querySelectorAll('.js-call-track').forEach(function(link) {{
  link.addEventListener('click', function() {{
    if (window.gtag) {{
      window.gtag('event', 'phone_call_click', {{
        event_category: 'lead',
        event_label: window.location.pathname
      }});
    }}
  }});
}});
(function() {{
  var WA = "{esc(BUSINESS["whatsapp"])}";
  document.querySelectorAll('.js-callback').forEach(function(form) {{
    form.addEventListener('submit', function(e) {{
      e.preventDefault();
      var name = form.querySelector('[name=name]');
      var phone = form.querySelector('[name=phone]');
      var need = form.querySelector('[name=need]');
      var ok = true;
      [name, phone].forEach(function(f) {{
        if (!f.value.trim()) {{ f.classList.add('cb-invalid'); ok = false; }}
        else {{ f.classList.remove('cb-invalid'); }}
      }});
      if (!ok) {{ (name.value.trim() ? phone : name).focus(); return; }}
      var city = form.getAttribute('data-city') || '';
      var service = form.getAttribute('data-service') || 'intervention';
      var msg = "Bonjour, je suis " + name.value.trim() + " (" + phone.value.trim() + ")."
        + " Demande de rappel pour " + service + (city ? " à " + city : "") + "."
        + (need.value.trim() ? " Détail : " + need.value.trim() : "");
      if (window.gtag) {{
        window.gtag('event', 'callback_request', {{ event_category: 'lead', event_label: service + ' - ' + city }});
      }}
      window.open('https://wa.me/' + WA + '?text=' + encodeURIComponent(msg), '_blank', 'noopener');
    }});
  }});
}})();
</script>
"""


def local_business_schema(
    title: str,
    description: str,
    path: str,
    city: City | None,
    service_key: str | None,
    build: BuildConfig,
) -> dict:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    country = "FR"
    if city:
        phone_display, phone_href = phone_for(city)
        country = city.country
    service = SERVICES[service_key] if service_key else SERVICES["serrurier"]
    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": service["schema_type"],
                "@id": f"{page_url(path, build)}#business",
                "name": BUSINESS["name"],
                "image": service.get("image"),
                "url": page_url(path, build),
                "telephone": phone_display,
                "email": BUSINESS["email"],
                "priceRange": "€€",
                "contactPoint": {
                    "@type": "ContactPoint",
                    "telephone": phone_href,
                    "contactType": "customer service",
                    "areaServed": "FR, CH",
                    "availableLanguage": ["fr"],
                },
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": BUSINESS["address"],
                    "addressCountry": country,
                },
                "openingHoursSpecification": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "opens": "00:00",
                    "closes": "23:59",
                },
            },
            {
                "@type": "WebPage",
                "@id": f"{page_url(path, build)}#webpage",
                "url": page_url(path, build),
                "name": title,
                "description": description,
                "isPartOf": {"@type": "WebSite", "name": BUSINESS["name"], "url": build.site_url},
            },
            {
                "@type": "BreadcrumbList",
                "@id": f"{page_url(path, build)}#breadcrumb",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Accueil",
                        "item": build.site_url.rstrip("/") + "/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": title,
                        "item": page_url(path, build),
                    },
                ],
            },
        ],
    }
    if city:
        schema["@graph"][0]["areaServed"] = {"@type": "City", "name": city.name}
    if city and service_key:
        schema["@graph"].append(
            {
                "@type": "Service",
                "@id": f"{page_url(path, build)}#service",
                "serviceType": f"{service['label']} {service['plural']}",
                "name": f"{service['label']} à {city.name}",
                "description": str(service["short"]),
                "provider": {"@id": f"{page_url(path, build)}#business"},
                "areaServed": {"@type": "City", "name": city.name},
                "availableChannel": {
                    "@type": "ServiceChannel",
                    "servicePhone": phone_href,
                    "availableLanguage": ["fr"],
                },
                "hoursAvailable": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                    "opens": "00:00",
                    "closes": "23:59",
                },
            }
        )
        cases = SERVICE_LOCAL_CASES[service_key]
        faq_question, faq_answer = cases["faq"]
        schema["@graph"].append(
            {
                "@type": "FAQPage",
                "@id": f"{page_url(path, build)}#faq",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"Intervenez-vous à {city.name} ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Oui, les demandes sur {city.name} sont qualifiées par téléphone avant déplacement afin de confirmer le secteur, le délai possible et les conditions.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": "Le devis est-il annoncé avant intervention ?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Oui. Le prix dépend de l'accès, de l'horaire, du matériel et de la complexité. Il doit être confirmé avant le début des travaux.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": faq_question,
                        "acceptedAnswer": {"@type": "Answer", "text": faq_answer},
                    },
                    *[
                        {
                            "@type": "Question",
                            "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a},
                        }
                        for q, a in EXTRA_FAQ.get(service_key, [])
                    ],
                ],
            }
        )
    return schema


def service_links_for_city(city: City, build: BuildConfig, exclude_service_key: str | None = None) -> str:
    links = []
    for key in build.service_keys:
        if key == exclude_service_key:
            continue
        service = SERVICES[key]
        links.append(f'<a href="{service_path(city, key, build)}">{esc(service["label"])} à {esc(city.name)}</a>')
    if not links:
        return ""
    return '<div class="service-links">' + "\n".join(links) + "</div>"


GENERIC_LOCAL_NOTES = [
    "À {city}, les interventions couvrent le centre comme les secteurs résidentiels alentour ; préciser le quartier et l'accès au téléphone permet d'arriver plus vite.",
    "{city} est rattachée au bassin {zone} : selon la disponibilité d'une équipe proche, le délai d'intervention est annoncé dès l'appel.",
    "À {city}, qu'il s'agisse d'un logement, d'un commerce ou d'un local professionnel, la demande est qualifiée avant déplacement pour confirmer le secteur et les conditions.",
    "Située en {region}, {city} bénéficie d'une couverture locale avec un numéro adapté et un devis annoncé avant toute intervention.",
]


def local_seo_for(city: City, nearby: list[City]) -> dict[str, object]:
    if city.slug in LOCAL_SEO:
        return LOCAL_SEO[city.slug]
    nearby_names = [item.name for item in nearby[:6]]
    if len(nearby_names) < 3:
        nearby_names = [city.zone, city.region, city.name]
    note = pick(city.slug, GENERIC_LOCAL_NOTES, "note").format(
        city=city.name, zone=city.zone, region=city.region
    )
    return {"micro_areas": nearby_names, "local_note": note}


def local_enrichment_section(city: City, service_key: str, nearby: list[City]) -> str:
    local = local_seo_for(city, nearby)
    cases = SERVICE_LOCAL_CASES[service_key]
    case_items = "\n".join(f"<li>{esc(item)} à {esc(city.name)} ou dans un secteur proche</li>" for item in cases["cases"])
    nearby_sentence = ", ".join(item.name for item in nearby[:5])
    if nearby_sentence:
        nearby_text = f"Le maillage local relie aussi {esc(city.name)} aux communes proches comme {esc(nearby_sentence)}."
    else:
        nearby_text = f"Le maillage local relie cette page au bassin {esc(city.zone)}."
    return f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Repères locaux à {esc(city.name)}</h2>
        <p>{esc(local["local_note"])}</p>
        <p style="margin-bottom:0">{nearby_text}</p>
      </div>
      <div class="card">
        <h2>{esc(cases["title"])}</h2>
        <ul class="check-list">{case_items}</ul>
      </div>
    </div>
  </section>
"""


def local_cases_section(city: City, service_key: str) -> str:
    """Section « Exemples d'interventions » à partir de cas RÉELS collectés.

    Renvoie une chaîne vide tant qu'aucun cas réel n'est renseigné pour la ville
    et le métier : on ne fabrique jamais de faux chantier."""
    cases = CITY_CASES.get(city.slug, {}).get(service_key, [])
    if not cases:
        return ""
    ordered = take(city.slug, list(cases), len(cases), "cases")
    cards = []
    for case in ordered:
        rows = []
        if case.get("secteur"):
            rows.append(
                f'<p class="case-meta">{icon("pin")}<span>{esc(case["secteur"])}</span></p>'
            )
        rows.append(
            f'<p class="case-line"><strong>Situation</strong>{esc(case["situation"])}</p>'
        )
        if case.get("solution"):
            rows.append(
                f'<p class="case-line"><strong>Intervention</strong>{esc(case["solution"])}</p>'
            )
        if case.get("delai"):
            rows.append(
                f'<p class="case-line"><strong>Délai constaté</strong>{esc(case["delai"])}</p>'
            )
        cards.append(f'<article class="case-card">{"".join(rows)}</article>')
    return f"""
  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Interventions à {esc(city.name)}</span>
        <h2>Exemples d'interventions récentes à {esc(city.name)}</h2>
        <p>Des situations réellement traitées dans le secteur, présentées sans donnée personnelle, adresse précise ni élément identifiant.</p>
      </div>
      <div class="case-grid">{"".join(cards)}</div>
    </div>
  </section>
"""


def trust_band(service: dict[str, object]) -> str:
    items = [str(item) for item in service["trust_points"]]
    band_icons = ["shield", "tag", "clock", "pin"]
    cards = "\n".join(
        f"""
        <div class="trust-item">
          <div class="ti-ico">{icon(band_icons[index % len(band_icons)])}</div>
          <strong>{esc(item)}</strong>
          <span>Point vérifié avant ou pendant l'intervention.</span>
        </div>
        """
        for index, item in enumerate(items[:4])
    )
    return f"""
  <section class="trust-band" aria-label="Garanties d'intervention">
    <div class="wrap trust-grid">{cards}</div>
  </section>
"""


def reassurance_strip(phone_display: str, service_key: str | None = None) -> str:
    third = SERVICE_REASSURANCE.get(
        service_key or "",
        ("shield", "Sans surprise", "Conditions claires annoncées avant intervention"),
    )
    items = [
        ("clock", "Disponible 24h/24", "Soir, week-end et jours fériés"),
        ("phone", "Devis au téléphone", "Prix annoncé avant déplacement"),
        third,
        ("pin", "Artisan de proximité", "Numéro local France et Genève"),
    ]
    cells = "\n".join(
        f"""
        <div class="reassure-item">
          {icon(ic)}
          <div><b>{esc(title)}</b><span>{esc(sub)}</span></div>
        </div>
        """
        for ic, title, sub in items
    )
    return f"""
  <section class="reassure" aria-label="Engagements">
    <div class="wrap reassure-grid">{cells}</div>
  </section>
"""


def reviews_section(city: City, service: dict[str, object], service_key: str) -> str:
    label = str(service["label"]).lower()
    reviews = take(city.slug, SERVICE_REVIEWS.get(service_key, SERVICE_REVIEWS["serrurier"]), 3, "reviews")
    cards = "\n".join(
        f"""
        <figure class="review-card">
          <div class="stars" aria-label="Note 5 sur 5">{icon("star") * 5}</div>
          <blockquote><p>« {esc(text)} »</p></blockquote>
          <figcaption class="review-meta">
            <span class="review-avatar" aria-hidden="true">{esc(who[0])}</span>
            <span><b>{esc(who)} · {esc(context)}</b><span>{esc(city.name)} et secteur</span></span>
          </figcaption>
        </figure>
        """
        for text, who, context in reviews
    )
    return f"""
  <section id="avis" class="section">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Retours clients</span>
        <h2>Ce que disent les clients après une intervention {esc(label)}</h2>
        <p>Exemples représentatifs des retours reçus pour ce type d'intervention. Les avis vérifiés sont collectés après chaque dépannage réussi à {esc(city.name)} et dans le secteur proche.</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>
"""


def proof_section(city: City, service: dict[str, object], service_key: str) -> str:
    images = PROOF_IMAGES.get(service_key, [])
    if not images:
        return ""
    label = str(service["label"]).lower()
    tag = '<span class="proof-tag">Illustration</span>' if PROOF_ILLUSTRATIVE else ""
    cards = "\n".join(
        f"""
        <figure class="proof-card">
          {tag}
          <img src="{esc(url)}" alt="{esc(caption)} — {esc(label)} à {esc(city.name)}" loading="lazy" decoding="async" width="900" height="675">
          <figcaption>{esc(caption)}</figcaption>
        </figure>
        """
        for url, caption in images
    )
    intro = (
        "Photos d'illustration des prestations. Les clichés de nos interventions réelles à "
        f"{esc(city.name)} sont ajoutés au fur et à mesure, sans élément permettant d'identifier un client."
        if PROOF_ILLUSTRATIVE
        else f"Aperçu d'interventions {esc(label)} réalisées à {esc(city.name)} et dans le secteur proche."
    )
    return f"""
  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Nos réalisations</span>
        <h2>À quoi ressemble une intervention {esc(label)}</h2>
        <p>{intro}</p>
      </div>
      <div class="proof-grid">{cards}</div>
    </div>
  </section>
"""


def quartiers_section(city: City, service_key: str, nearby: list[City], build: BuildConfig) -> str:
    local = local_seo_for(city, nearby)
    micro_areas = [str(item) for item in local["micro_areas"]]
    if not micro_areas:
        return ""
    chips = "\n".join(
        f'<a class="zone-chip" href="#rappel">{icon("pin")} {esc(area)}</a>' for area in micro_areas
    )
    nearby_chips = "".join(
        f'<a class="zone-chip" href="{service_path(c, service_key, build)}">{esc(c.name)}</a>' for c in nearby[:6]
    )
    nearby_block = (
        f'<p class="zone-note">Communes proches également couvertes :</p><div class="zone-chips">{nearby_chips}</div>'
        if nearby_chips
        else ""
    )
    return f"""
  <section class="section alt">
    <div class="wrap">
      <div class="zone-head">
        <div class="section-head" style="margin-bottom:0">
          <span class="eyebrow">{icon("pin")} Zones couvertes</span>
          <h2>Quartiers de {esc(city.name)} desservis</h2>
          <p>Une urgence dans l'un de ces secteurs ? Indiquez-le lors de votre appel ou de votre demande de rappel pour gagner du temps.</p>
        </div>
      </div>
      <div class="zone-chips">{chips}</div>
      {nearby_block}
    </div>
  </section>
"""


def detail_section(city: City, service: dict[str, object], service_key: str) -> str:
    items = reorder(city.slug, SERVICE_DETAIL.get(service_key, []), "detail")
    if not items:
        return ""
    label = str(service["label"]).lower()
    plural = str(service["plural"])
    intro = pick(city.slug, SERVICE_INTRO_VARIANTS.get(service_key, [""]), "intro")
    icons = {"serrurier": "key", "plombier": "drop", "degorgement": "pipe"}
    svc_icon = icons.get(service_key, "shield")
    cards = "\n".join(
        f"""
        <article class="card detail-card">
          <div class="ico">{icon(svc_icon)}</div>
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </article>
        """
        for title, text in items
    )
    return f"""
  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Prestations à {esc(city.name)}</span>
        <h2>Nos interventions de {esc(plural)} en détail</h2>
        <p class="lead">{esc(intro)}</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>
"""


def advice_section(city: City, service: dict[str, object], service_key: str) -> str:
    items = reorder(city.slug, SERVICE_ADVICE.get(service_key, []), "advice")
    if not items:
        return ""
    label = str(service["label"]).lower()
    cards = "\n".join(
        f"""
        <article class="advice-card">
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </article>
        """
        for title, text in items
    )
    return f"""
  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Conseils &amp; bons réflexes</span>
        <h2>Que faire avant l'arrivée du {esc(label)} à {esc(city.name)} ?</h2>
        <p>Quelques gestes simples évitent d'aggraver la situation et permettent une intervention plus rapide et moins coûteuse.</p>
      </div>
      <div class="grid-2">{cards}</div>
    </div>
  </section>
"""


def process_section(service: dict[str, object], city: City) -> str:
    steps = [(str(title), str(text)) for title, text in service["steps"]]
    cards = "\n".join(
        f"""
        <article class="card">
          <span class="card-number">{index}</span>
          <h3>{esc(title)}</h3>
          <p>{esc(text)}</p>
        </article>
        """
        for index, (title, text) in enumerate(steps, start=1)
    )
    return f"""
  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Déroulé d'intervention à {esc(city.name)}</h2>
        <p>Le but est de qualifier correctement l'urgence, d'éviter les mauvaises surprises et de garder une trace claire de ce qui est prévu.</p>
      </div>
      <div class="grid-4">{cards}</div>
    </div>
  </section>
"""


def expertise_section(city: City, service_key: str, service: dict[str, object], nearby: list[City]) -> str:
    audience = str(service["audience"])
    promise = str(service["promise"])
    value_title, value_texts = SERVICE_VALUE.get(
        service_key,
        ("Une intervention claire, du premier appel à la fin du dépannage", [str(service["promise"])]),
    )
    value_text = pick(city.slug, value_texts, "value")
    local = local_seo_for(city, nearby)
    areas = ", ".join(str(item) for item in local["micro_areas"][:4])
    return f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="split-panel">
        <h2>{esc(value_title)}</h2>
        <p>{esc(value_text)}</p>
        <p style="margin-bottom:0">Interventions pour {esc(audience)} à {esc(city.name)}.</p>
      </div>
      <div>
        <h2>Ce qui est vérifié avant déplacement</h2>
        <p>{esc(promise)}</p>
        <p>Les secteurs comme {esc(areas)} sont traités avec la même logique : comprendre l'accès, l'urgence, le matériel possible et les conditions tarifaires avant validation.</p>
      </div>
    </div>
  </section>
"""


def final_cta_section(city: City, service: dict[str, object], phone_display: str, phone_href: str) -> str:
    return f"""
  <section class="section">
    <div class="wrap">
      <div class="cta-panel">
        <div>
          <h2>Besoin d'un avis rapide à {esc(city.name)} ?</h2>
          <p>Appelez avec l'adresse, une photo si possible et une description courte du problème. Le prix est confirmé avant intervention.</p>
        </div>
        <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">Appeler {esc(phone_display)}</a>
      </div>
    </div>
  </section>
"""


def callback_form(city_name: str, service_label: str, phone_display: str, phone_href: str, anchor_id: str = "rappel") -> str:
    heading = f"Être rappelé pour une intervention à {esc(city_name)}" if city_name else "Être rappelé rapidement"
    placeholder = (
        f"Ex. {esc(service_label)} à {esc(city_name)} : décrivez en quelques mots"
        if city_name
        else "Votre ville + nature du problème en quelques mots"
    )
    uid = re.sub(r"[^a-z0-9]+", "-", f"{anchor_id}-{service_label}".lower()).strip("-")
    return f"""
  <section id="{esc(anchor_id)}" class="section alt">
    <div class="wrap grid-2 cb-grid">
      <div>
        <span class="eyebrow">{icon("phone")} Rappel gratuit</span>
        <h2>{heading}</h2>
        <p class="lead">Décrivez votre situation en deux lignes. On vous rappelle pour confirmer le créneau et le prix avant tout déplacement — sans engagement.</p>
        <ul class="check-list" style="margin-top:18px">
          <li>Réponse rapide, 7j/7</li>
          <li>Devis annoncé avant intervention</li>
          <li>Vos informations servent uniquement à vous rappeler</li>
        </ul>
        <div class="cta-sub" style="color:var(--ink-soft);margin-top:18px">{icon("clock")} Urgence immédiate ? <a href="tel:{esc(phone_href)}" class="js-call-track" style="color:var(--accent);font-weight:800">Appelez le {esc(phone_display)}</a></div>
      </div>
      <form class="cb-form js-callback" data-city="{esc(city_name)}" data-service="{esc(service_label)}" novalidate>
        <div class="cb-field">
          <label for="{uid}-name">Votre prénom</label>
          <input id="{uid}-name" name="name" type="text" autocomplete="given-name" placeholder="Prénom" required>
        </div>
        <div class="cb-field">
          <label for="{uid}-phone">Votre téléphone</label>
          <input id="{uid}-phone" name="phone" type="tel" autocomplete="tel" placeholder="06 00 00 00 00" required>
        </div>
        <div class="cb-field">
          <label for="{uid}-need">Votre besoin</label>
          <textarea id="{uid}-need" name="need" rows="3" placeholder="{placeholder}"></textarea>
        </div>
        <button type="submit" class="call-btn cb-submit">{icon("wa")} Demander un rappel</button>
        <p class="cb-hint">Le bouton ouvre WhatsApp avec votre message pré-rempli. Aucune donnée n'est stockée sur ce site.</p>
      </form>
    </div>
  </section>
"""


def service_page(city: City, service_key: str, all_cities: list[City], build: BuildConfig) -> str:
    service = SERVICES[service_key]
    phone_display, phone_href = phone_for(city)
    path = service_path(city, service_key, build)
    title = f"{service['label']} à {city.name} | {BUSINESS['name']} urgence 24/7"
    description = f"{BUSINESS['name']} : {service['short']} Intervention à {city.name} et secteur proche. Appel direct, devis avant intervention."
    nearby = [c for c in all_cities if c.zone == city.zone and c.slug != city.slug][:8]
    nearby_links = " ".join(f'<a class="pill" href="{service_path(c, service_key, build)}">{esc(c.name)}</a>' for c in nearby)
    benefits = "\n".join(f"<li>{esc(item)}</li>" for item in reorder(city.slug, service["benefits"], "benefits"))
    pricing_rows = "\n".join(
        f"<tr><td>{esc(label)}</td><td>{esc(price)}</td></tr>" for label, price in service["pricing"]
    )
    other_services = service_links_for_city(city, build, service_key)
    hero = service["hero"].format(city=city.name)
    headline = service["headline"].format(city=city.name)
    local_section = local_enrichment_section(city, service_key, nearby)
    cases_section = local_cases_section(city, service_key)
    trust_section = trust_band(service)
    expertise = expertise_section(city, service_key, service, nearby)
    process = process_section(service, city)
    final_cta = final_cta_section(city, service, phone_display, phone_href)
    reassure = reassurance_strip(phone_display, service_key)
    reviews = reviews_section(city, service, service_key)
    proof = proof_section(city, service, service_key)
    detail = detail_section(city, service, service_key)
    advice = advice_section(city, service, service_key)
    quartiers = quartiers_section(city, service_key, nearby, build)
    callback = callback_form(city.name, str(service["label"]), phone_display, phone_href)
    service_icon = {"serrurier": "key", "plombier": "drop", "degorgement": "pipe"}.get(service_key, "shield")
    extra_faq = "\n".join(
        f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        for q, a in reorder(city.slug, EXTRA_FAQ.get(service_key, []), "faq")
    )
    local_lead = pick(city.slug, SERVICE_LOCAL_LEAD, "lead").format(
        name=BUSINESS["name"], city=city.name, label=str(service["label"]).lower(), zone=city.zone, region=city.region
    )
    hero_support = pick(city.slug, HERO_SUPPORT, "herosupport").format(city=city.name)
    service_faq_question, service_faq_answer = SERVICE_LOCAL_CASES[service_key]["faq"]
    if other_services:
        related_section = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Prestations complémentaires à {esc(city.name)}</h2>
        <p>Les prestations restent séparées pour garder un message clair et des URLs exploitables par métier.</p>
        {other_services}
      </div>
      <div class="card">
        <h2>Préparer votre appel</h2>
        <p>Indiquez la ville, l'accès au logement ou au local, l'urgence exacte, les photos disponibles et l'horaire souhaité. Ces éléments permettent d'éviter un déplacement mal qualifié.</p>
      </div>
    </div>
  </section>
"""
    else:
        related_section = f"""
  <section class="section">
    <div class="wrap">
      <div class="card">
        <h2>Préparer votre appel</h2>
        <p>Indiquez la ville, l'accès au logement ou au local, l'urgence exacte, les photos disponibles et l'horaire souhaité. Ces éléments permettent d'éviter un déplacement mal qualifié.</p>
      </div>
    </div>
  </section>
"""
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('{esc(service["image"])}')">
    <div class="hero-grid">
      <div>
        <span class="live-pill"><span class="live-dot"></span>Équipe disponible maintenant · {esc(city.zone)}</span>
        <h1>{esc(service["label"])} à <em>{esc(city.name)}</em>, intervention en urgence</h1>
        <p>{esc(hero)} {esc(hero_support)}</p>
        <div class="hero-badges">
          <span class="hero-badge">{icon("tag")} Devis avant intervention</span>
          <span class="hero-badge">{icon("clock")} 24h/24 · 7j/7</span>
          <span class="hero-badge">{icon("shield")} {esc(SERVICE_REASSURANCE.get(service_key, ("", "Conditions claires"))[1])}</span>
        </div>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">{icon("phone")} Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="{whatsapp_link()}" target="_blank" rel="noopener">{icon("wa")} Envoyer une photo</a>
        </div>
        <div class="cta-sub">{icon("check")} Décrivez votre situation, recevez un prix clair, sans engagement.</div>
      </div>
      <aside class="hero-card" aria-label="Points clés">
        <div class="service-card"><div class="ico">{icon(service_icon)}</div></div>
        <h2>Votre intervention à {esc(city.name)}</h2>
        <ul>{benefits}</ul>
        <div class="hero-meta">
          <div><strong>24/7</strong><span>urgence qualifiée</span></div>
          <div><strong>Devis</strong><span>annoncé avant travaux</span></div>
        </div>
      </aside>
    </div>
  </section>

{reassure}

{trust_section}

  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <h2>{esc(service["label"])} local à {esc(city.name)}</h2>
          <p>{esc(local_lead)}</p>
        </div>
        <ul class="check-list">{benefits}</ul>
      </div>
      <div class="card">
        <h3>Zones proches couvertes</h3>
        <p>Selon la disponibilité des équipes, une intervention peut aussi être organisée dans les communes proches du même secteur.</p>
        <div class="pill-row">{nearby_links}</div>
      </div>
    </div>
  </section>

{detail}

{expertise}

{proof}

{local_section}

{cases_section}

{quartiers}

{process}

{advice}

  <section id="tarifs" class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Tarifs et devis</h2>
        <p>Les prix dépendent de l'accès, de l'horaire, du matériel et de la complexité. Le devis est annoncé avant intervention.</p>
      </div>
      <table class="price-table">
        <thead><tr><th>Prestation</th><th>Prix indicatif</th></tr></thead>
        <tbody>{pricing_rows}</tbody>
      </table>
      <p class="notice">Les tarifs sont indicatifs. Le prix final est confirmé avant toute intervention, notamment en soirée, week-end, jour férié ou lorsqu'une pièce spécifique est nécessaire.</p>
    </div>
  </section>

{reviews}

{related_section}

{callback}

{final_cta}

  <section id="faq" class="section alt faq">
    <div class="wrap">
      <div class="section-head">
        <span class="eyebrow">Questions fréquentes</span>
        <h2>Questions fréquentes à {esc(city.name)}</h2>
      </div>
      <div class="grid-2">
        <details open><summary>Intervenez-vous vraiment à {esc(city.name)} ?</summary><p>Oui, les demandes sur {esc(city.name)} sont traitées avec une priorité locale et une vérification du secteur avant déplacement.</p></details>
        <details><summary>Le devis est-il obligatoire ?</summary><p>Oui. En urgence comme sur rendez-vous, le prix doit être annoncé avant l'intervention.</p></details>
        <details><summary>{esc(service_faq_question)}</summary><p>{esc(service_faq_answer)}</p></details>
        {extra_faq}
        <details><summary>Quel numéro utiliser ?</summary><p>Utilisez un numéro local cohérent avec la zone : +41 pour Genève, 04 pour les zones France couvertes.</p></details>
      </div>
    </div>
  </section>
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, city, service_key, build)
    return layout(title, description, path, body, schema, build)


def city_page(city: City, all_cities: list[City], build: BuildConfig) -> str:
    phone_display, phone_href = phone_for(city)
    path = city_hub_path(city)
    title = f"Intervention à {city.name} | Serrurier, plombier, dégorgement Solybat"
    description = f"Solybat intervient à {city.name} en serrurerie, plomberie et dégorgement. Choisissez le service adapté : urgence serrure, fuite d'eau ou canalisation bouchée."
    nearby = [c for c in all_cities if c.zone == city.zone and c.slug != city.slug][:8]
    local = local_seo_for(city, nearby)
    sector_pills = " ".join(f'<span class="pill">{esc(area)}</span>' for area in local["micro_areas"])
    nearby_links = " ".join(f'<a class="pill" href="{city_hub_path(c)}">{esc(c.name)}</a>' for c in nearby)
    svc_icons = {"serrurier": "key", "plombier": "drop", "degorgement": "pipe"}
    service_cards = "\n".join(
        f"""
        <a class="card service-card" href="{service_path(city, service_key, build)}">
          <div class="ico">{icon(svc_icons.get(service_key, "shield"))}</div>
          <h3>{esc(service["label"])} à {esc(city.name)}</h3>
          <p>{esc(service["short"])}</p>
          <span class="go">Voir la page {esc(service["label"].lower())} {icon("check")}</span>
        </a>
        """
        for service_key in build.service_keys
        for service in [SERVICES[service_key]]
    )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="live-pill"><span class="live-dot"></span>Disponible maintenant · {esc(city.zone)}</span>
        <h1>Dépannage en urgence à <em>{esc(city.name)}</em></h1>
        <p>Serrurerie, plomberie et dégorgement : choisissez le service correspondant à votre urgence pour accéder à la page locale la plus précise et au bon numéro.</p>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">{icon("phone")} Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="#services-ville">Choisir un service</a>
        </div>
        <div class="cta-sub">{icon("check")} Un seul appel, le bon artisan pour votre situation.</div>
      </div>
      <aside class="hero-card">
        <h2>Services disponibles à {esc(city.name)}</h2>
        <ul>
          <li>Ouverture de porte et serrure bloquée</li>
          <li>Fuite d'eau et dépannage sanitaire</li>
          <li>Canalisation bouchée et camion pompe</li>
          <li>Devis confirmé avant intervention</li>
        </ul>
      </aside>
    </div>
  </section>

{reassurance_strip(phone_display)}

  <section id="services-ville" class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>Quel service cherchez-vous à {esc(city.name)} ?</h2>
        <p>Chaque métier a sa propre page locale pour répondre plus vite à l'intention de recherche.</p>
      </div>
      <div class="grid-3">{service_cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Repères locaux</h2>
        <p>{esc(local["local_note"])}</p>
        <div class="pill-row">{sector_pills}</div>
      </div>
      <div class="card">
        <h2>Communes proches</h2>
        <p>Le maillage relie {esc(city.name)} aux villes du même bassin d'intervention.</p>
        <div class="pill-row">{nearby_links}</div>
      </div>
    </div>
  </section>

{callback_form(city.name, "une intervention", phone_display, phone_href)}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, city, "serrurier", build)
    return layout(title, description, path, body, schema, build)


def home_page(cities: list[City], build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    homepage_path = "/campagnes-locales/" if build.preserve_existing_home else "/"
    p1 = [c for c in cities if c.priority == 1]

    if build.primary_service_key:
        primary = SERVICES[build.primary_service_key]
        primary_label = str(primary["label"])
        service_scope = service_names(build)
        title = f"{BUSINESS['name']} | {primary_label} urgence 24/7"
        description = f"{BUSINESS['name']} intervient en {service_scope} avec des pages locales par ville, appel direct et devis avant intervention."
        domain_scope = "la serrurerie" if build.primary_service_key == "serrurier" else "la plomberie"
        priority_links = "\n".join(
            f'<a class="pill priority-1" href="{service_path(c, build.primary_service_key, build)}">{esc(c.name)}</a>' for c in p1
        )
        home_icons = {"serrurier": "key", "plombier": "drop", "degorgement": "pipe"}
        cards = "\n".join(
            f"""
        <a class="card service-card" href="{example_service_path(key, build)}">
          <div class="ico">{icon(home_icons.get(key, "shield"))}</div>
          <h3>{esc(SERVICES[key]["label"])}</h3>
          <p>{esc(SERVICES[key]["short"])}</p>
          <span class="go">Voir un exemple à Lyon {icon("check")}</span>
        </a>
        """
            for key in build.service_keys
        )
        primary_benefits = "\n".join(f"<li>{esc(item)}</li>" for item in primary["benefits"])
        home_trust = trust_band(primary)
        home_reassure = reassurance_strip(phone_display)
        body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('{esc(primary["image"])}')">
    <div class="hero-grid">
      <div>
        <span class="live-pill"><span class="live-dot"></span>{esc(BUSINESS["name"])} · urgence locale 24/7</span>
        <h1><em>{esc(primary_label)}</em> de confiance, ville par ville</h1>
        <p>Un service dédié à {esc(domain_scope)} pour répondre vite aux demandes urgentes, ville par ville, avec une qualification claire et un prix annoncé avant déplacement.</p>
        <div class="hero-badges">
          <span class="hero-badge">{icon("pin")} Intervention locale</span>
          <span class="hero-badge">{icon("tag")} Devis avant travaux</span>
          <span class="hero-badge">{icon("phone")} Appel direct</span>
        </div>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">{icon("phone")} Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="/zones/">Voir les villes</a>
        </div>
        <div class="cta-sub">{icon("check")} Réponse immédiate, devis confirmé avant tout déplacement.</div>
      </div>
      <aside class="hero-card">
        <h2>Intervention locale</h2>
        <ul>
          {primary_benefits}
          <li>Devis annoncé avant intervention</li>
        </ul>
        <div class="hero-meta">
          <div><strong>{len(cities)}</strong><span>villes desservies</span></div>
          <div><strong>24/7</strong><span>urgence qualifiée</span></div>
        </div>
      </aside>
    </div>
  </section>

{home_reassure}

{home_trust}

  <section class="section">
    <div class="wrap">
      <div class="section-head center">
        <h2>Prestations couvertes</h2>
        <p>Les prestations sont présentées séparément pour aider l'appelant à expliquer rapidement son besoin.</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Un parcours clair pour votre urgence</h2>
        <p>L'objectif est simple : comprendre vite le problème, confirmer la zone et annoncer les conditions avant intervention.</p>
      </div>
      <div class="grid-3">
        <article class="card">
          <h3>Votre ville</h3>
          <p>Les pages locales permettent de vérifier rapidement la zone concernée et le bon numéro à utiliser.</p>
        </article>
        <article class="card">
          <h3>Votre problème</h3>
          <p>La demande est qualifiée avant déplacement pour éviter une intervention mal préparée.</p>
        </article>
        <article class="card">
          <h3>Votre accord</h3>
          <p>Le prix et les conditions doivent être confirmés avant le début de l'intervention.</p>
        </article>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="wrap">
      <div class="section-head">
        <h2>Villes couvertes en priorité</h2>
        <p>Les liens ci-dessous pointent directement vers les pages locales du site {esc(primary_label.lower())}.</p>
      </div>
      <div class="pill-row">{priority_links}</div>
    </div>
  </section>

{callback_form("", primary_label, phone_display, phone_href)}
</main>
{footer(phone_display, phone_href, build)}
"""
        schema = local_business_schema(title, description, homepage_path, None, build.primary_service_key, build)
        return layout(title, description, homepage_path, body, schema, build)

    title = f"{BUSINESS['name']} | Serrurerie, plomberie et dégorgement"
    description = "Solybat intervient en serrurerie, plomberie et dégorgement camion pompe avec des pages locales par ville et par métier."
    priority_links = "\n".join(
        f'<a class="pill priority-1" href="{service_path(c, "serrurier", build)}">{esc(c.name)}</a>' for c in p1
    )
    home_icons = {"serrurier": "key", "plombier": "drop", "degorgement": "pipe"}
    cards = "\n".join(
        f"""
        <a class="card service-card" href="{example_service_path(key, build)}">
          <div class="ico">{icon(home_icons.get(key, "shield"))}</div>
          <h3>{esc(service["label"])}</h3>
          <p>{esc(service["short"])}</p>
          <span class="go">Voir un exemple à Lyon {icon("check")}</span>
        </a>
        """
        for key in build.service_keys
        for service in [SERVICES[key]]
    )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1558002038-1091a1661116?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="live-pill"><span class="live-dot"></span>Solybat · urgence locale 24/7</span>
        <h1>Serrurier, plombier &amp; <em>dégorgement</em> près de chez vous</h1>
        <p>Un seul point d'entrée pour les urgences locales : ouverture de porte, fuite d'eau, canalisation bouchée et intervention camion pompe selon le besoin.</p>
        <div class="cta-row">
          <a class="call-btn js-call-track" href="tel:{esc(phone_href)}">{icon("phone")} Appeler {esc(phone_display)}</a>
          <a class="ghost-btn" href="/campagnes-locales/">Voir les services</a>
        </div>
        <div class="cta-sub">{icon("check")} Le bon métier, le bon numéro local, un prix annoncé avant déplacement.</div>
      </div>
      <aside class="hero-card">
        <h2>Intervention locale</h2>
        <ul>
          <li>Serrurerie, plomberie et dégorgement</li>
          <li>France et canton de Genève</li>
          <li>Appel direct sur mobile</li>
          <li>Devis annoncé avant intervention</li>
        </ul>
      </aside>
    </div>
  </section>

{reassurance_strip(phone_display)}

  <section class="section">
    <div class="wrap">
      <div class="section-head center">
        <h2>Services Solybat</h2>
        <p>Les services sont présentés séparément pour que chaque demande trouve rapidement la bonne réponse.</p>
      </div>
      <div class="grid-3">{cards}</div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap">
      <div class="section-head">
        <h2>Villes couvertes en priorité</h2>
        <p>Les grandes zones ci-dessous concentrent les demandes les plus urgentes et les volumes d'intervention les plus importants.</p>
      </div>
      <div class="pill-row">{priority_links}</div>
    </div>
  </section>

{callback_form("", "une intervention", phone_display, phone_href)}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, homepage_path, None, "serrurier", build)
    return layout(title, description, homepage_path, body, schema, build)


def zones_page(cities: list[City], build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    scope = service_names(build)
    title = f"Zones d'intervention {build.label} | {BUSINESS['name']}"
    description = f"Toutes les villes ciblées par Solybat pour les pages {scope}."
    sections: list[str] = []
    zones = sorted({(c.region, c.zone) for c in cities})
    for region, zone in zones:
        zone_cities = [c for c in cities if c.region == region and c.zone == zone]
        links = "\n".join(
            f"""
            <div class="card">
              <h3><a href="{city_hub_path(c) if build.include_city_hubs else service_path(c, build.primary_service_key or build.service_keys[0], build)}">{esc(c.name)}</a></h3>
              <p>Priorité {c.priority} · {esc(c.country)}</p>
              {service_links_for_city(c, build, build.primary_service_key if not build.include_city_hubs else None)}
            </div>
            """
            for c in zone_cities
        )
        sections.append(
            f"""
            <section class="section">
              <div class="wrap">
                <div class="section-head">
                  <h2>{esc(zone)}</h2>
                  <p>{esc(region)} · {len(zone_cities)} villes ciblées</p>
                </div>
                <div class="grid-3">{links}</div>
              </div>
            </section>
            """
        )
    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
  <section class="hero" style="--hero-image: url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1800&auto=format&fit=crop')">
    <div class="hero-grid">
      <div>
        <span class="eyebrow">Ciblage géographique</span>
        <h1>Zones d'intervention {esc(build.label)}</h1>
        <p>Liste complète des villes couvertes, avec accès direct aux pages {esc(scope)}.</p>
      </div>
      <aside class="hero-card">
        <h2>Règle d'exploitation</h2>
        <ul>
          <li>Accès rapide par ville</li>
          <li>Services séparés par domaine</li>
          <li>France et canton de Genève</li>
        </ul>
      </aside>
    </div>
  </section>
  {''.join(sections)}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema_key = build.primary_service_key or build.service_keys[0]
    schema = local_business_schema(title, description, "/zones/", None, schema_key, build)
    return layout(title, description, "/zones/", body, schema, build)


def legal_page(kind: str, build: BuildConfig) -> str:
    phone_display = BUSINESS["fr_phone_display"]
    phone_href = BUSINESS["fr_phone_href"]
    schema_key = build.primary_service_key or build.service_keys[0]
    scope = service_names(build)
    if kind == "mentions":
        path = "/mentions-legales/"
        title = f"Mentions légales | {BUSINESS['name']}"
        description = f"Mentions légales du site {BUSINESS['name']} dédié aux interventions {scope}."
        content = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <span class="eyebrow">Informations légales</span>
          <h1>Mentions légales</h1>
          <p>Cette page regroupe les informations d'édition, de contact et d'hébergement du site.</p>
        </div>
      </div>
      <div class="card">
        <h2>Éditeur du site</h2>
        <p><strong>{esc(BUSINESS["legal_name"])}</strong><br>{esc(BUSINESS["legal_form"])}<br>{esc(BUSINESS["address"])}</p>
        <p>SIRET : {esc(BUSINESS["siret"])}<br>TVA : {esc(BUSINESS["vat"])}</p>
        <p>Responsable de publication : {esc(BUSINESS["director"])}</p>
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Contact</h2>
        <p>Téléphone : <a href="tel:{esc(phone_href)}">{esc(phone_display)}</a><br>Email : <a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a></p>
      </div>
      <div class="card">
        <h2>Hébergement</h2>
        <p>{esc(BUSINESS["host_name"])}<br>{esc(BUSINESS["host_address"])}</p>
      </div>
      <div class="card">
        <h2>Activité</h2>
        <p>Le site présente des services d'intervention {esc(scope)}. Les tarifs affichés sont indicatifs et peuvent varier selon la zone, l'horaire, l'accès, le matériel et la complexité de l'intervention.</p>
      </div>
      <div class="card">
        <h2>Responsabilité</h2>
        <p>Les informations publiées sont fournies à titre informatif. Un devis ou prix confirmé doit être communiqué avant toute intervention payante.</p>
      </div>
    </div>
  </section>
"""
    elif kind == "privacy":
        path = "/confidentialite/"
        title = f"Politique de confidentialité | {BUSINESS['name']}"
        description = f"Politique de confidentialité du site {BUSINESS['name']} dédié aux interventions {scope}."
        content = f"""
  <section class="section">
    <div class="wrap grid-2">
      <div>
        <div class="section-head">
          <span class="eyebrow">Données personnelles</span>
          <h1>Politique de confidentialité</h1>
          <p>Cette page explique quelles données peuvent être transmises lors d'une demande d'intervention et comment exercer vos droits.</p>
        </div>
      </div>
      <div class="card">
        <h2>Responsable du traitement</h2>
        <p>{esc(BUSINESS["legal_name"])}<br>{esc(BUSINESS["address"])}<br><a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a></p>
      </div>
    </div>
  </section>

  <section class="section alt">
    <div class="wrap grid-2">
      <div class="card">
        <h2>Données concernées</h2>
        <p>Lors d'un appel, d'un email ou d'un message WhatsApp, vous pouvez transmettre votre nom, téléphone, adresse d'intervention, photos du problème et informations nécessaires à la qualification de l'urgence.</p>
      </div>
      <div class="card">
        <h2>Finalités</h2>
        <p>Les données servent à répondre à la demande, qualifier l'intervention, établir un devis, organiser le déplacement et assurer le suivi administratif ou commercial lié à l'intervention.</p>
      </div>
      <div class="card">
        <h2>Durée de conservation</h2>
        <p>Les données sont conservées pendant la durée nécessaire au traitement de la demande, puis selon les obligations comptables, contractuelles ou légales applicables.</p>
      </div>
      <div class="card">
        <h2>Vos droits</h2>
        <p>Vous pouvez demander l'accès, la rectification ou la suppression de vos données en écrivant à <a href="mailto:{esc(BUSINESS["email"])}">{esc(BUSINESS["email"])}</a>.</p>
      </div>
      <div class="card">
        <h2>Mesure d'audience et appels</h2>
        <p>Le site peut utiliser des outils de mesure d'audience ou de suivi de clics téléphone pour comprendre l'origine des demandes. Les paramètres exacts doivent être vérifiés lors de l'installation des tags publicitaires.</p>
      </div>
      <div class="card">
        <h2>Services tiers</h2>
        <p>Un clic WhatsApp ouvre le service WhatsApp. Les appels, emails et outils publicitaires peuvent impliquer leurs propres traitements de données.</p>
      </div>
    </div>
  </section>
"""
    else:
        raise ValueError(f"Unknown legal page: {kind}")

    body = f"""
{header(phone_display, phone_href, build)}
<main id="contenu">
{content}
</main>
{footer(phone_display, phone_href, build)}
"""
    schema = local_business_schema(title, description, path, None, schema_key, build)
    return layout(title, description, path, body, schema, build)


def sitemap(cities: list[City], build: BuildConfig) -> str:
    paths = ["/zones/", "/mentions-legales/", "/confidentialite/"]
    if build.preserve_existing_home:
        paths = ["/", "/campagnes-locales/", "/zones/", "/mentions-legales/", "/confidentialite/"]
    else:
        paths.insert(0, "/")
    for city in cities:
        if build.include_city_hubs:
            paths.append(city_hub_path(city))
        for service_key in build.service_keys:
            paths.append(service_path(city, service_key, build))

    city_paths = {city_hub_path(city) for city in cities} if build.include_city_hubs else set()
    service_paths = {service_path(city, service_key, build) for city in cities for service_key in build.service_keys}

    def sitemap_priority(path: str) -> str:
        if path == "/":
            return "1.0"
        if path in service_paths:
            return "0.8"
        if path in city_paths:
            return "0.6"
        return "0.5"

    urls = "\n".join(
        f"  <url><loc>{esc(page_url(path, build))}</loc><lastmod>{GENERATED_DATE}</lastmod><changefreq>weekly</changefreq><priority>{sitemap_priority(path)}</priority></url>"
        for path in paths
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n'


def write_ads_files(cities: list[City], build: BuildConfig) -> None:
    ads_dir = operations_root(build) / "google-ads"
    ads_dir.mkdir(parents=True, exist_ok=True)

    with (ads_dir / "negative-keywords.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["level", "match_type", "negative_keyword"])
        for keyword in NEGATIVE_KEYWORDS:
            writer.writerow(["campaign", "Phrase", keyword])

    with (ads_dir / "landing-pages.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["priority", "country", "region", "zone", "city", "service", "final_url", "recommended_phone"])
        for city in cities:
            phone_display, _ = phone_for(city)
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                writer.writerow([
                    city.priority,
                    city.country,
                    city.region,
                    city.zone,
                    city.name,
                    service["label"],
                    page_url(service_path(city, service_key, build), build),
                    phone_display,
                ])

    with (ads_dir / "keyword-plan.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["campaign", "ad_group", "match_type", "keyword", "google_ads_syntax", "final_url"])
        for city in cities:
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                campaign = f"{service['label']} - {'Genève' if city.country == 'CH' else city.region}"
                ad_group = f"{service['label']} - {city.name}"
                final_url = page_url(service_path(city, service_key, build), build)
                for template in service["keywords"]:
                    keyword = template.format(city=city.name)
                    writer.writerow([campaign, ad_group, "Phrase", keyword, f'"{keyword}"', final_url])

    with (ads_dir / "campaign-settings.md").open("w", encoding="utf-8") as f:
        f.write(f"""# Configuration Google Ads Solybat

## Structure

- 1 campagne par métier et grande zone.
- 1 groupe d'annonces par ville.
- 1 page finale par ville et métier.
- Type de correspondance : expression exacte uniquement, avec guillemets.
- Requête large interdite au lancement.

## Ciblage

- Option de lieu : Présence, personnes situées dans vos zones ciblées.
- Ne pas utiliser l'option par défaut Présence ou intérêt.
- Genève : numéro suisse +41.
- France : numéro local/régional en 04.

## Enchères

- Phase 1, 14 jours : CPC maximal ou Maximiser les clics avec plafonds.
- Phase 2 : basculer sur Maximiser les conversions puis CPA cible après 15 à 30 appels suivis.

## Tracking

- Installer le tag Google Ads / gtag.
- Déclarer les clics sur `.js-call-track` comme conversions d'appel.
- Ajouter le call tracking dynamique avant d'activer le CPA cible.
- Installer ClickCease ou équivalent avant ouverture du budget.

## A remplacer avant production

- Domaine actuel dans ce build : `{build.site_url}`
- Numéro France actuel : `{BUSINESS["fr_phone_display"]}`
- Numéro Genève actuel : `{BUSINESS["ch_phone_display"]}`
""")


def write_seo_files(cities: list[City], build: BuildConfig) -> None:
    seo_dir = operations_root(build) / "seo"
    seo_dir.mkdir(parents=True, exist_ok=True)
    priority_cities = [city for city in cities if city.priority == 1]

    with (seo_dir / "local-enrichment-priority.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "priority",
            "city",
            "service",
            "url",
            "micro_areas_to_cover",
            "proofs_to_collect",
            "photos_to_collect",
            "reviews_to_request",
            "content_status",
        ])
        for city in priority_cities:
            local = local_seo_for(city, [])
            areas = ", ".join(str(item) for item in local["micro_areas"])
            for service_key in build.service_keys:
                service = SERVICES[service_key]
                writer.writerow([
                    city.priority,
                    city.name,
                    service["label"],
                    page_url(service_path(city, service_key, build), build),
                    areas,
                    "adresse/secteur réel d'intervention, problème traité, délai annoncé, solution appliquée",
                    "photo véhicule/outillage, photo avant-après si autorisée, photo non identifiable du chantier",
                    "demander un avis client après intervention réussie",
                    "base enrichie générée, preuves réelles à ajouter",
                ])

    # Modèle de collecte des cas d'interventions réels. Le client remplit les
    # colonnes situation / secteur / solution / delai, puis on régénère avec
    #   SOLYBAT_CASES_FILE=<ce fichier rempli> python3 generate_site.py ...
    with (seo_dir / "real-cases-template.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city_slug", "service", "situation", "secteur", "solution", "delai"])
        for city in priority_cities:
            for service_key in build.service_keys:
                writer.writerow([city.slug, service_key, "", "", "", ""])

    with (seo_dir / "content-collection-checklist.md").open("w", encoding="utf-8") as f:
        f.write("""# Checklist SEO local Solybat

Objectif : renforcer progressivement les pages villes sans publier de fausses preuves.

## Pour chaque ville prioritaire

- Ajouter 3 à 6 secteurs réels couverts.
- Ajouter au moins 1 exemple d'intervention réel par métier en remplissant
  `real-cases-template.csv` (colonnes situation / secteur / solution / delai),
  puis régénérer avec `SOLYBAT_CASES_FILE=<fichier rempli>`.
- Ajouter une photo non sensible : véhicule, matériel, chantier sans visage ni adresse visible.
- Ajouter 1 avis client réel si le client l'a publié ou autorisé.
- Ajouter un délai moyen réaliste par zone si la donnée est suivie.
- Vérifier que le numéro affiché correspond bien au pays et à la zone.

## Ne pas publier

- Faux avis.
- Faux chantiers.
- Photos prises ailleurs sans rapport avec Solybat.
- Délais garantis impossibles à tenir.
- Coordonnées client, plaques, digicodes ou adresses privées.
""")


def production_warnings() -> list[str]:
    checks = {
        "SOLYBAT_ADDRESS": BUSINESS["address"],
        "SOLYBAT_FR_PHONE_DISPLAY": BUSINESS["fr_phone_display"],
        "SOLYBAT_FR_PHONE_HREF": BUSINESS["fr_phone_href"],
        "SOLYBAT_CH_PHONE_DISPLAY": BUSINESS["ch_phone_display"],
        "SOLYBAT_CH_PHONE_HREF": BUSINESS["ch_phone_href"],
        "SOLYBAT_WHATSAPP": BUSINESS["whatsapp"],
        "SOLYBAT_LEGAL_FORM": BUSINESS["legal_form"],
        "SOLYBAT_SIRET": BUSINESS["siret"],
        "SOLYBAT_DIRECTOR": BUSINESS["director"],
    }
    warning_markers = ("à compléter", "00 00", "+33400000000", "+41220000000", "33600000000", "SIRET")
    warnings: list[str] = []
    for env_name, value in checks.items():
        if any(marker in str(value) for marker in warning_markers):
            warnings.append(env_name)
    return warnings


def write_production_checklist(build: BuildConfig) -> None:
    warnings = production_warnings()
    warning_lines = "\n".join(f"- {item}" for item in warnings) if warnings else "- Aucun placeholder détecté dans les champs critiques."
    write(
        operations_root(build) / "preproduction-checklist.md",
        f"""# Checklist préproduction - {build.label}

## Données à confirmer

{warning_lines}

## Vérifications avant mise en ligne

- Domaine final renseigné dans `SERRURIER_SITE_URL` ou `PLOMBIER_SITE_URL`.
- Numéros d'appel testés depuis mobile.
- WhatsApp testé avec le numéro final.
- Mentions légales complétées : forme juridique, SIRET, responsable de publication, adresse.
- Balises Google Ads / Analytics installées si nécessaires.
- Conversion de clic téléphone testée avec `.js-call-track`.
- Pages `/mentions-legales/`, `/confidentialite/`, `/robots.txt` et `/sitemap.xml` accessibles.
- Aucun fichier `google-ads/`, `seo/`, `ops/` ou `README.md` dans le dossier public `dist`.
""",
    )


def write_readme(cities: list[City], build: BuildConfig) -> None:
    if build.preserve_existing_home:
        pages_summary = f"""- L'accueil `index.html` existant est conservé.
- {len(cities)} villes issues du document Word.
- {len(build.service_keys)} métiers : {service_names(build)}.
- {len(cities)} pages hubs villes (`/lyon/`, `/geneve/`, etc.).
- {len(cities) * len(build.service_keys)} pages locales.
- Une page d'entrée technique : `campagnes-locales/index.html`."""
        generate_command = "python3 generate_site.py"
    else:
        pages_summary = f"""- `index.html` est l'accueil du site {build.label}.
- {len(cities)} villes issues du document Word.
- Services inclus : {service_names(build)}.
- Les pages du service principal sont à la racine (`/lyon/`, `/geneve/`, etc.).
- {len(cities) * len(build.service_keys)} pages locales."""
        generate_command = f"python3 generate_site.py --target {build.key}"
    ops_path = display_path(operations_root(build))

    readme_path = build.output_root / "README.md" if build.output_root == ROOT else operations_root(build) / "README.md"
    write(
        readme_path,
        f"""# Site local Solybat - {build.label}

Ce dossier contient un site statique généré pour la stratégie Google Ads et SEO local.

{pages_summary}
- `sitemap.xml` et `robots.txt`.
- Pages légales : `/mentions-legales/` et `/confidentialite/`.
- Fichiers d'exploitation Google Ads et SEO local générés dans `{ops_path}`.

## Générer le site

```bash
{generate_command}
```

## Générer les deux domaines séparés

```bash
python3 generate_site.py --target split
```

## Avant mise en ligne

Remplacer dans `generate_site.py` :

- `site_url` ou passer `--site-url` pour un build unique
- `SERRURIER_SITE_URL` et `PLOMBIER_SITE_URL` pour `--target split`
- `fr_phone_display` et `fr_phone_href`
- `ch_phone_display` et `ch_phone_href`
- `whatsapp`
- `email`
- `address`

Les numéros actuels sont des valeurs temporaires. Ne lancez pas Google Ads avant remplacement et test du suivi d'appel.
""",
    )


def build_config(target: str, output_root: Path | None = None, site_url: str | None = None) -> BuildConfig:
    if target == "full":
        resolved_output = output_root or ROOT
        preserve_existing_home = resolved_output == ROOT
        return BuildConfig(
            key="full",
            label="multi-services",
            site_url=site_url or os.environ.get("SOLYBAT_SITE_URL", BUSINESS["site_url"]),
            output_root=resolved_output,
            service_keys=tuple(SERVICES.keys()),
            primary_service_key=None,
            include_city_hubs=True,
            preserve_existing_home=preserve_existing_home,
        )
    if target == "serrurier":
        return BuildConfig(
            key="serrurier",
            label="serrurier",
            site_url=site_url or os.environ.get("SERRURIER_SITE_URL", SPLIT_DOMAIN_DEFAULTS["serrurier"]),
            output_root=output_root or ROOT / "dist" / "serrurier",
            service_keys=("serrurier",),
            primary_service_key="serrurier",
            include_city_hubs=False,
        )
    if target == "plombier":
        return BuildConfig(
            key="plombier",
            label="plombier",
            site_url=site_url or os.environ.get("PLOMBIER_SITE_URL", SPLIT_DOMAIN_DEFAULTS["plombier"]),
            output_root=output_root or ROOT / "dist" / "plombier",
            service_keys=("plombier", "degorgement"),
            primary_service_key="plombier",
            include_city_hubs=False,
        )
    raise ValueError(f"Unknown target: {target}")


def render_build(cities: list[City], build: BuildConfig) -> int:
    prepare_output(build)
    if build.preserve_existing_home:
        write(output_path_for("/campagnes-locales/", build), home_page(cities, build))
    else:
        write(output_path_for("/", build), home_page(cities, build))

    write(output_path_for("/zones/", build), zones_page(cities, build))
    write(output_path_for("/mentions-legales/", build), legal_page("mentions", build))
    write(output_path_for("/confidentialite/", build), legal_page("privacy", build))
    for city in cities:
        if build.include_city_hubs:
            write(output_path_for(city_hub_path(city), build), city_page(city, cities, build))
        for service_key in build.service_keys:
            write(output_path_for(service_path(city, service_key, build), build), service_page(city, service_key, cities, build))

    write(build.output_root / "sitemap.xml", sitemap(cities, build))
    write(
        build.output_root / "robots.txt",
        f"User-agent: *\nDisallow: /google-ads/\nSitemap: {build.site_url.rstrip('/')}/sitemap.xml\n",
    )
    write_ads_files(cities, build)
    write_seo_files(cities, build)
    write_readme(cities, build)
    write_production_checklist(build)
    return 4 + (len(cities) if build.include_city_hubs else 0) + len(cities) * len(build.service_keys)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Solybat static pages.")
    parser.add_argument(
        "--target",
        choices=("full", "serrurier", "plombier", "split"),
        default="full",
        help="full keeps the historical mixed site; split writes dist/serrurier and dist/plombier.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output directory for full/serrurier/plombier. With --target split, this is the parent output directory.",
    )
    parser.add_argument(
        "--site-url",
        help="Canonical domain for a single target build. For split, use SERRURIER_SITE_URL and PLOMBIER_SITE_URL.",
    )
    args = parser.parse_args()
    if args.target == "split" and args.site_url:
        parser.error("--site-url cannot be used with --target split; use SERRURIER_SITE_URL and PLOMBIER_SITE_URL.")
    return args


def main() -> None:
    args = parse_args()
    cities = load_cities()
    load_real_cases()
    if args.target == "split":
        output_parent = args.output or ROOT / "dist"
        builds = [
            build_config("serrurier", output_parent / "serrurier"),
            build_config("plombier", output_parent / "plombier"),
        ]
    else:
        builds = [build_config(args.target, args.output, args.site_url)]

    for build in builds:
        page_count = render_build(cities, build)
        print(f"Generated {page_count} HTML pages for {build.label} in {display_path(build.output_root)}.")


if __name__ == "__main__":
    main()
