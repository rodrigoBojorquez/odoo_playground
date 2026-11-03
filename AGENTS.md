# Contexto de proyecto: ERP en Odoo para Safe Vitia

## 1. Propósito de este documento

Este archivo concentra el contexto útil de la conversación **“Módulos Odoo para Agua”** para continuar el análisis, la propuesta comercial o el desarrollo de una solución ERP en Odoo para Safe Vitia.

No es un levantamiento formal ni una especificación aprobada por el cliente. Los hallazgos provienen de la información pública revisada durante la conversación original y las propuestas incluyen inferencias que deben validarse antes de cotizar o desarrollar.

Fuentes consideradas en la conversación:

- Sitio web: <https://safevitia.com/>
- Facebook: <https://www.facebook.com/SafeVitiaMX/>
- Conversación de origen: <chatgpt-conversation://6ae231c3-d5fc-83e8-9105-4bf78f820bec>

La página de Facebook no pudo consultarse directamente en la revisión original. No se deben atribuir a esa página datos que no hayan sido comprobados.

## 2. Contexto del cliente

Safe Vitia comercializa y distribuye agua purificada en garrafones. Su comunicación pública está dirigida principalmente a clientes empresariales y organizaciones que requieren suministro recurrente, no solamente a ventas domésticas aisladas.

Los segmentos mencionados en su sitio incluyen:

- escuelas y colegios;
- construcción y obras;
- restaurantes y hotelería;
- entretenimiento y eventos;
- corporativos y oficinas.

Las zonas de servicio identificadas durante la conversación fueron Cancún, Zona Hotelera, Centro, Puerto Cancún, Bonfil y Puerto Morelos.

La propuesta ERP debe presentarse como una solución integral para centralizar clientes, pedidos, entregas, rutas, garrafones retornables, consumos, facturación y cobranza. Comercialmente conviene hablar de resultados operativos y no de una lista aislada de módulos de Odoo.

## 3. Hallazgos del sitio web

En la revisión original se reportaron las siguientes señales públicas:

- Safe Vitia indicaba atender a más de 150 empresas.
- Ofrece entregas programadas y acuerda con cada cliente ubicación, horario y frecuencia de suministro.
- Recibe solicitudes mediante un formulario web, WhatsApp o llamada.
- El formulario solicita empresa o proyecto, cantidad de garrafones, datos de contacto, correo, WhatsApp y dirección de entrega.
- Promueve facturación adaptada a la periodicidad requerida por cada empresa.
- Ofrece control de consumos y estados de cuenta.
- El precio anunciado comenzaba desde $40 MXN por garrafón y podía variar por volumen y zona.
- La pureza del agua y los análisis periódicos forman parte de sus argumentos comerciales.

Estos datos pueden haber cambiado. Deben verificarse de nuevo en una fase de descubrimiento antes de convertirlos en requisitos, reglas de precio o compromisos contractuales.

## 4. Modelo de negocio inferido

La hipótesis de trabajo es un modelo principalmente **B2B, recurrente y orientado a distribución**, con estas características:

1. Se capta una empresa interesada o se recibe una solicitud de suministro.
2. Se acuerdan cantidad, dirección o sucursal, ventana de entrega, frecuencia y precio.
3. El suministro puede repetirse varios días por semana o con otra periodicidad.
4. La empresa entrega garrafones llenos y recupera envases vacíos.
5. El precio puede depender del volumen, la zona y el acuerdo comercial.
6. La facturación puede realizarse por entrega o consolidarse semanal, quincenal o mensualmente.
7. Algunos clientes empresariales probablemente operan a crédito y requieren estados de cuenta.

La principal separación conceptual es:

- **Agua:** producto consumible que se vende.
- **Garrafón:** envase retornable cuyo saldo y movimientos deben controlarse por cliente.

La fabricación o purificación propia no quedó confirmada. Producción, trazabilidad de lotes, calidad y mantenimiento de planta son oportunidades potenciales, no alcance confirmado.

## 5. Módulos estándar de Odoo recomendados

| Prioridad | Aplicación o capacidad | Uso propuesto |
|---|---|---|
| Alta | Contactos | Empresas, contactos, RFC y domicilios o sucursales de entrega. |
| Alta | CRM | Prospectos B2B, pipeline comercial, sector, consumo estimado y seguimiento. |
| Alta | Ventas | Cotizaciones, pedidos, condiciones comerciales y listas de precios. |
| Alta | Inventario | Existencias de garrafones llenos, vacíos, dañados, tapas e insumos; movimientos entre almacén, unidad y cliente. |
| Alta | Facturación / Contabilidad | Cuentas por cobrar, estados de cuenta, pagos, límites o alertas de crédito y facturación. |
| Alta | Localización mexicana | CFDI, complementos de pago y datos fiscales, sujetos a la versión de Odoo y configuración fiscal elegidas. |
| Media | Compras | Adquisición de envases, tapas, filtros, químicos, combustible, refacciones y servicios. |
| Media | Flota | Unidades, responsables, kilometraje, combustible, seguros y mantenimiento. |
| Media | Portal | Consulta de pedidos, facturas y pagos; requerirá extensiones para consumos, próximas entregas y envases. |
| Media | Sitio web / CRM | Recepción de solicitudes del formulario actual sin reemplazar inicialmente el sitio existente. |
| Condicional | Fabricación | Purificación, lavado, llenado, consumos, rendimiento y lotes, solo si Safe Vitia produce. |
| Condicional | Calidad | Análisis, parámetros, incidencias y liberación de lotes, solo si existe un proceso formal de calidad. |
| Condicional | Mantenimiento | Equipos de purificación y embotellado, si forman parte de la operación propia. |

La disponibilidad exacta de aplicaciones, funciones y licencias depende de la versión y edición de Odoo. No se ha definido si la solución será Community o Enterprise.

## 6. Desarrollos personalizados propuestos

### 6.1. Control de envases retornables

Es el desarrollo diferenciador más importante. Debe mantener un kardex auditable de movimientos de garrafones por cliente y, cuando aplique, por sucursal.

Movimientos mínimos:

- entrega de envase lleno;
- recepción de vacío;
- préstamo o depósito;
- venta o reposición del envase;
- pérdida;
- daño;
- devolución;
- ajuste autorizado.

Regla conceptual:

`saldo de envases con el cliente = entregados - recuperados - vendidos/repuestos - ajustes aplicables`

Ejemplo: se entregan 30 garrafones y se recuperan 26 vacíos; el saldo pendiente aumenta en 4. El sistema debe conservar fecha, cliente, pedido o entrega relacionada, usuario y motivo de cualquier ajuste.

### 6.2. Planes de suministro y pedidos recurrentes

Un plan de suministro debe registrar, como mínimo:

- cliente y sucursal;
- producto y cantidad habitual;
- días o frecuencia;
- ventana de horario;
- fecha inicial y final, cuando exista;
- precio o lista acordada;
- zona o ruta;
- contacto e instrucciones de acceso.

El plan debe generar o proponer los pedidos correspondientes sin depender de mensajes semanales. La política exacta —generación automática o confirmación previa— debe acordarse con el cliente.

### 6.3. Planeación de reparto y “Operación del día”

Vista central para agrupar entregas, asignar repartidor y unidad, preparar carga y dar seguimiento.

Estados propuestos:

`Pendiente → Asignado → Cargado → En ruta → Entregado`

También deben contemplarse `Incidencia` y `Cancelado`, sin borrar el historial.

Datos útiles por parada: cliente, sucursal, zona, pedido, cantidad, ventana de entrega, teléfono, instrucciones, repartidor, unidad y estado. La optimización automática de rutas no debe prometerse hasta conocer volumen, restricciones y servicio de mapas disponible.

### 6.4. Interfaz móvil para repartidores

Desde el teléfono, el repartidor debe poder consultar su ruta y confirmar una entrega registrando:

- cantidades entregadas;
- envases vacíos recibidos;
- incidencia o diferencia;
- forma o referencia de pago, si corresponde;
- observaciones;
- evidencia fotográfica y/o firma, si el cliente lo aprueba.

La confirmación debe actualizar de forma consistente el pedido, la entrega, el inventario, el kardex de envases y la información necesaria para facturación. Debe decidirse durante el levantamiento si se necesita operación sin conexión.

### 6.5. Integración del formulario web

No se propone reemplazar el sitio actual en la primera etapa. El formulario existente debe enviar la solicitud a Odoo para:

- crear una oportunidad si es un prospecto nuevo;
- asociar la solicitud con un cliente existente cuando la identificación sea confiable;
- guardar dirección, cantidad y datos de contacto;
- crear una solicitud de cotización o pedido pendiente de revisión, según la regla acordada.

No debe confirmarse automáticamente una venta sin validar cliente, cobertura, disponibilidad y precio.

### 6.6. Precios por volumen, zona y contrato

Usar primero las listas de precios estándar de Odoo. Añadir personalización únicamente si las reglas reales no caben en ellas. La hipótesis es que el precio puede combinar:

- rango de volumen;
- zona o costo logístico;
- contrato o tarifa negociada por cliente.

Los precios publicados o ejemplificados en la conversación no son una tarifa aprobada.

### 6.7. Portal empresarial ampliado

Sobre el portal estándar, se propone mostrar:

- historial y próxima entrega;
- consumo por periodo;
- saldo de garrafones;
- facturas, XML/PDF y pagos;
- estado de cuenta;
- solicitud de una entrega adicional.

### 6.8. Facturación periódica, crédito y cobranza

La operación debe permitir facturar por entrega o consolidar por periodo, después de validar las reglas fiscales y contables. También se proponen días de crédito, límite de crédito, saldo vencido y alertas antes de aceptar nuevos pedidos. El bloqueo automático debe ser una decisión explícita del cliente; inicialmente puede ser solo una advertencia.

### 6.9. WhatsApp, tableros y automatizaciones

Como extensiones posteriores pueden agregarse confirmaciones, recordatorios y estados de entrega por WhatsApp, además de indicadores de ventas, litros o garrafones entregados, puntualidad, envases pendientes, cobranza y productividad. Las integraciones de mensajería requieren revisar proveedor, costos, consentimiento y plantillas autorizadas.

## 7. Flujo operativo objetivo

```text
Prospecto o solicitud web
        ↓
CRM y calificación
        ↓
Cotización + condiciones comerciales
        ↓
Cliente, sucursal y plan de suministro
        ↓
Pedido puntual o recurrente
        ↓
Planeación diaria + asignación de unidad/repartidor
        ↓
Preparación y carga
        ↓
Entrega + evidencia + cobro/incidencia
        ↓
Registro de vacíos y saldo de envases
        ↓
Actualización de inventario
        ↓
Factura por entrega o consolidada
        ↓
Cobranza + complemento de pago, cuando corresponda
        ↓
Portal, estado de cuenta e indicadores
```

Una entrega con diferencias no debe forzarse como entrega perfecta: las cantidades realmente entregadas y recuperadas deben quedar registradas, y la incidencia debe seguir un flujo de resolución.

## 8. Fases de implementación

### Fase 0 — Descubrimiento y diseño

- Confirmar versión y edición de Odoo, número de usuarios y dispositivos.
- Documentar el proceso actual desde pedido hasta cobro.
- Levantar catálogos, zonas, listas de precios, clientes, sucursales y saldos iniciales.
- Confirmar reglas de envases, depósitos, crédito, facturación y cancelaciones.
- Medir pedidos diarios, unidades, repartidores, almacenes y volumen de movimientos.
- Confirmar si Safe Vitia purifica y llena el agua o solo distribuye.
- Definir integraciones con sitio, WhatsApp, mapas, PAC, bancos u otros sistemas.

### Fase 1 — Núcleo comercial y administrativo

- Contactos, CRM y Ventas.
- Inventario básico.
- Facturación mexicana y cuentas por cobrar.
- Integración del formulario web.
- Control inicial de garrafones retornables.
- Migración de datos acordada y capacitación de usuarios clave.

Resultado esperado: una sola fuente para clientes, pedidos, inventario, envases, facturas y saldos.

### Fase 2 — Distribución recurrente

- Planes de suministro y generación de pedidos.
- Operación del día, rutas, unidades y repartidores.
- Interfaz móvil y evidencias de entrega.
- Registro de vacíos, diferencias e incidencias en campo.
- Flota y controles operativos necesarios.

Resultado esperado: planear, ejecutar y comprobar las entregas recurrentes desde Odoo.

### Fase 3 — Autoservicio y optimización

- Portal ampliado de clientes.
- Indicadores y automatizaciones.
- WhatsApp, si se aprueba la integración.
- Producción, calidad y mantenimiento, únicamente si fueron confirmados.
- Mejoras de rutas basadas en datos reales de la fase 2.

Resultado esperado: reducir trabajo manual, mejorar visibilidad para clientes y gestionar por indicadores.

## 9. Decisiones de diseño ya sugeridas

- Posicionar la oferta como **“Sistema integral Safe Vitia”**, no como una venta de módulos.
- Mantener el sitio web actual al inicio e integrarlo con Odoo.
- Modelar el agua y el envase retornable como conceptos separados.
- Priorizar pedidos, reparto, envases, facturación y cobranza antes que producción o analítica avanzada.
- Usar capacidades estándar de Odoo antes de desarrollar funciones nuevas.
- Mantener trazabilidad de entregas, diferencias y ajustes; no corregir saldos borrando movimientos.
- Implementar por fases para reducir riesgo y permitir que la operación real guíe las mejoras.

## 10. Cautelas y pendientes de validación

- Los datos públicos del sitio no sustituyen entrevistas, observación operativa ni muestras de documentos reales.
- No se verificó Facebook en la conversación original.
- Deben confirmarse cobertura, precios, número de clientes y periodicidades vigentes.
- No está confirmado si la empresa produce/purifica, almacena para terceros o únicamente distribuye.
- Deben identificarse tipos, capacidades, propiedad, depósitos y saldos iniciales de los envases.
- Se necesitan reglas claras para daños, pérdidas, préstamos, ventas y ajustes de garrafones.
- La localización mexicana, CFDI, complementos de pago y, si aplica, Carta Porte deben validarse con el contador y contra la versión elegida de Odoo. No debe asumirse que toda entrega requiere Carta Porte.
- Facturación consolidada, anticipos, depósitos y venta/reposición de envases requieren definición fiscal y contable.
- Firma, fotografías, ubicación y datos de contacto implican permisos, retención y protección de datos.
- Mapas, WhatsApp, PAC y otros servicios pueden generar licencias o costos externos.
- La migración debe definir fuentes, limpieza, responsables y fecha de corte, especialmente para cuentas por cobrar y saldos de envases.
- Deben definirse roles y permisos para ventas, almacén, tráfico, repartidores, facturación, cobranza y administración.

## 11. Contexto e instrucciones para continuar con Codex

### Objetivo del proyecto

Construir o especificar en Odoo una solución para Safe Vitia que cubra el ciclo:

`Cliente → Pedido → Planificación → Carga → Ruta → Entrega → Retorno de envases → Facturación → Cobranza`

El valor diferencial debe concentrarse en el **control auditable de garrafones retornables**, los **pedidos recurrentes** y la **ejecución de reparto**.

### Estado actual

- Solo existe este contexto derivado de una conversación y de una revisión pública del sitio.
- No hay versión o edición de Odoo confirmada.
- No hay repositorio, módulos existentes, modelo de datos aprobado ni credenciales de integración descritos en este documento.
- Ningún requisito se considera aprobado hasta validarlo con Safe Vitia.

### Instrucciones de trabajo para Codex

1. Antes de escribir código, inspeccionar el repositorio, sus instrucciones, la versión de Odoo, módulos instalados, pruebas, datos de demostración y convenciones existentes.
2. Buscar primero capacidades y patrones ya presentes en el proyecto; evitar duplicar lógica estándar de Ventas, Inventario, Contabilidad, Portal o Flota.
3. Mantener el alcance por fases. No implementar producción, calidad, optimización de rutas, modo sin conexión o WhatsApp sin confirmación explícita.
4. Diseñar el control de envases como un libro de movimientos auditable. No guardar únicamente un saldo editable sin historial.
5. Vincular los movimientos de envases y de inventario con la entrega real, conservando manejo de cancelaciones, devoluciones, diferencias y reintentos.
6. Evitar crear pedidos o facturas definitivos desde entradas públicas sin validación de identidad, cobertura, disponibilidad y precio.
7. Respetar multiempresa, moneda, zona horaria, impuestos, permisos y trazabilidad según la configuración real del proyecto.
8. Añadir pruebas pequeñas para la lógica crítica: cálculo de saldo de envases, generación recurrente sin duplicados, diferencias de entrega, cancelación y permisos.
9. No introducir dependencias externas si Odoo o el proyecto ya resuelven la necesidad.
10. Documentar las suposiciones que sigan abiertas y detener cualquier decisión que pueda modificar datos fiscales, saldos o inventario sin una regla aprobada.

### Entidades personalizadas mínimas a evaluar

Los nombres técnicos son provisionales y deben adaptarse a las convenciones del repositorio:

- **Plan de suministro:** cliente, sucursal, producto, cantidad, calendario, horario, tarifa y vigencia.
- **Ruta o jornada de reparto:** fecha, unidad, repartidor, estado y paradas.
- **Parada o entrega operativa:** pedido, secuencia, ventana, cantidades planeadas y reales, vacíos recibidos, evidencia e incidencia.
- **Movimiento de envase:** cliente/sucursal, tipo, cantidad, fecha, referencia, usuario y motivo.

Antes de crear modelos nuevos, comprobar si una entidad estándar puede extenderse de forma segura. En particular, pedidos, transferencias, entregas, contactos y vehículos deben seguir siendo objetos estándar cuando sea posible.

### Primera entrega técnica recomendada

Producir una especificación breve y verificable del MVP de fase 1 que incluya:

- casos de uso y roles;
- estados y reglas del control de envases;
- relación entre pedido, entrega, inventario y factura;
- campos mínimos y permisos;
- datos maestros y estrategia de migración;
- criterios de aceptación y pruebas;
- lista explícita de decisiones pendientes del cliente.

No conviene comenzar por una aplicación móvil o un optimizador de rutas. El primer objetivo es asegurar que un pedido y su entrega actualicen correctamente inventario, envases, facturación y saldo del cliente.

### Preguntas que Codex debe mantener abiertas

- ¿Qué versión, edición y modalidad de alojamiento de Odoo se utilizarán?
- ¿Cuántos usuarios, almacenes, vehículos, repartidores y entregas diarias existen?
- ¿Cada cliente puede tener varias sucursales, precios y calendarios?
- ¿Cómo se controlan hoy los envases y cuál será el saldo inicial confiable?
- ¿Los garrafones se prestan, depositan, venden o combinan estas modalidades?
- ¿Cuándo se factura y qué eventos permiten consolidar entregas?
- ¿Qué ocurre con entregas parciales, rechazos, daños, pérdidas y reprogramaciones?
- ¿Se cobra en campo y qué métodos requieren conciliación?
- ¿Safe Vitia produce y libera lotes o solo distribuye?
- ¿Qué servicios externos y costos están autorizados?

## 12. Resumen ejecutivo de la propuesta

La oportunidad no es una implementación genérica de Odoo. Es una solución vertical para distribución recurrente de agua que combine las aplicaciones estándar de Odoo con tres capacidades propias: **envases retornables, suministro recurrente y reparto comprobable**. La primera fase debe resolver el control transaccional; las automatizaciones y optimizaciones deben incorporarse después de observar datos reales de operación.
