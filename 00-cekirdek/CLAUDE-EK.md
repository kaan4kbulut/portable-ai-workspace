# Claude Code'a özel ekler

Ortak kurallar `AGENTS.md`'de; bunlar yalnızca Claude Code içindir.

- Kapsamı belirsiz ya da üç dosyadan fazlasına dokunan işte önce **plan modu**; küçük, net işte doğrudan uygula.
- Araştırma ve geniş taramalarda alt ajan kullan (`Explore`); inceleme için `inceleyici` alt ajanı (salt okunur).
  Düzen/kurulum sorunlarında `bakimci` alt ajanı ya da `/bakim`.
- Oturum biterken `/kapat`; karar alınınca `/karar`; gelen kutusu için `/ayikla`; düzen kontrolü `/denetle`.
- Otomatik hafıza bu depoda kapalıdır (`autoMemoryEnabled: false`). Kalıcı bilgi `40-hafiza/`'ya yazılır.
- Hook'lar engellediğinde kuralı aşmaya çalışma; nedenini kullanıcıya söyle.
- Commit'e `Co-Authored-By` satırı eklenmez (`attribution` kapalı); commit zaten yalnızca kullanıcı isteyince atılır.
