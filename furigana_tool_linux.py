import uno
import csv
import time
import os

# You need to define home_dir first
home_dir = os.path.expanduser('~')

# Path to your CSV (Only used for the Add function)
CSV_PATH = os.path.join(home_dir, 'Documents', 'JP_Total_List.CSV')
CSV_PATH_2 = os.path.join(home_dir, 'Documents', 'DO_NOT_FURIGANIZE.txt')

def msgbox(message, title="Macro Notification", buttons=1, type_msg="infobox"):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    parent = toolkit.getDesktopWindow()
    msg = toolkit.createMessageBox(parent, type_msg, buttons, title, str(message))
    return msg.execute()

def is_in_selection(found_item, selection):
    """Checks if found_item is within any of the selected ranges."""
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
    
    # --- STEP 1: LOAD FILES ---
    load_start = time.perf_counter()
    word_map = {}
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2: word_map[row[0].strip()] = row[1].strip()
    except Exception as e:
        msgbox(f"Error loading CSV: {str(e)}", "Error", type_msg="errorbox")
        return

    known_words = []
    try:
        if os.path.exists(CSV_PATH_2):
            with open(CSV_PATH_2, 'r', encoding='utf-8-sig') as f:
                known_words = [line.strip() for line in f if line.strip()]
    except Exception as e:
        msgbox(f"Error loading known words: {str(e)}", "Error", type_msg="errorbox")
    
    load_time = time.perf_counter() - load_start

    # --- INITIALIZE SEARCH ---
    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""
    doc.lockControllers()
    words_added = 0
    words_removed = 0
    
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchCaseSensitive = True
        
        # --- PHASE 1: ADD FURIGANA ---
        phase1_start = time.perf_counter()
        sorted_keys = sorted(word_map.keys(), key=len, reverse=True)
        for target in sorted_keys:
            search_desc.SearchString = target
            found_all = doc.findAll(search_desc)
            if found_all:
                reading = word_map[target]
                for j in range(found_all.getCount()):
                    m = found_all.getByIndex(j)
                    if has_active_selection and not is_in_selection(m, selection): continue
                    if not getattr(m, "RubyText", None):
                        m.RubyText = reading
                        words_added += 1
        phase1_time = time.perf_counter() - phase1_start

        # --- PHASE 2: REMOVE KNOWN ---
        phase2_start = time.perf_counter()
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
        phase2_time = time.perf_counter() - phase2_start

    finally:
        doc.unlockControllers()
    
    total_time = time.perf_counter() - global_start
    
    # --- RESULTS REPORT ---
    report = (
        f"Process Results:\n"
        f"------------------\n"
        f"Added: {words_added}\n"
        f"Removed: {words_removed}\n\n"
        f"Timing Breakdown:\n"
        f"------------------\n"
        f"File Loading: {load_time:.3f}s\n"
        f"Phase 1 (Add): {phase1_time:.3f}s\n"
        f"Phase 2 (Remove): {phase2_time:.3f}s\n"
        f"Total Duration: {total_time:.3f}s"
    )
    msgbox(report, "Performance Results")

def remove_furigana_selection():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    start_time = time.perf_counter()
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
    
    duration = time.perf_counter() - start_time
    msgbox(f"Furigana cleared from {count} items.\nTime: {duration:.3f}s", "Reset Complete")

def add_to_known_words():
    """Takes current selection, adds to text file, and clears its furigana document-wide."""
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    selection = doc.getCurrentSelection()
    
    if not selection or selection.getCount() == 0: return
    selected_text = selection.getByIndex(0).getString().strip()
    
    if not selected_text:
        msgbox("Please select a word first.")
        return

    try:
        start_time = time.perf_counter()
        # Append word to the exclusion file
        with open(CSV_PATH_2, 'a', encoding='utf-8-sig') as f:
            f.write(f"\n{selected_text}")
        
        # --- NEW LOGIC: Document-wide stripping for this specific word ---
        doc.lockControllers()
        instances_cleared = 0
        try:
            search_desc = doc.createSearchDescriptor()
            search_desc.SearchString = selected_text
            search_desc.SearchCaseSensitive = True
            
            # Find every occurrence of the word in the document
            found_all = doc.findAll(search_desc)
            if found_all:
                for i in range(found_all.getCount()):
                    item = found_all.getByIndex(i)
                    # Clear RubyText if it is not already empty
                    if getattr(item, "RubyText", "") != "":
                        item.RubyText = ""
                        instances_cleared += 1
        finally:
            doc.unlockControllers()
            
        duration = time.perf_counter() - start_time
        
        msgbox(
            f"'{selected_text}' added to exclusion list.\n"
            f"Furigana cleared from {instances_cleared} instances document-wide.\n"
            f"Total Time: {duration:.3f}s", 
            "Word Excluded"
        )
    except Exception as e:
        msgbox(f"File Error: {str(e)}")
        
def lookup_selection_data():
    """Looks up information for the selected text in dictionary.csv."""
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    doc = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx).getCurrentComponent()
    
    selection = doc.getCurrentSelection()
    if not selection or selection.getCount() == 0:
        return
    
    selected_text = selection.getByIndex(0).getString().strip()
    if not selected_text:
        msgbox("Please select text to look up.")
        return

    # Path to your dictionary file
    DICT_PATH = r"C:\Files\dictionary.csv"
    
    start_time = time.perf_counter()
    found_data = None
    
    try:
        if not os.path.exists(DICT_PATH):
            msgbox(f"Dictionary file not found: {DICT_PATH}", "Error")
            return

        with open(DICT_PATH, 'r', encoding='utf-8-sig') as f:
            # Use delimiter='\t' for tab separation
            reader = csv.reader(f, delimiter='\t')
            for row in reader:
                # Ensure row has enough columns and matches selection
                if len(row) >= 4 and row[0].strip() == selected_text:
                    found_data = {
                        "word": row[0].strip(),
                        "kana": row[1].strip(),
                        "meaning": row[2].strip(),
                        "tags": row[3].strip()
                    }
                    break # Stop at first match
                    
    except Exception as e:
        msgbox(f"Error reading dictionary: {str(e)}", "Error")
        return

    duration = time.perf_counter() - start_time

    if found_data:
        report = (
            f"Lookup Results for: {found_data['word']}\n"
            f"----------------------------------\n"
            f"Reading: {found_data['kana']}\n"
            f"Meaning: {found_data['meaning']}\n"
            f"Tags: {found_data['tags']}\n\n"
            f"Search Time: {duration:.3f}s"
        )
        msgbox(report, "Dictionary Lookup")
    else:
        msgbox(f"No entry found for '{selected_text}' in dictionary.", "Not Found")

g_exportedScripts = (add_furigana_fast, remove_furigana_selection, add_to_known_words, lookup_selection_data)
