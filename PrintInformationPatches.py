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

        self._global_stack = CuraApplication.getInstance().getGlobalContainerStack()

        if self._global_stack:
            self._global_stack.containersChanged.connect(self._onContainersChanged)

    def _onContainersChanged(self, container: Any) -> None:
        self._print_information._updateJobName()


    ##  Created an acronymn-like abbreviated machine name from the currently active machine name
    #   Called each time the global stack is switched
    def _defineAbbreviatedMachineName(self) -> None:
        global_container_stack = self._print_information._application.getGlobalContainerStack()
        if not global_container_stack:
            self._print_information._abbr_machine = ""
            return

        extruder_stack = self._print_information._application.getMachineManager()._active_container_stack
        if not extruder_stack:
            return

        material_type = self._abbreviate_name(extruder_stack.material.getMetaDataEntry("material"))
        printer_name = self._abbreviate_name(global_container_stack.getName())
        self._print_information._abbr_machine = "%s_%s" % (printer_name, material_type)
        return

    def _abbreviate_name(self, name: str) -> str:
        abbr_name = ""
        for word in re.findall(r"[\w']+", name):
            if word.lower() == "ultimaker":
                abbr_name += "UM"
            elif word.isdigit():
                abbr_name += word
            else:
                stripped_word = self._print_information._stripAccents(word.upper())
                # - use only the first character if the word is too long (> 3 characters)
                # - use the whole word if it's not too long (<= 3 characters)
                if len(stripped_word) > 3:
                    stripped_word = stripped_word[0]
                abbr_name += stripped_word

        return abbr_name
