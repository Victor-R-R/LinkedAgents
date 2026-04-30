---
name: linkedin-messages-agent
description: >
  Manage LinkedIn inbox via MCP tools: read messages, reply, search conversations, and draft contextual responses.
  Trigger: "lire mes messages LinkedIn", "répondre à mes messages", "inbox LinkedIn", "check LinkedIn messages",
  "gérer ma messagerie LinkedIn", "voir mes conversations LinkedIn", "répondre à [nom] sur LinkedIn".
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

# LinkedIn Messages Agent

Gestion complète de la messagerie LinkedIn via les outils MCP natifs.

> Ce skill utilise directement les outils MCP LinkedIn — pas d'API REST, pas de token à gérer.
> Les outils MCP gèrent la session LinkedIn de façon transparente.

---

## When to Use

- L'utilisateur veut lire sa boîte de réception LinkedIn
- L'utilisateur veut répondre à un ou plusieurs messages
- L'utilisateur veut chercher une conversation spécifique
- L'utilisateur veut rédiger une réponse contextuelle (prospection, suivi, networking)
- L'utilisateur veut trier ou résumer ses messages non lus

---

## MCP Tools Available

| Outil MCP | Usage |
|-----------|-------|
| `mcp__linkedin__get_inbox` | Récupère la liste des conversations récentes |
| `mcp__linkedin__get_conversation` | Lit le fil complet d'une conversation |
| `mcp__linkedin__search_conversations` | Cherche dans toutes les conversations par mot-clé |
| `mcp__linkedin__send_message` | Envoie un message via la compose overlay (contacts directs) |
| `mcp__linkedin__reply_in_thread` | Répond dans un fil existant (contourne les restrictions) |
| `mcp__linkedin__connect_with_person` | Envoie une demande de connexion avec note (max 300 chars) |
| `mcp__linkedin__get_person_profile` | Récupère le profil de l'interlocuteur pour contexte |

### Quel outil utiliser pour envoyer un message ?

```
Contact existant (fil actif) → reply_in_thread(thread_id, linkedin_username)
Contact connecté (pas de fil) → send_message(linkedin_username)  [si composer_unavailable → connect_with_person]
Nouveau contact non connecté  → connect_with_person(linkedin_username, note)
```

**`reply_in_thread` vs `send_message`** :
- `send_message` utilise la compose overlay LinkedIn → échoue si la personne bloque les messages de non-relations (retourne `composer_unavailable`)
- `reply_in_thread` navigue via le profil → recherche dans l'inbox → clique sur le fil → ouvre le volet thread React → fonctionne pour tous les contacts avec qui tu as déjà échangé, indépendamment des paramètres de confidentialité
- `reply_in_thread` requiert `linkedin_username` pour un lookup fiable (le thread_id seul ne suffit pas en mode headless)

---

## Standard Workflows

### 1. Lecture de l'inbox

```
1. Appeler get_inbox pour lister les conversations récentes
2. Identifier les conversations non lues / urgentes
3. Pour chaque conversation intéressante → get_conversation (fil complet)
4. Résumer : qui a écrit quoi, depuis quand, quelle action requise
```

**Format de résumé inbox** :
```
📬 Inbox LinkedIn — {date}

Non lus ({N}) :
  • [Prénom Nom] — {extrait du dernier message} — il y a {durée}
  • ...

À répondre ({N}) :
  • [Prénom Nom] — {contexte en 1 ligne}
  • ...

Aucune action requise ({N}) : ...
```

---

### 2. Réponse contextuelle

Avant de rédiger une réponse :

```
1. get_conversation → lire tout le fil pour comprendre le contexte
2. get_person_profile → récupérer titre, entreprise, parcours de l'interlocuteur
3. Analyser : quel est le but du message ? (recrutement, prospection, networking, collaboration)
4. Rédiger une réponse adaptée au contexte (voir règles ci-dessous)
5. Confirmer avec l'utilisateur avant d'envoyer
6. send_message → envoyer
```

**Toujours confirmer avant d'envoyer.** Ne jamais envoyer automatiquement.

---

### 3. Recherche de conversation

```
1. search_conversations avec le mot-clé fourni
2. Afficher les résultats avec : nom, extrait, date
3. Si l'utilisateur veut ouvrir une conversation → get_conversation
```

---

## Règles de Rédaction de Réponses

### Ton par type de message

| Type de message reçu | Ton recommandé | Longueur |
|----------------------|----------------|----------|
| Recrutement entrant | Chaleureux + direct | 3-5 lignes |
| Prospection commerciale | Neutre + poli | 2-3 lignes |
| Networking / intro | Ouvert + engageant | 4-6 lignes |
| Collaboration technique | Professionnel + précis | 5-8 lignes |
| Suivi sans réponse | Bref + relance douce | 2-3 lignes |
| Demande d'info | Utile + concis | selon complexité |

### Structure d'une bonne réponse LinkedIn

```
[Accroche personnalisée — référence à leur message ou contexte]
[Corps — réponse directe à leur demande]
[CTA clair — prochaine étape concrète ou question]
```

### À éviter absolument

- Les formules génériques : "Merci pour votre message"
- Les réponses > 10 lignes (LinkedIn n'est pas un email)
- Les pièces jointes non demandées
- Les pitches commerciaux dans une première réponse

---

## Gestion de session

Si `mcp__linkedin__close_session` est disponible, l'appeler en fin de session pour libérer les ressources.

---

## Flux complet type

```
Utilisateur : "Lis mes messages LinkedIn"
  → get_inbox
  → Résumer les conversations non lues
  → Proposer : "Veux-tu que je lise et résume [conversation X] ?"

Utilisateur : "Oui, et prépare une réponse pour [nom]"
  → get_conversation(conversation_id)
  → get_person_profile(profile_id) — optionnel, pour contexte
  → Rédiger 1-2 variantes de réponse
  → Présenter à l'utilisateur pour validation
  → Sur confirmation : send_message

Utilisateur : "Cherche si j'ai un message de quelqu'un chez [entreprise]"
  → search_conversations(query: "entreprise")
  → Afficher résultats
```

---

## Intégration avec les autres LinkedIn Agents

```
linkedin-messages-agent
├── linkedin-profile-agent  → enrichir le contexte d'un interlocuteur
├── linkedin-research-agent → si le message est lié à une entreprise/topic à creuser
└── linkedin-orchestrator   → si les messages révèlent des opportunités de posts
```

---

## Notes importantes

- **Vie privée** : Ne jamais stocker ou logger le contenu des messages sans accord explicite de l'utilisateur
- **Rate limits** : Espacer les appels MCP si lecture de nombreuses conversations (attendre 1-2s entre chaque `get_conversation`)
- **Contexte** : Toujours lire le fil complet avant de rédiger — un message isolé peut être mal interprété
- **Langue** : Répondre dans la langue du message reçu (FR si FR, EN si EN)
