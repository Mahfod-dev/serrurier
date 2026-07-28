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
- MCC **`Flowcontent`** — 418-450-2107
- Compte client **`Serrio — Serrurerie Lyon`** — 602-385-7315
- **Suivi de conversion vérifié en conditions réelles** : un clic sur le numéro
  émet `gtag('event','conversion',{send_to:'AW-18353985421/bnRXCJevyNccEI2v7q9E'})`
- **Campagne pilote publiée, en veille** : `Serrurier - Bron & Lyon - Search`,
  25 €/jour, 2 groupes (Bron, Lyon), 2 annonces, 24 exclusions au niveau campagne,
  composant Appel

---

## 3. Ce qui reste — par ordre de priorité

### 🔴 Dépend du client, bloque tout le reste

1. **Moyen de paiement** dans le compte Ads. Sans lui, aucune diffusion.
   Le compte doit rester **au nom du client**, facturation directe. Ne jamais
   saisir sa carte dans un compte au nom de l'agence.
2. **Assurance RC pro étendue à la serrurerie.** Il est assuré pour la
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
`SERRURIER_ADS_CALL_LABEL=bnRXCJevyNccEI2v7q9E`

`SERRURIER_GA_ID` **absent** — aucune propriété GA4 créée.

---

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
