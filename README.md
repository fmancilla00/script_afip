# Script Facturación AFIP
Generación de facturas mediante web scrapping.

Se necesita un archivo JSON del que recibir los items a facturar y una ruta en la que se encuentre. Se espera que el nombre del archivo JSON tenga el formato 0001-________. 

Necesita Python y Selenium. Además de Chrome y WebDriver. 

Version para Linux (recomendada) en la que se usa un chromium-browser y su respectivo webdriver

Para su uso se pretende que dentro del código se añada la ruta a la carpeta donde se almacenan los remitos (RUTA) y en cuit_usr cargar el cuit del receptor. Una vez seteado eso se podrá usar.

El archivo JSON a recibir es de la forma:
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
      "desc": "item 3",
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
Se pueden generar archivos de este tipo con este proyecto: [Sistema Remitos](https://github.com/fmancilla00/Sistema-Remitos)

Dentro de Head se encuentra local que es la localidad en la que se encuentra el receptor, dolar indica si se remitió utilizando moneda dolar y dirVariable indica si el receptor tiene más de una dirección de facturación. 

