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

    property string dialogTitle: catalog.i18nc("@title:window", "Custom Printjob Prefix")
    property string explanation: catalog.i18nc("@info", "Enter the prefix to use for printer %0.").arg(Cura.MachineManager.activeMachine.name)

    title: dialogTitle

    minimumWidth: 400 * screenScaleFactor
    minimumHeight: 120 * screenScaleFactor
    width: minimumWidth
    height: minimumHeight

    property variant catalog: UM.I18nCatalog { name: "cura" }

    Column
    {
        anchors.fill: parent

        Label
        {
            text: base.explanation + "\n" //Newline to make some space using system theming.
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

