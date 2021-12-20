# Copyright (c) 2020 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

from cura.CuraApplication import CuraApplication

import re
import os.path
import unicodedata

from PyQt5.QtCore import Qt, QDate, QTime, QObject, pyqtProperty, pyqtSignal, pyqtSlot

from typing import Any, Optional, TYPE_CHECKING

import uuid

if TYPE_CHECKING:
    from cura.Settings.GlobalStack import GlobalStack

from UM.i18n import i18nCatalog

catalog = i18nCatalog("cura")


class PrintInformationPatches(QObject):
    def __init__(self, print_information, parent: QObject = None) -> None:
        super().__init__(parent)

        self._print_information = print_information
        self._application = CuraApplication.getInstance()

        self._preferences = self._application.getPreferences()
        self._preferences.addPreference("customjobprefix/add_separator", True)
        self._preferences.addPreference("customjobprefix/sanitise_affixes", True)
        self._preferences.addPreference("customjobprefix/use_base_name", True)
        if self._preferences.getValue("cura/jobname_prefix") == None:
            self._preferences.addPreference("cura/jobname_prefix",
                                            True)  # restore preference that was removed in Cura 4.7
        self._preferences.preferenceChanged.connect(self._onPreferencesChanged)

        self._application.globalContainerStackChanged.disconnect(self._print_information._updateJobName)
        self._application.globalContainerStackChanged.connect(self._updateJobName)
        self._print_information._updateJobName = self._updateJobName

        self._print_information.currentPrintTimeChanged.connect(self._triggerJobNameUpdate)
        self._print_information.materialWeightsChanged.connect(self._triggerJobNameUpdate)
        self._print_information.jobNameChanged.connect(self._onJobNameChanged)
        self._application.workspaceLoaded.disconnect(self._print_information.setProjectName)

        self._application.getOutputDeviceManager().activeDeviceChanged.connect(self._onOutputDeviceChanged)

        self._formatted_path = ""
        self._formatted_prefix = ""
        self._formatted_postfix = ""

        self._path_enabled_output_devices = ["RemovableDriveOutputDevice", "OctoPrintOutputDevice",
                                             "DuetRRFOutputDevice"]

        self._global_stack = None  # type: Optional[GlobalStack]
        self._application.getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        self._onMachineChanged()

        # limit this to Cura 4.5 and newer
        if hasattr(CuraApplication, "getWorkspaceMetadataStorage"):
            self._ignore_base_name_change = False
            self._last_base_name = ""
            self._print_information.jobNameChanged.connect(self._onBaseNameChanged)  # baseNameChanged does not work
            self._application.workspaceLoaded.connect(self._onWorkSpaceLoaded)

    def _onBaseNameChanged(self) -> None:
        if self._ignore_base_name_change:
            self._ignore_base_name_change = False
            return

        base_name = self._print_information._base_name
        if base_name == self._last_base_name:
            return

        self._last_base_name = base_name

        metadata_storage = self._application.getWorkspaceMetadataStorage()
        metadata = metadata_storage.getPluginMetadata("CustomJobPrefix")

        if "base_name" not in metadata or metadata["base_name"] != base_name:
            metadata_storage.setEntryToStore("CustomJobPrefix", "base_name", base_name)

        self.jobAffixesChanged.emit()

    def _onWorkSpaceLoaded(self, workspace_name: str) -> None:
        self._ignore_base_name_change = True
        base_name = self._print_information._base_name

        metadata_storage = self._application.getWorkspaceMetadataStorage()
        metadata = metadata_storage.getPluginMetadata("CustomJobPrefix")

        if "base_name" in metadata and metadata["base_name"] != base_name:
            self.setBaseName(metadata["base_name"])

    def _onJobNameChanged(self) -> None:
        if self._print_information._is_user_specified_job_name:
            job_name = self._print_information._job_name
            if job_name == catalog.i18nc("@text Print job name", "Untitled"):
                return

            self._print_information._is_user_specified_job_name = False

    def _onMachineChanged(self) -> None:
        if self._global_stack:
            self._global_stack.containersChanged.disconnect(self._triggerJobNameUpdate)
            self._global_stack.metaDataChanged.disconnect(self._triggerJobNameUpdate)

        self._global_stack = CuraApplication.getInstance().getGlobalContainerStack()

        if self._global_stack:
            self._global_stack.containersChanged.connect(self._triggerJobNameUpdate)
            self._global_stack.metaDataChanged.connect(self._triggerJobNameUpdate)

    def _onPreferencesChanged(self, name: str) -> None:
        if name in ["cura/jobname_prefix", "customjobprefix/add_separator", "customjobprefix/sanitise_affixes",
                    "customjobprefix/use_base_name"]:
            self._updateJobName()
            self.jobAffixesChanged.emit()

    def _onOutputDeviceChanged(self) -> None:
        self._triggerJobNameUpdate()
        self.outputDeviceChanged.emit()

    def _triggerJobNameUpdate(self, *args, **kwargs) -> None:
        self._updateJobName()

    def _updateJobName(self) -> None:
        base_name = self._stripAccents(self._print_information._base_name)
        if self._preferences.getValue("customjobprefix/sanitise_affixes"):
            base_name = re.sub(r"[; \?\*\:]", "_", base_name).strip("_")

        if base_name == "":
            self._print_information._job_name = catalog.i18nc("@text Print job name", "Untitled")
            self._print_information._is_user_specified_job_name = False
            self._print_information.jobNameChanged.emit()
            return

        if self._preferences.getValue("cura/jobname_prefix") and not self._print_information._pre_sliced:
            self._formatdAffixes()
            separator = "_" if self._preferences.getValue("customjobprefix/add_separator") else ""
            use_base_name = self._preferences.getValue("customjobprefix/use_base_name")
            self._print_information._job_name = self._formatted_prefix + (separator if self._formatted_prefix else "") + \
                                                (base_name if use_base_name else "") + \
                                                (separator if self._formatted_postfix else "") + self._formatted_postfix
        else:
            self._print_information._job_name = base_name

        # Add path
        if self._formatted_path and type(
                self._application.getOutputDeviceManager().getActiveDevice()).__name__ in self._path_enabled_output_devices:
            self._print_information._job_name = "%s/%s" % (self._formatted_path, self._print_information._job_name)

        # In case there are several buildplates, a suffix is attached
        if self._print_information._multi_build_plate_model.maxBuildPlate > 0:
            connector = "_#"
            suffix = connector + str(self._print_information._active_build_plate + 1)
            if connector in self._print_information._job_name:
                self._print_information._job_name = self._print_information._job_name.split(connector)[
                    0]  # get the real name
            if self._print_information._active_build_plate != 0:
                self._print_information._job_name += suffix

        self._print_information.jobNameChanged.emit()

    def _formatdAffixes(self) -> None:
        self._formatted_prefix = ""
        self._formatted_postfix = ""
        self._formatted_path = ""

        if not self._global_stack:
            return

        extruder_stack = self._application.getExtruderManager().getActiveExtruderStacks()[0]
        if not extruder_stack:
            return
        try:
            extruder_nr = int(extruder_stack.getProperty("extruder_nr", "value"))
        except ValueError:
            return

        job_path = self._global_stack.getMetaDataEntry("custom_job_path", "")
        job_prefix = self._global_stack.getMetaDataEntry("custom_job_prefix", "{printer_type}")
        job_postfix = self._global_stack.getMetaDataEntry("custom_job_postfix", "")

        profile_name = self._global_stack.quality.getName()
        if self._global_stack.qualityChanges.id != "empty_quality_changes":
            profile_name = self._global_stack.qualityChanges.getName()
        material_name = "%s %s" % (extruder_stack.material.getMetaDataEntry("brand"), extruder_stack.material.getName())

        replacements = {
            "{printer_name}": self._abbreviate_name(self._global_stack.getName()),
            "{printer_name_full}": self._global_stack.getName(),
            "{printer_type}": self._abbreviate_name(self._global_stack.definition.getName()),
            "{printer_type_full}": self._global_stack.definition.getName(),
            "{layer_height}": self._abbreviate_number(self._global_stack.getProperty("layer_height", "value")),
            "{machine_nozzle_size}": self._abbreviate_number(
                extruder_stack.getProperty("machine_nozzle_size", "value")),
            "{infill_sparse_density}": self._abbreviate_number(
                extruder_stack.getProperty("infill_sparse_density", "value")),
            "{speed_print}": self._abbreviate_number(extruder_stack.getProperty("speed_print", "value")),
            "{material_flow}": self._abbreviate_number(extruder_stack.getProperty("material_flow", "value")),
            "{profile_name}": self._abbreviate_name(profile_name),
            "{profile_name_full}": profile_name,
            "{material_name}": self._abbreviate_name(material_name),
            "{material_name_full}": material_name,
            "{material_type}": self._abbreviate_name(extruder_stack.material.getMetaDataEntry("material")),
            "{material_type_full}": extruder_stack.material.getMetaDataEntry("material"),
            "{material_weight}": str(round(self._print_information.materialWeights[extruder_nr]) if extruder_nr < len(
                self._print_information.materialWeights) else 0),
            "{print_time_hours}": str(
                self._print_information.currentPrintTime.days * 24 + self._print_information.currentPrintTime.hours),
            "{print_time_minutes}": str(self._print_information.currentPrintTime.minutes).zfill(2),
            "{date_iso}": QDate.currentDate().toString(format=Qt.ISODate),
            "{date_year}": QDate.currentDate().toString("yy"),
            "{date_month}": QDate.currentDate().toString("MM"),
            "{date_day}": QDate.currentDate().toString("dd"),
            "{time_iso}": QTime.currentTime().toString(format=Qt.ISODate),
            "{time_hour}": QTime.currentTime().toString("HH"),
            "{time_minutes}": QTime.currentTime().toString("mm"),
            "{random}": uuid.uuid4().hex[:10]  # 10 random hex digits
        }
        replacements = dict((re.escape(k), v) for k, v in replacements.items())  # escape for re
        pattern = re.compile("|".join(replacements.keys()))
        job_prefix = pattern.sub(lambda m: replacements[re.escape(m.group(0))], job_prefix)
        job_postfix = pattern.sub(lambda m: replacements[re.escape(m.group(0))], job_postfix)
        job_path = pattern.sub(lambda m: replacements[re.escape(m.group(0))], job_path)

        if self._preferences.getValue("customjobprefix/sanitise_affixes"):
            job_prefix = self._stripAccents(job_prefix).replace(" ", "_")
            job_postfix = self._stripAccents(job_postfix).replace(" ", "_")

            job_path = self._stripAccents(job_path).replace(" ", "_").strip("/")

        if job_prefix != self._formatted_prefix or job_postfix != self._formatted_postfix or job_path != self._formatted_path:
            self._formatted_prefix = job_prefix
            self._formatted_postfix = job_postfix
            self._formatted_path = job_path
            self.jobAffixesChanged.emit()

    def _abbreviate_number(self, number: float) -> str:
        return str(number).replace(".", "")

    def _abbreviate_name(self, name: str) -> str:
        abbr_name = ""
        for word in re.findall(r"[\w']+", name):
            if word.lower() == "ultimaker":
                abbr_name += "UM"
            elif word.isdigit():
                abbr_name += word
            else:
                stripped_word = self._stripAccents(word.upper())
                # - use only the first character if the word is too long (> 4 characters)
                # - use the whole word if it's not too long (<= 4 characters)
                if len(stripped_word) > 4:
                    stripped_word = stripped_word[0]
                abbr_name += stripped_word

        return abbr_name

    jobAffixesChanged = pyqtSignal()

    @pyqtProperty(str, notify=jobAffixesChanged)
    def formattedPrefix(self) -> str:
        if not self._preferences.getValue("cura/jobname_prefix"):
            return ""
        if self._formatted_prefix == "":
            return ""
        separator = "_" if self._preferences.getValue("customjobprefix/add_separator") else ""
        return self._formatted_prefix + separator

    @pyqtProperty(str, notify=jobAffixesChanged)
    def formattedPostfix(self) -> str:
        if not self._preferences.getValue("cura/jobname_prefix"):
            return ""
        if self._formatted_postfix == "":
            return ""
        separator = "_" if self._preferences.getValue("customjobprefix/add_separator") else ""
        return separator + self._formatted_postfix

    @pyqtProperty(str, notify=jobAffixesChanged)
    def formattedPath(self) -> str:
        if not self._preferences.getValue("cura/jobname_prefix"):
            return ""

        if self._formatted_postfix != "" or self._formatted_path.endswith(os.path.sep):
            return self._formatted_path
        return self._formatted_path + os.path.sep

    @pyqtProperty(str, notify=jobAffixesChanged)
    def baseName(self) -> str:
        return self._print_information._base_name

    @pyqtSlot(str)
    def setBaseName(self, base_name) -> None:
        self._print_information._base_name = base_name
        self._print_information.baseNameChanged.emit()
        self._updateJobName()

    outputDeviceChanged = pyqtSignal()

    @pyqtProperty(bool, notify=outputDeviceChanged)
    def outputDeviceSupportsPath(self) -> bool:
        return type(
            self._application.getOutputDeviceManager().getActiveDevice()).__name__ in self._path_enabled_output_devices

    def _stripAccents(self, to_strip: str) -> str:
        """Utility method that strips accents from characters (eg: â -> a)"""

        return ''.join(char for char in unicodedata.normalize('NFD', to_strip) if unicodedata.category(char) != 'Mn')
