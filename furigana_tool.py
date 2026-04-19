import uno
import unohelper
import csv
import time
import os
import re
import platform

# --- 1. DYNAMISCHE PAD-DETECTIE (OS) ---
current_os = platform.system()
if current_os == "Windows":
    BASE_DIR = r"C:\Files\FuriganaTool"
else:
    BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "FuriganaTool")

CSV_PATH = os.path.join(BASE_DIR, "JP_Total_List.CSV")
CSV_PATH_2 = os.path.join(BASE_DIR, "DO_NOT_FURIGANIZE.txt")
DICT_PATH = os.path.join(BASE_DIR, "dictionary.csv")
RULES_PATH = os.path.join(BASE_DIR, "rules.csv")
NEW_ENTRIES_PATH = os.path.join(BASE_DIR, "new_entries.csv")

# --- 2. TAALINSTELLINGEN EN VERTALEN ---
CURRENT_LANG = "EN" # Standaard taal

TRANSLATIONS = {
    "EN": {
        "add": "Add Furigana (All)",
        "remove": "Remove Furigana",
        "new": "New Entry (Selected)",
        "known": "Mark as Known",
        "edit": "Edit Known List",
        "dict": "Lookup Dictionary",
        "switch": "Switch to Japanese / 日本語に切り替え",
        "title": "Furigana Tool Menu"
    },
    "JP": {
        "add": "振り仮名を付ける（全部）",
        "remove": "振り仮名を消す",
        "new": "新しい登録（選択中）",
        "known": "既知としてマーク",
        "edit": "既知のリストを編集",
        "dict": "辞書を引く",
        "switch": "Switch to English / 英語に切り替え",
        "title": "ふりがなツールメニュー"
    }
}

# --- LIVE ROMAJI NAAR KANA CONVERSIE ---
KANA_MAP = {
    # Basis klanken
    'ka':'か','ki':'き','ku':'く','ke':'け','ko':'こ',
    'sa':'さ','shi':'し','su':'す','se':'せ','so':'そ',
    'ta':'た','chi':'ち','tsu':'つ','te':'て','to':'と',
    'na':'な','ni':'に','nu':'ぬ','ne':'ね','no':'の',
    'ha':'は','hi':'ひ','fu':'ふ','he':'へ','ho':'ほ',
    'ma':'ま','mi':'み','mu':'む','me':'め','mo':'も',
    'ya':'や','yu':'ゆ','yo':'よ',
    'ra':'ら','ri':'り','ru':'る','re':'れ','ro':'ろ',
    'wa':'わ','wo':'を','nn':'ん','n ':'ん',
    
    # Dakuten (G/Z/D/B)
    'ga':'が','gi':'ぎ','gu':'ぐ','ge':'げ','go':'ご',
    'za':'ざ','ji':'じ','zu':'ず','ze':'ぜ','zo':'ぞ',
    'da':'だ','di':'ぢ','du':'づ','de':'で','do':'ど',
    'ba':'ば','bi':'び','bu':'ぶ','be':'べ','bo':'ぼ',
    
    # Handakuten (P)
    'pa':'ぱ','pi':'ぴ','pu':'ぷ','pe':'ぺ','po':'ぽ',
    
    # Alternatieve invoer (L-reeks voor R)
    'la':'ら','li':'り','lu':'る','le':'れ','lo':'ろ',
    
    # Digraphs (Kombinatie klanken)
    'kya':'きゃ','kyu':'きゅ','kyo':'きょ',
    'sha':'しゃ','shu':'しゅ','sho':'しょ',
    'cha':'ちゃ','chu':'ちゅ','cho':'ちょ',
    'nya':'にゃ','nyu':'にゅ','nyo':'nyo',
    'hya':'ひゃ','hyu':'ひゅ','hyo':'hyo',
    'mya':'みゃ','myu':'みゅ','myo':'myo',
    'rya':'りゃ','ryu':'りゅ','ryo':'ryo',
    'gya':'ぎゃ','gyu':'ぎゅ','gyo':'ぎょ',
    'ja':'じゃ','ju':'じゅ','jo':'じょ',
    'bya':'びゃ','byu':'びゅ','byo':'byo',
    'pya':'ぴゃ','pyu':'ぴゅ','pyo':'pyo',
    
    # Losse klinkers
    'a':'あ','i':'い','u':'う','e':'え','o':'お'
}

def convert_string_to_kana(text):
    res = text
    for romaji in sorted(KANA_MAP.keys(), key=len, reverse=True):
        res = res.replace(romaji, KANA_MAP[romaji])
    res = re.sub(r'([kkssppttggzzjdbhr])\1', r'っ\1', res)
    return res

class LiveKanaListener(unohelper.Base, uno.getClass("com.sun.star.awt.XTextListener")):
    def __init__(self, control):
        self.control = control
        self.active = False
    def textChanged(self, event):
        if self.active: return
        self.active = True
        try:
            current_text = self.control.getText()
            converted = convert_string_to_kana(current_text)
            if current_text != converted:
                self.control.setText(converted)
                pos = len(converted)
                self.control.setSelection(uno.createUnoStruct("com.sun.star.awt.Selection", pos, pos))
        finally:
            self.active = False
    def disposing(self, event): pass

# --- UI HELPERS ---

def msgbox(message, title="Furigana Tool", buttons=1, type_msg="infobox"):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    parent = toolkit.getDesktopWindow()
    msg = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return msg.execute()

def input_box_kana(message, title="Kana Input"):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", ctx)
    dialog_model.Width = 160 ; dialog_model.Height = 80 ; dialog_model.Title = title
    label = dialog_model.createInstance("com.sun.star.awt.UnoControlFixedTextModel")
    label.PositionX = 10 ; label.PositionY = 10 ; label.Width = 140 ; label.Height = 25 ; label.Label = message
    dialog_model.insertByName("label", label)
    edit_model = dialog_model.createInstance("com.sun.star.awt.UnoControlEditModel")
    edit_model.PositionX = 10 ; edit_model.PositionY = 35 ; edit_model.Width = 140 ; edit_model.Height = 15
    dialog_model.insertByName("edit", edit_model)
    btn_model = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
    btn_model.Name = "ok_btn" ; btn_model.Label = "OK" ; btn_model.PositionX = 50 ; btn_model.PositionY = 55 ; btn_model.Width = 60 ; btn_model.Height = 15
    btn_model.PushButtonType = 1 
    dialog_model.insertByName("ok_btn", btn_model)
    dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", ctx)
    dialog.setModel(dialog_model)
    edit_control = dialog.getControl("edit")
    listener = LiveKanaListener(edit_control)
    edit_control.addTextListener(listener)
    dialog.setVisible(True)
    res = edit_control.getText() if dialog.execute() == 1 else None
    dialog.dispose()
    return res

def is_in_selection(found_item, selection):
    for i in range(selection.getCount()):
        sel_range = selection.getByIndex(i)
        text_obj = sel_range.getText()
        if text_obj.compareRegionEnds(sel_range.getStart(), found_item.getStart()) >= 0 and \
           text_obj.compareRegionEnds(sel_range.getEnd(), found_item.getEnd()) <= 0:
            return True
    return False

# --- KERN FUNCTIES ---

def add_furigana_fast():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    if not hasattr(doc, "Text"): return
    global_start = time.perf_counter()
    word_map = {}
    for path in [CSV_PATH, NEW_ENTRIES_PATH]:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8-sig') as f:
                for row in csv.reader(f):
                    if len(row) >= 2: word_map[row[0].strip()] = row[1].strip()
    context_rules = []
    if os.path.exists(RULES_PATH):
        with open(RULES_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f) ; next(reader, None)
            context_rules = [row for row in reader if len(row) >= 4]
    known_words = []
    if os.path.exists(CSV_PATH_2):
        with open(CSV_PATH_2, 'r', encoding='utf-8-sig') as f:
            known_words = [line.strip() for line in f if line.strip()]
    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""
    doc.lockControllers()
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchCaseSensitive = True
        search_desc.SearchRegularExpression = True
        for rule in context_rules:
            target, direction, pattern, reading = rule[0].strip(), rule[1].strip().upper(), rule[2].strip(), rule[3].strip()
            search_desc.SearchString = (pattern + target) if direction == "B" else (target + pattern)
            found = doc.findAll(search_desc)
            if found:
                for j in range(found.getCount()):
                    m = found.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    cursor = m.getText().createTextCursorByRange(m)
                    if direction == "B": cursor.collapseToEnd() ; cursor.goLeft(len(target), True)
                    else: cursor.collapseToStart() ; cursor.goRight(len(target), True)
                    if not getattr(cursor, "RubyText", ""): cursor.RubyText = reading
        search_desc.SearchRegularExpression = False 
        for target in sorted(word_map.keys(), key=len, reverse=True):
            search_desc.SearchString = target
            found = doc.findAll(search_desc)
            if found:
                reading = word_map[target]
                for j in range(found.getCount()):
                    m = found.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    if not getattr(m, "RubyText", ""): m.RubyText = reading
        for target in known_words:
            search_desc.SearchString = target
            found = doc.findAll(search_desc)
            if found:
                for j in range(found.getCount()):
                    m = found.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    m.RubyText = ""
    finally:
        doc.unlockControllers()
    msgbox(f"Done in {time.perf_counter()-global_start:.2f}s")

def add_custom_entry():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    if not selection or not selection.getByIndex(0).getString().strip():
        msgbox("Please select a word.", "Error") ; return
    selected_text = selection.getByIndex(0).getString().strip()
    kana_reading = input_box_kana(f"Word: {selected_text}\nEnter KANA furigana:", "New Entry")
    if not kana_reading: return
    preview = f"{selected_text},{kana_reading}"
    if msgbox(f"Save entry?\n\nEntry: {preview}", "Confirm", buttons=4, type_msg="querybox") == 2:
        try:
            with open(NEW_ENTRIES_PATH, 'a', encoding='utf-8-sig', newline='') as f:
                csv.writer(f).writerow([selected_text, kana_reading.strip()])
            msgbox(f"Saved!")
        except Exception as e: msgbox(f"Error: {e}")

def add_to_known_words():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    if not selection or not selection.getByIndex(0).getString().strip(): return
    word = selection.getByIndex(0).getString().strip()
    try:
        with open(CSV_PATH_2, 'a', encoding='utf-8-sig') as f: f.write(f"\n{word}")
        doc.lockControllers()
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchString = word
        found = doc.findAll(search_desc)
        if found:
            for i in range(found.getCount()): found.getByIndex(i).RubyText = ""
        doc.unlockControllers()
        msgbox(f"'{word}' marked as known.")
    except Exception as e: msgbox(str(e))

def edit_known_words_file():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    content = ""
    if os.path.exists(CSV_PATH_2):
        with open(CSV_PATH_2, 'r', encoding='utf-8-sig') as f:
            content = f.read()
    dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", ctx)
    dialog_model.Width = 200 ; dialog_model.Height = 250 ; dialog_model.Title = "Edit Known Words"
    edit_model = dialog_model.createInstance("com.sun.star.awt.UnoControlEditModel")
    edit_model.PositionX = 5 ; edit_model.PositionY = 5 ; edit_model.Width = 190 ; edit_model.Height = 215
    edit_model.MultiLine = True ; edit_model.VScroll = True ; edit_model.Text = content
    dialog_model.insertByName("editor", edit_model)
    save_btn = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
    save_btn.Name = "save_btn" ; save_btn.Label = "Save" ; save_btn.PositionX = 40 ; save_btn.PositionY = 225
    save_btn.Width = 50 ; save_btn.Height = 15 ; save_btn.PushButtonType = 1 
    dialog_model.insertByName("save_btn", save_btn)
    dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", ctx)
    dialog.setModel(dialog_model)
    dialog.setVisible(True)
    if dialog.execute() == 1:
        new_content = dialog.getControl("editor").getText()
        os.makedirs(os.path.dirname(CSV_PATH_2), exist_ok=True)
        with open(CSV_PATH_2, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(new_content)
        msgbox("Updated.")
    dialog.dispose()

def remove_furigana_selection():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    doc.lockControllers()
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchRegularExpression = True ; search_desc.SearchString = "." 
        found = doc.findAll(search_desc)
        if found:
            for i in range(found.getCount()):
                m = found.getByIndex(i)
                if selection and not is_in_selection(m, selection): continue
                m.RubyText = ""
    finally:
        doc.unlockControllers()
    msgbox("Furigana removed.")

def lookup_selection_data():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    if not selection: return
    word = selection.getByIndex(0).getString().strip()
    matches = []
    try:
        with open(DICT_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 4 and row[0].strip() == word:
                    matches.append(f"Reading: {row[1]}\nMeaning: {row[2]}\nTags: {row[3]}")
    except: pass
    if matches: msgbox("\n---\n".join(matches), f"Dict: {word}")
    else: msgbox("Not found.")

# --- MENU ---

def furigana_main_menu():
    global CURRENT_LANG
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    
    t = TRANSLATIONS[CURRENT_LANG]
    dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", ctx)
    dialog_model.Width = 150 ; dialog_model.Height = 170 ; dialog_model.Title = t["title"]
    
    options = [
        (t["add"], 5, add_furigana_fast),
        (t["remove"], 25, remove_furigana_selection),
        (t["new"], 45, add_custom_entry),
        (t["known"], 65, add_to_known_words),
        (t["edit"], 85, edit_known_words_file),
        (t["dict"], 105, lookup_selection_data),
        (t["switch"], 135, "SWITCH") # Speciale actie voor taal
    ]
    
    for i, (label, y_pos, _) in enumerate(options):
        btn = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
        btn.Name = f"btn_{i}" ; btn.Label = label ; btn.PositionX = 10 ; btn.PositionY = y_pos
        btn.Width = 130 ; btn.Height = 15 ; dialog_model.insertByName(btn.Name, btn)
    
    dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", ctx)
    dialog.setModel(dialog_model)
    
    class ButtonListener(unohelper.Base, uno.getClass("com.sun.star.awt.XActionListener")):
        def __init__(self, dialog, options):
            self.dialog = dialog ; self.options = options ; self.choice = None
        def actionPerformed(self, event):
            idx = int(event.Source.getModel().Name.split('_')[1])
            self.choice = self.options[idx][2] ; self.dialog.endExecute()
        def disposing(self, event): pass

    listener = ButtonListener(dialog, options)
    for i in range(len(options)): dialog.getControl(f"btn_{i}").addActionListener(listener)
    dialog.setVisible(True) ; dialog.execute() ; dialog.dispose()
    
    if listener.choice == "SWITCH":
        CURRENT_LANG = "JP" if CURRENT_LANG == "EN" else "EN"
        furigana_main_menu() # Heropen menu met nieuwe taal
    elif listener.choice:
        listener.choice()

g_exportedScripts = (furigana_main_menu, add_furigana_fast, remove_furigana_selection, add_custom_entry, add_to_known_words, edit_known_words_file, lookup_selection_data)