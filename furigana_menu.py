import uno
import unohelper
from com.sun.star.awt import XActionListener

class SelectionHandler(unohelper.Base, XActionListener):
    def __init__(self, dialog, listbox):
        self.dialog = dialog
        self.listbox = listbox
        self.selected_value = None

    def actionPerformed(self, actionEvent):
        # This triggers when the 'OK' button is pressed
        self.selected_value = self.listbox.getSelectedItem()
        self.dialog.endExecute()

def show_selection_menu(*args):
    ctx = uno.getComponentContext()
    smgr = ctx.getServiceManager()
    
    # 1. Create the Dialog model
    dialog_model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", ctx)
    dialog_model.PositionX = 100
    dialog_model.PositionY = 100
    dialog_model.Width = 150
    dialog_model.Height = 100
    dialog_model.Title = "Python Selection Menu"

    # 2. Create the ListBox (The Menu)
    listbox_model = dialog_model.createInstance("com.sun.star.awt.UnoControlListBoxModel")
    listbox_model.PositionX = 10
    listbox_model.PositionY = 10
    listbox_model.Width = 130
    listbox_model.Height = 60
    listbox_model.Name = "MyListBox"
    # Add your options here
    options = ("Add furigana", "Remove furigana", "Do not add furigana")
    listbox_model.StringItemList = options
    dialog_model.insertByName("MyListBox", listbox_model)

    # 3. Create the OK Button
    button_model = dialog_model.createInstance("com.sun.star.awt.UnoControlButtonModel")
    button_model.PositionX = 45
    button_model.PositionY = 75
    button_model.Width = 60
    button_model.Height = 15
    button_model.Label = "Confirm"
    button_model.Name = "OKButton"
    dialog_model.insertByName("OKButton", button_model)

    # 4. Create the Control and execute
    dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", ctx)
    dialog.setModel(dialog_model)
    
    # Set up the listener
    listbox_control = dialog.getControl("MyListBox")
    handler = SelectionHandler(dialog, listbox_control)
    
    button_control = dialog.getControl("OKButton")
    button_control.addActionListener(handler)

    # Show the dialog
    dialog.setVisible(True)
    dialog.execute()

    # 5. Handle the result
    if handler.selected_value:
        # Example action: Insert selection into the document
        doc = XSCRIPTCONTEXT.getDocument()
        text = doc.Text
        cursor = text.createTextCursor()
        text.insertString(cursor, f"You selected: {handler.selected_value}", 0)

    dialog.dispose()