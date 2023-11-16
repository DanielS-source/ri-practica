
<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Practica RIWS</h3>

  <p align="center">
    Web creada a partir de datos recolectados con scrapy e indexados con ElasticSearch
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Tabla de contenidos</summary>
  <ol>
    <li>
      <a href="#about-the-project">Sobre el proyecto</a>
      <ul>
        <li><a href="#built-with">Hecho con</a></li>
      </ul>
    </li>
    <li><a href="#installation">Instalación</a></li>
  </ol>
</details>

## Sobre el proyecto

Trabajo de RIWS. Página web con críticas de videojuegos extraídas de [metacritic](https://www.metacritic.com/) con Scrapy 

<p align="right">(<a href="#readme-top">Volver al índice</a>)</p>

### Hecho con

* [![Angular][Angular.io]][Angular-url]

* [![FastAPI][FastAPI.com]][FastAPI-url]

- [![ElsaticSearch][Elastic.co]][Elastic-url]

* <a href="https://scrapy.org"><img src="https://scrapy.org/img/scrapylogo.png" alt="drawing" style="width:100px;"/></a>

<p align="right">(<a href="#readme-top">Volver al índice</a>)</p>

## Instalación

### Local
Esta opcion de despliegue ejecuta todos los servicios en local a excepción de ElasticSearch. Opción ideal durante el desarrollo, en caso contrario se recomienda utilizar las alternativas recomendadas mas abajo.

Prerequisitos:
- npm 20 o nvm
- python 3.11
- pip
- Docker
- Docker Compose

Comandos: 
#### Lanzar ElasticSearch
```sh
docker compose -f installation/docker-compose-elastic-only.yml up -d
```

#### Lanzar el backend
```sh
pip install -r requirements.txt
```

Navega a el backend

```sh
cd critic-verse/backend
```

Reemplaza
- ELASTICSEARCH_HOST=http://elastic:riwspractica@host.docker.internal:9200
por:
- ELASTICSEARCH_HOST=http://elastic:riwspractica@localhost:9200

Si se quiere poblar elasticsearch:

```sh
python -u init_elastic.py
```

Para lanzar el servidor:
```sh
python main.py
```
o
```sh
./run_server.sh
```

Vuelve a abrir otro terminar en la raiz del poryecto para los siguientes pasos:

#### Lanzar la web:
```sh
cd critic-verse/frontend/
```
(Opcional) Si se usa nvm para cambiar la version de npm
```sh
nvm use
```
o
```sh
nvm use 20
```

Instalar dependecias con npm
```sh
npm install
```

Lanzar la aplicacion en [localhost](http://localhost:4200)
```sh
ng serve -o
```


### Docker

Despliegue usando los Dockerfile del repositorio. Opción ideal si se quiere garantizar utilizar la versión más reciente del repositorio.

Prerequisitos:
- Docker
- Docker compose

Comandos:
```sh
docker compose up -d
```

### DockerHub

Despliegue usando imágenes de DockerHub, si se usa este metodo no es necesario clonar el repositorio. Con el fichero es suficiente. Opción ideal para realizar la instalación más simple posible usando imágenes estables subidas a DockerHub.

Prerequisitos:
- Docker
- Docker compose

Comandos: 
```sh
docker compose -f installation/docker-compose.yml up -d
```

<p align="right">(<a href="#readme-top">Volver al índice</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[FastAPI.com]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com
[Elastic.co]: https://img.shields.io/badge/-ElasticSearch-005571?style=for-the-badge&logo=elasticsearch
[Elastic-url]: https://www.elastic.co/es/elasticsearch
[Scrapy.org]: https://scrapy.org/img/scrapylogo.png
[Scrapy-url]: https://scrapy.org

