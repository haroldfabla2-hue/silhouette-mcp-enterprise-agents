# COMANDOS RÁPIDOS DE OPERACIÓN - FRAMEWORK SILHOUETTE V4.0

## 🚀 DESPLIEGUE Y GESTIÓN DE SERVICIOS

### Despliegue Completo
```bash
# Despliegue completo automático
./deploy_production.sh

# Despliegue manual paso a paso
docker compose up -d
docker compose ps
```

### Gestión de Servicios
```bash
# Ver estado de todos los servicios
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f marketing_team

# Reiniciar un servicio específico
docker compose restart optimization_team

# Parar todos los servicios
docker compose down

# Parar y eliminar volúmenes (CUIDADO: borra datos)
docker compose down -v
```

### Verificación de Salud
```bash
# Health check de todos los servicios
curl http://localhost:8000/health     # Orchestrator
curl http://localhost:8001/health     # API Gateway
curl http://localhost:8002/health     # Marketing
curl http://localhost:8003/health     # Sales
curl http://localhost:3000/health     # Optimization

# Verificar conectividad de base de datos
docker exec -i $(docker compose ps -q postgres) psql -U postgres -c "SELECT version();"

# Verificar conectividad de Redis
docker exec -i $(docker compose ps -q redis) redis-cli ping
```

## 📊 MONITOREO Y MÉTRICAS

### Monitoreo de Recursos
```bash
# Ver uso de recursos en tiempo real
docker stats

# Ver espacio en disco
docker system df
docker system prune -f

# Ver logs con timestamps
docker compose logs -t -f

# Ver logs de las últimas 2 horas
docker compose logs --since=2h
```

### Métricas de Performance
```bash
# Obtener métricas de un equipo específico
curl -X GET http://localhost:8002/metrics

# Verificar workflow dinámico activo
curl -X GET http://localhost:3000/api/workflows/status

# Obtener estado de coordinación
curl -X GET http://localhost:3000/api/coordination/status
```

## 🔧 DESARROLLO Y DEBUGGING

### Acceso a Containers
```bash
# Acceder al shell de un container
docker exec -it $(docker compose ps -q marketing_team) bash

# Acceder a PostgreSQL
docker exec -it $(docker compose ps -q postgres) psql -U postgres

# Acceder a Redis CLI
docker exec -it $(docker compose ps -q redis) redis-cli

# Ver procesos dentro de un container
docker exec $(docker compose ps -q orchestrator) ps aux
```

### Logs y Debugging
```bash
# Ver logs con niveles específicos
docker compose logs --level=error

# Buscar errores en logs
docker compose logs | grep ERROR

# Ver logs de los últimos 10 minutos
docker compose logs --since=10m

# Exportar logs a archivo
docker compose logs > framework_logs_$(date +%Y%m%d_%H%M%S).txt
```

## 💾 BACKUP Y RESTAURACIÓN

### Backup de Base de Datos
```bash
# Backup de PostgreSQL
docker exec $(docker compose ps -q postgres) pg_dump -U postgres silhoutte_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de Redis
docker exec $(docker compose ps -q redis) redis-cli BGSAVE
docker cp $(docker compose ps -q redis):/data/dump.rdb ./redis_backup_$(date +%Y%m%d_%H%M%S).rdb
```

### Restauración
```bash
# Restaurar PostgreSQL
docker exec -i $(docker compose ps -q postgres) psql -U postgres silhoutte_db < backup_file.sql

# Cargar backup de Redis
docker cp redis_backup.rdb $(docker compose ps -q redis):/data/dump.rdb
docker compose restart redis
```

## 🔄 ACTUALIZACIONES Y MANTENIMIENTO

### Actualizar Framework
```bash
# Actualizar código y reconstruir
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d

# Actualizar solo un servicio
docker compose build --no-cache marketing_team
docker compose restart marketing_team
```

### Mantenimiento
```bash
# Limpiar imágenes no utilizadas
docker image prune -f

# Limpiar containers no utilizados
docker container prune -f

# Limpiar volúmenes no utilizados
docker volume prune -f

# Limpiar todo el sistema
docker system prune -a -f
```

## 🧪 TESTING Y VALIDACIÓN

### Ejecutar Tests
```bash
# Tests de integración del framework
curl -X POST http://localhost:3000/api/tests/integration

# Test de workflows dinámicos
curl -X GET http://localhost:3000/api/workflows/test

# Test de coordinación entre equipos
curl -X GET http://localhost:3000/api/coordination/test
```

### Validación de Configuración
```bash
# Validar docker-compose.yml
docker compose config

# Validar variables de entorno
docker compose config --env-file .env

# Verificar dependencias
pip list | grep -E "(fastapi|uvicorn|redis)"
npm list | grep -E "(express|winston|axios)"
```

## 📡 APIS Y ENDPOINTS PRINCIPALES

### Endpoints de Equipos
```bash
# Marketing Team
curl http://localhost:8002/api/campaigns
curl http://localhost:8002/api/analytics

# Sales Team  
curl http://localhost:8003/api/leads
curl http://localhost:8003/api/deals

# Research Team
curl http://localhost:8004/api/research
curl http://localhost:8004/api/analysis

# Audiovisual Team
curl http://localhost:8005/api/production
curl http://localhost:8005/api/assets
```

### Endpoints de Optimización
```bash
# Status de workflows
curl http://localhost:3000/api/workflows/status

# Métricas de performance
curl http://localhost:3000/api/metrics

# Coordinación entre equipos
curl http://localhost:3000/api/coordination
```

## 🛠️ TROUBLESHOOTING

### Problemas Comunes

#### Servicio no responde
```bash
# Verificar logs del servicio
docker compose logs [servicio]

# Reiniciar servicio específico
docker compose restart [servicio]

# Verificar recursos del sistema
docker stats --no-stream
```

#### Problemas de conectividad
```bash
# Verificar red de Docker
docker network ls
docker network inspect [network_name]

# Verificar puertos en uso
netstat -tulpn | grep :800
```

#### Problemas de base de datos
```bash
# Verificar estado de PostgreSQL
docker exec $(docker compose ps -q postgres) pg_isready -U postgres

# Verificar conexiones activas
docker exec $(docker compose ps -q postgres) psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"
```

### Comandos de Emergencia
```bash
# Parar todos los servicios inmediatamente
docker kill $(docker ps -q)

# Reiniciar toda la stack
docker compose down --remove-orphans
docker compose up -d --force-recreate

# Liberar memoria del sistema
docker system prune -a -f --volumes
```

## 📞 INFORMACIÓN DE CONTACTO

**Framework:** Silhouette V4.0  
**Versión:** 4.0.0  
**Estado:** Producción Ready  
**Documentación:** `/workspace/docs/`  
**Logs:** `docker compose logs`  
**Soporte:** Contactar al equipo de desarrollo

---

**Última actualización:** 2025-11-09  
**Autor:** MiniMax Agent  
**Estado:** Validado para Producción ✅
