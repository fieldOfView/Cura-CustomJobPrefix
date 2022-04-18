// Copyright (c) 2022 Aldo Hoeben / fieldOfView
// CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.0

import UM 1.5 as UM
import Cura 1.0 as Cura


UM.Dialog
{
    id: base

    title: catalog.i18nc("@title:window", "Custom Printjob Naming")

    buttonSpacing: UM.Theme.getSize("default_margin").width
    minimumWidth: 450 * screenScaleFactor
    minimumHeight: contents.childrenRect.height + 3 * UM.Theme.getSize("default_margin").height
    width: minimumWidth
    height: minimumHeight

    onAccepted:
    {
        manager.setJobAffixes(prefixField.text, postfixField.text, pathField.text);
    }

    property variant catalog: UM.I18nCatalog { name: "cura" }
    property variant palette: SystemPalette {}

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
        id: contents
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").height

        UM.Label
        {
            text:
            {
                var printer_name = Cura.MachineManager.activeMachineName;
                if (printer_name === undefined) printer_name = Cura.MachineManager.activeMachine.name;
                return catalog.i18nc("@info", "Enter name patterns to use for printer %0.").arg(printer_name);
            }
            font.bold: true
            width: parent.width
            wrapMode: Text.WordWrap
        }

        Grid
        {
            columns: 2;
            columnSpacing: UM.Theme.getSize("default_margin").width
            rowSpacing: UM.Theme.getSize("default_lining").height
            verticalItemAlignment: Grid.AlignVCenter

            UM.Label
            {
                text: catalog.i18nc("@label", "Prefix:")
            }

            Cura.TextField
            {
                id: prefixField
                text: manager.jobPrefix
                width: Math.floor(base.width * 0.8)
                maximumLength: 255
                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]\;\~\&\"]*$/
                }
                enabled: prefixJobNameCheckbox.checked
            }

            UM.Label
            {
                text: catalog.i18nc("@label", "Postfix:")
            }

            Cura.TextField
            {
                id: postfixField
                text: manager.jobPostfix
                width: Math.floor(base.width * 0.8)
                maximumLength: 255
                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]\;\~\&\"]*$/
                }
                enabled: prefixJobNameCheckbox.checked
            }

            UM.Label
            {
                text: catalog.i18nc("@label", "Path:")
            }

            Row
            {
                spacing: UM.Theme.getSize("narrow_margin").width

                UM.TooltipArea
                {
                    id: pathFieldContainer
                    width: childrenRect.width;
                    height: childrenRect.height;

                    text: catalog.i18nc("@info:tooltip", "This path must be relative and will only be used with selected outputs, such as the removable drive output.")

                    Cura.TextField
                    {
                        id: pathField
                        text: manager.jobPath
                        width: Math.floor(base.width * 0.8)
                        maximumLength: 255
                        validator: RegExpValidator {
                            regExp: /^[^\/][^\\\*\?\|\[\]\;\~\&\"]*$/
                        }
                        enabled: prefixJobNameCheckbox.checked
                    }
                }
                UM.TooltipArea
                {
                    width: childrenRect.width;
                    height: childrenRect.height;
                    anchors.verticalCenter: pathFieldContainer.verticalCenter
                    visible: !manager.printInformation.outputDeviceSupportsPath

                    text: catalog.i18nc("@info:tooltip", "The current output does not support paths.")

                    UM.RecolorImage
                    {
                        width: Math.round(pathFieldContainer.height * 0.6) | 0
                        height: width
                        source: UM.Theme.getIcon("warning")

                        color: palette.buttonText
                    }
                }
            }
        }

        UM.Label
        {
            text: catalog.i18nc("@info", "Available replacement patterns:")
            width: parent.width
            wrapMode: Text.WordWrap
        }

        TextEdit
        {
            text: "{printer_name}, {printer_name_full}, {printer_type}, {printer_type_full}, {layer_height}, {machine_nozzle_size}, {infill_sparse_density}, {speed_print}, {material_flow}, {profile_name}, {profile_name_full}, " +
                  "{material_name}, {material_name_full}, {material_type}, {material_type_full}, {material_weight}, {print_time_hours}, {print_time_minutes}, {date_iso}, {date_year}, {date_month}, {date_day}, {time_iso}, {time_hour}, {time_minutes}"
            width: parent.width
            renderType: Text.NativeRendering
            readOnly: true
            wrapMode: Text.WordWrap
            selectByMouse: true
            mouseSelectionMode: TextEdit.SelectWords
            onSelectionStartChanged: updateSelection()
            onSelectionEndChanged: updateSelection()

            function updateSelection()
            {
                var start = selectionStart
                var end = selectionEnd

                if(start > 0 && text.substr(start - 1, 1) == "{")
                    start--;
                if(end < text.length && text.substr(end, 1) == "}")
                    end++;

                if(start != selectionStart || end != selectionEnd)
                    select(start, end);
            }
        }

        UM.Label
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

                UM.CheckBox
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

                UM.CheckBox
                {
                    id: addSeparatorCheckbox
                    text: catalog.i18nc("@option:check", "Add '_' between jobname parts")
                    checked: boolCheck(UM.Preferences.getValue("customjobprefix/add_separator"))
                    onCheckedChanged: UM.Preferences.setValue("customjobprefix/add_separator", checked)
                    enabled: prefixJobNameCheckbox.checked
                }
            }

            UM.TooltipArea
            {
                width: childrenRect.width
                height: childrenRect.height
                text: catalog.i18nc("@info:tooltip", "Remove accents and replace spaces with an `_` character?")

                UM.CheckBox
                {
                    id: stripAccentsAndSpaces
                    text: catalog.i18nc("@option:check", "Sanitise jobname parts")
                    checked: boolCheck(UM.Preferences.getValue("customjobprefix/sanitise_affixes"))
                    onCheckedChanged: UM.Preferences.setValue("customjobprefix/sanitise_affixes", checked)
                    enabled: prefixJobNameCheckbox.checked
                }
            }
        }
    }

    rightButtons: [
        Cura.SecondaryButton
        {
            text: catalog.i18nc("@action:button","Cancel")
            onClicked: base.reject()
        },
        Cura.PrimaryButton
        {
            text: catalog.i18nc("@action:button", "OK")
            onClicked: base.accept()
        }
    ]
}

