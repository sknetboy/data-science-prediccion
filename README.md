# ChurnInsight — Predicción de Cancelación de Clientes (MVP)

## Descripción
ChurnInsight es un proyecto listo para ejecutar que entrena un modelo de churn y expone predicciones a través de un microservicio Python y un backend principal en Java Spring Boot.

## Guía rápida para principiantes (paso a paso)
- Objetivo: entrenar el modelo, levantar el servicio de predicción y el backend.
- Requisitos mínimos:
<<<<<<< HEAD
  - Python 3.11 o superior (Recomendado: 3.13).
  - Navegador y conexión a internet.
  - Para el backend: Java 21 y Maven 3.9.12 (opcional si sólo quieres probar el microservicio).
=======
  - Python 3.13 o superior.
  - Navegador y conexión a internet.
  - Para el backend: Java 21 y Maven (opcional si sólo quieres probar el microservicio).
>>>>>>> b21d8

### 1) Entrenar el modelo (Data Science)
- Abre una terminal (PowerShell en Windows) y ejecuta:
```
python data-science/train_model.py
```
- Esto crea el archivo `data-science/model.joblib` y muestra métricas (Accuracy, Precision, Recall y F1).

### 2) Levantar el microservicio de predicción (Python)
- Instala dependencias:
```
pip install -r prediction-service/requirements.txt
```
- Arranca el servicio (Opción A, más sencilla):
```
cd prediction-service
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
- Si prefieres no cambiar de carpeta (Opción B):
```
$env:PYTHONPATH="$PWD\prediction-service"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
- Prueba el endpoint desde otra terminal:
```
Invoke-RestMethod -Uri http://127.0.0.1:8001/predict -Method Post -ContentType application/json -Body '{"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}'
```
- Debe responder con algo como:
```
{
  "prevision": "Va a cancelar",
  "probabilidad": 0.81
}
```

### 3) Levantar el backend principal (Java + Spring Boot)
<<<<<<< HEAD
- Requisitos: Java 21 y Maven 3.9.12 instalados.
=======
- Requisitos: Java 21 y Maven instalados.
>>>>>>> b21d8
- En una terminal:
```
mvn -f backend/pom.xml spring-boot:run
```
- El backend escucha en `http://localhost:8080` y llama al microservicio en `http://localhost:8001`.
- Probar el backend:
```
Invoke-RestMethod -Uri http://localhost:8080/predict -Method Post -ContentType application/json -Body '{"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}'
```

### 4) Alternativa con Docker (opcional)
- Si tienes Docker Desktop:
```
docker compose up --build
```
- Backend: `http://localhost:8080`  |  Microservicio: `http://localhost:8001`
- **Nota:** Las imágenes de Docker utilizan **Java 21 (Eclipse Temurin)** y **Python 3.13**.

### Problemas comunes y soluciones
- "uvicorn no se reconoce": instala dependencias con `pip install -r prediction-service/requirements.txt` o usa `python -m uvicorn ...`.
- Error de importación en `app.main`: usa la Opción A (entrar a la carpeta `prediction-service`) o la Opción B con `PYTHONPATH`.
- Maven no se reconoce: instala Maven 3.9.12 y Java 21, o usa el wrapper `./mvnw` en la carpeta `backend`, o Docker Compose.

## Arquitectura
- Cliente → `backend` (Java) → `prediction-service` (Python FastAPI) → `model.joblib`
- Capas desacopladas: Data Science, Microservicio de Predicción, Back-end Principal.

## Módulo Data Science
- Ubicación: `data-science/`
- Dependencias: `pandas`, `numpy`, `scikit-learn`, `joblib`
- Archivos:
  - `data-science/data/churn.csv`
  - `data-science/train_model.py`
  - `data-science/train_model.ipynb`
  - `data-science/model.joblib` (se genera al entrenar)

### Entrenamiento del modelo
- Ejecutar:
  - `python data-science/train_model.py`
- El script asegura la existencia del dataset sintético, realiza EDA básico en consola, entrena un `LogisticRegression` con `ColumnTransformer` y guarda `model.joblib`.

## Microservicio de Predicción (FastAPI)
- Ubicación: `prediction-service/`
- Dependencias en `requirements.txt` (compatible con Python 3.13).
- Arranque local:
  - `pip install -r prediction-service/requirements.txt`
  - Opción A: `cd prediction-service && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
  - Opción B: `$env:PYTHONPATH="$PWD\prediction-service"; python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
- Endpoints:
  - `POST /predict`
    - Request:
      ```json
      {"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}
      ```
    - Response:
      ```json
      {"prevision":"Va a cancelar","probabilidad":0.81}
      ```
  - `GET /stats`

El servicio carga `model.joblib` al inicio y, si no existe, entrena automáticamente un modelo sintético mínimo.

## Back-end Principal (Java + Spring Boot)
- Ubicación: `backend/`
- **Java 21**, Spring Boot WebFlux.
- **Maven 3.9.12** (enforced).
- Arranque local:
  - `mvn -f backend/pom.xml spring-boot:run`
- Endpoint:
  - `POST /predict` delega al microservicio Python.
- Configuración:
  - `backend/src/main/resources/application.yml` establece `prediction.service.base-url`.

## Contrato de Integración
- Request:
  ```json
  {"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}
  ```
- Response:
  ```json
  {"prevision":"Va a cancelar","probabilidad":0.81}
  ```

## Docker Compose
- Levantar todo el stack:
  - `docker compose up --build`
- Servicios:
  - `prediction-service` en `http://localhost:8001` (Python 3.13)
  - `backend` en `http://localhost:8080` (Java 21)

### Healthchecks en Compose
- Los servicios incluyen `healthcheck`:
  - `prediction-service`: consulta `GET /stats`.
  - `backend`: consulta `GET /actuator/health`.
- `backend` espera a que `prediction-service` esté `healthy` antes de iniciar.

## Ejemplos cURL
- Predicción vía backend:
  - `curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}'`
- Predicción directa al microservicio:
  - `curl -X POST http://localhost:8001/predict -H "Content-Type: application/json" -d '{"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}'`

## Variables de entorno
- `prediction.service.base-url` en backend.
- `PREDICTION_SERVICE_URL` en Docker Compose para el backend.

## Pruebas y verificación
- Microservicio: se puede probar con cURL o Postman.
- Backend: se puede probar con cURL o Postman.

## Plantilla de Repositorio GitHub
- Este proyecto es apto para ser marcado como plantilla en GitHub. Pasos:
  - Crear un repositorio en GitHub y subir el contenido.
  - En la pestaña Settings → General, activar "Template repository".
  - Opcional: añadir `Topics` como `churn`, `ml`, `fastapi`, `spring-boot`.
- Incluye `.gitignore` para Python y Java.

## Prompts por Módulo
- Data Science:
  - "Genera un dataset sintético de churn y entrena un modelo binario con `RandomForestClassifier` usando `ColumnTransformer` y `StandardScaler`. Exporta a `model.joblib` y reporta Accuracy, Precision, Recall y F1."
- Microservicio de Predicción (FastAPI):
  - "Crea un servicio FastAPI que cargue `model.joblib` al iniciar y exponga `POST /predict` con validación de tipos y respuesta `{prevision, probabilidad}`; añade `GET /stats`."
- Backend Principal (Spring Boot):
  - "Implementa un endpoint `POST /predict` que valide entrada, delegue al microservicio Python con `WebClient`, y maneje errores: 400 por validación y 502 si falla el microservicio."
- Infraestructura (Docker Compose):
  - "Orquesta `prediction-service` y `backend` con Docker Compose; parametriza la URL del microservicio vía `PREDICTION_SERVICE_URL`."

## Despliegue en OCI Free Tier + Docker Compose
- Requisitos:
  - Instancia Compute (Always Free) con Ubuntu/Debian.
  - Docker y Docker Compose instalados.
- Pasos:
  - Clonar el repositorio en la instancia.
  - Ejecutar: `docker compose -f docker-compose.oci.yml up --build -d`
  - Abrir puertos en el "Network Security Group" o "Security List": TCP `8080`, `8001`.
  - Verificar:
    - `curl -X POST http://<PUBLIC_IP>:8080/predict -H "Content-Type: application/json" -d '{"tiempo_contrato_meses":12,"retrasos_pago":2,"uso_mensual":14.5,"plan":"Premium"}'`
- Notas:
  - `restart: unless-stopped` mantiene los servicios tras reinicios.
  - Puedes cambiar imágenes `churninsight/*:latest` por tags propios en un registry.

## CI (GitHub Actions)
- Flujo en `.github/workflows/ci.yml`:
  - Construye `backend` con Maven.
  - Instala dependencias Python y ejecuta `data-science/train_model.py`.
  - Construye imágenes Docker y realiza una prueba de integración lanzando ambos servicios en una red Docker y llamando `POST /predict`.
#### Cargar automáticamente el modelo entrenado
- Si ya entrenaste con `data-science/train_model.py`, el microservicio cargará el modelo sin pasos manuales:
  - Local: busca `prediction-service/model.joblib` y, si no existe, usa `data-science/model.joblib`.
  - Docker Compose: monta `data-science/model.joblib` dentro del contenedor y se usa `MODEL_PATH=/app/model.joblib`.
