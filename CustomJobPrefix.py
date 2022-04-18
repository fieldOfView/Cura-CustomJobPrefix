# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import os.path

from UM.Extension import Extension
from UM.Logger import Logger
from UM.Version import Version
from cura.CuraApplication import CuraApplication

try:
    from PyQt6.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot
except ImportError:
    from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import PrintInformationPatches
from . import OutputDevicePatcher

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

from typing import Optional

class CustomJobPrefix(Extension, QObject,):
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance()

        self._use_controls1 = False
        try:
            if self._application.getAPIVersion() < Version(8) and self._application.getVersion() != "master":
                self._use_controls1 = True
        except AttributeError:
             # UM.Application.getAPIVersion was added for API > 6 (Cura 4)
            self._use_controls1 = True
        self._qml_folder = "qml" if not self._use_controls1 else "qml_controls1"

        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set name options"), self.showNameDialog)

        self._prefix_dialog = None  # type: Optional[QObject]
        self._print_information_patches = None  # type: Optional[PrintInformationPatches.PrintInformationPatches]
        self._output_device_patcher = OutputDevicePatcher.OutputDevicePatcher()

        self._application.engineCreatedSignal.connect(self._onEngineCreated)
        self._application.globalContainerStackChanged.connect(self._onGlobalStackChanged)

    def _onEngineCreated(self) -> None:
        self._print_information_patches = PrintInformationPatches.PrintInformationPatches(self._application.getPrintInformation())
        self._createAdditionalComponentsView()

    def _createAdditionalComponentsView(self) -> None:
        Logger.log("d", "Creating additional ui components for CustomJobPrefix")

        try:
            major_api_version = self._application.getAPIVersion().getMajor()
        except AttributeError:
            # UM.Application.getAPIVersion was added for API > 6 (Cura 4)
            # Since this plugin version is only compatible with Cura 3.5 and newer, it is safe to assume API 5
            major_api_version = 5

        if not self._use_controls1:
            qml_file = "JobSpecsPatcher.qml"
        elif major_api_version <= 5:
            qml_file = "JobSpecsPatcher3x.qml"
        else:
            qml_file = "JobSpecsPatcher4x.qml"
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, qml_file)

        self._additional_components = self._application.createQmlComponent(path, {"customJobPrefix": self})
        if not self._additional_components:
            Logger.log("w", "Could not create additional components for CustomJobPrefix")
            return

        self._application.addAdditionalComponent("jobSpecsButton", self._additional_components)
        self._additional_components.patchParent()

    def _onGlobalStackChanged(self) -> None:
        self.jobAffixesChanged.emit()

    @pyqtSlot()
    def showNameDialog(self) -> None:
        global_container_stack = self._application.getGlobalContainerStack()
        if not global_container_stack:
            return

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._qml_folder, "PrefixDialog.qml")
        self._prefix_dialog = self._application.createQmlComponent(path, {"manager": self})
        if self._prefix_dialog:
            self._prefix_dialog.show()

    jobAffixesChanged = pyqtSignal()

    @pyqtSlot(str, str, str)
    def setJobAffixes(self, prefix: str, postfix: str, path: str) -> None:
        global_container_stack = self._application.getGlobalContainerStack()
        if not global_container_stack:
            return

        global_container_stack.setMetaDataEntry("custom_job_prefix", prefix)
        global_container_stack.setMetaDataEntry("custom_job_postfix", postfix)
        global_container_stack.setMetaDataEntry("custom_job_path", path)
        self.jobAffixesChanged.emit()

    @pyqtProperty(str, notify=jobAffixesChanged)
    def jobPrefix(self) -> str:
        global_container_stack = self._application.getGlobalContainerStack()
        if not global_container_stack:
            return ""

        return global_container_stack.getMetaDataEntry("custom_job_prefix", "{printer_type}")

    @pyqtProperty(str, notify=jobAffixesChanged)
    def jobPostfix(self) -> str:
        global_container_stack = self._application.getGlobalContainerStack()
        if not global_container_stack:
            return ""

        return global_container_stack.getMetaDataEntry("custom_job_postfix", "")

    @pyqtProperty(str, notify=jobAffixesChanged)
    def jobPath(self) -> str:
        global_container_stack = self._application.getGlobalContainerStack()
        if not global_container_stack:
            return ""

        return global_container_stack.getMetaDataEntry("custom_job_path", "")

    @pyqtProperty(QObject, constant=True)
    def printInformation(self) -> Optional[PrintInformationPatches.PrintInformationPatches]:
        return self._print_information_patches
