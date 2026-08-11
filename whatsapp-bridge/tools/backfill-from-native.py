#!/usr/bin/env python3
"""Doplni do WhatsApp bridge DB zpravy, ktere bridge propasl behem vypadku.

Zdroj pravdy = nativni WhatsApp.app databaze (ChatStorage.sqlite), ktera je
uplna, protoze aplikace bezi porad. Bridge od 3. 8. 2026 spadl 999x
(nestabilni sit v zahranici) a v techto oknech zpravy neprijal.

Parovani je presne: ZSTANZAID v nativni DB == messages.id v bridge DB.

Spousti se s --apply, jinak jen dry-run.
Dopita 2026-08-11
"""
import argparse
import datetime
import os
import re
import sqlite3
import sys
from collections import Counter

APPLE_EPOCH = 978307200  # 2001-01-01 vs 1970-01-01

# Odvozeno empiricky z 23 208 zprav, ktere maji obe DB spolecne.
TYPE_MAP = {0: "", 1: "image", 2: "video", 3: "audio", 7: "", 8: "document", 11: "video"}

EXT = {"image": "jpg", "video": "mp4", "audio": "ogg", "document": "bin"}


def own_ids(bridge):
    """Vlastni LID a telefonni ID se ctou z DB, nejsou v kodu.

    Bridge uklada u odchozich zprav jednou LID a jednou telefonni cislo podle
    typu chatu. Obe hodnoty jsou proste nejcastejsi sender u is_from_me = 1.
    """
    lid = bridge.execute(
        "SELECT sender FROM messages WHERE is_from_me = 1 AND chat_jid LIKE '%@lid' "
        "GROUP BY sender ORDER BY count(*) DESC LIMIT 1"
    ).fetchone()
    phone = bridge.execute(
        "SELECT sender FROM messages WHERE is_from_me = 1 "
        "AND chat_jid LIKE '%@s.whatsapp.net' GROUP BY sender ORDER BY count(*) DESC LIMIT 1"
    ).fetchone()
    if not lid or not phone:
        raise SystemExit("CHYBA: v bridge DB nejsou odchozi zpravy, nelze urcit vlastni ID")
    return lid[0], phone[0]


def jid_user(jid):
    """22360103088266@lid -> 22360103088266"""
    if not jid:
        return ""
    return jid.split("@", 1)[0]


def build_offset_map(bridge):
    """Den -> UTC offset, jak ho bridge realne zapisoval.

    Bridge uklada cas jako lokalni cas stroje vcetne offsetu ('...+02:00').
    Offset se v case meni (letni cas, jina casova zona pri cestovani), takze
    doplnene zpravy musi nest stejny offset jako sousedni radky. Jinak by se
    razeni podle timestamp stringu rozjelo o hodinu.
    """
    rows = bridge.execute(
        "SELECT substr(timestamp,1,10), substr(timestamp,20) FROM messages "
        "WHERE length(timestamp)=25"
    ).fetchall()
    per_day = {}
    for day, off in rows:
        per_day.setdefault(day, Counter())[off] += 1
    return {day: c.most_common(1)[0][0] for day, c in per_day.items()}


def nearest_offset(offsets, day, sorted_days):
    if day in offsets:
        return offsets[day]
    best = None
    for d in sorted_days:
        if best is None or abs_days(d, day) < abs_days(best, day):
            best = d
    return offsets.get(best, "+02:00")


def abs_days(a, b):
    from datetime import date
    da = date(*map(int, a.split("-")))
    db = date(*map(int, b.split("-")))
    return abs((da - db).days)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    ap.add_argument("--bridge", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    native = sqlite3.connect(f"file:{args.native}?immutable=1", uri=True)
    native.text_factory = lambda b: b.decode("utf-8", "replace")
    bridge = sqlite3.connect(args.bridge)

    OWN_LID, OWN_PHONE = own_ids(bridge)
    offsets = build_offset_map(bridge)
    sorted_days = sorted(offsets)
    if not sorted_days:
        print("CHYBA: bridge DB nema zadne pouzitelne timestampy", file=sys.stderr)
        return 2

    have = {r[0] for r in bridge.execute("SELECT id FROM messages")}
    known_chats = {r[0] for r in bridge.execute("SELECT jid FROM chats")}

    placeholders = ",".join("?" * len(TYPE_MAP))
    rows = native.execute(
        f"""
        SELECT m.ZSTANZAID, cs.ZCONTACTJID, cs.ZPARTNERNAME, m.ZISFROMME,
               m.ZMESSAGETYPE, m.ZTEXT, m.ZMESSAGEDATE, m.ZFROMJID,
               gm.ZMEMBERJID, mi.ZMEDIAURL, mi.ZFILESIZE, mi.ZMEDIALOCALPATH
        FROM ZWAMESSAGE m
        JOIN ZWACHATSESSION cs ON m.ZCHATSESSION = cs.Z_PK
        LEFT JOIN ZWAGROUPMEMBER gm ON m.ZGROUPMEMBER = gm.Z_PK
        LEFT JOIN ZWAMEDIAITEM  mi ON mi.ZMESSAGE = m.Z_PK
        WHERE m.ZSTANZAID IS NOT NULL
          AND cs.ZCONTACTJID NOT LIKE '%@status'
          AND cs.ZCONTACTJID LIKE '%@%'
          AND m.ZMESSAGETYPE IN ({placeholders})
        """,
        tuple(TYPE_MAP),
    ).fetchall()

    to_insert, new_chats, skipped = [], {}, Counter()

    for (stanza, chat_jid, partner, from_me, mtype, text, mdate, from_jid,
         member_jid, media_url, file_size, local_path) in rows:
        if stanza in have:
            skipped["uz_v_bridge"] += 1
            continue
        if mdate is None:
            skipped["bez_data"] += 1
            continue

        media_type = TYPE_MAP.get(mtype, "")
        if not media_type and not (text or "").strip():
            skipped["prazdna"] += 1
            continue

        ts = int(mdate) + APPLE_EPOCH
        day = datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d")
        off = nearest_offset(offsets, day, sorted_days)
        sign = 1 if off[0] == "+" else -1
        secs = sign * (int(off[1:3]) * 3600 + int(off[4:6]) * 60)
        local = datetime.datetime.utcfromtimestamp(ts + secs)
        timestamp = local.strftime("%Y-%m-%d %H:%M:%S") + off

        if from_me:
            sender = OWN_PHONE if chat_jid.endswith("@s.whatsapp.net") else OWN_LID
        elif chat_jid.endswith("@g.us"):
            sender = jid_user(member_jid) or jid_user(from_jid)
        else:
            sender = jid_user(chat_jid)
        if not sender:
            skipped["bez_odesilatele"] += 1
            continue

        filename = ""
        if media_type:
            if local_path:
                filename = os.path.basename(local_path)
            if not filename:
                stamp = local.strftime("%Y%m%d_%H%M%S")
                filename = f"{media_type}_{stamp}.{EXT[media_type]}"

        if chat_jid not in known_chats and chat_jid not in new_chats:
            new_chats[chat_jid] = (partner or jid_user(chat_jid), timestamp)

        to_insert.append(
            (stanza, chat_jid, sender, text or "", timestamp, 1 if from_me else 0,
             media_type, filename, media_url or "", int(file_size or 0))
        )

    # jmena chatu: bridge ma u casti chatu jen holé cislo, nativni app zna jmeno
    numeric = re.compile(r"^\d+$")
    name_fixes = []
    native_names = {
        j: n
        for j, n in native.execute(
            "SELECT ZCONTACTJID, ZPARTNERNAME FROM ZWACHATSESSION "
            "WHERE ZPARTNERNAME IS NOT NULL AND trim(ZPARTNERNAME) <> ''"
        )
    }
    # druhy zdroj jmen: push name, ktery app zna i u @lid kontaktu bez ulozeneho jmena
    push_names = {
        j: n
        for j, n in native.execute(
            "SELECT ZJID, ZPUSHNAME FROM ZWAPROFILEPUSHNAME "
            "WHERE ZPUSHNAME IS NOT NULL AND trim(ZPUSHNAME) <> ''"
        )
    }
    def is_placeholder(n):
        """'+43 660 7409965' nebo '120363...' - neni to jmeno, je to jen adresa."""
        if not n:
            return True
        stripped = re.sub(r"[^0-9+]", "", n)
        return stripped == re.sub(r"[\s‎‏‪-‮()\-]", "", n)

    for jid, name in bridge.execute("SELECT jid, name FROM chats"):
        cur = (name or "").strip()
        # vlastni ID jako jmeno cizi konverzace je chyba bridge - vypada to,
        # ze pulka chatu je stejny clovek. Takove jmeno je horsi nez zadne.
        own_id_bug = cur in (OWN_LID, OWN_PHONE) and jid_user(jid) != cur
        nat = (native_names.get(jid) or "").strip()
        push = (push_names.get(jid) or "").strip()

        real = ""
        if own_id_bug or is_placeholder(cur):
            # bridge nema pouzitelne jmeno - vezmi cokoli lepsiho
            for cand in (nat, push):
                if cand and not is_placeholder(cand):
                    real = cand
                    break
            if not real and own_id_bug:
                real = jid_user(jid)  # radeji cislo chatu nez cizi identita
        elif nat and not is_placeholder(nat):
            # obe strany maji jmeno - nativni app je zivy zdroj pravdy
            # (bridge si drzi stara jmena skupin z doby prvniho sync)
            real = nat

        if not real or real == cur:
            continue
        name_fixes.append((real, jid))

    print(f"zprav k doplneni : {len(to_insert)}")
    print(f"novych chatu     : {len(new_chats)}")
    print(f"oprav jmen chatu : {len(name_fixes)}")
    print(f"preskoceno       : {dict(skipped)}")

    if not args.apply:
        print("\n(dry-run, nic se nezapsalo - spust s --apply)")
        for r in to_insert[:5]:
            print("  ukazka:", r[4], r[1], r[2], repr((r[3] or r[6])[:50]))
        return 0

    with bridge:
        bridge.executemany(
            "INSERT OR IGNORE INTO chats (jid, name, last_message_time) VALUES (?,?,?)",
            [(j, n, t) for j, (n, t) in new_chats.items()],
        )
        bridge.executemany(
            "INSERT OR IGNORE INTO messages "
            "(id, chat_jid, sender, content, timestamp, is_from_me, media_type, "
            " filename, url, file_length) VALUES (?,?,?,?,?,?,?,?,?,?)",
            to_insert,
        )
        bridge.executemany("UPDATE chats SET name = ? WHERE jid = ?", name_fixes)
        # last_message_time musi sedet, jinak by se chat radil spatne v list_chats
        bridge.execute(
            "UPDATE chats SET last_message_time = ("
            "  SELECT max(timestamp) FROM messages WHERE messages.chat_jid = chats.jid"
            ") WHERE EXISTS (SELECT 1 FROM messages WHERE messages.chat_jid = chats.jid)"
        )
    print("\nzapsano.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
