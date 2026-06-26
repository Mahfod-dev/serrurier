# Guide SEO local — ce que le client doit collecter

Ce site est techniquement prêt : pages par ville, données structurées, maillage
interne, contenu varié d'une ville à l'autre. Pour **ranker en SEO naturel**
(et pas seulement convertir via Google Ads), il faut ajouter des **preuves
locales réelles**, ville par ville. Ce document explique quoi collecter et
comment l'intégrer.

> Règle d'or : **ne jamais publier de fausse preuve.** Pas de faux avis, pas de
> faux chantiers, pas de photos prises ailleurs, pas de délai garanti intenable.
> Google sait les repérer et un site pénalisé est très long à récupérer.

---

## 1. Par où commencer : la priorité

N'essayez pas d'enrichir les 129 villes. Concentrez l'effort sur :

1. **Villes P1 (16)** : Genève, Lyon, Villeurbanne, Grenoble, Annecy, Annemasse,
   Marseille, Aix-en-Provence, Toulon, Nice, Cannes, Antibes, Avignon, Valence,
   Chambéry, Saint-Étienne.
2. **Villes P2 (29)** : déjà dotées de vrais quartiers, à enrichir ensuite.
3. **Le reste (P3)** : laissez-les vivre en Google Ads, enrichissez seulement
   celles qui génèrent réellement des appels.

Le fichier `ops/serrurier/seo/local-enrichment-priority.csv` (généré
automatiquement) liste déjà ces villes avec les colonnes à remplir.

---

## 2. Ce qu'il faut collecter pour chaque ville prioritaire

### a) Quartiers réellement couverts (3 à 6)
Les vrais secteurs où vous intervenez (ex. à Lyon : Part-Dieu, Croix-Rousse…).
→ S'intègrent dans le dictionnaire `LOCAL_SEO` de `generate_site.py`.

### b) 1 à 2 exemples d'intervention réels par métier
Format court, sans donnée personnelle :
- **Situation** : « Porte claquée, clés à l'intérieur, immeuble années 70 »
- **Quartier** : « secteur Part-Dieu »
- **Solution** : « ouverture fine sans dégât, en X minutes »
- **Délai constaté** : « intervention le soir même »

→ Ces exemples s'affichent automatiquement en cartes « Exemples d'interventions »
sur la page de la ville concernée. **Comment faire :** ouvrez le fichier
`ops/<site>/seo/real-cases-template.csv` (généré à chaque build), remplissez une
ligne par cas réel (colonnes `situation`, `secteur`, `solution`, `delai`), puis
régénérez :

```bash
SOLYBAT_CASES_FILE=ops/serrurier/seo/real-cases-template.csv \
  python3 generate_site.py --target split
```

Tant qu'une ville n'a aucun cas rempli, la section ne s'affiche pas (aucun
chantier inventé). Une fois remplie, elle apparaît automatiquement.

### c) Photos réelles (le plus fort signal de confiance)
Autorisées :
- véhicule d'intervention, matériel, outillage ;
- chantier **sans visage, sans adresse, sans plaque, sans digicode** ;
- avant/après si le client a donné son accord écrit.

Interdites : photos de banque d'images présentées comme vos chantiers, toute
photo identifiant un client ou un logement.

→ Remplacent les visuels d'illustration dans `PROOF_IMAGES`. Une fois de vraies
photos en place, générez avec `SOLYBAT_PROOF_REAL=1` pour retirer le badge
« Illustration ».

### d) Avis clients vérifiés
- Demandez systématiquement un avis après une intervention réussie.
- Centralisez-les sur la **fiche Google Business Profile** (voir §4).
- Ne recopiez sur le site que des avis réellement reçus, idéalement avec lien
  vers la source. **Tant qu'il n'y a pas de vrais avis, on n'affiche aucune note
  agrégée dans les données structurées** (c'est déjà le cas dans le code).

### e) Délais moyens réels par zone (optionnel)
Si vous suivez vos temps d'arrivée, un délai moyen honnête par grande zone est un
excellent argument. Sinon, on garde la formulation prudente actuelle.

---

## 3. Comment intégrer le contenu collecté (côté technique)

Tout passe par `generate_site.py` puis une régénération.

| Donnée collectée | Où l'ajouter | Effet |
|---|---|---|
| Vrais quartiers | `LOCAL_SEO["slug-ville"]["micro_areas"]` | Quartiers cliquables + texte unique |
| Note locale propre à la ville | `LOCAL_SEO["slug-ville"]["local_note"]` | Paragraphe unique |
| Vraies photos | `PROOF_IMAGES["serrurier"]` + `SOLYBAT_PROOF_REAL=1` | Galerie réelle |
| Exemples d'intervention | `real-cases-template.csv` + `SOLYBAT_CASES_FILE=...` | Section « Exemples d'interventions » par ville |

Régénération :
```bash
SOLYBAT_PROOF_REAL=1 python3 generate_site.py --target split
```

> Le contenu est déjà **varié automatiquement** d'une ville à l'autre
> (introductions, avis, ordre des sections, FAQ, accroches). La similarité du
> texte visible entre deux villes est passée de ~99 % à ~75 %. Le contenu réel
> collecté ici sert à descendre encore et surtout à **gagner en pertinence**.

---

## 4. Hors site : les leviers les plus puissants du SEO local

1. **Google Business Profile (fiche d'établissement)** — souvent **plus
   important que les pages elles-mêmes** pour le local. Créez/optimisez une fiche
   par zone réelle d'activité (adresse réelle ou zone de service), avec photos,
   horaires, services, et collecte d'avis.
2. **Cohérence NAP** (Name, Address, Phone) identique partout : site, GBP,
   annuaires (PagesJaunes, etc.).
3. **Backlinks locaux** : partenaires, fournisseurs, presse locale, annuaires de
   qualité.
4. **Numéro local cohérent** : +41 pour Genève, 04 pour les zones France (déjà
   géré automatiquement par le site).

---

## 5. Checklist rapide par ville prioritaire

- [ ] 3 à 6 quartiers réels renseignés
- [ ] 1 à 2 exemples d'intervention par métier
- [ ] 2 à 3 photos réelles non identifiantes
- [ ] Fiche Google Business Profile active et alimentée
- [ ] Premiers avis clients réels collectés
- [ ] Numéro affiché cohérent avec la zone
- [ ] Régénération du site effectuée

---

## 6. À ne jamais faire

- Faux avis ou fausse note moyenne.
- Faux exemples de chantiers.
- Photos de stock présentées comme vos interventions.
- Délais garantis impossibles à tenir (ex. « 30 min garanti » partout).
- Coordonnées, plaques, digicodes ou adresses de clients.

Ces points sont aussi rappelés dans `ops/<site>/seo/content-collection-checklist.md`,
généré automatiquement à chaque build.
