# Copyright (c) 2022 Aldo Hoeben / fieldOfView
# CustomJobPrefix is released under the terms of the AGPLv3 or higher.

from cura.CuraApplication import CuraApplication

from pathlib import Path

from typing import Set, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.OutputDevice.OutputDevice import OutputDevice

class OutputDevicePatcher():
    def __init__(self) -> None:
        self._application = CuraApplication.getInstance()
        self._application.getOutputDeviceManager().outputDevicesChanged.connect(self._onOutputDevicesChanged)
        self._output_device_ids = set()  # type: Set[OutputDevice]
        self._patched_output_devices = {}  # type: Dict[str, PatchedOutputDevice]

    def _onOutputDevicesChanged(self) -> None:
        output_device_ids = set(self._application.getOutputDeviceManager().getOutputDeviceIds())
        for output_device_id in output_device_ids - self._output_device_ids:
            output_device = self._application.getOutputDeviceManager().getOutputDevice(output_device_id)
            if output_device and type(output_device).__name__ == "RemovableDriveOutputDevice":
                self._patched_output_devices[output_device.getId()] = PatchedOutputDevice(output_device)

        self._output_device_ids = output_device_ids

class PatchedOutputDevice():
    def __init__(self, output_device) -> None:
        self._output_device = output_device
        self._requestWrite = self._output_device.requestWrite
        self._output_device.requestWrite = self.requestWrite

    def requestWrite(self, nodes, file_name = None, filter_by_machine = False, file_handler = None, **kwargs):
        path_name = (Path() / self._output_device.getId() / file_name).parent
        Path(path_name).mkdir(parents=True, exist_ok=True)

        self._requestWrite(nodes, file_name, filter_by_machine, file_handler, **kwargs)
