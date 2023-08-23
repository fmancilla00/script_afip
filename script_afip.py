from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from funciones import login, abrirArchivo, ingresarRemito, obtenerDolar, seleccionarTipoComprobante, set_datos_emision, set_datos_op, set_datos_receptor, abrirPagina


if __name__ == '__main__':

    #Scrap
    chrome_options = webdriver.ChromeOptions()
    #chrome_options.binary_location = '/usr/bin/chromium-browser'  # Ruta al binario de Chromium
    
    print('================= Facturación ==================\n')
    
    RUTA = ''        # Completar
    cuit_usr = ''    # Completar

    PASSWORD = input(' * Ingresá la contraseña de AFIP: ')

    while True:

        # Construyo nombre del archivo
        remito_in = ingresarRemito()
        remito_file = '0001-' + remito_in + '.json'
        RUTA_JSON = RUTA + remito_file

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

        if usaDolar:
            DOLAR = obtenerDolar(driver)
        
        driver = abrirPagina("https://auth.afip.gob.ar/contribuyente_/login.xhtml?action=SYSTEM&system=rcel", chrome_options)

        login(driver, cuit_usr, PASSWORD)

        # Selección de empresa
        clickable_empresa = driver.find_element(By.XPATH, "//input[@class='btn_empresa ui-button ui-widget ui-state-default ui-corner-all']")
        clickable_empresa.click()

        # Selección de operación
        clickable_gen = driver.find_element(By.XPATH, '//*[@id="btn_gen_cmp"]/span[2]')
        clickable_gen.click()

        # Tipo comprobante
        seleccionarTipoComprobante(driver)

        # Datos de emisión
        set_datos_emision(driver, DOLAR, usaDolar)
        
        # Datos receptor
        set_datos_receptor(driver, CUIT, REMITO, LOCAL, usaDir)

        # Datos operación
        set_datos_op(driver, mats, OCs)
        

        print('\n')
        entrada = input(" * Enter para emitir una nueva factura. No te olvides de confirmar e imprimir la anterior ")
        print('\n')
        driver.quit()
