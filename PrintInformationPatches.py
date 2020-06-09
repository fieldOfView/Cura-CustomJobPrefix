# Copyright (c) 2020 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

from cura.CuraApplication import CuraApplication
import re

from PyQt5.QtCore import Qt, QDate, QTime

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cura.Settings.GlobalStack import GlobalStack

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

class PrintInformationPatches():
    def __init__(self, print_information) -> None:
        self._print_information = print_information
        if hasattr(self._print_information, "_defineAbbreviatedMachineName"):
            self._print_information._defineAbbreviatedMachineName = self._defineAbbreviatedMachineName
        else:
            self._print_information._setAbbreviatedMachineName = self._defineAbbreviatedMachineName # 4.0 and before
        self._print_information.currentPrintTimeChanged.connect(self._triggerJobNameUpdate)
        self._print_information.materialWeightsChanged.connect(self._triggerJobNameUpdate)
        self._print_information.jobNameChanged.connect(self._onJobNameChanged)

        self._application = self._print_information._application

        self._global_stack = None # type: Optional[GlobalStack]
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        self._onMachineChanged()

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

    def _triggerJobNameUpdate(self, *args, **kwargs) -> None:
        self._print_information._updateJobName()

    ##  Hijacked to create a full prefix instead of an acronymn-like abbreviated machine name from the active machine name
    #   Called each time the global stack is switched, when settings change, when the global stack metadata changes and
    #   when a slice is completed
    def _defineAbbreviatedMachineName(self) -> None:
        self._print_information._abbr_machine = self._getFormattedPrefix()

    def _getFormattedPrefix(self) -> str:
        if not self._global_stack:
            return ""

        extruder_stack = self._application.getExtruderManager().getActiveExtruderStacks()[0]
        if not extruder_stack:
            return ""
        try:
            extruder_nr = int(extruder_stack.getProperty("extruder_nr", "value"))
        except ValueError:
            return ""

        job_prefix = self._global_stack.getMetaDataEntry("custom_job_prefix", "")
        if not job_prefix:
            # Use the default abbreviation of the active machine name
            active_machine_type_name = self._global_stack.definition.getName()
            return self._abbreviate_name(active_machine_type_name)
        else:
            replacements = {
                "{printer_name}": self._abbreviate_name(self._global_stack.getName()),
                "{printer_type}": self._abbreviate_name(self._global_stack.definition.getName()),
                "{layer_height}": self._abbreviate_number(self._global_stack.getProperty("layer_height", "value")),
                "{machine_nozzle_size}": self._abbreviate_number(extruder_stack.getProperty("machine_nozzle_size", "value")),
                "{infill_sparse_density}": self._abbreviate_number(extruder_stack.getProperty("infill_sparse_density", "value")),
                "{speed_print}": self._abbreviate_number(extruder_stack.getProperty("speed_print", "value")),
                "{material_type}": self._abbreviate_name(extruder_stack.material.getMetaDataEntry("material")),
                "{material_weight}": str(round(self._print_information.materialWeights[extruder_nr]) if extruder_nr < len(self._print_information.materialWeights) else 0),
                "{print_time_hours}": str(self._print_information.currentPrintTime.days * 24 + self._print_information.currentPrintTime.hours),
                "{print_time_minutes}": str(self._print_information.currentPrintTime.minutes),
                "{date_year}": QDate.currentDate().toString("yy"),
                "{date_month}": QDate.currentDate().toString("MM"),
                "{date_day}": QDate.currentDate().toString("dd"),
                "{time_hour}": QTime.currentTime().toString("HH"),
                "{time_minutes}": QTime.currentTime().toString("mm")
            }
            for pattern, replacement in replacements.items():
                job_prefix = job_prefix.replace(pattern, replacement)
            return job_prefix

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
                stripped_word = self._print_information._stripAccents(word.upper())
                # - use only the first character if the word is too long (> 4 characters)
                # - use the whole word if it's not too long (<= 4 characters)
                if len(stripped_word) > 4:
                    stripped_word = stripped_word[0]
                abbr_name += stripped_word

        return abbr_name
