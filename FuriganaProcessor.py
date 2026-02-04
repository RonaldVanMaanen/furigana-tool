import uno
import csv
import time

# Path to your CSV (Only used for the Add function)
CSV_PATH = r"C:\Files\JP_Total_List.CSV"

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
        start_ok = text_obj.compareRegionEnds(sel_range.getStart(), found_item.getStart()) >= 0
        end_ok = text_obj.compareRegionEnds(sel_range.getEnd(), found_item.getEnd()) <= 0
        if start_ok and end_ok:
            return True
    return False

def remove_furigana_selection():
    """Fast removal: Loops through text portions and clears RubyText without using a CSV."""
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()

    if not hasattr(doc, "Text"):
        return

    start_time = time.perf_counter()
    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    doc.lockControllers()
    cleared_count = 0
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchRegularExpression = True
        search_desc.SearchString = "." 
        
        found_all = doc.findAll(search_desc)
        if found_all:
            for i in range(found_all.getCount()):
                m = found_all.getByIndex(i)
                if has_active_selection and not is_in_selection(m, selection):
                    continue
                
                if getattr(m, "RubyText", "") != "":
                    m.RubyText = ""
                    cleared_count += 1
    finally:
        doc.unlockControllers()
    
    duration = time.perf_counter() - start_time
    msgbox(f"Time: {duration:.2f}s\nFurigana cleared from {cleared_count} portions.", "Reset")

def add_furigana_fast():
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()

    if not hasattr(doc, "Text"):
        return
        
    start_time = time.perf_counter()
    
    # Load CSV
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

    selection = doc.getCurrentSelection()
    has_active_selection = selection and selection.getCount() > 0 and selection.getByIndex(0).getString() != ""

    doc.lockControllers()
    words_updated = 0
    
    try:
        search_desc = doc.createSearchDescriptor()
        search_desc.SearchCaseSensitive = True
        search_desc.SearchWords = False
        
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
                        words_updated += 1
    finally:
        doc.unlockControllers()
        
    duration = time.perf_counter() - start_time
    msgbox(f"Time: {duration:.2f}s\nUpdated: {words_updated} instances", "Finished")

g_exportedScripts = (add_furigana_fast, remove_furigana_selection)
