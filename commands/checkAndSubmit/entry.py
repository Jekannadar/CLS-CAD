import json
import adsk.core
import os
import inspect
import copy
from ...lib.cls_python_compat import *
from ...lib import fusion360utils as futil
from ... import config

app = adsk.core.Application.get()
ui = app.userInterface
joint = None

CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cns'
CMD_NAME = 'Súbmit'
CMD_Description = 'Check and Submit part to repository.'
IS_PROMOTED = True

WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'CRAWL'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resources
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'resources', '')

ROOT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..',
                           '..')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []


def start():
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME,
                                                        CMD_Description,
                                                        ICON_FOLDER)
    futil.add_handler(cmd_def.commandCreated, command_created)

    # UI Register
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)
    control.isPromoted = IS_PROMOTED


def stop():
    #Clean entire Panel
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    for i in range(panel.controls.count):
        if panel.controls.item(0):
            panel.controls.item(0).deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


typeTextBoxInput = adsk.core.TextBoxCommandInput.cast(None)


def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')
    global typeTextBoxInput

    # Handlers
    futil.add_handler(args.command.execute,
                      command_execute,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged,
                      command_input_changed,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview,
                      command_preview,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.destroy,
                      command_destroy,
                      local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs,
                      command_validate,
                      local_handlers=local_handlers)

    inputs = args.command.commandInputs
    args.command.setDialogMinimumSize(800, 800)
    args.command.setDialogInitialSize(800, 800)

    # UI
    typeTextBoxInput = inputs.addTextBoxCommandInput('typeTextBox', 'Issues',
                                                     '', 1, True)

    typeTextBoxInput.numRows = 12


def winapi_path(dos_path, encoding=None):
    if (not isinstance(dos_path, str) and encoding is not None):
        dos_path = dos_path.decode(encoding)
    path = os.path.abspath(dos_path)
    if path.startswith(u"\\\\"):
        return u"\\\\?\\UNC\\" + path[2:]
    return u"\\\\?\\" + path


def command_executePreview(args: adsk.core.CommandEventHandler):
    return


def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug
    futil.log(f'{CMD_NAME} Command Execute Event')

    inputs = args.command.commandInputs

    # Get Inputs
    nesting_input: adsk.core.BoolValueCommandInput = inputs.itemById('nesting')

    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)

    providesAttributes = json.loads(
        getattr(
            design.rootComponent.attributes.itemByName("CLS-PART",
                                                       "ProvidesAttributes"),
            "value", "[]"))
    providesParts = json.loads(
        getattr(
            design.rootComponent.attributes.itemByName("CLS-PART",
                                                       "ProvidesParts"),
            "value", "[]"))

    #Demo of data interchange to backend
    joInfos = []
    for jointTyping in design.findAttributes("CLS-INFO", "UUID"):
        jo = jointTyping.parent
        joUUID = jo.attributes.itemByName("CLS-INFO", "UUID").value
        joReqFormats = json.loads(
            jo.attributes.itemByName("CLS-JOINT", "RequiresFormats").value)
        joReqParts = json.loads(
            jo.attributes.itemByName("CLS-JOINT", "RequiresParts").value)
        joReqAttributes = json.loads(
            jo.attributes.itemByName("CLS-JOINT", "RequiresAttributes").value)
        joProvFormats = json.loads(
            jo.attributes.itemByName("CLS-JOINT", "ProvidesFormats").value)
        joInfos.append((joUUID, [s + "_format" for s in joReqFormats] +
                        [s + "_part" for s in joReqParts] +
                        [s + "_attribute" for s in joReqAttributes],
                        [s + "_attribute" for s in providesAttributes] +
                        [s + "_part" for s in providesParts] +
                        [s + "_format" for s in joProvFormats]))
    configurations = []
    partDict = {"partConfigs": []}
    for info in joInfos:
        reqJoints = [x for x in joInfos if x != info]
        partDict["partConfigs"].append({
            "jointOrderUuids": [x[0] for x in reqJoints],
            "providesUuid": info[0]
        })
        arrow = Type.intersect(info[2])
        for reqJoint in reqJoints:
            arrow = Arrow(Type.intersect(reqJoint[1]), arrow)
        configurations.append(
            Arrow("_".join([x[0] for x in reqJoints + [info]]), arrow))
    partDict["combinator"] = CLSEncoder().default(
        Type.intersect(configurations))
    partDict["partName"] = app.activeDocument.name
    # this might be wrong and return the browsed ID
    partDict["forgeProjectId"] = app.data.activeProject.id
    partDict["forgeFolderId"] = app.data.activeFolder.id
    partDict["forgeDocumentId"] = app.activeDocument.dataFile.id

    with open(
            winapi_path(
                os.path.join(
                    ROOT_FOLDER, "_".join([
                        app.data.activeProject.id, app.data.activeFolder.id,
                        app.activeDocument.dataFile.id
                    ]).replace(":", "-") + ".json")), "w+") as f:
        json.dump(
            partDict,
            f,
            cls=CLSEncoder,
            indent=4,
        )


def command_preview(args: adsk.core.CommandEventArgs):
    inputs = args.command.commandInputs
    futil.log(f'{CMD_NAME} Command Preview Event')


def command_validate(args: adsk.core.ValidateInputsEventArgs):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    global typeTextBoxInput
    if design.findAttributes("CLS-JOINT", "ProvidesFormats"):
        typeTextBoxInput.formattedText = ""
        args.areInputsValid = True
    else:
        typeTextBoxInput.formattedText = "Parts need to at least provide one joint origin that has a  \"Provides\" type."
        args.areInputsValid = False
    futil.log(f'{CMD_NAME} Command Preview Event')


def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs
    futil.log(
        f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}'
    )


def command_destroy(args: adsk.core.CommandEventArgs):
    global local_handlers
    local_handlers = []
    futil.log(f'{CMD_NAME} Command Destroy Event')
