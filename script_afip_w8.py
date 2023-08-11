from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
import json

# Configura el navegador utilizando las opciones y el controlador

#Scrap
chrome_options = webdriver.ChromeOptions()
#chrome_options.binary_location = '/usr/bin/chromium-browser'  # Ruta al binario de Chrome
driver = webdriver.Chrome()
driver.quit()


print('================= Facturación Nicfer ==================\n')


PASSWORD = input(' * Ingresá la contraseña de AFIP: ')
RUTA = '/home/fmancilla/Remitos/'


while True:

    while True:
        try:
            remito_in = input(" * Ingresá el remito, sin incluir el punto de venta por ejemplo 00012400: ")
            if len(remito_in) != 8 or not remito_in.isdigit():
                raise ValueError("El número debe tener exactamente 8 dígitos y ser un número válido.")
            break  # Salir del bucle si la entrada es válida
        except ValueError as error:
            print("Error:", error)

    remito_file = '0001-' + remito_in + '.json'

    
    RUTA_JSON = RUTA + remito_file

    try:
        with open(RUTA_JSON, "r") as archivo_json:
            data = json.load(archivo_json)
    except FileNotFoundError:
        raise FileNotFoundError("El archivo no se encontró. Es posible que se haya remitido de manera errónea.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Error al decodificar el archivo")

    mats, head = data.values()

    CUIT = head['cuit'].replace('-','')
    REMITO = remito_in
    OC_DIRTY = head['OC']
    usaDolar = head['dolar']
    usaDir = head['dirVariable']
    LOCAL = head['local']

    

    if usaDolar:
        driver.get("https://www.bna.com.ar/Personas")
        DOLAR = driver.find_element(By.XPATH, '//*[@id="billetes"]/table/tbody/tr[1]/td[3]').text
        DOLAR = DOLAR.replace(',','.')
    

    #//*[@id="monedaextranjera"] //Check

    OCs = [valor.strip() for valor in OC_DIRTY.split('/')]

    driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml?action=SYSTEM&system=rcel")


    driver.maximize_window()
    width, height = driver.execute_script("return [window.screen.availWidth, window.screen.availHeight];")
    driver.set_window_position(0, 0)
    driver.set_window_size(800, height)

    driver.find_element(By.ID,'F1:username').send_keys('27223443414')
    driver.find_element(By.ID,'F1:btnSiguiente').click()
    driver.find_element(By.ID,'F1:password').send_keys(PASSWORD)
    driver.find_element(By.ID,'F1:btnIngresar').click()
    element = driver.find_element(By.XPATH, "//input[@class='btn_empresa ui-button ui-widget ui-state-default ui-corner-all']")
    element.click()
    driver.find_element(By.XPATH, '//*[@id="btn_gen_cmp"]/span[2]').click()
    select_element = driver.find_element(By.ID,"puntodeventa")
    opcion = select_element.find_element(By.XPATH, '//*[@id="puntodeventa"]/option[2]')
    opcion.click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click()
    driver.find_element(By.XPATH, '//*[@id="idconcepto"]/option[2]').click()

    if usaDolar:
        driver.find_element(By.XPATH, '//*[@id="monedaextranjera"]').click()
        driver.find_element(By.XPATH, '//*[@id="tipocambio"]').send_keys(DOLAR)

    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click()
    driver.find_element(By.XPATH, '//*[@id="idivareceptor"]/option[2]').click()
    driver.find_element(By.XPATH, '//*[@id="nrodocreceptor"]').send_keys(CUIT)


    #//*[@id="domicilioreceptor"]/option[3]
    driver.find_element(By.XPATH, '//*[@id="formulario"]/div/div/table[2]/tbody/tr[5]/th/label').click()
    time.sleep(1)

    opcion = 1

    if usaDir:
        print("\nEl proveedor tiene más de una dirección de facturación posible. Elegí alguna de las opciones:\n")
        print(f"El remito tiene localidad: {LOCAL} \n")
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
    driver.find_element(By.XPATH, '//*[@id="tablacmpasoc"]/tbody/tr[2]/td[2]/input').send_keys(REMITO)
    driver.find_element(By.XPATH, '//*[@id="formulario"]/input[2]').click()


    for i in range(len(mats) - 1):
        desc_precio = f"detalle_precio{i + 1}"
        driver.find_element(By.XPATH, '//*[@id="detalles_datos"]/input').click()

    precios = driver.find_elements(By.NAME, 'detallePrecio')
    descripciones = driver.find_elements(By.NAME, 'detalleDescripcion')
    cantidades = driver.find_elements(By.NAME, 'detalleCantidad')
    medidas = driver.find_elements(By.CSS_SELECTOR, "option[value='7'][style='padding-left:10px;']")
    ocs = driver.find_elements(By.NAME, 'impuestoDetalle')

    elementos_select = driver.find_elements(By.CSS_SELECTOR, "select[name='detalleTipoIVA']")

    ivas = []

    for elemento_select in elementos_select:
        ivita = elemento_select.find_element(By.CSS_SELECTOR, "option[value='4']")
        ivas.append(ivita)

    for index, elem in enumerate(OCs):
        orden = 'OC: ' + elem
        ocs[len(ocs) - 1 - index].send_keys(orden)
    
    for index, elem in enumerate(mats):
        precios[index].send_keys(elem['precio'])
        descripciones[index].send_keys(elem['desc'])
        cantidades[index].clear()
        cantidades[index].send_keys(elem['cantidad'])
        medidas[index].click()
        if elem['iva'] == '10.5':
            ivas[index].click()

    print('\n')
    entrada = input(" * Enter para emitir una nueva factura. No te olvides de confirmar e imprimir la anterior ")
    print('\n')
    driver.quit()
