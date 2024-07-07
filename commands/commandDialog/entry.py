import adsk.core, adsk.fusion
import os
from ...lib import fusionAddInUtils as futil
from ... import config
app = adsk.core.Application.get()
ui = app.userInterface

# Necesitamos traer los parametros del diseño para poder modificarlos en el Fx
design = adsk.fusion.Design.cast(app.activeProduct)
userParams = design.userParameters

# TODO *** Specify the command identity information. ***
CMD_ID = f'{config.COMPANY_NAME}_{config.ADDIN_NAME}_cmdDialog'
CMD_NAME = 'Command Dialog Sample'
CMD_Description = 'A Fusion Add-in Command with a dialog'

# Specify that the command will be promoted to the panel.
IS_PROMOTED = True

# TODO *** Define the location where the command button will be created. ***
# This is done by specifying the workspace, the tab, and the panel, and the 
# command it will be inserted beside. Not providing the command to position it
# will insert it at the end.
WORKSPACE_ID = 'FusionSolidEnvironment'
PANEL_ID = 'SolidScriptsAddinsPanel'
COMMAND_BESIDE_ID = 'ScriptsManagerCommand'

# Resource location for command icons, here we assume a sub folder in this directory named "resources".
ICON_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', '')

# Local list of event handlers used to maintain a reference so
# they are not released and garbage collected.
local_handlers = []

# Obtener los parametros del usuario que tienen que existir dentro de la lista de parametros los guardo para usarlos despues
# Analizando tenemos tres grupos de movimiento
# 1 - Dedo Indicie 
# 2 - Resto de los dedos - el dedo gordo
# 3 - Dedo Gordo

# Variables de parametros de angulo del dedo indice
#ang_indice = design.userParameters.itemByName('ang_indice')
#ang_indice_pm = design.userParameters.itemByName('ang_indice_pm')
#ang_indice_pm = design.userParameters.itemByName('ang_indice_pm')

# Variables de parametros de angulo del esto de los dedos - el dedo gordo
#ang_otros = design.userParameters.itemByName('ang_otros')
#ang_otros_dp = design.userParameters.itemByName('ang_otros_dp')
#ang_otros_pm = design.userParameters.itemByName('ang_otros_pm')

# Variables de parametros de angulo del Dedo Gordo
#ang_gordo = design.userParameters.itemByName('ang_gordo')
#ang_gordo_g = design.userParameters.itemByName('ang_gordo_g')

# Executed when add-in is run.
def start():
    # Create a command Definition.
    cmd_def = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_Description, ICON_FOLDER)

    # Define an event handler for the command created event. It will be called when the button is clicked.
    futil.add_handler(cmd_def.commandCreated, command_created)

    # ******** Add a button into the UI so the user can run the command. ********
    # Get the target workspace the button will be created in.
    workspace = ui.workspaces.itemById(WORKSPACE_ID)

    # Get the panel the button will be created in.
    panel = workspace.toolbarPanels.itemById(PANEL_ID)

    # Create the button command control in the UI after the specified existing command.
    control = panel.controls.addCommand(cmd_def, COMMAND_BESIDE_ID, False)

    # Specify if the command is promoted to the main toolbar. 
    control.isPromoted = IS_PROMOTED


# Executed when add-in is stopped.
def stop():
    # Get the various UI elements for this command
    workspace = ui.workspaces.itemById(WORKSPACE_ID)
    panel = workspace.toolbarPanels.itemById(PANEL_ID)
    command_control = panel.controls.itemById(CMD_ID)
    command_definition = ui.commandDefinitions.itemById(CMD_ID)

    # Delete the button command control
    if command_control:
        command_control.deleteMe()

    # Delete the command definition
    if command_definition:
        command_definition.deleteMe()


# Function that is called when a user clicks the corresponding button in the UI.
# This defines the contents of the command dialog and connects to the command related events.
def command_created(args: adsk.core.CommandCreatedEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Created Event')

    # https://help.autodesk.com/view/fusion360/ENU/?contextId=CommandInputs
    inputs = args.command.commandInputs

    # TODO Define the dialog for your command by adding different inputs to the command.

    # Create a simple text box input.
    #inputs.addTextBoxCommandInput('text_box', 'Some Text', 'Hola como estas', 1, False)

    # Create a value input field and set the default using 1 unit of the default length unit.
    #defaultLengthUnits = app.activeProduct.unitsManager.defaultLengthUnits
    
    #default_value = adsk.core.ValueInput.createByString('100')
    
    #inputs.addValueInput('value_input', 'Some Value', defaultLengthUnits, default_value)
    
    # Aqui creo os sliders para poder usar en la interfaz
    # lembrando que 1 = 57.3 entonces usando regla de 3 puede hacerse la correlacion
    
    # Slider para el dedo indice
    # ref 1cm da 57.3 graus
    ref = 57.3
    
    #valor de referencia dedo indice distal - proximal = 82'
    ang_base_dp = 82
    ang_dp = ang_base_dp  / ref
    
    # Slider para el dedo indice
    inputs.addFloatSliderCommandInput('ang_dedoindice','Angulo dedo Indice', 'deg', 0, ang_dp, False)
    
    # Slider para los Otros delos menos el dedo gordo
    inputs.addFloatSliderCommandInput('ang_otros','Angulo otros dedos', 'deg', 0, ang_dp, False)
    
    
    # Slider para el dedo gordo
    # inputs.addFloatSliderCommandInput('float_slider_ang','Angulo dedo gordo', 'deg',0, 1.431065, False)
    
    
    
    
    
    #inputs.addIntegerSliderCommandInput('float_slider_tam', 'Tamaño horizontal', 10, 100, False)
    
    #vamos a mostrar la informacion de las variables que creamos
    #inputs.addTextBoxCommandInput('text_box', 'Parametro Anterior angulo', ang.expression, 1, True)
    #inputs.addTextBoxCommandInput('text_box2', 'Parametro Anterior tamaño', tamano.expression, 1, True)
    


    # TODO Connect to the events that are needed by this command.
    futil.add_handler(args.command.execute, command_execute, local_handlers=local_handlers)
    futil.add_handler(args.command.inputChanged, command_input_changed, local_handlers=local_handlers)
    futil.add_handler(args.command.executePreview, command_preview, local_handlers=local_handlers)
    futil.add_handler(args.command.validateInputs, command_validate_input, local_handlers=local_handlers)
    futil.add_handler(args.command.destroy, command_destroy, local_handlers=local_handlers)


# This event handler is called when the user clicks the OK button in the command dialog or 
# is immediately called after the created event not command inputs were created for the dialog.
def command_execute(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Execute Event')

    # TODO ******************************** Your code here ********************************

    # Get a reference to your command's inputs.
    inputs = args.command.commandInputs
 
    
    
    # aqui actualizamos el valor de parametro cuando usamos el slider
    #novoAngulo: adsk.core.FloatSliderCommandInput = inputs.itemById('ang_dedoindice')
    #novoTamano: adsk.core.IntegerSliderCommandInput = inputs.itemById('float_slider_tam')
    
    #userParams.itemByName('ang').expression = novoAngulo.expressionOne
    #userParams.itemByName('tamano').expression = novoTamano.expressionOne
    
    
    
    
    


# This event handler is called when the command needs to compute a new preview in the graphics window.
def command_preview(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Preview Event')
    inputs = args.command.commandInputs
    
    # aqui actualizamos el valor de parametro cuando usamos el slider
    
    # lee el valor del slider del Indice
    novoAngDI: adsk.core.FloatSliderCommandInput = inputs.itemById('ang_dedoindice')
    
    # lee el valor del slider del Indice
    novoAngOt: adsk.core.FloatSliderCommandInput = inputs.itemById('ang_otros')
    
    
    # pasa el nuevo valor a la variable para actualizar la posicion del dedo indice
    userParams.itemByName('ang_indice').expression = novoAngDI.expressionOne
    userParams.itemByName('ang_indice_pm').expression = str_float_computo(novoAngDI.expressionOne, -90.0)
    
    # pasa el nuevo valor a la variable para actualizar la posicion de los otros dedos
    userParams.itemByName('ang_otros').expression = novoAngOt.expressionOne
    userParams.itemByName('ang_otros_pm').expression = str_float_computo(novoAngOt.expressionOne, 0.0)

    
    


# This event handler is called when the user changes anything in the command dialog
# allowing you to modify values of other inputs based on that change.
def command_input_changed(args: adsk.core.InputChangedEventArgs):
    changed_input = args.input
    inputs = args.inputs

    # General logging for debug.
    futil.log(f'{CMD_NAME} Input Changed Event fired from a change to {changed_input.id}')


# This event handler is called when the user interacts with any of the inputs in the dialog
# which allows you to verify that all of the inputs are valid and enables the OK button.
def command_validate_input(args: adsk.core.ValidateInputsEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Validate Input Event')

    inputs = args.inputs
    
    # Verify the validity of the input values. This controls if the OK button is enabled or not.
    valueInput = inputs.itemById('value_input')
    if valueInput.value >= 0:
        args.areInputsValid = True
    else:
        args.areInputsValid = False
        

# This event handler is called when the command terminates.
def command_destroy(args: adsk.core.CommandEventArgs):
    # General logging for debug.
    futil.log(f'{CMD_NAME} Command Destroy Event')

    global local_handlers
    local_handlers = []


def str_float_computo(str_in, ang_base):
    # 48.2 deg
    angDI = str_in.replace(" deg", "")
    valor = ang_base + float(angDI)
    str_valor = str(valor) + " deg"
    futil.log(str_valor)
    return str_valor