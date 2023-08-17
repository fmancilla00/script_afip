from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


def login(driver, username, password):
    driver.find_element(By.ID, 'F1:username').send_keys(username)
    driver.find_element(By.ID, 'F1:btnSiguiente').click()
    driver.find_element(By.ID, 'F1:password').send_keys(password)
    driver.find_element(By.ID, 'F1:btnIngresar').click()

def abrirArchivo(ruta):
    try:
        with open(ruta, "r") as archivo_json:
            return json.load(archivo_json)
    except FileNotFoundError:
        raise FileNotFoundError("El archivo no se encontró. Es posible que se haya remitido de manera errónea.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Error al decodificar el archivo")
    
def ingresarRemito():
    while True:
        try:
            remito_in = input(" * Ingresá el remito, sin incluir el punto de venta por ejemplo 00012400: ")
            if len(remito_in) != 8 or not remito_in.isdigit():
                raise ValueError("El número debe tener exactamente 8 dígitos y ser un número válido.")
            return remito_in
        except ValueError as error:
            print("Error:", error)

def obtenerDolar(driver):
    try:
        driver.get("https://www.bna.com.ar/Personas")
        DOLAR = driver.find_element(By.XPATH, '//*[@id="billetes"]/table/tbody/tr[1]/td[3]').text
        DOLAR = DOLAR.replace(',', '.')
        return DOLAR
    except Exception as e:
        print("Ha ocurrido un error al obtener el valor del dólar:")
        valor_ingresado = input("Ingresa el valor del dólar manualmente: ")
        return valor_ingresado

def seleccionarTipoComprobante(driver):
    select_element = driver.find_element(By.ID,"puntodeventa")
    opcion = select_element.find_element(By.XPATH, '//*[@id="puntodeventa"]/option[2]')
    opcion.click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//option[@value="10" and text()="Factura A"]'))) #espero hasta que procese la opcion
    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click()  # Continue
    
def set_datos_emision(driver):
    driver.find_element(By.XPATH, '//*[@id="idconcepto"]/option[2]').click()    # Selección productos
    if usaDolar:
        driver.find_element(By.XPATH, '//*[@id="monedaextranjera"]').click()
        driver.find_element(By.XPATH, '//*[@id="tipocambio"]').send_keys(DOLAR)
    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click() # Continuar

def set_datos_receptor(driver, cuit, remito, local, usaDir):
    driver.find_element(By.XPATH, '//*[@id="idivareceptor"]/option[2]').click()
    driver.find_element(By.XPATH, '//*[@id="nrodocreceptor"]').send_keys(cuit)

    driver.find_element(By.XPATH, '//*[@id="formulario"]/div/div/table[2]/tbody/tr[5]/th/label').click()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="domicilioreceptor"]/option[1]'))) #Espero a que carguen las dir

    opcion = 1

    if usaDir:
        print("\nEl proveedor tiene más de una dirección de facturación posible. Elegí alguna de las opciones:\n")
        print(f"El remito tiene localidad: {local} \n")
        sel = driver.find_element(By.XPATH, '//*[@id="domicilioreceptor"]')
        opciones = sel.find_elements(By.TAG_NAME, 'option')
        for index, opcion in enumerate(opciones):
            print(f' - {index + 1}: {opcion.text}')
        
        while True:
            opcion = input('\nIngresa numero del item: ').strip()
            if (not(opcion.isdigit()) or int(opcion) > len(opciones) or int(opcion) < 1):
                print("Valor invalido, intenta nuevamente")
            else:
                break
    

    # Direccion:
    path = f'//*[@id="domicilioreceptor"]/option[{opcion}]'
    driver.find_element(By.XPATH, path).click()

    driver.find_element(By.XPATH, '//*[@id="tablacmpasoc"]/tbody/tr[2]/td[1]/input').send_keys('00001')
    driver.find_element(By.XPATH, '//*[@id="tablacmpasoc"]/tbody/tr[2]/td[2]/input').send_keys(remito)
    driver.find_element(By.XPATH, '//*[@id="formulario"]/input[2]').click()

def set_datos_op(driver, mats, ordenes):

    # Agrego items necesarios
    for i in range(len(mats) - 1):
        driver.find_element(By.XPATH, '//*[@id="detalles_datos"]/input').click()

    # Obtengo referencias necesarias
    precios = driver.find_elements(By.NAME, 'detallePrecio')
    descripciones = driver.find_elements(By.NAME, 'detalleDescripcion')
    cantidades = driver.find_elements(By.NAME, 'detalleCantidad')
    medidas = driver.find_elements(By.CSS_SELECTOR, "option[value='7'][style='padding-left:10px;']")
    ocs = driver.find_elements(By.NAME, 'impuestoDetalle')
    # Referencias al IVA
    elementos_select = driver.find_elements(By.CSS_SELECTOR, "select[name='detalleTipoIVA']")
    ivas = []
    for elemento_select in elementos_select:
        ivita = elemento_select.find_element(By.CSS_SELECTOR, "option[value='4']")
        ivas.append(ivita)

    # Seteo Ordenes de Compra
    for index, elem in enumerate(ordenes):
        orden = 'OC: ' + elem
        ocs[len(ocs) - 1 - index].send_keys(orden)
    
    # Seteo info para cada material
    for index, elem in enumerate(mats):
        precios[index].send_keys(elem['precio'])
        descripciones[index].send_keys(elem['desc'])
        cantidades[index].clear()
        cantidades[index].send_keys(elem['cantidad'])
        medidas[index].click()
        if elem['iva'] == '10.5':
            ivas[index].click()

def abrirPagina(url):
    driver = webdriver.Chrome(options=chrome_options)
    width, height = driver.execute_script("return [window.screen.availWidth, window.screen.availHeight];")
    driver.set_window_size(800, height)
    driver.set_window_position(width - 700, 0)
    driver.get(url)
    return driver


if __name__ == '__main__':

    #Scrap
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = '/usr/bin/chromium-browser'  # Ruta al binario de Chrome
    
    PASSWORD = input(' * Ingresá la contraseña de AFIP: ')
    RUTA = '/home/fmancilla/Remitos/'
    cuit_usr = '27223443414'

    print('================= Facturación Nicfer ==================\n')

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

        if usaDolar:
            DOLAR = obtenerDolar(driver)
        
        driver = abrirPagina("https://auth.afip.gob.ar/contribuyente_/login.xhtml?action=SYSTEM&system=rcel")

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
        set_datos_emision(driver)
        
        # Datos receptor
        set_datos_receptor(driver, CUIT, REMITO, LOCAL, usaDir)

        # Datos operación
        set_datos_op(driver, mats, OCs)
        

        print('\n')
        entrada = input(" * Enter para emitir una nueva factura. No te olvides de confirmar e imprimir la anterior ")
        print('\n')
        driver.quit()
