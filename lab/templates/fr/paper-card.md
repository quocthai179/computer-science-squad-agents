---
id: <paper-id>
title: <titre de l'article>
year: <année>
venue: <conférence ou revue>
link: <url>
pass: 2                   # 1 = scout, 2 = reader, 3 = --deep (reproduction)
relevance: <0-3>
tags: []
fulltext: <papers/raw/<id>/paper.tex ou .pdf>
---

# <id> : <titre de l'article> (<année>, <venue>)

## En une phrase

<ce que fait l'article et ce qu'il trouve, en une phrase>

## Les cinq C

- **Category (catégorie) :** <type d'article : nouvelle méthode, analyse, benchmark, état de l'art, système...>
- **Context (contexte) :** <sur quels travaux il s'appuie ; les 2 à 4 articles les plus proches>
- **Correctness (justesse) :** <les hypothèses sont-elles raisonnables ?>
- **Contributions :** <les contributions principales, 3 au plus>
- **Clarity (clarté) :** <est-il bien écrit ?>

## Affirmations principales

> Pour chaque affirmation : citation mot pour mot de 25 mots au plus, avec sa localisation (section, tableau, figure, page).

1. « <citation> » — §<section> / Table <n>

## Méthode

<assez pour reproduire au niveau des idées : entrée, sortie, architecture ou algorithme, fonction de perte, données, coût>

## Expérience clé

<sur quelle expérience repose l'affirmation principale ? quelles lignes de base ? combien de graines aléatoires ? permet-elle de distinguer l'hypothèse des auteurs d'une explication plus banale ?>

| configuration | métrique | valeur rapportée | localisation |
|---|---|---|---|

## Quatre questions sceptiques (Lipton & Steinhardt)

- **Explication ou spéculation ?**
- **L'origine de l'amélioration a-t-elle été isolée par ablation ? La ligne de base est-elle réglée avec le même soin ?**
- **Les mathématiques éclairent-elles, ou servent-elles à impressionner ?**
- **La terminologie est-elle employée au-delà de son sens ?**

## Hypothèses implicites et limites

## Quel problème de la réserve débloque-t-il ?

<renvoyer à une ligne de research/ideas/backlog.md, ou « aucun »>

## Si vous le reproduisez

- données :
- calcul estimé :
- où l'on risque de se tromper :
- plus petit résultat qui vaut la peine d'être reproduit :

## Explain-back (restitution)

> Trois questions auxquelles l'utilisateur répond sans regarder la fiche. Le Lead compare les réponses à la fiche.

1.
2.
3.
