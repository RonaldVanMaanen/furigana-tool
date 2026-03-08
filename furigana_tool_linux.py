import uno
import csv
import time
import os
import re

# You need to define home_dir first
home_dir = os.path.expanduser('~')

# Path to your CSV (Only used for the Add function)
CSV_PATH = os.path.join(home_dir, 'Documents', 'FuriganaTool/JP_Total_List.CSV')
CSV_PATH_2 = os.path.join(home_dir, 'Documents', 'FuriganaTool/DO_NOT_FURIGANIZE.txt')
DICT_PATH = os.path.join(home_dir, 'Documents', 'FuriganaTool/dictionary.csv')

def msgbox(message, title="Macro Notification", buttons=1, type_msg="infobox"):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    parent = toolkit.getDesktopWindow()
    msg = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return msg.execute()

def is_in_selection(found_item, selection):
    for i in range(selection.getCount()):
        sel_range = selection.getByIndex(i)
        text_obj = sel_range.getText()
        start_ok = text_obj.compareRegionEnds(sel_range.getStart(), found_item.getStart()) >= 0
        end_ok = text_obj.compareRegionEnds(sel_range.getEnd(), found_item.getEnd()) <= 0
        if start_ok and end_ok:
            return True
    return False

def add_furigana_fast():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()
    if not hasattr(doc, "Text"): return
        
    global_start = time.perf_counter()
    
    # --- LOAD FILES ---
    context_rules = []
    try:
        if os.path.exists(RULES_PATH):
            with open(RULES_PATH, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                next(reader) # Skip Header
                context_rules = [row for row in reader if len(row) >= 4]
    except Exception as e:
        msgbox(f"Rules Error: {str(e)}")

    word_map = {}
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2: word_map[row[0].strip()] = row[1].strip()
    except Exception as e:
        msgbox(f"CSV Error: {str(e)}")
        return

    known_words = []
    if os.path.exists(CSV_PATH_2):
        with open(CSV_PATH_2, 'r', encoding='utf-8-sig') as f:
            known_words = [line.strip() for line in f if line.strip()]

    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""
    doc.lockControllers()
    
    rules_applied = 0
    words_added = 0
    words_removed = 0
    
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchCaseSensitive = True
        
        # --- PHASE 0: CONTEXT RULES ---
        search_desc.SearchRegularExpression = True
        for rule in context_rules:
            target, direction, pattern, reading = rule[0].strip(), rule[1].strip().upper(), rule[2].strip(), rule[3].strip()
            search_desc.SearchString = (pattern + target) if direction == "B" else (target + pattern)
            
            found_all = doc.findAll(search_desc)
            if found_all:
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    cursor = m.getText().createTextCursorByRange(m)
                    if direction == "B":
                        cursor.collapseToEnd()
                        cursor.goLeft(len(target), True)
                    else:
                        cursor.collapseToStart()
                        cursor.goRight(len(target), True)
                    
                    if getattr(cursor, "RubyText", "") == "":
                        cursor.RubyText = reading
                        rules_applied += 1
        
        # --- PHASE 1: GENERAL DICTIONARY ---
        search_desc.SearchRegularExpression = False 
        sorted_keys = sorted(word_map.keys(), key=len, reverse=True)
        for target in sorted_keys:
            search_desc.SearchString = target
            found_all = doc.findAll(search_desc)
            if found_all:
                reading = word_map[target]
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    if getattr(m, "RubyText", "") == "":
                        m.RubyText = reading
                        words_added += 1

        # --- PHASE 2: REMOVE KNOWN ---
        for target in known_words:
            search_desc.SearchString = target
            found_all = doc.findAll(search_desc)
            if found_all:
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    if getattr(m, "RubyText", "") != "":
                        m.RubyText = ""
                        words_removed += 1
                        
    finally:
        doc.unlockControllers()
    
    msgbox(f"Rules: {rules_applied}\nAdded: {words_added}\nRemoved: {words_removed}\nTime: {time.perf_counter()-global_start:.3f}s")

def remove_furigana_selection():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    doc.lockControllers()
    count = 0
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchRegularExpression = True
        search_desc.SearchString = "." 
        found_all = doc.findAll(search_desc)
        if found_all:
            for i in range(found_all.getCount()):
                m = found_all.getByIndex(i)
                if has_active_selection and not is_in_selection(m, selection): continue
                if getattr(m, "RubyText", "") != "":
                    m.RubyText = ""
                    count += 1
    finally:
        doc.unlockControllers()
    msgbox(f"Cleared {count} items.")

def add_to_known_words():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    if not selection or selection.getCount() == 0: return
    selected_text = selection.getByIndex(0).getString().strip()
    if not selected_text: return

    try:
        with open(CSV_PATH_2, 'a', encoding='utf-8-sig') as f:
            f.write(f"\n{selected_text}")
        doc.lockControllers()
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchString = selected_text
        found_all = doc.findAll(search_desc)
        if found_all:
            for i in range(found_all.getCount()):
                item = found_all.getByIndex(i)
                item.RubyText = ""
        doc.unlockControllers()
        msgbox(f"Excluded '{selected_text}'")
    except Exception as e:
        msgbox(str(e))

def lookup_selection_data():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    if not selection: return
    selected_text = selection.getByIndex(0).getString().strip()
    if not selected_text: return
        
    matches = []
    try:
        with open(DICT_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                if len(row) >= 4 and row[0].strip() == selected_text:
                    matches.append(f"Reading: {row[1]}\nMeaning: {row[2]}\nTags: {row[3]}")
    except Exception as e:
        msgbox(str(e))
        return

    if matches:
        msgbox("\n---\n".join(matches), f"Results for: {selected_text}")
    else:
        msgbox("Not found.")

g_exportedScripts = (add_furigana_fast, remove_furigana_selection, add_to_known_words, lookup_selection_data)