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

            Button
            {
                id: folderIcon
                anchors.verticalCenter: parent.verticalCenter
                width: UM.Theme.getSize("save_button_specs_icons").width
                height: UM.Theme.getSize("save_button_specs_icons").height
                visible: customJobPrefix.jobPath != ""

                onClicked:
                {
                    customJobPrefix.showNameDialog()
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
                            source: UM.Theme.getIcon("load")
                        }
                    }
                }
            }

            // conditional spacer
            Item { width: UM.Theme.getSize("narrow_margin").width + 3 * screenScaleFactor; height: 1; visible: folderIcon.visible }

            Label
            {
                id: prefixLabel
                text: customJobPrefix.printInformation.formattedPrefix
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

            TextField
            {
                id: modelNameTextfield
                height: UM.Theme.getSize("jobspecs_line").height
                width: __contentWidth + UM.Theme.getSize("default_margin").width
                maximumLength: 120
                text: (PrintInformation === null) ? "" : customJobPrefix.printInformation.baseName
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
                        customJobPrefix.printInformation.setBaseName(new_name)
                    }
                    modelNameTextfield.focus = false
                }

                validator: RegExpValidator {
                    regExp: /^[^\\\/\*\?\|\[\]\;\~\&\"]*$/
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

            Label
            {
                id: postfixLabel
                text: customJobPrefix.printInformation.formattedPostfix
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
