from RPA.Robocorp.Vault import Vault, Secret

tag = "Environment : "
# Function to retrieve secrets
def get_azure_connection_string():
    return _getVariable('AZURE_CONNECTION_STRING')
    
def get_user_name():
    return _getVariable(key='USER_NAME')

def get_user_password():
    return _getVariable(key='PASSWORD')

def get_excel_flag():
    return _getVariable(key='USE_EXCEL')

def _getVariable(key):
    vault = Vault()
    secret: Secret = vault.get_secret(key)
    variable = secret.get(key)
    if variable:
        print(f'\n{tag} environment variable OK for key: {key} - {variable}')
        return variable
    
    print(f'\n{tag} environment variable is ka-boom!! - key: {key}')
    
    raise KeyError('Environment variables not found. ' +
                'Please set the variables in the Control Room vault. You need to set AZURE_CONNECTION_STRING, USER_NAME, USE_EXCEL = 1 or 0 in the Vault tab of the Control Room ')

