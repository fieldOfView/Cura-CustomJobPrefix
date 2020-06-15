# Copyright (c) 2020 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import os.path

from UM.Extension import Extension
from UM.Logger import Logger
from cura.CuraApplication import CuraApplication

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSignal, pyqtSlot

from . import PrintInformationPatches

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")


class CustomJobPrefix(Extension, QObject,):
    def __init__(self, parent = None) -> None:
        QObject.__init__(self, parent)
        Extension.__init__(self)

        self._application = CuraApplication.getInstance()

        self.addMenuItem(catalog.i18nc("@item:inmenu", "Set name options"), self.showNameDialog)

        self._create_profile_window = None
        self._print_information_patches = None

        self._application.engineCreatedSignal.connect(self._onEngineCreated)
        self._application.globalContainerStackChanged.connect(self._onGlobalStackChanged)

    def _onEngineCreated(self) -> None:
        self._print_information_patches = PrintInformationPatches.PrintInformationPatches(self._application.getPrintInformation())
        self._createAdditionalComponentsView()

    def _createAdditionalComponentsView(self) -> None:
        Logger.log("d", "Creating additional ui components for CustomJobPrefix")

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "JobSpecsPatcher.qml")
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

        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qml", "PrefixDialog.qml")
        self._create_profile_window = self._application.createQmlComponent(path, {"manager": self})
        self._create_profile_window.show()

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

        return global_container_stack.getMetaDataEntry("custom_job_prefix", "")

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
    def printInformation(self) -> PrintInformationPatches:
        return self._print_information_patches
