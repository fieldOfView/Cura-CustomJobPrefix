// Copyright (c) 2020 fieldOfView
// CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.3 as UM
import Cura 1.0 as Cura

UM.Dialog
{
    id: base

    title: catalog.i18nc("@title:window", "Custom Printjob Prefix")

    minimumWidth: 400 * screenScaleFactor
    minimumHeight: 220 * screenScaleFactor
    width: minimumWidth
    height: minimumHeight

    onAccepted: manager.jobPrefix = prefixField.text

    property variant catalog: UM.I18nCatalog { name: "cura" }

    function boolCheck(value) //Hack to ensure a good match between python and qml.
    {
        if(value == "True")
        {
            return true
        }else if(value == "False" || value == undefined)
        {
            return false
        }
        else
        {
            return value
        }
    }

    Column
    {
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").height

        Label
        {
            text:
            {
                var printer_name = Cura.MachineManager.activeMachineName;
                if (printer_name === undefined) printer_name = Cura.MachineManager.activeMachine.name;
                return catalog.i18nc("@info", "Enter the prefix to use for printer %0.").arg(printer_name);
            }
            width: parent.width
            wrapMode: Text.WordWrap
        }

        TextField
        {
            id: prefixField
            width: parent.width
            text: manager.jobPrefix
            maximumLength: 255
            validator: RegExpValidator {
                regExp: /^[^\\\/\*\?\|\[\]]*$/
            }
            enabled: prefixJobNameCheckbox.checked
        }

        Label
        {
            text: catalog.i18nc("@info", "Available replacement patterns:")
            width: parent.width
            wrapMode: Text.WordWrap
        }
        Label
        {
            text: "{printer_name}, {printer_type}, {layer_height}, {machine_nozzle_size}, {infill_sparse_density}, {speed_print}, {material_type}, {material_weight}, {print_time_hours}, {print_time_minutes}, {date_year}, {date_month}, {date_day}, {time_hour}, {time_minutes}"
            width: parent.width
            wrapMode: Text.WordWrap
        }

        UM.TooltipArea
        {
            width: childrenRect.width
            height: childrenRect.height
            text: catalog.i18nc("@info:tooltip", "Add a customisable prefix to the print job name automatically?")

            CheckBox
            {
                id: prefixJobNameCheckbox
                text: catalog.i18nc("@option:check", "Add prefix to job name")
                checked: boolCheck(UM.Preferences.getValue("cura/jobname_prefix"))
                onCheckedChanged: UM.Preferences.setValue("cura/jobname_prefix", checked)
            }
        }
    }

    rightButtons: [
        Button
        {
            id: cancelButton
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Button
        {
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
            isDefault: true
        }
    ]
}

