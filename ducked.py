#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from src.gui.search import Search
from src.gui.indexing import Indexing
from src.lib.indexer import Indexer
import sys
from src.lib.log import Log
from src.api import API

class Ducked:

    Index = Indexer()

    def __init__(self):

        CustomLog = Log()
        CustomLog.setup_custom_logger('ducked')

        # API stuff, no GUI
        if len(sys.argv) > 1:
            APILayer = API()
            APILayer.run()
        # No API stuff, so do the GUI
        else:
            IndexingWindow = Indexing()
            SearchWindow = Search()

            if self.Index.needs_synchronization():
                IndexingWindow.draw()

                self.Index.index_apps()

                IndexingWindow.remove()
                SearchWindow.draw()
            else:
                SearchWindow.draw()

    def main(self):
        gtk.main()


ThisIsSoDucked = Ducked()
ThisIsSoDucked.main()
