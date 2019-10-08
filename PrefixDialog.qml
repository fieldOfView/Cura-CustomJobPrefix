// Copyright (c) 2019 fieldOfView
// CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 1.1
import QtQuick.Dialogs 1.2
import QtQuick.Window 2.1

import UM 1.3 as UM
import Cura 1.1 as Cura

UM.Dialog
{
    id: base

    title: catalog.i18nc("@title:window", "Custom Printjob Prefix")

    minimumWidth: 400 * screenScaleFactor
    minimumHeight: 180 * screenScaleFactor
    width: minimumWidth
    height: minimumHeight

    property variant catalog: UM.I18nCatalog { name: "cura" }

    Column
    {
        anchors.fill: parent
        spacing: UM.Theme.getSize("default_margin").height

        Label
        {
            text: catalog.i18nc("@info", "Enter the prefix to use for printer %0.").arg(Cura.MachineManager.activeMachineName)
            width: parent.width
            wrapMode: Text.WordWrap
        }

        TextField
        {
            id: prefixField
            width: parent.width
            text: manager.jobPrefix
            maximumLength: 80
            validator: RegExpValidator {
                regExp: /^[^\\\/\*\?\|\[\]]*$/
            }
        }

        Label
        {
            text: catalog.i18nc("@info", "Available replacement patterns:")
            width: parent.width
            wrapMode: Text.WordWrap
        }
        Label
        {
            text: "{printer_name}, {printer_type}, {material_type}, {layer_height}, {machine_nozzle_size}"
            width: parent.width
            wrapMode: Text.WordWrap
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
            onClicked: {
            	manager.jobPrefix = prefixField.text
            	base.accept()
            }
            isDefault: true
        }
    ]
}

