# -*- coding: utf-8 -*-
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import yaml

def bulk_close_orders():
    with open('config/credentials.yaml', 'r') as f:
        config = yaml.safe_load(f)
    profiles = config.get("profiles", {})
    profile = profiles.get("appOmnioCondor")
    if not profile:
        print("❌ No se encontró el perfil appOmnioCondor en credentials.yaml")
        return

    base_url = profile["api_base_url"].rstrip('/')
    company_id = str(profile["company_id"])
    token = profile["token"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    orders_url = f"{base_url}/api/1.0/tenants/{company_id}/orders"
    print(f"🔍 Obteniendo órdenes para Company ID {company_id}...")
    res = requests.get(orders_url, headers=headers)
    if not res.ok:
        print(f"❌ Error al consultar órdenes: {res.status_code} - {res.text}")
        return

    orders = res.json().get("data", res.json() if isinstance(res.json(), list) else [])
    if isinstance(orders, dict): orders = orders.get("data", [])

    print(f"📦 Se encontraron {len(orders)} órdenes. Iniciando actualización a estado 'closed'...")

    success_count = 0
    for order in orders:
        order_id = order.get("id")
        order_num = order.get("order_num")
        if not order_id: continue

        # 1. Si la orden tiene envíos (shipments), los actualizamos a estado 'shipped'
        shipments = order.get("shipments") or []
        for shipment in shipments:
            s_id = shipment.get("id")
            s_num = shipment.get("shipment_number") or order_num
            if s_id:
                s_url = f"{base_url}/api/1.0/tenants/{company_id}/shipments/{s_id}"
                s_payload = {
                    "shipment_number": s_num,
                    "status_name": "shipped",
                    "tracking_number": f"TRACK-{order_num}"
                }
                requests.put(s_url, json=s_payload, headers=headers)

        # 2. Actualizamos la orden
        update_url = f"{base_url}/api/1.0/tenants/{company_id}/orders/{order_id}"
        payload = {
            "order_num": order_num,
            "status_name": "closed",
            "currency_id": 1,
            "ship_method": order.get("ship_method") or "AVC-AIR",
            "ship_carrier": order.get("ship_carrier") or "AVC"
        }

        upd_res = requests.put(update_url, json=payload, headers=headers)
        if upd_res.status_code in [200, 201]:
            print(f"✅ Envíos y Orden {order_num} (ID: {order_id}) marcados como 'shipped' / 'closed'.")
            success_count += 1
        else:
            print(f"❌ Error en orden {order_num} (ID: {order_id}): {upd_res.text[:120]}")

    print(f"\n🎉 Finalizado: {success_count}/{len(orders)} órdenes fueron actualizadas a 'closed'.")

if __name__ == "__main__":
    bulk_close_orders()
