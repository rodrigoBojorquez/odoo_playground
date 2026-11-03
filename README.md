# Safe Vitia — ERP demo en Odoo 17

Este proyecto levanta Odoo 17 Community con un único módulo de escenario, `safevitia_demo`. El módulo instala y enlaza solamente las aplicaciones solicitadas:

- Contactos
- CRM
- Ventas
- Inventario
- Facturación / Contabilidad
- Localización mexicana
- Compras
- Flota

## Arranque

```bash
docker compose up -d
```

La interfaz queda disponible en <http://localhost:8069>. La base preparada se llama `safevitia_playground`; se usa el usuario administrador creado al inicializarla.

## Recorrido sugerido

1. **CRM:** revisar oportunidades `[DEMO]` en distintas etapas, incluidas ganadas y perdidas.
2. **Ventas:** filtrar la referencia de cliente por `DEMO-` para ver cotizaciones, pedidos pendientes, entregados, facturados y pagados.
3. **Inventario:** consultar existencias del almacén Cancún y las recepciones/entregas generadas por compras y ventas.
4. **Facturación:** filtrar la referencia por `DEMO-` para ver facturas borrador, publicadas, pagadas y una factura de proveedor.
5. **Compras:** filtrar referencia de proveedor por `DEMO-` para ver solicitudes, órdenes y recepciones.
6. **Flota:** revisar seis unidades, conductores, kilometraje y servicios.

Todos los nombres, correos, teléfonos, RFC, importes y documentos son ficticios. Las facturas publicadas se pueden imprimir, pero no son CFDI timbrados y no tienen validez fiscal.

## Reinstalación en otra base

Con la base creada y el país México seleccionado:

```bash
docker compose stop web
docker compose run --rm web odoo -d NOMBRE_BASE -i safevitia_demo --load-language=es_MX --stop-after-init
docker compose up -d web
```

