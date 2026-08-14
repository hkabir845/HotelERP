from pathlib import Path
import re

ROOT = Path(r"I:\ITProjects\HotelERP\frontend\app")

CONFIG_KIND = {
    "frontdesk/config/packages": "packages",
    "frontdesk/config/room-view-types": "room-view-types",
    "frontdesk/config/bed-info": "bed-info",
    "frontdesk/config/room-facilities": "room-facilities",
    "frontdesk/config/room-groups": "room-groups",
    "frontdesk/config/room-types": "room-types",
    "frontdesk/config/rooms": "rooms",
    "frontdesk/config/extra-charge-items": "extra-charge-items",
    "frontdesk/config/extra-charge-groups": "extra-charge-groups",
    "frontdesk/config/booking-agents": "booking-agents",
    "frontdesk/config/companies": "companies",
    "frontdesk/config/rate-plans": "rate-plans",
    "frontdesk/config/cancellation-rules": "cancellation-rules",
    "frontdesk/config/board-types": "board-types",
    "frontdesk/config/complimentary-options": "complimentary-options",
    "frontdesk/config/guest-sources": "guest-sources",
    "frontdesk/config/room-type-special-rates": "rate-plans",
    "inventory/config/items": "inventory-items",
    "inventory/config/categories": "inventory-categories",
    "inventory/config/units": "inventory-units",
    "inventory/config/warehouses": "inventory-warehouses",
    "inventory/suppliers": "inventory-suppliers",
    "inventory/purchases": "purchases",
    "inventory/purchases/new": "purchases",
    "inventory/purchases/return": "purchases",
    "inventory/requisitions": "requisitions",
    "inventory/requisitions/new": "requisitions",
    "accounts/chart-of-accounts": "chart-of-accounts",
    "accounts/chart-of-accounts/accounts": "accounts",
    "accounts/chart-of-accounts/groups": "account-groups",
    "accounts/vouchers": "vouchers",
    "accounts/vouchers/cash-payment": "vouchers",
    "accounts/vouchers/bank-payment": "vouchers",
    "accounts/vouchers/cash-receipt": "vouchers",
    "accounts/vouchers/bank-receipt": "vouchers",
    "accounts/vouchers/contra": "vouchers",
    "accounts/vouchers/journal": "vouchers",
    "assets": "assets",
    "assets/types": "asset-types",
    "assets/categories": "asset-categories",
    "assets/vendors": "asset-vendors",
}

SKIP_PARTS = (
    "frontdesk/reservations/new",
    "frontdesk/room-rack",
    "frontdesk/reservations/page",
    "home/page",
    "fnb/orders",
)


def title_of(text: str, rel: str) -> str:
    m = re.search(r"<h1[^>]*>([^<]+)</h1>", text)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    return rel.replace("-", " ").replace("/", " / ").title()


def render(title: str, kind: str, endpoint: str = "/catalog", read_only: bool = False) -> str:
    extra = ""
    if endpoint != "/catalog":
        extra += f"\n      endpoint={endpoint!r}"
    if read_only:
        extra += "\n      readOnly"
    return (
        "'use client'\n"
        "import CatalogScreen from '@/components/CatalogScreen'\n\n"
        "export default function Page() {\n"
        "  return (\n"
        "    <CatalogScreen\n"
        f"      title={title!r}\n"
        f"      kind={kind!r}{extra}\n"
        "    />\n"
        "  )\n"
        "}\n"
    )


changed = 0
skipped = 0
for path in ROOT.rglob("page.tsx"):
    rel = path.relative_to(ROOT).as_posix().replace("/page.tsx", "")
    if any(part in path.as_posix().replace("\\", "/") for part in SKIP_PARTS):
        skipped += 1
        continue
    text = path.read_text(encoding="utf-8")
    if "coming soon" not in text.lower():
        continue
    if path.stat().st_size > 8000:
        skipped += 1
        continue
    title = title_of(text, rel)
    if rel.startswith("reports/") or "/reports/" in rel:
        body = render(title, rel, endpoint="/reports/run", read_only=True)
    elif rel in CONFIG_KIND:
        body = render(title, CONFIG_KIND[rel], endpoint="/config")
    elif rel.startswith("frontdesk/config/"):
        body = render(title, rel.split("/")[-1], endpoint="/config")
    else:
        body = render(title, rel.replace("/", "_"))
    path.write_text(body, encoding="utf-8")
    changed += 1

print(f"updated={changed} skipped={skipped}")
