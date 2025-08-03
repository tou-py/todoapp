# Implementación básica de una ToDo App utilizando FastAPI en formato restful API

## Breve descripción

Una fácil y rápida forma de crear una app que maneja operaciones CRUD de tareas de un usuario que utiliza una base de datos SQLite

La app tiene una implementación genérica del patrón `Repository` para facilitar el acceso a la capa de datos y mejorar 
la legibilidad del código.
Aúnque el uso de esta capa no es obligatoria me facilitó enormemente su construcción, ya que tiene su principal 
funcionalidad en las operaciones CRUD.

La documentación generada automáticamente por FastAPI se encuentra en `/docs`

## Funcionamiento

Es simple, las rutas manejan peticiones GET, POST, PUT, PATCH y DELETE,
 además del listado adicional tanto en `/users` como en `/tasks`.

## ¿Cómo usarlo?
Descarga el repo con `git clone` y tienes las siguientes opciones
### De forma local
```
pip install -r requirements.txt 
```
```
uvicorn main:app --reload
```
### Con Docker
Crea y levanta la imagen con:

```
docker build -t web .
docker run -p 127.0.0.1:8000:8000 web
```

O también con docker compose
```
docker compose up --build
```
La aplicación deberá ejecutarse en http://localhost/8000/

## ¿Quién puede usar este repo?
Cualquiera que lo desee. 
Estoy abierto a sugerencias y consejos :)