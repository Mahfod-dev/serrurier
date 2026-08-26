# Passation — Serrio & Plombio

État au **28 juillet 2026**. Ce document permet de reprendre le projet sans
contexte préalable. Aucun secret n'y figure.

---

## 0. Mise à jour du 24 août 2026 — lire en premier

Trois faits nouveaux, vérifiés dans l'interface Google Ads le 24/08 :

1. **La campagne `Serrurier - Bron & Lyon - Search` diffuse.** Elle a été mise en
   veille puis **réactivée le jour même à la demande de l'utilisateur**.
2. **Son budget est de 300,00 €/jour : c'est une demande du client.** Les mentions
   de 25 €/jour ailleurs dans ce document sont périmées sur ce point. ⚠️ Ne pas
   traiter ce montant comme une dérive et ne pas proposer de le réduire.
3. **Dépense réelle : 1 096,52 € sur 25 juil. – 23 août** (212 clics, CPC moyen
   5,17 €, 2 499 impressions). Le §2 ci-dessous parle de 49,33 € : c'était l'état
   au 1er août.

**Conversions : 26, et elles sont réelles.** Le §2 annonçait un double comptage ;
vérification faite le 24/08, il n'y en a pas. Le site câble trois chemins avec
trois libellés distincts, et chacun a son action :

| Action | Libellé | Conversions |
|---|---|---|
| `Lead par téléphone` | `3QJXCIbG5dgcEI2v7q9E` | **20** |
| `Lead WhatsApp` | `J34oCMPA4OEcEI2v7q9E` | **6** |
| `Lead demande de rappel` | `ZXThCMbA4OEcEI2v7q9E` | 0 (formulaire récent) |

Soit **~42 € par contact**, pas 122 €.

**Ménage fait le 24/08** : trois actions parasites en « Principale », toutes à 0
conversion et en « mauvaise configuration », sont passées en **Secondaire** —
`Clic numéro site`, `Lead par téléphone (1)` et `Lead par téléphone (2)`, toutes
orphelines (aucun libellé émis par le site). `Appels à partir des annonces` reste
en Principale : elle mesure les appels depuis l'extension d'appel, chemin distinct.

Principale/Secondaire ne se règle que dans `action → Modifier les paramètres →
Optimisation des actions`. Le menu ⋮ et la sélection multiple ne proposent que
« Supprimer » — **à ne jamais faire**, c'est irréversible et l'historique part avec.

### État réel de la campagne serrurerie (vérifié le 24/08 au soir)

Le §2 la décrit comme un « pilote sur 2 villes ». **C'est faux depuis longtemps.**
Relevé dans l'interface :

| | Valeur |
|---|---|
| État | **Activée**, « Stratégie d'enchères limitée » (avertissement, pas un blocage) |
| Budget | **300,00 €/jour** (choix client) |
| Groupes d'annonces | **67**, pas 2 — Lyon, Bron, Lyon 6, Oullins, Meyzieu, mais aussi **Annecy, Annemasse, Thonon-les-Bains, Chambéry, Cluses, Aix-les-Bains, Albertville, Ambérieu-en-Bugey…** |
| Zones géographiques | **58 ciblées**, et **Paris exclu** (leçon de juillet appliquée) |
| Option de ciblage | **Présence** (pas « Présence ou intérêt ») ✅ |
| Réseaux | **Recherche Google seule**, sans partenaires ✅ |
| Stratégie d'enchères | Maximiser les clics |
| Requête large | **Désactivée** ✅ |
| Composants auto / AI Max | **Désactivés** ✅ |
| Annonces | **« Éligible »** — voir ci-dessous |

**La question ouverte depuis le 28/07 est tranchée : les annonces contenant le mot
« Serrurier » sont ÉLIGIBLES.** Elles diffusent, l'examen est passé. La restriction
Local Services frappe les **mots-clés**, pas les créations — inutile de réécrire les
titres.

**Répartition du coût** : `Serrurier - Lyon` pèse **665,02 € sur 1 096,52 €** (61 %),
1 504 impressions, CTR 8,11 %. Les villes savoyardes restent marginales (Annecy
83,61 €, Annemasse 41,34 €, Chambéry 28,95 €).

⚠️ **Point à trancher avec le client** : Annecy, Thonon, Cluses, Albertville et
Aix-les-Bains sont à **100–200 km de Bron**. Sur du dépannage en urgence, un lead
qui vient de là est difficilement servable. Les pages existent (le site couvre 130
villes), mais la question est commerciale : l'artisan s'y déplace-t-il vraiment ?

**Plombio se prépare en parallèle**, sans rien retirer à la serrurerie : le
dégorgement est dans l'activité déclarée 43.22A et assuré, donc sans restriction
Local Services sur les mots-clés. Les imports Ads Editor sont générés :

```bash
python3 ops/plombier/google-ads/build_editor_import.py
```

→ `ops/plombier/google-ads/editor-import/` : deux campagnes **à 25 €/jour
chacune, en veille**, `Dégorgement - Bron & Lyon - Search` (11 groupes : Bron,
Lyon et ses 9 arrondissements, 55 mots-clés) et `Dégorgement - Rhône - Search`
(34 communes, 170 mots-clés), 40 exclusions par campagne. Mode d'emploi complet
et pièges dans `editor-import/README-import.md`.

### Brouillon de campagne débouchage créé dans le compte Serrio (24/08/2026)

**`Degorgement - Bron et Lyon - Search`** — `draftId=10210785649`,
`campaignId=281499152191416`. **Brouillon, non activé, sans budget : rien ne peut
diffuser.** Il se retrouve dans `Campagnes → onglet Brouillons`.

Ce qui est déjà réglé :

| Réglage | Valeur |
|---|---|
| Type | Réseau de Recherche |
| Réseaux | **Recherche Google seule** — partenaires ET Display décochés |
| Enchères | **Maximiser les clics** (pas de tag Plombio, donc rien à apprendre pour « conversions ») |
| Zones | **Bron + Lyon**, ciblage **Présence** |
| Langue | Français |
| Site | `https://www.plombio.fr` · Téléphone `07 85 04 02 48` (France) |
| AI Max | **désactivé** · génération de mots-clés par IA **ignorée** |
| Mots-clés | 5 saisis pour Lyon, en expression exacte |

**Ce qui reste** : l'annonce responsive, le budget, et les 10 autres groupes
(Bron + les 9 arrondissements). ➜ **Passer par Ads Editor** avec
`ops/plombier/google-ads/editor-import/` : c'est 5 minutes contre plusieurs
centaines de clics dans l'interface web.

⚠️ **Deux pièges rencontrés dans le parcours de création, à connaître** :
1. **Google recommande un budget de 256,61 €/jour** (options à 205 € et 307 €)
   pour deux villes. Il faut **« Définir un budget personnalisé » et saisir 25 €**.
2. **Une confirmation d'identité est demandée** au moment du budget — seul
   l'utilisateur peut la passer.
3. Taper du texte hors d'un champ déclenche les **raccourcis clavier** de Google
   Ads et fait quitter le formulaire. Toujours cliquer dans le champ d'abord.
4. Le champ de zone géographique propose **les résultats américains en premier**
   (« Bron » → « Bronx, New York ») : écrire « Bron, Auvergne » pour désambiguïser.

### Deux croyances de ce dossier corrigées le 24/08/2026

**1. La RC pro couvre la serrurerie.** Confirmé par le client. Le « bloquant n°2 »
qui traîne depuis juillet — *l'artisan vend de la serrurerie sans être assuré
pour* — n'existe pas. Le risque juridique sur les 212 clics déjà servis tombe,
et le compte Serrio ne porte plus de risque de suspension particulier.

**2. Les mots-clés « serrurier <ville> » sont déjà dans le compte et diffusent.**
Le §5 dit que Local Services les bloque et qu'il faut une dérogation. Vérification
faite dans `Mots clés` : **337 mots-clés**, dont `"serrurier Chambéry"` en
**expression exacte et Éligible**. **Il n'y a donc pas de dérogation à demander**
— la restriction vue dans Ads Editor le 28/07 n'a pas empêché la publication.

⚠️ **Nuance capitale ajoutée le 25/08/2026 : la dérogation a bien un objet.**
Les mots-clés existants diffusent, c'est vrai — mais Google refuse désormais
**toute création** d'un mot-clé contenant « serrurier », avec ou sans ville
(`policyViolationError`, politique `LOCAL_SERVICES`, `isExemptible: true`).
`serrurier lyon 4` est refusé ; `ouverture de porte lyon` passe. La
restriction vise le nom du métier, pas la ville ni le mot « serrure ».

✅ **Elle se lève par `exemptPolicyViolationKeys`** — testé à blanc le 25/08,
`serrurier lyon 4` passe :

```json
"exemptPolicyViolationKeys": [
  { "policyName": "LOCAL_SERVICES", "violatingText": "serrurier lyon 4" }
]
```

C'est le « Demander une dérogation » de l'interface, côté API. Le compte n'est
pas gelé. Mais lire le §5 avant de s'en servir : c'est une auto-certification,
pas un examen, et un dossier faux remonte au MCC.

Contournement appliqué le 25/08 : groupe `Serrurier - Situations urgence`,
10 mots-clés qui achètent la situation plutôt que le métier — `enferme
dehors`, `cle cassee dans la serrure`, `cle perdue`, `ouverture de porte`,
`serrure bloquee`… soit ~10 600 recherches/mois que le compte ne captait pas.

⚠️ Ce document a un temps dit que `"serrurier lyon 3"` et `"serrurier lyon 7"`
étaient « en veille sans raison connue, à réactiver ». **C'est faux, et il ne faut
pas les réactiver.** Relevé API du 24/08/2026 : le compte contient **340 mots-clés,
330 actifs, 9 en veille, 1 supprimé**. Les 9 en veille sont `serrurier lyon 1` à
`serrurier lyon 9`, en expression exacte, dans le groupe générique
`Serrurier - Lyon`. Ils ont été mis en veille par l'API le **22/08 à 22h14**, six
minutes après la création des neuf groupes d'arrondissement à 22h08 : chaque
arrondissement a désormais son propre groupe avec **3 mots-clés actifs**
(`serrurier Lyon N`, `serrurier urgence Lyon N`, `depannage serrurier Lyon N`),
soit **27 mots-clés à la place de 9**. Les réactiver remettrait deux groupes en
concurrence sur la même requête, ce que la séparation des arrondissements visait
précisément à supprimer.

Le mot-clé **supprimé** est `"serrurerie lyon"`, retiré le **23/08 à 19h38** par
`GOOGLE_ADS_RECOMMENDATIONS` — c'est-à-dire **par Google lui-même**, via
l'application automatique des recommandations, et non par nous. À traiter :
désactiver l'auto-application dans `Recommandations` → `Application automatique`,
sinon Google continuera de modifier le compte sans qu'on le décide.

Conséquence sur l'architecture des comptes : **Plombio peut aller dans le compte
Serrio**, l'argument du risque de contagion ne tient plus. Deux précautions si on
fait ce choix : définir les **objectifs de conversion au niveau de la campagne**
Plombio (au lieu de « Par défaut dans le compte ») pour ne pas mélanger les
signaux d'enchères, et renommer le compte, qui s'appelle encore
« Serrio — Serrurerie Lyon ».

### Savoie, Haute-Savoie et Isère en standby sur Serrio (24/08/2026, soir)

**Demande du client.** Plutôt que de retirer les 33 villes concernées des zones
ciblées une par une, les **trois départements ont été EXCLUS** au niveau de la
campagne : dans Google Ads l'exclusion prime sur l'inclusion, c'est 3 opérations
au lieu de 33, et le retour arrière se fait en supprimant les 3 exclusions.

État après enregistrement : **Ciblées : 58 lieux — Exclues : 4 lieux**
(Paris, déjà exclu depuis juillet, + Savoie, Haute-Savoie, Isère).

⚠️ **Les 33 groupes d'annonces de ces villes restent ACTIFS** (`Serrurier - Annecy`,
`- Chambéry`, `- Grenoble`…). L'exclusion géographique suffit à couper la
diffusion locale, mais un internaute **présent à Lyon** qui taperait
« serrurier annecy » pourrait encore déclencher le groupe Annecy. Résiduel, mais
à traiter si le standby dure : les mettre en veille.

**Ce que ce standby coupe, chiffres à l'appui** (25/07 – 23/08) : les
départements 73/74 avaient produit **5 conversions sur 26** pour ~207 €, dont
**Annemasse — le meilleur coût par conversion du compte, 13,78 €** (contre 51 €
pour Lyon et 42 € de moyenne). Annecy 1 conv./83,61 €, Chambéry 1 conv./28,95 €.
Le client a été informé de ces chiffres et a maintenu sa décision — le motif est
la distance, pas la performance.

### La ville dans le mot-clé nous privait de l'essentiel du marché (25/08/2026)

Analyse Keyword Planner du 25/08, avant de porter le budget à 150 €/jour.

**Le marché « avec ville » est minuscule et cher.** `debouchage canalisation
lyon` : 390 recherches/mois, enchère haut de page **2,93 → 15,75 €**. Tout le
reste du local est entre 10 et 70/mois ; `débouchage wc lyon` monte à
**26,94 €** l'enchère haute pour 30 recherches.

**Le marché « sans ville » est dix fois plus gros, et aussi qualifié :**

| Requête | Volume | Enchère haut de page |
|---|---|---|
| deboucheur toilette | 2 900/mois | 2,46 → 13,12 € |
| déboucheur canalisation professionnel | 1 300/mois | 1,00 → 6,59 € |
| entreprise débouchage canalisation | 1 000/mois | 1,62 → 10,34 € |
| débouchage canalisation urgence | 720/mois | 1,75 → 10,58 € |
| societe debouchage canalisation | 590/mois | 2,30 → 15,84 € |
| débouchage canalisation tarif | 590/mois | 1,00 → 6,07 € |

**Le ciblage `PRESENCE` fait déjà le tri géographique : l'internaute n'a pas
besoin d'écrire « lyon » pour qu'on sache qu'il y est.** Exiger le nom de la
ville dans le mot-clé nous coupait de ces requêtes. Un groupe
**`Debouchage - Generique Rhone`** a été créé dans la campagne Rhône —
12 mots-clés en expression exacte, une annonce, destination l'accueil.

**Lire l'enchère basse plutôt que le volume.** `deboucher wc` fait
14 800/mois mais son enchère basse est à **0,49 €**, et `deboucher evier`
à **0,15 €** : personne ne mise sur quelqu'un qui veut faire lui-même. Les
gros volumes de ce marché sont informationnels. L'écart bas/haut trahit
l'intention mieux que le volume.

**Plafond d'enchère posé à 8 €** sur les deux campagnes. « Maximiser les
clics » sans plafond suivrait les enchères hautes : à 150 €/jour, deux clics
à 25 € mangeraient le tiers de la journée.

Budget porté à **150 €/jour** — 100 € sur le Rhône (qui porte désormais le
groupe générique), 50 € sur le pilote lyonnais.

### Le standby 73/74/38 ne fonctionnait pas — corrigé le 25/08/2026

Posé le 24/08 en excluant les trois départements au niveau campagne. **C'était
insuffisant** : chez Google la zone la plus précise l'emporte, et les villes
restaient ciblées explicitement. Résultat, **145,70 € dépensés en deux jours**
sur Annecy (23,52 €), Chambéry (31,77 €), Aix-les-Bains (28,20 €), Annemasse
(26,70 €), Thonon (13,79 €), Sallanches (12,44 €) et Albertville (9,28 €) —
contre la demande explicite du client.

**24 villes retirées du ciblage positif** le 25/08 : les 24 communes de Savoie
et Haute-Savoie de `CITY_GROUPS`. Il reste **34 zones**, Rhône et Ain — l'Ain
(Bourg-en-Bresse, Oyonnax, Gex, Ferney-Voltaire, Divonne, Valserhône,
Ambérieu, Saint-Genis-Pouilly, Miribel) n'était pas concerné par le standby.
Les exclusions de départements sont conservées par sécurité.

Les groupes d'annonces de ces villes restent actifs mais sans zone : ils ne
peuvent plus diffuser, et tout revient si on rallume le ciblage.

**Règle** : vérifier un standby par la dépense réelle par groupe les jours
suivants, jamais par le compteur de zones de l'interface — voir
[[google-ads-pieges-diagnostic]].

### Le débouchage diffuse : deux campagnes, 150 €/jour (25/08/2026)

| Campagne | Budget | Groupes | Mots-clés |
|---|---|---|---|
| `Plombio — Search — Local par ville` | 15 €/j | 11 | 88 |
| `Plombio Rhône — Search — Local par ville` | 10 €/j | 23 | 460 |

Les deux `ENABLED`, `SERVING`, ciblage `PRESENCE`, créées par
`campaign-plan/publish` — 159 puis 576 ressources, aucun échec.

**Budget : 25 €/jour, décision du 25/08.** Les 150 €/jour voulus par le client
ont été posés puis ramenés à 25 € dans la foulée, le temps d'observer les
requêtes réelles avant d'engager la dépense. La montée reste prévue ; elle se
décidera sur `search_term_view`, pas sur le calendrier. La répartition
15/10 suit le volume mesuré tout en laissant les deux périmètres diffuser :
un budget trop mince sur le Rhône le rendrait muet, donc inobservable.

**Le budget dépasse volontairement le marché mesuré.** Relevé Keyword Planner
du 25/08 sur les 88 mots-clés du périmètre Lyon/Bron : **516 recherches par
mois au total, et 82 mots-clés sur 88 à zéro**. `debouchage canalisation lyon`
porte à lui seul **416/mois**, soit 81 % du marché ; les neuf arrondissements
sont à **0**. À 8 % de taux de clic et 5 € le clic, ce périmètre absorbe
**environ 7 €/jour**, pas 150.

C'est pour cette raison que l'élargissement au Rhône a été fait **en même temps
que la hausse de budget**, et pas après : un budget qu'on ne peut pas dépenser
pousse Google à élargir seul les requêtes servies — le mécanisme même qui a
porté le CPC de Serrio à 5,19 €, contre ~1,70 € chez ses concurrents pour une
dépense identique.

**À surveiller sous 48 h** : `search_term_view`. Si les requêtes réelles
dérivent (produits, DIY, plomberie générale), redescendre le budget plutôt que
d'ajouter des exclusions une par une.

⚠️ Google ne connaît pas la commune nouvelle **« Oullins-Pierre-Bénite »**
(2024). Le ciblage porte « Oullins » ; la page d'arrivée reste
`/oullins-pierre-benite/`. Le builder a refusé de publier avant correction —
« on ne publie pas avec un ciblage approximatif ».

### La vérification de l'annonceur est TERMINÉE (constaté le 24/08/2026)

Ce document annonçait une échéance au **31 août sous peine de suspension du
compte**. **C'est faux et périmé.** Relevé dans `Admin → Règlement → Compte`
le 24/08/2026 au soir : les quatre étapes sont cochées, et l'encart de droite
affiche le badge servi sur les annonces —

```
Advertiser identity verified
ADVERTISER : A2H PLOMBERIE
LOCATION   : FR
```

| Étape | Date |
|---|---|
| Questions sur l'entreprise | 1er août 2026 |
| Informations Dun & Bradstreet | 2 août 2026 |
| Pas d'annonces politiques UE | 1er août 2026 |
| Responsable du paiement | 1er août 2026 |

**Aucun document n'est à fournir, aucune suspension n'est en attente.** Le
dossier était « en cours d'examen » au 01/08 ; il a abouti dans les jours qui
ont suivi et personne n'a mis la note à jour.

### Correction : l'application automatique des recommandations n'est pas activée

Il a été écrit le 24/08 que Google avait supprimé `serrurerie lyon` « tout
seul ». Le `change_event` porte bien `client_type = GOOGLE_ADS_RECOMMENDATIONS`,
mais ce champ désigne **l'écran d'où part l'action, pas une automatisation**.
Le panneau « Application automatique » de la vue d'ensemble dit l'inverse :
« Vous avez appliqué ces recommandations au cours des 90 derniers jours. Pour
appliquer ces recommandations automatiquement […] **activez** l'application
automatique. » C'est donc un clic humain sur *Appliquer*, dans
`Recommandations` → *Supprimer les mots clés redondants*. Rien à désactiver.

### Le débouchage se vend comme du débouchage, pas comme de la plomberie (24/08/2026, nuit)

Deux découvertes du même soir, en essayant de publier la campagne Plombio par
l'API Flowcontent plutôt que par Ads Editor.

**1. Le campaign-builder de Flowcontent fonctionne, et il vaut mieux qu'Ads
Editor.** Endpoints `POST /api/google-ads/campaign-plan/{build,validate,publish}`,
déployés en prod, écran `/[locale]/lancer-ma-publicite`. Création atomique en une
requête `googleAds:mutate`, campagne créée `PAUSED`, `PRESENCE` en dur, mode
`validateOnly` qui vérifie chez Google sans rien écrire. Le `build` a produit un
plan complet sur le compte Serrio, pages ville comprises.

⚠️ L'écran n'envoie **pas** `landingPages`, `extraKeywords` ni
`confirmedComplianceKeys`, et n'appelle jamais `validate`. Utilisé tel quel, il
enverrait les onze groupes sur la page d'accueil. Passer par l'API tant que ces
champs manquent — le jeton se lit dans la session NextAuth de l'admin
(`GET /api/auth/session` → `user.apiToken`), l'API est `https://flowbackendapi.store/api`.

**2. Le playbook `plomberie` vendait la mauvaise prestation.** Sur les onze
groupes, il produisait 18 mots-clés par ville dont 10 de plomberie générale :
`plombier {ville}`, `chauffe eau en panne {ville}`, `dégât des eaux {ville}`,
`radiateur qui fuit {ville}`. Sur un site devenu 100 % débouchage, ce sont des
clics payés pour une prestation que les pages n'annoncent pas.

Un playbook **`degorgement`** a été créé (`backend-flowcontent`, commit
`a42f9a4f`, **non déployé** : le conteneur `blog-api-blue` tourne encore
l'ancien code). Il achète le symptôme et refuse en exclusion ce que le site ne
vend pas. `plombier` n'est **pas** exclu : « plombier wc bouché » est un bon
client, qui nomme le métier faute de connaître le mot « déboucheur ».

**3. Le site parlait comme l'artisan.** Relevé du champ lexical d'un spécialiste
du créneau : il écrit « WC bouché », « évier bouché », « regard qui déborde » là
où nous écrivions « dégorgement », « hydrocurage », « camion pompe ». Les pages
ont été réécrites (commit `bff5c43`, en ligne) : symptôme d'abord, prestations
rangées par équipement, positionnement « déboucheur ≠ plombier » dans le bénéfice
central et la FAQ.

**4. Le « à partir de 120 € » a été retiré du site.** Il n'avait jamais été
confirmé par Abderrahim Hemani, et le builder refuse — à juste titre — de publier
une campagne qui achète du trafic vers une page affichant un prix non validé. La
grille est désormais structurée en trois forfaits (débouchage manuel, inspection
caméra, hydrocurage/camion pompe), tous « Sur devis » **en attente des montants
de l'artisan**. Il fait les trois prestations, confirmé par l'utilisateur le
24/08. Dès que les prix arrivent, ils se posent dans
`SERVICES["degorgement"]["pricing"]` et nulle part ailleurs.

**5. La campagne Plombio est publiée — EN PAUSE.** Le 24/08/2026 à 22h50, par
`campaign-plan/publish` : **159 ressources créées, aucun échec**. Vérifié
ensuite par l'API Google Ads, indépendamment de l'outil qui a écrit :

```
Plombio — Search — Local par ville   PAUSED   budget 25 €/j
11 groupes · 88 mots-clés · 0 mot-clé de plomberie générale
```

Le playbook `degorgement` n'étant pas déployé, le plan a été construit avec
`vertical: 'plombier'` puis **corrigé côté client avant validation** : retrait
des 110 mots-clés de plomberie générale, ajout de 13 exclusions, et réécriture
des 11 annonces, qui promettaient « Plombier à {ville} », « Chauffe-eau et
sanitaires » et « Recherche de fuite » — des prestations que les pages
n'annoncent pas. C'est un rattrapage manuel : **déployer le playbook rend ce
travail inutile la prochaine fois.**

À noter : Google résout les arrondissements lyonnais en codes postaux
(`69001`, `2nd arrondissement`…), sauf **« Lyon 6 », résolu en « Lyon »** —
sans conséquence de diffusion ici, Lyon entier étant déjà ciblé.

**Ce qui reste avant d'activer la campagne Plombio :**

1. **Tarifs : arbitrage rendu, sujet clos.** Les montants affichés
   (99 / 129 / 240 € TTC, déplacement gratuit, sans majoration) ont été posés
   **par l'agence le 24/08/2026**, calés sous un relevé concurrent, parce que
   l'artisan a dit ne pas avoir de tarifs arrêtés. Il facturera ce que le site
   annonce, ou il y aura litige. C'est la dette la plus urgente du dossier.
2. Supprimer le brouillon web `Degorgement - Bron et Lyon - Search`, devenu
   inutile — son nom diffère, il ne fait doublon avec rien mais encombre.
3. ✅ **Fait le 24/08/2026.** Trois actions de conversion créées par
   `POST /google-ads/conversions` de Flowcontent, une par chemin de contact :

   | Action | ID | Libellé gtag |
   |---|---|---|
   | Plombio — Lead par téléphone | `7732671333` | `3i1FCOXmnOccEI2v7q9E` |
   | Plombio — Lead WhatsApp | `7732465151` | `FiogCP-bkOccEI2v7q9E` |
   | Plombio — Demande de rappel | `7732671246` | `NGR5CI7mnOccEI2v7q9E` |

   `PLOMBIER_ADS_ID` = `AW-18353985421` — **le même compte que Serrio**, donc
   le même identifiant de conversion ; ce sont les libellés qui séparent les
   deux marques. Variables posées sur le projet Vercel `plombio`, redéployé,
   les quatre balises sont vérifiées en ligne.

   ⚠️ Les trois actions sont créées **primaires** par le service. Elles ont été
   repassées en **secondaires** aussitôt : primaires, elles seraient entrées
   dans les objectifs du compte, donc dans les enchères de la campagne
   serrurerie à 300 €/jour. La campagne Plombio enchérit sur `MAXIMIZE_CLICKS`
   et n'en a pas besoin ; les conversions restent mesurées.
4. Déployer le playbook `degorgement` (`./deploy.sh`, blue-green sans coupure).

### Plombio est devenu un site de DÉBOUCHAGE (24/08/2026, soir)

**Décision structurante.** Plombio générait deux pages par ville — une plomberie
(`/lyon/`) et une dégorgement (`/degorgement/lyon/`) — qui se disputaient la même
requête locale, et son accueil tombait dans la branche « multi-métier » du
générateur : la section prestations n'affichait que **2 cartes dans une grille
prévue pour 3**, avec un vide à droite.

`BUILDS["plombier"]` est donc passé à `service_keys=("degorgement",)` /
`primary_service_key="degorgement"`. Conséquences :

- **282 pages → 143**, une ville = une page, à la racine, **exactement
  l'architecture de Serrio**
- Accueil : titre « Plombio | Dégorgement urgence 24/7 », H1 « Dégorgement de
  confiance, ville par ville », **6 cartes de prestations** (la branche
  mono-métier), avis « Intervention dégorgement », nav épurée
- **143/143 titres ≤ 60 et meta-descriptions dans 120-160**, 0 ancre morte
  ⚠️ mesurer après `html.unescape()` : `&#x27;` compte 6 caractères bruts et
  fait croire à des dépassements sur les villes à apostrophe (L'Isle-d'Abeau,
  Saint-Martin-d'Hères)
- **Le contenu plomberie n'est pas supprimé** : il reste dans `SERVICES` et se
  rallume en remettant `"plombier"` dans `service_keys`

**Redirections 301** posées dans `vercel.json` pour les anciennes URL indexées et
utilisées comme destination par les annonces :
`/degorgement/:slug/` → `/:slug/`.
⚠️ **Piège Vercel** : avec `trailingSlash: true`, la normalisation de l'URL a lieu
**avant** l'évaluation des redirects. Une source sans slash final
(`/degorgement/:slug`) n'est donc jamais atteinte et la page tombe en 404 — la
source doit porter le slash.

Les CSV Ads ont été régénérés : les URL finales pointent désormais vers
`https://www.plombio.fr/<ville>/`. Le chemin d'affichage des annonces reste
`degorgement/<ville>` — décoratif, il décrit bien la page.

### www.plombio.fr est en ligne (24/08/2026, après-midi)

Domaine acheté chez **Infomaniak** et branché sur Vercel le jour même :

- `A @ → 216.150.1.1`, `CNAME www → 72cb9a4e97540290.vercel-dns-016.com.`
  (⚠️ CNAME **unique par projet**, différent de celui de serrio)
- Apex → www en **308**, HTTPS actif
- **`SITE_NOINDEX=0`** et redéployé : `robots.txt` normal, `Sitemap:` déclaré,
  `index, follow`, **282 URL** dont **139 pages `/degorgement/<ville>/`**
- `SMTP_USER=contact@plombio.fr`, `SMTP_HOST=mail.infomaniak.com`, `SMTP_PORT=465`

Différences Infomaniak / OVH : **aucun enregistrement de parking** (le piège des
`AAAA` IPv6 d'OVH ne se pose pas), et la messagerie est pré-câblée dès l'achat
(MX, SPF, **DKIM**, **DMARC `p=reject`**, SRV) — ne pas y toucher. Le certificat
n'est pas venu seul : il a fallu `POST /v9/projects/plombio/domains/<d>/verify`
puis `POST /v7/certs {"cns":[...]}`.

**✅ Formulaire de rappel Plombio OPÉRATIONNEL (24/08/2026)** — testé en production :
`POST /api/callback/` → **200 `{"ok": true}` en 2,6 s**, e-mail réellement parti.
Garde-fous vérifiés : nom vide → 422, téléphone invalide → 422. Bouton passé à
« Demander un rappel ».

Le mot de passe SMTP est un **mot de passe d'application Infomaniak** (Service Mail →
l'adresse → onglet *Appareil connecté* → « Ajouter un appareil » → **« Configurer
moi-même »**, qui génère un mot de passe dédié). Avantage sur Serrio : il est
**indépendant du mot de passe de la boîte**, donc l'artisan peut configurer son
téléphone sans casser le formulaire. Compte Infomaniak : **`strategie@flowcontent.io`**
(organisation FLOWBLOG) — noter que `plombio.fr` est donc détenu par FlowContent.

**Ce qui manque encore pour lancer Plombio** : le compte Ads Plombio sous le MCC, les
variables `PLOMBIER_ADS_ID` / `PLOMBIER_ADS_CALL_LABEL` (+ redéploiement), la
propriété Search Console, et la validation du seul tarif chiffré du site
(« débouchage simple à partir de 120 € »).

⚠️ `/degorgement/` seul renvoie 404 (seules les pages ville existent), comme
`/serrurier/` sur Serrio. Absent du sitemap, sans effet SEO.

⚠️ **Échéance inchangée : validation de l'annonceur avant le 31 août 2026**, sans
quoi le compte passe en veille — un compte Plombio créé sous le même MCC dépend
de la même identité.

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
