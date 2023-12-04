import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def login(driver, username, password):
    while True:
        driver.find_element(By.ID, 'F1:username').send_keys(username)
        driver.find_element(By.ID, 'F1:btnSiguiente').click()
        driver.find_element(By.ID, 'F1:password').send_keys(password)
        driver.find_element(By.ID, 'F1:btnIngresar').click()
        errors = driver.find_elements(By.XPATH, '//*[@id="F1:msg"]')
        if len(errors) == 0:
            break
        password = input("Contraseña incorrecta. Ingresala de nuevo: ")
    return password

def abrirArchivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as archivo_json:
            return json.load(archivo_json)
    except FileNotFoundError:
        raise FileNotFoundError("El archivo no se encontró. Es posible que se haya remitido de manera errónea.")
    except json.JSONDecodeError:
        raise json.JSONDecodeError("Error al decodificar el archivo")
    
def ingresarRemito():
    while True:
        try:
            remito_in = input(" * Ingresá el remito, sin incluir el punto de venta por ejemplo 00012400: ")
            if not remito_in.isdigit():
                raise ValueError("Intenta nuevamente. No ingresaste un número válido.")
            remito_in = remito_in.zfill(8)
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

def seleccionarTipoComprobante(driver, fce):
    select_element = driver.find_element(By.ID,"puntodeventa")
    opcion = select_element.find_element(By.XPATH, '//*[@id="puntodeventa"]/option[2]')
    opcion.click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//option[@value="10" and text()="Factura A"]')))
    #espero hasta que procese la opcion
    if fce:
        driver.find_element(By.XPATH, '//*[@id="universocomprobante"]/option[12]').click()
    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click()  # Continue
    
def set_datos_emision(driver,dolar, usaDolar):
    driver.find_element(By.XPATH, '//*[@id="idconcepto"]/option[2]').click()    # Selección productos
    if usaDolar:
        driver.find_element(By.XPATH, '//*[@id="monedaextranjera"]').click()
        driver.find_element(By.XPATH, '//*[@id="tipocambio"]').send_keys(dolar)
    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click() # Continuar

def set_datos_emision_fce(driver,dolar, usaDolar, cbu, alias):
    driver.find_element(By.XPATH, '//*[@id="idconcepto"]/option[2]').click()           # Selección productos
    driver.find_element(By.XPATH, '//*[@id="cbuEmisor"]').send_keys(cbu)               # Cbu
    driver.find_element(By.XPATH, '//*[@id="aliasCbuEmisor"]').send_keys(alias)        # Alias
    driver.find_element(By.XPATH, '//*[@id="opcionTransferencia"]/option[3]').click()  # Opcion transf. 
    
    if usaDolar:
        driver.find_element(By.XPATH, '//*[@id="monedaextranjera"]').click()
        driver.find_element(By.XPATH, '//*[@id="tipocambio"]').send_keys(dolar)

    # Obtención fecha
    fecha_actual = datetime.now()
    days = input("Ingresá a cuantos días será la condición de pago \n")
    fecha_futura = fecha_actual + timedelta(days=int(days))
    fecha_futura = fecha_futura.strftime("%d/%m/%Y")
    print(fecha_futura)
    driver.find_element(By.XPATH, '//*[@id="vencimientopago"]').clear()
    driver.find_element(By.XPATH, '//*[@id="vencimientopago"]').send_keys(fecha_futura)

    driver.find_element(By.XPATH, '//*[@id="contenido"]/form/input[2]').click() # Continuar



def set_datos_receptor_fce(driver, cuit, remito, local, usaDir, fecha_r):
    driver.find_element(By.XPATH, '//*[@id="idivareceptor"]/option[2]').click()
    driver.find_element(By.XPATH, '//*[@id="nrodocreceptor"]').send_keys(cuit)

     # Fecha remito
    fecha_original = datetime.strptime(fecha_r, "%Y-%m-%d")
    fecha_formateada = fecha_original.strftime("%d/%m/%Y")
    driver.find_element(By.XPATH, '//*[@id="tablacmpasoc"]/tbody/tr[2]/td[4]/input').send_keys(fecha_formateada)

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



def abrirNavegador(options):
    driver = webdriver.Chrome(options)
    width, height = driver.execute_script("return [window.screen.availWidth, window.screen.availHeight];")
    driver.set_window_size(800, height)
    driver.set_window_position(width - 700, 0)
    return driver

