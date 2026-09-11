# Análisis de partidas de lol (50 últimas partidas)

Este es un pipeline ETL (Extracción, Transformación y Carga) automatizado que consume la API oficial de Riot Games, procesa el historial de partidas y almacena las estadísticas en una base de datos para su análisis estructurado

## Tecnologías usadas:
* **Lenguaje:** Python 3.x
* **Extracción:** API REST (Riot Games API), `requests`
* **Transformación:** `pandas`
* **Carga (Base de Datos):** SQL Server 2022, `pyodbc`, `SQLAlchemy`
* **Visualización:** `matplotlib`, `seaborn`
* **Seguridad:** `python-dotenv` (Gestión de credenciales)

## Arquitectura
1. **Extracción:** Conexión a la API de Riot Games para obtener el PUUID del jugador y el listado de las últimas 50 partidas
2. **Transformación :** Limpieza y estructuración de los datos JSON complejos utilizando diccionarios y Pandas DataFrames para aislar métricas clave como kills, daño, oro, winrate).
3. **Carga:** Inserción automatizada de los datos limpios en una instancia local de SQL Server utilizando el driver ODBC 17
4. **Visualización:** Generación de un dashboard en Python para analizar correlaciones entre rendimiento (Daño/Kills) y la tasa de victorias

## Uso e instalación

### 1. Clonar el repositorio
```bash
git clone [https://github.com/Rosesitokya/lol-meta-analysis.git](https://github.com/Rosesitokya/lol-meta-analysis.git)
cd lol-meta-analysis

### 2. Configurar el entorno virtual y las dependencias
python -m venv env
.\env\Scripts\activate
pip install requests pandas matplotlib seaborn python-dotenv sqlalchemy pyodbc

###3. Configurar API
Para la API necesitamos iniciar sesión en esta página web oficial de Riot Games:
https://developer.riotgames.com/
Una vez dentro generas tu API que solo estará disponible por 24 horas y reemplazas el env por tu propia API.

##4. SQL
Como es un análisis de partidas transportamos los datos para que en SQL puedas realizarle las preguntas correspondientes.
Así creamos la tabla en SQL para hacer las consultas:
CREATE TABLE MisPartidasLoL (
    ID_Partida INT IDENTITY(1,1) PRIMARY KEY,
    Campeon VARCHAR(50),
    Resultado VARCHAR(20),
    Kills INT,
    Deaths INT,
    Assists INT,
    Danio_Total INT,
    Oro_Ganado INT,
    Fecha_Registro DATETIME DEFAULT GETDATE()
);

Aquí dejaré algunas consultas que puedes hacer para iniciar:
1. Rendimiento entre victorias y derrotas:
SELECT 
    Resultado,
    COUNT(*) AS Total_Partidas,
    AVG(Kills) AS Promedio_Kills,
    AVG(Danio_Total) AS Promedio_Danio
FROM dbo.MisPartidasLoL
GROUP BY Resultado;
2.Cálculo de KDA:
SELECT 
    Campeon,
    Resultado,
    Kills,
    Deaths,
    Assists,
    ROUND(CAST((Kills + Assists) AS FLOAT) / ISNULL(NULLIF(Deaths, 0), 1), 2) AS KDA_Ratio
FROM dbo.MisPartidasLoL
ORDER BY KDA_Ratio DESC;
3. Ver con qué campeones genero más oro:
SELECT 
    Campeon,
    COUNT(*) AS Partidas_Jugadas,
    AVG(Oro_Ganado) AS Promedio_Oro,
    AVG(Danio_Total) AS Promedio_Danio
FROM dbo.MisPartidasLoL
GROUP BY Campeon
HAVING COUNT(*) > 1 
ORDER BY Promedio_Oro DESC;
4. Mejor partida con cada campeón:
WITH RankingCampeones AS (
    SELECT 
        Campeon,
        Resultado,
        Kills,
        Danio_Total,
        ROW_NUMBER() OVER(PARTITION BY Campeon ORDER BY Danio_Total DESC) as Rank_Danio
    FROM dbo.MisPartidasLoL
)
SELECT 
    Campeon,
    Resultado,
    Kills,
    Danio_Total AS Record_Personal_Danio
FROM RankingCampeones 
WHERE Rank_Danio = 1
ORDER BY Record_Personal_Danio DESC;

###5. Sobre mí.
Soy estudiante de la carrera de Ingeniería Empresarial y de Sistemas, es un código creado para medir el rendimiento de mis partidas y a la misma vez aplicar mis propios conocimientos, es bastante útil aunque esté limitado por el uso de una API pública, agradezco a Riot Games que pueda usar datos de ellos para hacer este proyecto, iré mejorando al pasar del tiempo y si te gustó podrías ver más sobre mi perfil, estaré actualizando proyectos y sobre todo, haré nuevamente el juego que hice para san valentin con muchas más cosas para que sea entretenido en solo 2 semanas que es lo que duré en hacer el primero.
