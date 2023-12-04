from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from funciones import login, abrirArchivo, ingresarRemito, obtenerDolar, seleccionarTipoComprobante, set_datos_emision, set_datos_op, set_datos_receptor, abrirNavegador, set_datos_emision_fce, set_datos_receptor_fce


if __name__ == '__main__':

    #Scrap
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = '/usr/bin/chromium-browser'  # Ruta al binario de Chromium
    
    config = abrirArchivo('config.json')

    RUTA = config['ruta']
    cuit_usr = config['cuit']
    CBU = config['cbu']
    ALIAS = config['alias']

    print('================= Facturación ==================\n')


    PASSWORD = input(' * Ingresá la contraseña de AFIP: ')

    while True:
        # Construyo nombre del archivo
        remito_in = ingresarRemito()
        remito_file = '0001-' + remito_in + '.json'
        RUTA_JSON = RUTA + remito_file

        # Input FCE
        fce = input("Ingresá el tipo de comprobante: \n 1. Factura A\n 2. FCE A\n")
        fce = True if (int(fce) == 2) else False

        # Leo datos
        data = abrirArchivo(RUTA_JSON)
        mats, head = data.values()

        # Obtengo valores variables
        CUIT = head['cuit'].replace('-','')
        REMITO = remito_in
        OC_DIRTY = head['OC']
        OCs = [valor.strip() for valor in OC_DIRTY.split('/')]
        usaDolar = head['dolar']
        usaDir = head['dirVariable']
        LOCAL = head['local']
        DOLAR = 0
        FECHA = head['fecha']

        driver = abrirNavegador(chrome_options)
        
        if usaDolar:
            DOLAR = obtenerDolar(driver)

        driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml?action=SYSTEM&system=rcel")

        PASSWORD = login(driver, cuit_usr, PASSWORD)

        # Selección de empresa
        clickable_empresa = driver.find_element(By.XPATH, "//input[@class='btn_empresa ui-button ui-widget ui-state-default ui-corner-all']")
        clickable_empresa.click()

        # Selección de operación
        clickable_gen = driver.find_element(By.XPATH, '//*[@id="btn_gen_cmp"]/span[2]')
        clickable_gen.click()

        # Tipo comprobante
        if not fce:
            seleccionarTipoComprobante(driver, False)

            # Datos de emisión
            set_datos_emision(driver, DOLAR, usaDolar)

            # Datos receptor
            set_datos_receptor(driver, CUIT, REMITO, LOCAL, usaDir)

            # Datos operación
            set_datos_op(driver, mats, OCs)
        else:
            seleccionarTipoComprobante(driver, True)

            # Datos de emisión
            set_datos_emision_fce(driver, DOLAR, usaDolar, CBU, ALIAS)

            set_datos_receptor_fce(driver, CUIT, REMITO, LOCAL, usaDir, FECHA)

            set_datos_op(driver, mats, OCs)

        print('\n')
        entrada = input(" * Enter para emitir una nueva factura. No te olvides de confirmar e imprimir la anterior ")
        print('\n')
        driver.quit()
