import uno
import csv
import time

# Paths to your files
CSV_PATH = r"C:\Files\JP_Total_List.CSV"
CSV_PATH_2 = r"C:\Files\DO_NOT_FURIGANIZE.txt"

def msgbox(message, title="Macro Notification", buttons=1, type_msg="infobox"):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    parent = toolkit.getDesktopWindow()
    msg = toolkit.createMessageBox(parent, type_msg, buttons, title, message)
    return msg.execute()

def is_in_selection(found_item, selection):
    """Checks if found_item is within any of the selected ranges."""
    for i in range(selection.getCount()):
        sel_range = selection.getByIndex(i)
        text_obj = sel_range.getText()
        # Ensure we are inside the start and end bounds of the selection
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

    if not hasattr(doc, "Text"):
        return
        
    start_time = time.perf_counter()
    
    # 1. Load Main Dictionary
    word_map = {}
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    word_map[row[0].strip()] = row[1].strip()
    except Exception as e:
        msgbox(f"Error loading CSV: {str(e)}", "Error", type_msg="errorbox")
        return

    # 2. Load Known Words (to be removed/skipped)
    known_words = []
    try:
        with open(CSV_PATH_2, 'r', encoding='utf-8-sig') as f:
            known_words = [line.strip() for line in f if line.strip()]
    except Exception as e:
        msgbox(f"Error loading known words: {str(e)}", "Error", type_msg="errorbox")
        return

    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    doc.lockControllers()
    words_added = 0
    words_removed = 0
    
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchCaseSensitive = True
        search_desc.SearchWords = False
        
        # --- PHASE 1: ADD FURIGANA ---
        sorted_keys = sorted(word_map.keys(), key=len, reverse=True)
        for target in sorted_keys:
            search_desc.SearchString = target
            found_all = doc.findAll(search_desc)
            
            if found_all:
                reading = word_map[target]
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection):
                        continue
                    
                    if not getattr(m, "RubyText", None):
                        m.RubyText = reading
                        words_added += 1

        # --- PHASE 2: AUTOMATIC REMOVAL OF KNOWN WORDS ---
        # We do this after adding to catch any overlaps or pre-existing furigana
        for target in known_words:
            search_desc.SearchString = target
            found_all = doc.findAll(search_desc)
            
            if found_all:
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection):
                        continue
                    
                    if getattr(m, "RubyText", "") != "":
                        m.RubyText = ""
                        words_removed += 1

    finally:
        doc.unlockControllers()
        
    duration = time.perf_counter() - start_time
    msgbox(f"Process Complete!\n\nTime: {duration:.2f}s\nAdded: {words_added}\nRemoved (Known): {words_removed}", "Finished")

def remove_furigana_selection():
    """Manual removal: Completely clears furigana from selection."""
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()
    if not hasattr(doc, "Text"): return

    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    doc.lockControllers()
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
    finally:
        doc.unlockControllers()
    msgbox("All furigana cleared in selection.", "Reset")

g_exportedScripts = (add_furigana_fast, remove_furigana_selection)