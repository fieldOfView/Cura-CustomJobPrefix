// Copyright (c) 2020 Aldo Hoeben / fieldOfView
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

    title: catalog.i18nc("@title:window", "Custom Printjob name")

    minimumWidth: 450 * screenScaleFactor
    minimumHeight: 290 * screenScaleFactor
    width: minimumWidth
    height: minimumHeight

    onAccepted:
    {
        manager.setJobAffixes(prefixField.text, postfixField.text);
    }

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
                return catalog.i18nc("@info", "Enter prefix and postfix to use for printer %0.").arg(printer_name);
            }
            font.bold: true
            width: parent.width
            wrapMode: Text.WordWrap
        }

        Grid
        {
            columns: 2;
            flow: Grid.TopToBottom;
            columnSpacing: Math.round(UM.Theme.getSize("default_margin").width / 2);
            verticalItemAlignment: Grid.AlignVCenter

            Label
            {
                text: catalog.i18nc("@label", "Prefix:")
            }
            Label
            {
                text: catalog.i18nc("@label", "Postfix:")
            }
            TextField
            {
                id: prefixField
                text: manager.jobPrefix
                width: Math.floor(base.width * 0.8)
                maximumLength: 255
                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]]*$/
                }
                enabled: prefixJobNameCheckbox.checked
            }

            TextField
            {
                id: postfixField
                text: manager.jobPostfix
                width: Math.floor(base.width * 0.8)
                maximumLength: 255
                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]]*$/
                }
                enabled: prefixJobNameCheckbox.checked
            }
        }

        Label
        {
            text: catalog.i18nc("@info", "Available replacement patterns:")
            width: parent.width
            wrapMode: Text.WordWrap
        }

        TextEdit
        {
            text: "{printer_name}, {printer_name_full}, {printer_type}, {printer_type_full}, {layer_height}, {machine_nozzle_size}, {infill_sparse_density}, {speed_print}, {material_flow}, {profile_name}, {profile_name_full}, " +
                  "{material_name}, {material_name_full}, {material_type}, {material_type_full}, {material_weight}, {print_time_hours}, {print_time_minutes}, {date_year}, {date_month}, {date_day}, {time_hour}, {time_minutes}"
            width: parent.width
            renderType: Text.NativeRendering
            readOnly: true
            wrapMode: Text.WordWrap
            selectByMouse: true
        }

        Label
        {
            text: catalog.i18nc("@info", "Options for all printers")
            font.bold: true
            width: parent.width
            wrapMode: Text.WordWrap
        }

        Column
        {
            UM.TooltipArea
            {
                width: childrenRect.width
                height: childrenRect.height
                text: catalog.i18nc("@info:tooltip", "Append a customisable prefix and postfix to the print job name automatically?")

                CheckBox
                {
                    id: prefixJobNameCheckbox
                    text: catalog.i18nc("@option:check", "Enable prefix and postfix")
                    checked: boolCheck(UM.Preferences.getValue("cura/jobname_prefix"))
                    onCheckedChanged: UM.Preferences.setValue("cura/jobname_prefix", checked)
                }
            }

            UM.TooltipArea
            {
                width: childrenRect.width
                height: childrenRect.height
                text: catalog.i18nc("@info:tooltip", "Separate the prefix, base name and postfix with an `_` character?")

                CheckBox
                {
                    id: addSeparatorCheckbox
                    text: catalog.i18nc("@option:check", "Add '_' between jobname parts")
                    checked: boolCheck(UM.Preferences.getValue("customjobprefix/add_separator"))
                    onCheckedChanged: UM.Preferences.setValue("customjobprefix/add_separator", checked)
                    enabled: prefixJobNameCheckbox.checked
                }
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

