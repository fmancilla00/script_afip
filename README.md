# Script Facturación AFIP
Generación de facturas mediante web scraping.

Este script permite generar facturas utilizando técnicas de web scraping. El proceso requiere un archivo JSON que contenga los elementos a facturar, así como una ruta específica donde se encuentra dicho archivo. El nombre del archivo JSON debe seguir el formato `0001-________`.

## Requisitos
- Python y Selenium.
- Google Chrome y el correspondiente WebDriver.

## Instalación
1. Instala Python en tu sistema.
2. Instala Selenium ejecutando el siguiente comando:
   ```
   pip install selenium
   ```
3. Descarga el navegador Google Chrome si no lo tienes instalado.
4. Descarga el WebDriver correspondiente a tu versión de Chrome y colócalo en una ubicación accesible.

## Uso
1. Abre el script y establece la ruta a la carpeta donde se almacenan los remitos en la variable `RUTA`.
2. Completa el campo `cuit_usr` con el CUIT del receptor.
3. Ejecuta el script.

## Disclaimer
Tener en cuenta que la forma de abrir una pestaña en el navegador puede variar según el WebDriver que estés utilizando. Es posible que debas ajustar la parte del script que controla la apertura de pestañas para que sea compatible con tu WebDriver específico.

## Archivo JSON
El archivo JSON necesario para el proceso de facturación debe tener la siguiente estructura:

```json
{
  "mats": [
    {
      "id": "74c56958-8244-49fe-9aa9-119c3f97f5aa",
      "cantidad": "20",
      "codigo": "",
      "desc": "Item 1",
      "precio": "20",
      "iva": "21"
    },
    {
      "id": "39c2ca84-e272-4682-8625-04f9093fc6ec",
      "cantidad": "90",
      "codigo": "",
      "desc": "Item 2",
      "precio": "80",
      "iva": "21"
    },
    {
      "id": "f651a1d7-d100-4e14-9518-b2fcf937f638",
      "cantidad": "90",
      "codigo": "",
      "desc": "Item 3",
      "precio": "90",
      "iva": "10.5"
    }
  ],
  "head": {
    "remito": "0001-00001234",
    "OC": "4500123456",
    "local": "BSAS",
    "cliente": "EMPRESA",
    "cuit": "99009900999",
    "dolar": false,
    "dirVariable": true
  }
}
```

Dentro de la sección `head`, encontrarás el campo `local`, que corresponde a la localidad del receptor; `dolar`, que indica si se remitió utilizando moneda dólar; y `dirVariable`, que indica si el receptor tiene más de una dirección de facturación.

Si necesitas generar archivos JSON como el mencionado anteriormente, puedes utilizar el proyecto "Sistema Remitos", disponible en [Sistema Remitos](https://github.com/fmancilla00/Sistema-Remitos).
