# Passation — Serrio & Plombio

État au **28 juillet 2026**. Ce document permet de reprendre le projet sans
contexte préalable. Aucun secret n'y figure.

---

## 1. Le projet en bref

Générateur de sites locaux multivilles (`generate_site.py`, Python, sans
dépendance) pour un artisan de la métropole lyonnaise. **Deux marques** issues
du même dépôt :

| Marque | Métier | Pages | Statut |
|---|---|---|---|
| **Serrio** | serrurerie | 134 | **en ligne sur `www.serrio.fr`**, indexable |
| **Plombio** | plomberie + dégorgement | 264 | `plombio-drab.vercel.app`, en `noindex` |

Le client réel : **Abderrahim Hemani (A2H Plomberie)**, SIRET 893 610 758 00011,
2 avenue Pierre Brossolette, 69500 Bron. **Activité déclarée 43.22A = plomberie.**
Téléphone unique pour les deux marques : `07 85 04 02 48`.

---

## 2. Ce qui fonctionne aujourd'hui

### Site Serrio
- `https://www.serrio.fr` — 134 pages, HTTPS, apex redirigé en 308 vers `www`
- Domaine OVH, DNS chez OVH, hébergement Vercel (projet `serrio`)
- **Indexable** : `SITE_NOINDEX=0`, sitemap de 134 URL toutes en 200
- Propriété Search Console validée par TXT DNS

### Formulaire de rappel
- `api/callback.py` — fonction serverless, stdlib seule
- Envoie un e-mail à `contact@serrio.fr` via le SMTP OVH
- **Testé en production** : `POST /api/callback/` → `200 {"ok": true}`
- Repli automatique sur WhatsApp si le SMTP échoue → aucune demande perdue
- ⚠️ Appeler **`/api/callback/` avec le slash final** (`trailingSlash: true`)

### Google Ads
- MCC **`Flowcontent`** — 418-450-2107, détenu par **`technical-lead@devhighway.com`**
  (⚠️ *pas* `strategie@flowcontent.io` : ce compte affiche « aucun compte Google Ads »
  dans l'interface web, alors que la connexion OAuth de l'API passe par lui — voir §4bis)
- Compte client **`Serrio — Serrurerie Lyon`** — 602-385-7315
- **Moyen de paiement en place** : Mastercard ••••5600, profil de paiement
  **A2H PLOMBERIE** `5104-8315-1394`. Ce profil est **partagé au niveau du MCC** :
  renommer l'organisation impacte tous les comptes qui l'utilisent.
- **Suivi de conversion en place** : un clic sur le numéro émet
  `gtag('event','conversion',{send_to:'AW-18353985421/3QJXCIbG5dgcEI2v7q9E'})`
  — action **« Lead par téléphone »**, câblée le 01/08/2026 en remplacement du
  libellé initial `bnRXCJevyNccEI2v7q9E`. Vérifiée en conditions réelles :
  `googleadservices.com/pagead/conversion/…&label=3QJXCIbG5dgcEI2v7q9E` → **200**.
  Il n'y a pas de page de remerciement : la conversion part au clic sur
  `.js-call-track`, pas au chargement d'une page.
- ⚠️ **4 actions de conversion coexistent**, dont **3 en « Principale »** :
  `Appels à partir des annonces`, `Clic numéro site` et `Lead par téléphone`.
  Les deux dernières mesurent probablement la même chose → risque de double
  comptage dès la première vraie conversion. Ménage à faire.
- **Campagne `Serrurier - Bron & Lyon - Search` : ACTIVÉE et diffusant** (le
  présent document la disait en veille, c'était faux). Publiée le 28/07/2026,
  premières impressions le 29/07, premiers clics le 31/07. 25 €/jour.

#### Premiers chiffres réels (au 01/08/2026)

| | 31 juil. | 1er août | Total |
|---|---|---|---|
| Clics facturés | 2 | 2 | **4** |
| Coût | 10,23 € | 39,10 € | **49,33 €** |
| CPC | 5,11 € | 19,55 € | 12,33 € |
| Clics invalides filtrés | 8 | 1 | **9** |
| Conversions | 0 | 0 | **0** |

Deux constats à ne pas perdre :

1. **Les requêtes réelles sont « serrurier lyon » et « serrurier bron »** — 100 %
   de la dépense. Les mots-clés « symptôme » (`ouverture porte Lyon`…) sont bien
   ceux achetés, mais la requête large les fait matcher sur le terme métier. **Le
   contournement de la restriction Local Services ne contourne rien**, et l'artisan
   n'est toujours pas assuré en serrurerie (§3).
2. **Ciblage géographique corrigé le 01/08/2026** : `positive_geo_target_type`
   est passé de `PRESENCE_OR_INTEREST` (défaut Google) à **`PRESENCE`**. Avant
   correction, la campagne diffusait à Paris, Bordeaux, Agen, Montpellier et
   **Doha (Qatar)** ; 2 clics parisiens ont coûté 10,23 €, soit 21 % du budget
   dépensé. Paris captait plus d'impressions que Bron et Lyon réunis.

### Validation de l'annonceur — échéance 31 août 2026
Sans elle, **le compte est mis en veille**. État au 01/08/2026 : **en cours d'examen**
(délai annoncé 1 à 10 jours).

- Étape 1 « questions sur votre entreprise » → **envoyée**, réponse : *nom légal
  d'une autre organisation* (et non « Serrio », qui est une marque sans existence
  juridique). Les annonces afficheront « Annonces financées par … » avec le nom légal.
- Étape 2 « informations Dun & Bradstreet » → **envoyée** sans numéro DUNS
  (**facultatif**, c'est seulement un accélérateur ; le portail `dunsnumberlookup.dnb.com`
  ne couvre pas la France, c'est Altares qui gère, 5 à 30 jours ouvrés).
- **Reste à faire par le client** : téléverser un document d'immatriculation +
  une pièce d'identité. ⚠️ **A2H Plomberie est une entreprise individuelle
  artisanale : elle n'a pas de Kbis.** Prendre l'**avis de situation SIRENE**
  (gratuit, immédiat, `avis-situation-sirene.insee.fr`, SIRET 893 610 758 00011).
- Nom légal exact au répertoire : **`ABDERRAHIM HEMANI (A2H PLOMBERIE)`**
- Tâche annexe : « annonces à caractère politique pour l'UE » → répondre **non**.

---

## 3. Ce qui reste — par ordre de priorité

### 🔴 Dépend du client, bloque tout le reste

1. ~~**Moyen de paiement**~~ — **réglé** (01/08/2026). Mastercard ••••5600 sur un
   profil de paiement au nom **A2H PLOMBERIE**, donc bien au nom du client.
   Reste à confirmer que la carte est celle de l'artisan et non celle de l'agence.
   **Nouveau bloquant à la place** : les documents de validation de l'annonceur,
   à fournir avant le 31 août sous peine de mise en veille du compte (§2).
2. **Assurance RC pro étendue à la serrurerie.** *Devenu urgent* : la campagne
   diffuse **déjà** sur « serrurier lyon » et « serrurier bron » et a été facturée
   pour, alors que la couverture n'existe pas. Il est assuré pour la
   plomberie (43.22A) mais le site vend de la serrurerie. Double conséquence :
   risque juridique, **et** blocage des mots-clés « serrurier » par Google
   (voir §5).
3. **Validation des tarifs.** Les prix viennent du générateur, pas du client,
   et l'engagent. Ils sont **désormais indexés**. Un écart annoncé/facturé est
   le motif classique de suspension d'un compte Ads en serrurerie.

### 🟠 Côté agence

4. **Campagne `Serrurier - France - Search` à 150 €/jour** — vide et en veille,
   mais à supprimer ou ramener à 25 €.
5. **Examen des annonces** — vérifier sous 48 h si elles passent malgré le mot
   « Serrurier » dans les titres. Si refusées, réécrire avec les 8 titres
   neutres déjà générés.
6. **Boîte `contact@serrio.fr`** — créée, mais vérifier qu'elle est relevée
   (webmail `https://mail.ovh.net/roundcube/` ou redirection vers l'adresse
   personnelle de l'artisan). Le PDF d'installation est dans
   `ops/guides/serrio-email-telephone.pdf`.
7. **Google Business Profile** — non créé. C'est le premier levier en dépannage
   local et le prérequis des Local Services Ads. Gratuit, effet lent : à lancer tôt.
8. **`plombio.fr`** — libre, non acheté (~8 €/an OVH).

### 🟢 Plus tard

9. **Jeton développeur API Google Ads** — à demander depuis le MCC
   (`Outils et paramètres → API Center`). Niveau **Basic** requis (le niveau
   Test ne touche que des comptes de test). Revue manuelle, plusieurs semaines.
   Intérêt réel : générer les 130 villes × 2 métiers par programme.
10. **Photos réelles** → `SITE_PROOF_REAL=1`. Tant que non, badge « Illustration »
    et champ `image` absent du JSON-LD.

---

## 4. Commandes et fichiers

```bash
# Build local
SITE_TARGET=serrurier python3 build_vercel.py     # → public/, 134 pages
SITE_TARGET=plombier  python3 build_vercel.py     # → public/, 264 pages
SITE_NOINDEX=1 SITE_TARGET=serrurier python3 build_vercel.py   # version non indexable

# Preview
cd public && python3 -m http.server 8801

# Régénérer les imports Google Ads
python3 ops/serrurier/google-ads/build_editor_import.py
python3 ops/serrurier/google-ads/build_keywords_symptomes.py
```

| Chemin | Contenu |
|---|---|
| `generate_site.py` | tout le générateur (~3900 lignes) |
| `build_vercel.py` | point d'entrée build, lit `SITE_TARGET` |
| `api/callback.py` | fonction serverless du formulaire |
| `ops/serrurier/google-ads/` | plan de mots-clés, négatifs, pages de destination |
| `ops/serrurier/google-ads/editor-import/` | CSV d'import Ads Editor + README |
| `ops/guides/` | PDF client pour l'e-mail |

⚠️ `ops/`, `seo/`, `google-ads/`, `public/`, `dist/` sont **gitignorés**.

### Variables d'environnement Vercel (projet `serrio`)

`SITE_TARGET=serrurier` · `SITE_NOINDEX=0` · `SMTP_USER=contact@serrio.fr` ·
`SMTP_PASSWORD` (secret, posé par l'utilisateur) · `SERRURIER_ADS_ID=AW-18353985421` ·
`SERRURIER_ADS_CALL_LABEL=3QJXCIbG5dgcEI2v7q9E`

⚠️ Ces variables sont **sensibles** côté Vercel : `vercel env pull` les rend
vides. Pour contrôler leur valeur, lire le HTML publié plutôt que le `.env` :
`curl -s https://www.serrio.fr/ | grep -o "send_to: '[^']*'"`.
Un changement de variable n'a d'effet qu'après redéploiement :
`vercel redeploy <url-du-dernier-deploiement> --scope mahfoddevs-projects`.

`SERRURIER_GA_ID` **absent** — aucune propriété GA4 créée.

---

## 4bis. Accès API Google Ads — la voie rapide

**L'API est opérationnelle et le jeton développeur est approuvé** (le §3 la classait
en « plus tard, à demander » : obsolète). Elle est bien plus fiable que l'interface
web, qui affiche des plages de dates périmées et se trompe sur les droits d'accès.

Les secrets vivent sur le serveur **`root@157.90.160.24`** (hôte `flowblog`) et
n'ont pas à en sortir :

| Élément | Où |
|---|---|
| `GOOGLE_ADS_DEVELOPER_TOKEN` | env du conteneur `blog-api-blue` |
| Jeton OAuth | Nango, connexion `74748dbf-86f8-49f0-8a5d-14fed0faa7ac` (`google-ads`) |
| `NANGO_SERVER_URL` / `NANGO_SECRET_KEY` | `/opt/blog-api/.env` |
| Code métier | `~/Desktop/backend-flowcontent/blog-api/src/modules/google-ads/` |

En-têtes : `login-customer-id: 4184502107` (le MCC), endpoint
`googleads.googleapis.com/v23/customers/6023857315/googleAds:search`.

⚠️ **Passer par un script envoyé sur stdin** (`ssh root@… 'python3 -' < script.py`) :
les requêtes GAQL contiennent des guillemets qui se perdent dans l'échappement
shell d'une commande SSH en ligne, et la requête revient silencieusement vide.

Requêtes qui ont servi et resserviront : `search_term_view` (les vraies requêtes
tapées, ≠ mots-clés achetés), `user_location_view` + `segments.geo_target_city`
(ville réelle de l'internaute), `metrics.invalid_clicks`, `segments.device`,
`segments.hour`, `campaign.geo_target_type_setting`.

## 5. Pièges connus — lire avant d'agir

### Google Ads — restriction Local Services
Google bloque les mots-clés désignant le **métier** ou la **prestation**, et
autorise ceux décrivant le **problème du client** :

| Bloqués | Autorisés |
|---|---|
| `serrurier <ville>`, `serrurier urgence <ville>`, `changement serrure <ville>` | `ouverture porte <ville>`, `serrure bloquée <ville>` |

**Ne pas cocher « Demander une dérogation » sans l'attestation d'assurance
serrurerie.** La revue Google l'exige. Un dossier faux entraîne une suspension
qui **remonte au MCC et aux autres comptes clients**, plus le jeton API visé.

Contournement en place : mots-clés « symptôme » générés par
`build_keywords_symptomes.py`.

### Google Ads Editor
- Un import répété **n'écrase pas, il ajoute** → doublons à supprimer
- Colonne `Account` requise si plusieurs comptes ouverts, mais si la valeur ne
  correspond pas exactement, l'import passe « dans le vide » et `Publier` reste
  grisé → préférer les fichiers `sans-account/` avec le compte sélectionné
- Colonne `Languages` interdite au niveau groupe d'annonces
- Négatifs : colonne `Negative Keyword`, pas `Keyword` (sinon groupes fantômes)
- L'application est en français, les en-têtes CSV en anglais → écran de
  correspondance des colonnes à mapper à la main
- Les exclusions se posent au niveau **Campagne**, pas Groupe d'annonces
  (le formulaire propose Groupe par défaut)

### Interface web Google Ads
- **Ne jamais construire d'URL à la main** (`/aw/...?ocid=`) : les paramètres de
  session s'empilent et finissent en `400 Bad Request`. Naviguer par clics.
- Un sous-compte MCC ne s'ouvre **que** par le MCC, jamais en accès direct
- L'assistant « Créer ma première campagne » pousse vers Performance Max —
  inadapté ici (budget dispersé, pas de mots-clés). Cliquer « Ignorer » à
  l'étape objectif fait basculer sur le parcours manuel.

### OVH / DNS
- La zone par défaut contient des **`AAAA` vers l'IPv6 du parking**. Les laisser
  fait atterrir les visiteurs IPv6 sur la page OVH → **les supprimer**.
- Vercel n'est pas registrar `.fr`. Garder le DNS chez OVH pour préserver les MX.
- Ne plus sonder les MX depuis le poste local : après une dizaine de `RCPT TO`
  de vérification, OVH bloque l'IP.

### Règle de fond du projet
**Aucune fausse preuve.** Pas de faux avis, pas d'`aggregateRating`, pas de
photos tierces présentées comme des chantiers, pas de délai garanti intenable.
Les avis sont des « exemples représentatifs », les photos portent un badge
« Illustration » tant qu'elles ne sont pas réelles.

---

## 6. Comment travailler avec l'utilisateur

- **En français**, exigence de qualité élevée
- Pour tout ce qui est **hors navigateur** (Ads Editor, espace OVH), il fait des
  **captures d'écran sur son Bureau** — les lire avec `Read` après
  `ls -lt ~/Desktop/*.png`. C'est de loin le moyen le plus rapide de débloquer
  une situation.
- Il accepte le pilotage de son Chrome mais **choisit le profil** lui-même
- Commit et push directs sur `main`
- **Annoncer explicitement tout montant** qui engage le budget du client — ne
  jamais le glisser dans un fichier de configuration.
