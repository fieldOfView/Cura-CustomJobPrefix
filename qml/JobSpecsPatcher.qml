// Copyright (c) 2020 Aldo Hoeben / fieldOfView
// CustomJobPrefix is released under the terms of the AGPLv3 or higher.

import QtQuick 2.2
import QtQuick.Controls 1.1
import QtQuick.Controls.Styles 1.1

import UM 1.2 as UM


Item
{
    id: customJobName

    UM.I18nCatalog
    {
        id: catalog
        name: "cura"
    }

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
            spacing: -3 * screenScaleFactor

            Button
            {
                id: printJobPencilIcon
                anchors.verticalCenter: parent.verticalCenter
                width: UM.Theme.getSize("save_button_specs_icons").width
                height: UM.Theme.getSize("save_button_specs_icons").height

                onClicked:
                {
                    modelNameTextfield.selectAll()
                    modelNameTextfield.focus = true
                }

                style: ButtonStyle
                {
                    background: Item
                    {
                        UM.RecolorImage
                        {
                            width: UM.Theme.getSize("save_button_specs_icons").width
                            height: UM.Theme.getSize("save_button_specs_icons").height
                            sourceSize.width: width
                            sourceSize.height: width
                            color: control.hovered ? UM.Theme.getColor("small_button_text_hover") : UM.Theme.getColor("small_button_text")
                            source: UM.Theme.getIcon("pencil")
                        }
                    }
                }
            }

            // spacer
            Item { width: UM.Theme.getSize("narrow_margin").width + 3 * screenScaleFactor; height: 1 }

            Label
            {
                id: prefixLabel
                text: customJobPrefix.printInformation.formattedPrefix + "_"
                color: UM.Theme.getColor("text_scene")
                opacity: 0.7
                font: UM.Theme.getFont("default")
                height: UM.Theme.getSize("jobspecs_line").height
                verticalAlignment: Text.AlignVCenter
                renderType: Text.NativeRendering
            }

            TextField
            {
                id: modelNameTextfield
                height: UM.Theme.getSize("jobspecs_line").height
                width: Math.max(__contentWidth + UM.Theme.getSize("default_margin").width, 50)
                maximumLength: 120
                text: (PrintInformation === null) ? "" : PrintInformation.jobName.slice(prefixLabel.text.length)
                horizontalAlignment: TextInput.AlignLeft

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
                        PrintInformation.setJobName(prefixLabel.text + new_name, true)
                    }
                    modelNameTextfield.focus = false
                }

                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]]*$/
                }

                style: TextFieldStyle
                {
                    textColor: UM.Theme.getColor("text_scene")
                    font: UM.Theme.getFont("default")
                    background: Rectangle
                    {
                        opacity: 0
                        border.width: 0
                    }
                }
            }
        }
    }
}
