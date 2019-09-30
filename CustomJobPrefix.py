# Copyright (c) 2019 fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

from UM.Extension import Extension
from cura.CuraApplication import CuraApplication

from PyQt5.QtCore import QObject

from . import PrintInformationPatches

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


class CustomJobPrefix(Extension, QObject,):
    def __init__(self, parent = None):
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance()

        self.setMenuName(catalog.i18nc("@item:inmenu", "Custom Printjob Prefix"))
        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set prefix"), self.showNameDialog)

        self._create_profile_window = None
        self._print_information_patches = None

        self._application.engineCreatedSignal.connect(self._onEngineCreated)

    def _onEngineCreated(self):
        self._print_information_patches = PrintInformationPatches.PrintInformationPatches(self._application.getPrintInformation())

    def showNameDialog(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PrefixDialog.qml")
        self._create_profile_window = self._application.createQmlComponent(path, {"manager": self})
        self._create_profile_window.show()

