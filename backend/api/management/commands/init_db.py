"""Initialize database tables and seed default users/tenant."""
from django.core.management.base import BaseCommand

from api.models import Tenant, User, UserRole


class Command(BaseCommand):
    help = 'Create database tables and initial superadmin, tenant, and tenant admin'

    def handle(self, *args, **options):
        from django.core.management import call_command

        self.stdout.write('Initializing database...')
        self.stdout.write('=' * 50)

        self.stdout.write('\n[1/2] Running migrations...')
        call_command('migrate', verbosity=0)
        self.stdout.write(self.style.SUCCESS('[OK] Database tables ready'))

        self.stdout.write('\n[2/2] Creating initial data...')
        self._create_initial_data()

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('[OK] Database initialization complete!'))

    def _create_initial_data(self):
        self._ensure_superadmin()
        tenant = self._ensure_tenant()
        self._ensure_tenant_admin(tenant)
        self._ensure_role_users(tenant)

        self.stdout.write('\nDefault Credentials:')
        self.stdout.write('  Superadmin: superadmin@admin.com / Admin@123')
        self.stdout.write('  Tenant Admin: admin@admin.com / Admin@123')
        self.stdout.write('  Role demos (password Admin@123):')
        self.stdout.write('    ops@turag.com | frontdesk@turag.com | hk@turag.com')
        self.stdout.write('    restaurant@turag.com | accountant@turag.com | purchase@turag.com')

    def _ensure_role_users(self, tenant):
        """Seed least-privilege demo users for each operational hotel role."""
        from api.models.utility import UserAccountPermission
        from api.rbac import resolve_role

        demos = [
            {
                'username': 'ops',
                'email': 'ops@turag.com',
                'first_name': 'Nadia',
                'last_name': 'Rahman',
                'role': UserRole.OPERATIONS_MANAGER,
                'department': 'Operations',
                'designation': 'Operations Manager',
            },
            {
                'username': 'frontdesk',
                'email': 'frontdesk@turag.com',
                'first_name': 'Karim',
                'last_name': 'Hossain',
                'role': UserRole.FRONTDESK,
                'department': 'Front Office',
                'designation': 'Front Desk Agent',
            },
            {
                'username': 'hk',
                'email': 'hk@turag.com',
                'first_name': 'Shirin',
                'last_name': 'Akter',
                'role': UserRole.HOUSEKEEPING,
                'department': 'Housekeeping',
                'designation': 'HK Supervisor',
            },
            {
                'username': 'restaurant',
                'email': 'restaurant@turag.com',
                'first_name': 'Rafi',
                'last_name': 'Islam',
                'role': UserRole.RESTAURANT,
                'department': 'Food & Beverage',
                'designation': 'Restaurant Supervisor',
            },
            {
                'username': 'accountant',
                'email': 'accountant@turag.com',
                'first_name': 'Lamia',
                'last_name': 'Chowdhury',
                'role': UserRole.ACCOUNTANT,
                'department': 'Accounts',
                'designation': 'Accountant',
            },
            {
                'username': 'purchase',
                'email': 'purchase@turag.com',
                'first_name': 'Imran',
                'last_name': 'Kabir',
                'role': UserRole.PURCHASE_OFFICER,
                'department': 'Procurement',
                'designation': 'Purchase Officer',
            },
        ]

        for spec in demos:
            user = User.objects.filter(email=spec['email']).first()
            created = False
            if not user:
                user = User(username=spec['username'], email=spec['email'])
                created = True
            user.first_name = spec['first_name']
            user.last_name = spec['last_name']
            user.role = spec['role']
            user.department = spec['department']
            user.designation = spec['designation']
            user.tenant = tenant
            user.is_active = True
            user.is_superuser = False
            user.is_staff = True
            user.set_password('Admin@123')
            user.save()

            role_def = resolve_role(spec['role'])
            acct = role_def.get('account_permissions')
            if acct:
                perm, _ = UserAccountPermission.objects.get_or_create(
                    tenant=tenant,
                    user=user,
                    defaults=acct,
                )
                for key, value in acct.items():
                    setattr(perm, key, value)
                perm.save()

            msg = f"[OK] {'Created' if created else 'Updated'} role user: {spec['email']} ({spec['role']})"
            self.stdout.write(self.style.SUCCESS(msg) if created else msg)
    def _ensure_superadmin(self):
        superadmin = User.objects.filter(
            models_q_superadmin()
        ).first()

        if not superadmin:
            superadmin = User(
                username='superadmin',
                email='superadmin@admin.com',
                first_name='Super',
                last_name='Admin',
            )
            self.stdout.write(self.style.SUCCESS('[OK] Created superadmin user'))
        else:
            self.stdout.write('[OK] Updated superadmin credentials')

        superadmin.role = UserRole.SUPERADMIN
        superadmin.is_active = True
        superadmin.is_superuser = True
        superadmin.is_staff = True
        superadmin.tenant = None
        superadmin.set_password('Admin@123')
        superadmin.save()

    def _ensure_tenant(self):
        from api.models.tenant import ProductType

        tenant = Tenant.objects.filter(subdomain='turag').first()
        if not tenant:
            tenant = Tenant(
                name='Turag Waterfront Resort',
                subdomain='turag',
                domain='turagwaterfrontresort.com',
                email='contact@turagwaterfrontresort.com',
                phone='+880 1970-863933',
                address='Mouchak-Fulbaria Road, Chabagan Bazar, Kaliakoir, Gazipur',
                city='Gazipur',
                state='Dhaka',
                country='Bangladesh',
                postal_code='1703',
                is_active=True,
                subscription_plan='premium',
                product_type=ProductType.RESORT,
                landing_enabled=True,
                landing_title='Turag Waterfront Resort',
                landing_tagline='Where Nature Meets Comfort. Experience Peace & Adventure at the Best Resort in Gazipur.',
                landing_template='turag',
                seo_title='Turag Waterfront Resort | Best Resort in Gazipur Bangladesh',
                seo_description='Peaceful riverside resort in Mouchak, Gazipur — wooden cottages, pool, dining, and nature on the banks of the Turag River.',
                seo_keywords='Turag Waterfront Resort, Gazipur resort, Mouchak, wooden cottage, riverside resort Bangladesh',
                og_image='/landings/turag/home-gazipur.jpeg',
                logo='/landings/turag/logo.png',
            )
            tenant.apply_product_preset(ProductType.RESORT)
            tenant.save()
            self.stdout.write(self.style.SUCCESS('[OK] Created tenant: Turag Waterfront Resort'))
        else:
            # Ensure SaaS fields are populated on existing tenants
            changed = False
            if not getattr(tenant, 'product_type', None) or tenant.product_type == 'hotel' and 'fnb' not in tenant.get_enabled_modules() and tenant.name.lower().find('resort') >= 0:
                tenant.product_type = ProductType.RESORT
                tenant.apply_product_preset(ProductType.RESORT)
                changed = True
            elif not tenant.enabled_modules or tenant.enabled_modules in ('', '[]'):
                tenant.apply_product_preset(tenant.product_type or ProductType.RESORT)
                changed = True
            if not tenant.landing_title:
                tenant.landing_title = tenant.name
                changed = True
            if not tenant.landing_tagline:
                tenant.landing_tagline = 'Where Nature Meets Comfort. Experience Peace & Adventure at the Best Resort in Gazipur.'
                changed = True
            # Keep Turag sample tenant aligned with official resort identity
            if tenant.subdomain == 'turag':
                updates = {
                    'name': 'Turag Waterfront Resort',
                    'domain': 'turagwaterfrontresort.com',
                    'email': 'contact@turagwaterfrontresort.com',
                    'phone': '+880 1970-863933',
                    'address': 'Mouchak-Fulbaria Road, Chabagan Bazar, Kaliakoir, Gazipur',
                    'city': 'Gazipur',
                    'state': 'Dhaka',
                    'country': 'Bangladesh',
                    'postal_code': '1703',
                    'landing_title': 'Turag Waterfront Resort',
                    'landing_tagline': 'Where Nature Meets Comfort. Experience Peace & Adventure at the Best Resort in Gazipur.',
                    'landing_template': 'turag',
                    'seo_title': 'Turag Waterfront Resort | Best Resort in Gazipur Bangladesh',
                    'seo_description': 'Peaceful riverside resort in Mouchak, Gazipur — wooden cottages, pool, dining, and nature on the banks of the Turag River.',
                    'seo_keywords': 'Turag Waterfront Resort, Gazipur resort, Mouchak, wooden cottage, riverside resort Bangladesh',
                    'og_image': '/landings/turag/home-gazipur.jpeg',
                    'product_type': ProductType.RESORT,
                    'logo': '/landings/turag/logo.png',
                }
                for key, value in updates.items():
                    if getattr(tenant, key) != value:
                        setattr(tenant, key, value)
                        changed = True
                if 'fnb' not in tenant.get_enabled_modules():
                    tenant.apply_product_preset(ProductType.RESORT)
                    changed = True
            if changed:
                tenant.save()
                self.stdout.write('Tenant already exists (SaaS fields refreshed to Resort)')
            else:
                self.stdout.write('Tenant already exists')
        return tenant

    def _ensure_tenant_admin(self, tenant):
        tenant_admin = User.objects.filter(email='admin@admin.com').first()
        if not tenant_admin:
            tenant_admin = User(
                username='admin',
                email='admin@admin.com',
                first_name='Admin',
                last_name='User',
            )
            self.stdout.write(self.style.SUCCESS('[OK] Created tenant admin user'))
        else:
            self.stdout.write('Tenant admin already exists')

        tenant_admin.role = UserRole.ADMIN
        tenant_admin.is_active = True
        tenant_admin.is_superuser = False
        tenant_admin.is_staff = True
        tenant_admin.tenant = tenant
        tenant_admin.set_password('Admin@123')
        tenant_admin.save()


def models_q_superadmin():
    from django.db.models import Q
    return Q(email='superadmin@admin.com') | Q(username='superadmin')
