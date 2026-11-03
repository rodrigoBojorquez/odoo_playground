from datetime import timedelta

from odoo import SUPERUSER_ID, Command, api, fields


MODULE = "safevitia_demo"


def _create(env, model, xmlid, values):
    record = env[model].create(values)
    env["ir.model.data"].create({
        "module": MODULE,
        "name": xmlid,
        "model": model,
        "res_id": record.id,
        "noupdate": True,
    })
    return record


def _tax(env, company, use, amount):
    return env["account.tax"].search([
        ("company_id", "=", company.id),
        ("type_tax_use", "=", use),
        ("amount", "=", amount),
        ("active", "=", True),
    ], limit=1)


def _deliver(order, done_date):
    for picking in order.picking_ids.filtered(lambda item: item.state not in ("done", "cancel")):
        picking.action_assign()
        for move in picking.move_ids.filtered(lambda item: item.state not in ("done", "cancel")):
            move.quantity = move.product_uom_qty
            move.picked = True
        picking.with_context(cancel_backorder=True, skip_sms=True)._action_done()
        picking.date_done = done_date


def _pay_invoice(env, invoice, payment_date):
    journal = env["account.journal"].search([
        ("company_id", "=", invoice.company_id.id),
        ("type", "in", ("bank", "cash")),
    ], limit=1)
    env["account.payment.register"].with_context(
        active_model="account.move",
        active_ids=invoice.ids,
    ).create({
        "payment_date": payment_date,
        "journal_id": journal.id,
        "amount": invoice.amount_residual,
    })._create_payments()


def _check_demo(env, company, demo_user):
    checks = {
        "clientes y proveedores": env["res.partner"].search_count([("ref", "like", "SV-DEMO-%")]) >= 24,
        "productos": env["product.template"].search_count([("default_code", "like", "SV-%")]) == 10,
        "oportunidades": env["crm.lead"].with_context(active_test=False).search_count([
            ("name", "like", "[DEMO] %"),
            ("user_id", "=", demo_user.id),
        ]) == 12,
        "ventas": env["sale.order"].search_count([
            ("client_order_ref", "like", "DEMO-%"),
            ("user_id", "=", demo_user.id),
        ]) == 14,
        "entregas completadas": env["stock.picking"].search_count([
            ("sale_id.client_order_ref", "like", "DEMO-%"),
            ("state", "=", "done"),
        ]) == 7,
        "compras": env["purchase.order"].search_count([("partner_ref", "like", "DEMO-%")]) == 7,
        "facturas publicadas": env["account.move"].search_count([
            ("company_id", "=", company.id),
            ("ref", "like", "DEMO-%"),
            ("state", "=", "posted"),
        ]) >= 5,
        "vehículos": env["fleet.vehicle"].search_count([("license_plate", "like", "SV-%")]) == 6,
    }
    failed = [label for label, result in checks.items() if not result]
    assert not failed, "Escenario Safe Vitia incompleto: %s" % ", ".join(failed)


def post_init_hook(env):
    env = api.Environment(env.cr, SUPERUSER_ID, env.context)
    demo_user = env["res.users"].search([
        ("active", "=", True),
        ("share", "=", False),
        ("id", "!=", SUPERUSER_ID),
    ], limit=1)
    assert demo_user, "Safe Vitia requiere un usuario interno activo para asignar los datos demo"
    company = env.company
    country = env.ref("base.mx")
    state = env.ref("base.state_mx_q_roo")
    currency = env.ref("base.MXN")
    today = fields.Date.today()
    now = fields.Datetime.now()

    company.partner_id.write({
        "name": "Safe Vitia (Demo)",
        "street": "Av. José López Portillo 218",
        "street2": "Bodega 4, Región 92",
        "city": "Cancún",
        "zip": "77516",
        "state_id": state.id,
        "country_id": country.id,
        "phone": "+52 998 555 0100",
        "email": "operaciones@safevitia.example",
        "website": "https://safevitia.com",
        "vat": "EKU9003173C9",
    })
    company.write({
        "name": "Safe Vitia (Demo)",
        "currency_id": currency.id,
        "account_use_credit_limit": True,
        "invoice_terms": "Información demostrativa. No representa un CFDI timbrado ni tiene validez fiscal.",
    })
    if "stock_move_sms_validation" in company._fields:
        company.stock_move_sms_validation = False
    env["ir.config_parameter"].set_param("crm.iap.lead.enrich.setting", "manual")
    for xmlid in (
        "crm_iap_enrich.ir_cron_lead_enrichment",
        "partner_autocomplete.ir_cron_partner_autocomplete",
    ):
        cron = env.ref(xmlid, raise_if_not_found=False)
        if cron:
            cron.active = False
    spanish = env["res.lang"].with_context(active_test=False).search([("code", "=", "es_MX")], limit=1)
    user_partners = env["res.users"].search([("share", "=", False)]).mapped("partner_id")
    user_partners.write({"tz": "America/Cancun"})
    if spanish and spanish.active:
        user_partners.lang = spanish.code

    if not env["account.account"].search_count([("company_id", "=", company.id)]):
        env["account.chart.template"].try_loading("mx", company, install_demo=False)

    env = api.Environment(env.cr, SUPERUSER_ID, dict(env.context, allowed_company_ids=[company.id]))
    company = env["res.company"].browse(company.id)
    warehouse = env["stock.warehouse"].search([("company_id", "=", company.id)], limit=1)
    warehouse.write({"name": "Almacén Cancún", "code": "CUN"})
    warehouse.lot_stock_id.name = "Existencias Safe Vitia"

    customer_tag = _create(env, "res.partner.category", "tag_customer", {"name": "Cliente Safe Vitia"})
    supplier_tag = _create(env, "res.partner.category", "tag_supplier", {"name": "Proveedor Safe Vitia"})
    driver_tag = _create(env, "res.partner.category", "tag_driver", {"name": "Repartidor"})
    segment_tags = {
        name: _create(env, "res.partner.category", "tag_segment_%s" % index, {"name": name})
        for index, name in enumerate(("Hotelería", "Restaurantes", "Corporativos", "Escuelas", "Construcción", "Eventos"), 1)
    }

    immediate = env.ref("account.account_payment_term_immediate")
    term_15 = env.ref("account.account_payment_term_15days")
    term_30 = env.ref("account.account_payment_term_30days")
    customers_data = [
        ("Hotel Costa Maya", "Hotelería", "Blvd. Kukulcán Km 8.5", "77500", 85000, term_30, "Compras", "Zona Hotelera"),
        ("Colegio Horizonte Cancún", "Escuelas", "Av. Huayacán 310", "77560", 45000, term_15, "Administración", "Huayacán"),
        ("Constructora Caribe Azul", "Construcción", "Av. Bonampak 120", "77500", 65000, term_30, "Obra Puerto Cancún", "Puerto Cancún"),
        ("Restaurante La Ceiba", "Restaurantes", "Av. Náder 28", "77500", 25000, term_15, "Almacén", "Centro"),
        ("Grupo Corporativo Nichupté", "Corporativos", "Av. Bonampak 77", "77500", 50000, term_30, "Recepción Torre B", "Puerto Cancún"),
        ("Eventos del Caribe", "Eventos", "Av. Tulum 145", "77500", 35000, term_15, "Bodega de Eventos", "Centro"),
        ("Clínica San Miguel", "Corporativos", "Av. Kabah 410", "77505", 30000, term_15, "Urgencias", "Región 93"),
        ("Hotel Arena Blanca", "Hotelería", "Blvd. Kukulcán Km 14", "77500", 90000, term_30, "Andén de Proveedores", "Zona Hotelera"),
        ("Cafeterías Mangle", "Restaurantes", "Av. Cobá 33", "77500", 28000, term_15, "Sucursal Centro", "Centro"),
        ("Residencial Lagos", "Corporativos", "Av. 135 901", "77536", 22000, term_15, "Caseta Principal", "Cancún Sur"),
        ("Obras Peninsulares", "Construcción", "Carr. Cancún-Puerto Morelos Km 21", "77580", 70000, term_30, "Campamento de Obra", "Puerto Morelos"),
        ("Instituto del Mar", "Escuelas", "Av. Kabah 216", "77505", 38000, term_15, "Acceso Docentes", "Cancún Centro"),
        ("Oficinas Maralto", "Corporativos", "Av. Bonampak 15", "77500", 32000, term_30, "Piso 6", "Puerto Cancún"),
        ("Banquetes Turquesa", "Eventos", "Av. Chac Mool 190", "77539", 30000, immediate, "Bodega", "Cancún Poniente"),
        ("Público en General", "Corporativos", "Av. Tulum 1", "77500", 0, immediate, "Mostrador", "Centro"),
    ]
    customers = []
    for index, (name, segment, street, zip_code, credit, payment_term, branch, zone) in enumerate(customers_data, 1):
        partner = _create(env, "res.partner", "customer_%02d" % index, {
            "name": name,
            "company_type": "company",
            "customer_rank": 1,
            "ref": "SV-DEMO-C%03d" % index,
            "street": street,
            "city": "Cancún" if "Puerto Morelos" not in street else "Puerto Morelos",
            "zip": zip_code,
            "state_id": state.id,
            "country_id": country.id,
            "phone": "+52 998 555 %04d" % (1000 + index),
            "email": "compras%02d@cliente.example" % index,
            "category_id": [Command.set([customer_tag.id, segment_tags[segment].id])],
            "property_payment_term_id": payment_term.id,
            "credit_limit": credit,
            "comment": "Zona de servicio: %s. Datos exclusivamente demostrativos." % zone,
            "vat": "XAXX010101000" if name == "Público en General" else False,
        })
        _create(env, "res.partner", "customer_%02d_shipping" % index, {
            "name": branch,
            "type": "delivery",
            "parent_id": partner.id,
            "street": street,
            "city": partner.city,
            "zip": zip_code,
            "state_id": state.id,
            "country_id": country.id,
            "phone": partner.phone,
            "ref": "SV-DEMO-E%03d" % index,
        })
        customers.append(partner)

    suppliers_data = [
        ("Envases del Caribe", "Garrafones y tapas", "Cancún"),
        ("Filtración Peninsular", "Filtros y consumibles", "Mérida"),
        ("Plásticos del Sureste", "Botellas y embalaje", "Cancún"),
        ("Taller Diésel Bonfil", "Mantenimiento de unidades", "Cancún"),
        ("Combustibles del Caribe", "Combustible", "Cancún"),
        ("Suministros Hoteleros MX", "Dispensadores", "Playa del Carmen"),
        ("Logística y Refacciones Maya", "Refacciones", "Cancún"),
    ]
    suppliers = []
    for index, (name, service, city) in enumerate(suppliers_data, 1):
        suppliers.append(_create(env, "res.partner", "supplier_%02d" % index, {
            "name": name,
            "company_type": "company",
            "supplier_rank": 1,
            "ref": "SV-DEMO-P%03d" % index,
            "street": "Calle Industrial %d" % (20 + index),
            "city": city,
            "zip": "77500",
            "state_id": state.id,
            "country_id": country.id,
            "phone": "+52 998 555 %04d" % (2000 + index),
            "email": "ventas%02d@proveedor.example" % index,
            "category_id": [Command.set([supplier_tag.id])],
            "property_supplier_payment_term_id": term_30.id,
            "comment": "%s. Datos exclusivamente demostrativos." % service,
        }))

    drivers = []
    for index, name in enumerate(("Luis May", "Jorge Pech", "Mariana Canul", "Carlos Ek"), 1):
        drivers.append(_create(env, "res.partner", "driver_%02d" % index, {
            "name": name,
            "company_type": "person",
            "ref": "SV-DEMO-R%03d" % index,
            "phone": "+52 998 555 %04d" % (3000 + index),
            "email": "reparto%02d@safevitia.example" % index,
            "category_id": [Command.set([driver_tag.id])],
        }))

    categories = {
        key: _create(env, "product.category", "category_%s" % key, {"name": name})
        for key, name in {
            "water": "Agua purificada",
            "containers": "Envases retornables",
            "accessories": "Accesorios",
            "supplies": "Insumos operativos",
            "services": "Servicios de distribución",
        }.items()
    }
    sale_tax_16 = _tax(env, company, "sale", 16)
    sale_tax_0 = _tax(env, company, "sale", 0)
    purchase_tax_16 = _tax(env, company, "purchase", 16)
    unit = env.ref("uom.product_uom_unit")
    products_data = [
        ("SV-AG20", "Agua purificada en garrafón 20 L", "water", "product", 42, 13, 680, sale_tax_0, purchase_tax_16),
        ("SV-AG15C", "Caja agua 1.5 L (12 botellas)", "water", "product", 118, 72, 125, sale_tax_0, purchase_tax_16),
        ("SV-AG600C", "Caja agua 600 ml (24 botellas)", "water", "product", 132, 79, 95, sale_tax_0, purchase_tax_16),
        ("SV-ENV20", "Garrafón PET 20 L retornable", "containers", "product", 185, 96, 420, sale_tax_16, purchase_tax_16),
        ("SV-DISP", "Dispensador cerámico", "accessories", "product", 690, 410, 18, sale_tax_16, purchase_tax_16),
        ("SV-BOMBA", "Bomba manual para garrafón", "accessories", "product", 145, 78, 32, sale_tax_16, purchase_tax_16),
        ("SV-TAPA", "Tapa de seguridad para garrafón", "supplies", "product", 1.8, 0.55, 2400, sale_tax_16, purchase_tax_16),
        ("SV-FILTRO", "Filtro de carbón activado", "supplies", "product", 950, 610, 14, sale_tax_16, purchase_tax_16),
        ("SV-EXPRESS", "Entrega express", "services", "service", 120, 0, 0, sale_tax_16, False),
        ("SV-PM", "Cargo logístico Puerto Morelos", "services", "service", 180, 0, 0, sale_tax_16, False),
    ]
    products = {}
    for index, (code, name, category, product_type, price, cost, stock, sale_tax, purchase_tax) in enumerate(products_data, 1):
        template = _create(env, "product.template", "product_%02d" % index, {
            "name": name,
            "default_code": code,
            "detailed_type": product_type,
            "categ_id": categories[category].id,
            "uom_id": unit.id,
            "uom_po_id": unit.id,
            "list_price": price,
            "standard_price": cost,
            "sale_ok": True,
            "purchase_ok": product_type == "product",
            "invoice_policy": "order",
            "purchase_method": "purchase",
            "taxes_id": [Command.set(sale_tax.ids)],
            "supplier_taxes_id": [Command.set(purchase_tax.ids if purchase_tax else [])],
            "description_sale": "Producto demostrativo Safe Vitia.",
        })
        product = template.product_variant_id
        products[code] = product
        if stock:
            env["stock.quant"]._update_available_quantity(product, warehouse.lot_stock_id, stock)

    corporate_pricelist = _create(env, "product.pricelist", "pricelist_corporate", {
        "name": "Tarifa corporativa Cancún",
        "currency_id": currency.id,
        "company_id": company.id,
    })
    _create(env, "product.pricelist.item", "pricelist_corporate_water_50", {
        "pricelist_id": corporate_pricelist.id,
        "applied_on": "0_product_variant",
        "product_id": products["SV-AG20"].id,
        "min_quantity": 50,
        "compute_price": "fixed",
        "fixed_price": 38,
    })
    _create(env, "product.pricelist.item", "pricelist_corporate_water_100", {
        "pricelist_id": corporate_pricelist.id,
        "applied_on": "0_product_variant",
        "product_id": products["SV-AG20"].id,
        "min_quantity": 100,
        "compute_price": "fixed",
        "fixed_price": 36,
    })
    puerto_pricelist = _create(env, "product.pricelist", "pricelist_puerto", {
        "name": "Tarifa Puerto Morelos",
        "currency_id": currency.id,
        "company_id": company.id,
    })
    _create(env, "product.pricelist.item", "pricelist_puerto_water", {
        "pricelist_id": puerto_pricelist.id,
        "applied_on": "0_product_variant",
        "product_id": products["SV-AG20"].id,
        "min_quantity": 1,
        "compute_price": "fixed",
        "fixed_price": 45,
    })

    stages = env["crm.stage"].search([], order="sequence, id")
    lost_reason = _create(env, "crm.lost.reason", "lost_reason_coverage", {"name": "Fuera de cobertura actual"})
    opportunities_data = [
        ("Convenio anual Hotel Coral", 68000, 80, 0, "open"),
        ("Suministro nueva torre corporativa", 36000, 55, 1, "open"),
        ("Campamento obra carretera", 52000, 35, 0, "open"),
        ("Festival gastronómico noviembre", 24000, 70, 1, "open"),
        ("Renovación Colegio Horizonte", 42000, 100, 2, "won"),
        ("Abastecimiento Hotel Arena Blanca", 96000, 100, 3, "won"),
        ("Nueva sucursal Cafeterías Mangle", 18000, 60, 4, "open"),
        ("Contrato Clínica San Miguel", 28000, 40, 5, "open"),
        ("Evento deportivo Puerto Morelos", 15000, 0, 6, "lost"),
        ("Residencial de 180 departamentos", 48000, 25, 7, "open"),
        ("Oficinas Maralto consumo mensual", 31000, 75, 8, "open"),
        ("Banquetes temporada alta", 27000, 50, 9, "open"),
    ]
    for index, (name, revenue, probability, customer_index, status) in enumerate(opportunities_data, 1):
        lead = _create(env, "crm.lead", "opportunity_%02d" % index, {
            "name": "[DEMO] %s" % name,
            "type": "opportunity",
            "partner_id": customers[customer_index].id,
            "expected_revenue": revenue,
            "probability": probability,
            "priority": "2" if revenue >= 50000 else "1",
            "stage_id": stages[min(index % max(len(stages) - 1, 1), len(stages) - 1)].id if stages else False,
            "date_deadline": today + timedelta(days=index * 3),
            "description": "Oportunidad demostrativa basada en consumo recurrente de agua purificada.",
            "user_id": demo_user.id,
        })
        if status == "won":
            lead.action_set_won()
        elif status == "lost":
            lead.action_set_lost(lost_reason_id=lost_reason.id)

    purchases_data = [
        (28, 0, "received", [("SV-ENV20", 120, 92), ("SV-TAPA", 2500, 0.52)]),
        (20, 1, "billed", [("SV-FILTRO", 8, 595)]),
        (14, 2, "confirmed", [("SV-AG600C", 80, 75)]),
        (8, 5, "confirmed", [("SV-DISP", 12, 395), ("SV-BOMBA", 24, 72)]),
        (5, 0, "draft", [("SV-ENV20", 80, 94)]),
        (3, 1, "draft", [("SV-FILTRO", 6, 610)]),
        (1, 2, "draft", [("SV-AG15C", 100, 69)]),
    ]
    for index, (days_ago, supplier_index, status, lines) in enumerate(purchases_data, 1):
        order_date = now - timedelta(days=days_ago)
        purchase = _create(env, "purchase.order", "purchase_%02d" % index, {
            "partner_id": suppliers[supplier_index].id,
            "partner_ref": "DEMO-OC-%03d" % index,
            "date_order": order_date,
            "company_id": company.id,
            "notes": "Orden de compra demostrativa Safe Vitia.",
            "order_line": [Command.create({
                "product_id": products[code].id,
                "name": products[code].display_name,
                "product_qty": quantity,
                "product_uom": products[code].uom_po_id.id,
                "price_unit": price,
                "date_planned": order_date + timedelta(days=4),
            }) for code, quantity, price in lines],
        })
        if status != "draft":
            purchase.button_confirm()
        if status == "received":
            for picking in purchase.picking_ids:
                picking.action_assign()
                for move in picking.move_ids:
                    move.quantity = move.product_uom_qty
                picking.button_validate()
                picking.date_done = order_date + timedelta(days=4)
        if status == "billed":
            purchase.action_create_invoice()
            bill = purchase.invoice_ids[:1]
            bill.write({"invoice_date": today - timedelta(days=days_ago - 3), "ref": "DEMO-FP-%03d" % index})
            bill.action_post()

    sales_data = [
        (32, 4, "paid", [("SV-AG20", 65, 38), ("SV-DISP", 1, 690)]),
        (27, 3, "paid", [("SV-AG20", 35, 40)]),
        (23, 0, "posted", [("SV-AG20", 180, 36), ("SV-AG600C", 12, 125)]),
        (19, 2, "posted", [("SV-AG20", 90, 38), ("SV-PM", 1, 180)]),
        (15, 1, "draft_invoice", [("SV-AG20", 55, 38), ("SV-BOMBA", 2, 145)]),
        (12, 8, "delivered", [("SV-AG20", 42, 40)]),
        (10, 6, "delivered", [("SV-AG20", 28, 40), ("SV-DISP", 1, 690)]),
        (8, 7, "confirmed", [("SV-AG20", 140, 36)]),
        (6, 10, "confirmed", [("SV-AG20", 80, 45), ("SV-PM", 1, 180)]),
        (4, 12, "quotation", [("SV-AG20", 45, 40)]),
        (3, 5, "quotation", [("SV-AG600C", 30, 126), ("SV-AG15C", 18, 112)]),
        (2, 11, "quotation", [("SV-AG20", 30, 40), ("SV-BOMBA", 3, 145)]),
        (1, 13, "quotation", [("SV-AG20", 75, 38), ("SV-EXPRESS", 1, 120)]),
        (0, 9, "quotation", [("SV-AG20", 24, 42)]),
    ]
    for index, (days_ago, customer_index, status, lines) in enumerate(sales_data, 1):
        order_date = now - timedelta(days=days_ago)
        customer = customers[customer_index]
        shipping = customer.child_ids.filtered(lambda child: child.type == "delivery")[:1]
        sale = _create(env, "sale.order", "sale_%02d" % index, {
            "partner_id": customer.id,
            "partner_invoice_id": customer.id,
            "partner_shipping_id": shipping.id or customer.id,
            "client_order_ref": "DEMO-PO-%03d" % index,
            "date_order": order_date,
            "validity_date": today + timedelta(days=7),
            "payment_term_id": customer.property_payment_term_id.id,
            "pricelist_id": puerto_pricelist.id if customer_index == 10 else corporate_pricelist.id,
            "note": "Pedido demostrativo. Ventana de entrega 09:00–12:00.",
            "user_id": demo_user.id,
            "order_line": [Command.create({
                "product_id": products[code].id,
                "name": products[code].get_product_multiline_description_sale(),
                "product_uom_qty": quantity,
                "product_uom": products[code].uom_id.id,
                "price_unit": price,
            }) for code, quantity, price in lines],
        })
        if status != "quotation":
            sale.action_confirm()
        if status in ("delivered", "draft_invoice", "posted", "paid"):
            done_date = order_date + timedelta(hours=5)
            _deliver(sale, done_date)
        if status in ("draft_invoice", "posted", "paid"):
            invoice = sale._create_invoices()[:1]
            invoice.write({
                "invoice_date": today - timedelta(days=max(days_ago - 1, 0)),
                "ref": "DEMO-FV-%03d" % index,
            })
            if status in ("posted", "paid"):
                invoice.action_post()
            if status == "paid":
                _pay_invoice(env, invoice, today - timedelta(days=max(days_ago - 5, 0)))

    brands = {}
    for index, name in enumerate(("Nissan", "Toyota", "Isuzu"), 1):
        brands[name] = _create(env, "fleet.vehicle.model.brand", "fleet_brand_%02d" % index, {"name": name})
    models = {}
    for index, (brand, name, fuel) in enumerate((("Nissan", "Urvan NV350", "gasoline"), ("Toyota", "Hilux", "diesel"), ("Isuzu", "ELF 200", "diesel")), 1):
        models[name] = _create(env, "fleet.vehicle.model", "fleet_model_%02d" % index, {
            "name": name,
            "brand_id": brands[brand].id,
            "vehicle_type": "car",
            "default_fuel_type": fuel,
            "transmission": "manual",
            "seats": 3,
            "doors": 4,
        })
    vehicles_data = [
        ("SV-101-A", "Urvan NV350", 0, "2022", 68420),
        ("SV-102-A", "Urvan NV350", 1, "2021", 91280),
        ("SV-201-C", "Hilux", 2, "2023", 42850),
        ("SV-202-C", "Hilux", 3, "2020", 118300),
        ("SV-301-K", "ELF 200", 0, "2022", 73940),
        ("SV-302-K", "ELF 200", 1, "2024", 21810),
    ]
    vehicles = []
    for index, (plate, model_name, driver_index, year, odometer) in enumerate(vehicles_data, 1):
        vehicle = _create(env, "fleet.vehicle", "vehicle_%02d" % index, {
            "model_id": models[model_name].id,
            "license_plate": plate,
            "driver_id": drivers[driver_index].id,
            "model_year": year,
            "acquisition_date": today - timedelta(days=365 * (2026 - int(year))),
            "location": "Base Cancún",
            "company_id": company.id,
            "odometer": odometer,
            "color": "Blanco",
        })
        vehicles.append(vehicle)
    service_types = env["fleet.service.type"].search([], limit=3)
    for index, vehicle in enumerate(vehicles, 1):
        _create(env, "fleet.vehicle.log.services", "fleet_service_%02d" % index, {
            "vehicle_id": vehicle.id,
            "service_type_id": service_types[(index - 1) % len(service_types)].id,
            "vendor_id": suppliers[3].id,
            "amount": 1200 + index * 350,
            "date": today - timedelta(days=index * 12),
            "odometer": vehicle.odometer - 700,
            "description": "Servicio preventivo demostrativo",
            "state": "done" if index < 5 else "running",
            "inv_ref": "DEMO-SRV-%03d" % index,
        })

    _check_demo(env, company, demo_user)
