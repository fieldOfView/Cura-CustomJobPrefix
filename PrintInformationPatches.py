from cura.CuraApplication import CuraApplication
import re

from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cura.Settings.GlobalStack import GlobalStack

class PrintInformationPatches():
    def __init__(self, print_information) -> None:
        self._print_information = print_information
        self._print_information._defineAbbreviatedMachineName = self._defineAbbreviatedMachineName

        self._global_stack = None # type: Optional[GlobalStack]
        CuraApplication.getInstance().getMachineManager().globalContainerChanged.connect(self._onMachineChanged)
        self._onMachineChanged()

    def _onMachineChanged(self) -> None:
        if self._global_stack:
            self._global_stack.containersChanged.disconnect(self._onContainersChanged)
            self._global_stack.metaDataChanged.disconnect(self._onContainersChanged)

        self._global_stack = CuraApplication.getInstance().getGlobalContainerStack()

        if self._global_stack:
            self._global_stack.containersChanged.connect(self._onContainersChanged)
            self._global_stack.metaDataChanged.connect(self._onContainersChanged)

    def _onContainersChanged(self, container: Any) -> None:
        self._print_information._updateJobName()


    ##  Hijacked to create a full prefix instead of an acronymn-like abbreviated machine name from the active machine name
    #   Called each time the global stack is switched, when settings change and when the global stack metadata changes
    def _defineAbbreviatedMachineName(self) -> None:
        self._print_information._abbr_machine = self.getFormattedPrefix()

    def getFormattedPrefix(self) -> str:
        global_container_stack = self._print_information._application.getGlobalContainerStack()
        if not global_container_stack:
            return ""

        extruder_stack = self._print_information._application.getMachineManager()._active_container_stack
        if not extruder_stack:
            return ""

        job_prefix = global_container_stack.getMetaDataEntry("custom_job_prefix", "")
        if not job_prefix:
            # Use the default abbreviation of the active machine name
            active_machine_type_name = global_container_stack.definition.getName()
            return self._abbreviate_name(active_machine_type_name)
        else:
            replacements = {
                "{printer_name}": self._abbreviate_name(global_container_stack.getName()),
                "{printer_type}": self._abbreviate_name(global_container_stack.definition.getName()),
                "{material_type}": self._abbreviate_name(extruder_stack.material.getMetaDataEntry("material")),
                "{layer_height}": self._abbreviate_number(global_container_stack.getProperty("layer_height", "value")),
                "{machine_nozzle_size}": self._abbreviate_number(extruder_stack.getProperty("machine_nozzle_size", "value"))
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
