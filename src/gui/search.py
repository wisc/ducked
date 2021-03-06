#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import pango
import os
from src.lib.search import Search
from src.lib.os_handler import OSHandler
from src.lib.db_handler import DBHandler
import logging
logger = logging.getLogger('ducked')

class Search:

    Search = Search()

    def destroy(self, widget=None, data=None):
        """Destroy all the things"""
        DB = DBHandler()
        DB.conn.close()
        gtk.main_quit()

    def shortcut_destroy(self, widget, AccelGroup, i, control_mask):
        """Destroy app through shortcut"""

        # entered a search query, 1 result, pressed escape
        # there's always Google as a result, chances are the user didn't find what they were looking for
        # so reindex
        if len(self.entry.get_text()) > 0 and self.liststore != None and len(self.liststore) == 1:
            row = self.liststore[0]
            app_name = row[1]

            # Pressed escape after querying and the app results skipped to Google.
            # Probably didn't find something a new app, so reindex
            if "Search" in app_name:
                logger.info("Escape pressed with no search results. Reindexing apps.")
                self.window.destroy()
                OS = OSHandler()
                OS.run_command_forked("ducked --reindex")

        self.destroy()

    def signal_input_changed(self,widget):
        """Signal on change for text entry. Searches for apps."""
        self.Search.signal_input_changed(self, widget)

    def signal_enter_key(self, widget, event):
        """App selection through enter key on listview."""

        # Did you press ctrl or shift?
        modifier_launch_new_app_pressed = False
        if (event.state & gtk.gdk.CONTROL_MASK) or (event.state & gtk.gdk.SHIFT_MASK):
            modifier_launch_new_app_pressed = True

        if event.keyval == 65293:
            (model, iter) = self.treeview.get_selection().get_selected()

            if iter:
                app_name = model.get_value(iter, 1)
                self.Search.signal_goto_app_name(app_name, modifier_launch_new_app_pressed)
                self.destroy()
                return True
            else:
                query = self.entry.get_text()
                self.Search.signal_goto_first_result(query, modifier_launch_new_app_pressed)
                self.destroy()
                return True
        return False

    def add_accelerator(self, widget, accelerator, callback):
        """Adds a keyboard shortcut"""
        if accelerator is not None:
            key, mod = gtk.accelerator_parse(accelerator)
            #widget.add_accelerator(signal, self.my_accelerators, key, mod, gtk.ACCEL_VISIBLE)
            self.my_accelerators.connect_group(key, mod, gtk.ACCEL_VISIBLE, callback)
            self.window.add_accel_group(self.my_accelerators)

    def draw(self):

        self.draw_window()
        self.draw_searchbox()
        self.draw_listview()
        self.clear_listview()

        self.set_shortcuts_signals()

        self.window.show_all()

    def draw_window(self):
        """Draw the main window"""
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_skip_taskbar_hint(True)

        self.window.connect("destroy", self.destroy)

        self.window.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ebebeb"))
        self.window.set_border_width(10)
        self.window.set_size_request(650,-1)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_title("Ducked")
        self.window.set_decorated(False)

        # We want the window at the top of the screen
        (x, y) = self.window.get_position()
        self.window.move(x, 150)

    def draw_searchbox(self):
        """Draw the search box on the window"""

        self.entry = gtk.Entry()
        self.entry.set_size_request(450,100)

        self.entry.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ebebeb"))
        self.entry.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse("#ebebeb"))
        self.entry.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse("#22352c"))
        self.entry.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#22352c"))

        font_description = pango.FontDescription('Lucida Sans %s' % 36)
        self.entry.modify_font(font_description)
        self.entry.set_inner_border(None)
        self.entry.set_has_frame(0)

        # Taaaaable
        self.table = gtk.Table(2, 2, True)
        self.table.set_homogeneous(False)
        self.table.attach(self.entry, 0, 1, 0, 1)

        OS = OSHandler()

        logo_pixbuf = gtk.gdk.pixbuf_new_from_file(OS.cwd() + "/resources/logo/ducked-96x96.png")

        self.logo = gtk.Image()
        self.logo.set_from_pixbuf(logo_pixbuf)

        # Taaaaable
        self.table.attach(self.logo, 1, 2, 0, 1)


        self.window.add(self.table)
        self.window.set_focus(self.entry)

        # key press for enter press
        self.window.connect('key-press-event', self.signal_enter_key)

    def draw_listview(self):

        # list store
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, 'gboolean')
        self.treeview = gtk.TreeView(self.liststore)

        # Create column 1
        self.tvcolumn = gtk.TreeViewColumn('')
        self.treeview.append_column(self.tvcolumn)

        # Render Icon
        self.cellpb = gtk.CellRendererPixbuf()
        self.cellpb.set_property('cell-background', '#ebebeb')
        self.tvcolumn.pack_start(self.cellpb, expand=False)
        # self.tvcolumn.set_attributes(self.cellpb, stock_id=1)
        self.tvcolumn.add_attribute(self.cellpb, 'pixbuf', 0)

        # Render App name
        self.cell = gtk.CellRendererText()
        font_description = pango.FontDescription('Lucida Sans %s' % 21)
        self.cell.set_property('font-desc', font_description)
        self.cell.set_property('cell-background', '#ebebeb')
        self.cell.set_property('foreground', '#525252')
        self.tvcolumn.pack_start(self.cell, True)
        # self.tvcolumn.set_attributes(self.cell, text=0)
        self.tvcolumn.add_attribute(self.cell, 'text', 1)

        # self.cell_shortcut = gtk.CellRendererText()
        # font_description = pango.FontDescription('Lucida Sans %s' % 21)
        # self.cell_shortcut.set_property('font-desc', font_description)
        # self.cell_shortcut.set_property('cell-background', '#ebebeb')
        # self.cell_shortcut.set_property('foreground', '#525252')
        # self.tvcolumn.pack_start(self.cell_shortcut, True)
        # self.tvcolumn.add_attribute(self.cell_shortcut, 'text', 2)

        self.treeview.set_headers_visible(False)

        self.tvcolumn.set_resizable(True)

        self.treeview.set_cursor(0)
        self.treeview.get_selection().set_mode(gtk.SELECTION_BROWSE)

        self.table.attach(self.treeview, 0, 2, 1, 2)
        self.window.resize(1,1)

    def remove_listview(self):
        if hasattr(self, "treeview"):
            self.table.remove(self.treeview)
        self.window.resize(1,1)

    def redraw_listview(self):
        self.remove_listview()
        self.draw_listview()

    def clear_listview(self):
        self.liststore.clear()
        self.treeview.hide()
        self.window.resize(1,1)
        self.window.resize(1,1)

    def append_to_listview(self, app_name, icon_name, shortcut, command):
        self.treeview.show()
        icon_location = self.translate_icon_to_path(icon_name)

        self.liststore.append([gtk.gdk.pixbuf_new_from_file_at_size(icon_location, 48, 48), app_name, shortcut, True])

    def draw_webview(self, content):

        self.web_buffer = gtk.TextBuffer()
        self.web_buffer.set_text(content)

        self.webview = gtk.TextView()
        self.webview.set_buffer(self.web_buffer)
        self.webview.set_cursor_visible(False)
        self.webview.set_wrap_mode(gtk.WRAP_WORD)
        self.webview.set_editable(False)

        self.table.attach(self.webview, 0, 2, 1, 2)
        self.webview.show()
        self.window.resize(1,1)

    def remove_webview(self):
        if hasattr(self, "webview"):
            self.table.remove(self.webview)
            self.webview = None
        self.window.resize(1,1)

    def switch_to_web(self, content):
        self.remove_listview()
        self.draw_webview(content)

    def switch_to_list(self):
        self.remove_webview()
        self.redraw_listview()

    def ensure_list_visibility(self):
        if hasattr(self, "webview") and self.webview != None:
            self.switch_to_list()
        else:
            self.redraw_listview()

    def translate_icon_to_path(self, icon_name):

        OS = OSHandler()

        if icon_name[-4:] == ".png":
            icon_location = icon_name
        else:
            theme = gtk.icon_theme_get_default()
            icon =  theme.lookup_icon(icon_name, 48, ())

            if icon:
                icon_location = icon.get_filename()
            else:
                icon_location = OS.cwd() + "/resources/icons/icon_not_found.png"

        if os.path.isfile(icon_location) == False:
            if os.path.isfile("/usr/share/icons/" + icon_location) == True:
                icon_location = "/usr/share/icons/" + icon_location
            else:
                icon_location = OS.cwd() + "/resources/icons/icon_not_found.png"

        return icon_location

    def set_shortcuts_signals(self):
        """Set shortcuts & signals"""

        self.my_accelerators = gtk.AccelGroup()
        self.add_accelerator(self.window, "Escape", self.shortcut_destroy)

        # on change for text entry
        self.entry.connect("changed", self.signal_input_changed)
