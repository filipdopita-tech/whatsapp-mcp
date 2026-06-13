# Graph Report - /Users/filipdopita/Code/whatsapp-mcp  (2026-05-27)

## Corpus Check
- 6 files · ~120,092 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 99 nodes · 149 edges · 17 communities detected
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 11 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]

## God Nodes (most connected - your core abstractions)
1. `MessageStore` - 8 edges
2. `extractMediaInfo()` - 8 edges
3. `MediaDownloader` - 8 edges
4. `handleMessage()` - 7 edges
5. `main()` - 6 edges
6. `handleHistorySync()` - 6 edges
7. `list_messages()` - 6 edges
8. `get_message_context()` - 6 edges
9. `Chat` - 5 edges
10. `format_message()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `send_audio_message()` --calls--> `convert_to_opus_ogg_temp()`  [INFERRED]
  /Users/filipdopita/Code/whatsapp-mcp/whatsapp-mcp-server/whatsapp.py → /Users/filipdopita/Code/whatsapp-mcp/whatsapp-mcp-server/audio.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.15
Nodes (18): analyzeOggOpus(), downloadMedia(), extractDirectPathFromURL(), extractTextContent(), GetChatName(), handleHistorySync(), handleMessage(), main() (+10 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (17): Contact, download_media(), format_message(), format_messages_list(), get_last_interaction(), get_message_context(), get_sender_name(), list_messages() (+9 more)

### Community 2 - "Community 2"
Cohesion: 0.2
Nodes (10): MessageStore, Chat, get_chat(), get_contact_chats(), get_direct_chat_by_contact(), list_chats(), Get chats matching the specified criteria., Get all chats involving the contact.          Args:         jid: The contact's J (+2 more)

### Community 3 - "Community 3"
Cohesion: 0.33
Nodes (2): extractMediaInfo(), MediaDownloader

### Community 4 - "Community 4"
Cohesion: 0.4
Nodes (5): convert_to_opus_ogg(), convert_to_opus_ogg_temp(), Convert an audio file to Opus format in an Ogg container.          Args:, Convert an audio file to Opus format in an Ogg container and store in a temporar, send_audio_message()

### Community 5 - "Community 5"
Cohesion: 0.4
Nodes (4): get_last_interaction(), Get most recent WhatsApp message involving the contact.          Args:         j, Send a WhatsApp message to a person or group. For group chats use the JID., send_message()

### Community 6 - "Community 6"
Cohesion: 1.0
Nodes (2): get_direct_chat_by_contact(), Get WhatsApp chat metadata by sender phone number.          Args:         sender

### Community 7 - "Community 7"
Cohesion: 1.0
Nodes (2): list_messages(), Get WhatsApp messages matching specified criteria with optional context.

### Community 8 - "Community 8"
Cohesion: 1.0
Nodes (2): Search WhatsApp contacts by name or phone number.          Args:         query:, search_contacts()

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (2): get_contact_chats(), Get all WhatsApp chats involving the contact.          Args:         jid: The co

### Community 10 - "Community 10"
Cohesion: 1.0
Nodes (2): list_chats(), Get WhatsApp chats matching specified criteria.          Args:         query: Op

### Community 11 - "Community 11"
Cohesion: 1.0
Nodes (2): Send any audio file as a WhatsApp audio message to the specified recipient. For, send_audio_message()

### Community 12 - "Community 12"
Cohesion: 1.0
Nodes (2): get_message_context(), Get context around a specific WhatsApp message.          Args:         message_i

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (2): get_chat(), Get WhatsApp chat metadata by JID.          Args:         chat_jid: The JID of t

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (2): download_media(), Download media from a WhatsApp message and get the local file path.          Arg

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (2): Send a file such as a picture, raw audio, video or document via WhatsApp to the, send_file()

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Determine if chat is a group based on JID pattern.

## Knowledge Gaps
- **30 isolated node(s):** `Message`, `SendMessageResponse`, `SendMessageRequest`, `DownloadMediaRequest`, `DownloadMediaResponse` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 6`** (2 nodes): `get_direct_chat_by_contact()`, `Get WhatsApp chat metadata by sender phone number.          Args:         sender`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (2 nodes): `list_messages()`, `Get WhatsApp messages matching specified criteria with optional context.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 8`** (2 nodes): `Search WhatsApp contacts by name or phone number.          Args:         query:`, `search_contacts()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 9`** (2 nodes): `get_contact_chats()`, `Get all WhatsApp chats involving the contact.          Args:         jid: The co`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 10`** (2 nodes): `list_chats()`, `Get WhatsApp chats matching specified criteria.          Args:         query: Op`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 11`** (2 nodes): `Send any audio file as a WhatsApp audio message to the specified recipient. For`, `send_audio_message()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 12`** (2 nodes): `get_message_context()`, `Get context around a specific WhatsApp message.          Args:         message_i`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (2 nodes): `get_chat()`, `Get WhatsApp chat metadata by JID.          Args:         chat_jid: The JID of t`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `download_media()`, `Download media from a WhatsApp message and get the local file path.          Arg`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `Send a file such as a picture, raw audio, video or document via WhatsApp to the`, `send_file()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Determine if chat is a group based on JID pattern.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `MessageStore` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.101) - this node is a cross-community bridge._
- **Why does `convert_to_opus_ogg_temp()` connect `Community 4` to `Community 2`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **What connects `Message`, `SendMessageResponse`, `SendMessageRequest` to the rest of the system?**
  _30 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.14 - nodes in this community are weakly interconnected._