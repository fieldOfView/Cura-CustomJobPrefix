// Copyright (c) 2021 Aldo Hoeben / fieldOfView
// CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import QtQuick 2.1
import QtQuick.Controls 2.0

import UM 1.5 as UM
import Cura 1.0 as Cura


Item
{
    id: customJobName

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

    property bool preSlicedData: PrintInformation !== null && PrintInformation.preSliced

    function patchParent()
    {
        var jobSpecs = parent.parent;
        var jobNameRow = jobSpecs.children[0];
        for(var index in jobNameRow.children)
        {
            jobNameRow.children[index].visible = false;
        }
        for(var index in newJobNameRowChildren.children)
        {
            newJobNameRowChildren.children[index].parent = jobNameRow;
        }
    }

    Item
    {
        id: newJobNameRowChildren
        visible: false

        Row
        {
            UM.SimpleButton
            {
                id: printJobPencilIcon
                anchors.verticalCenter: parent.verticalCenter
                width: UM.Theme.getSize("save_button_specs_icons").width
                height: UM.Theme.getSize("save_button_specs_icons").height
                iconSource: UM.Theme.getIcon("Pen")
                hoverColor: UM.Theme.getColor("small_button_text_hover")
                color:  UM.Theme.getColor("small_button_text")

                onClicked:
                {
                    modelNameTextfield.selectAll()
                    modelNameTextfield.focus = true
                }
            }

            // spacer
            Item { width: UM.Theme.getSize("narrow_margin").width + 3 * screenScaleFactor; height: 1 }

            UM.SimpleButton
            {
                id: folderIcon
                anchors.verticalCenter: parent.verticalCenter
                width: UM.Theme.getSize("save_button_specs_icons").width
                height: UM.Theme.getSize("save_button_specs_icons").height
                iconSource: UM.Theme.getIcon("Folder")
                hoverColor: UM.Theme.getColor("small_button_text_hover")
                color:  UM.Theme.getColor("small_button_text")

                visible: customJobPrefix.jobPath != "" && customJobPrefix.printInformation.outputDeviceSupportsPath

                onClicked:
                {
                    customJobPrefix.showNameDialog()
                }
            }

            // conditional spacer
            Item { width: UM.Theme.getSize("narrow_margin").width + 3 * screenScaleFactor; height: 1; visible: folderIcon.visible }

            UM.Label
            {
                id: prefixLabel
                text: customJobPrefix.printInformation.formattedPrefix
                visible: !preSlicedData
                color: UM.Theme.getColor("text_scene")
                opacity: 0.7
                font: UM.Theme.getFont("default")
                height: UM.Theme.getSize("jobspecs_line").height
                verticalAlignment: Text.AlignVCenter
                renderType: Text.NativeRendering

                MouseArea
                {
                    anchors.fill: parent
                    onPressed: customJobPrefix.showNameDialog()
                }

            }

            Cura.TextField
            {
                id: modelNameTextfield
                height: UM.Theme.getSize("jobspecs_line").height
                width: __contentWidth + UM.Theme.getSize("default_margin").width
                maximumLength: 120
                leftPadding: 0
                rightPadding: 0
                text: (PrintInformation === null) ? "" : customJobPrefix.printInformation.baseName
                horizontalAlignment: TextInput.AlignLeft
                y: 2 * UM.Theme.getSize("default_lining").height

                property string textBeforeEdit: ""

                onActiveFocusChanged:
                {
                    if (activeFocus)
                    {
                        textBeforeEdit = text
                    }
                }

                onEditingFinished:
                {
                    if (text != textBeforeEdit) {
                        var new_name = text == "" ? catalog.i18nc("@text Print job name", "Untitled") : text
                        customJobPrefix.printInformation.setBaseName(new_name)
                    }
                    modelNameTextfield.focus = false
                }

                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]\;\~\&\"]*$/
                }
            }

            UM.Label
            {
                id: postfixLabel
                text: customJobPrefix.printInformation.formattedPostfix
                visible: !preSlicedData
                color: UM.Theme.getColor("text_scene")
                opacity: 0.7
                font: UM.Theme.getFont("default")
                height: UM.Theme.getSize("jobspecs_line").height
                verticalAlignment: Text.AlignVCenter
                renderType: Text.NativeRendering

                MouseArea
                {
                    anchors.fill: parent
                    onPressed: customJobPrefix.showNameDialog()
                }
            }
        }
    }
}
