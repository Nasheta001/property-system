from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.documents.models import Document
from apps.leases.models import Lease
from apps.leases.services import activate_lease
from apps.maintenance.models import MaintenanceRequest, Vendor
from apps.maintenance.services import assign, verify
from apps.organizations.models import Membership, Organization
from apps.payments.models import Payment
from apps.payments.services import mark_payment_paid
from apps.properties.models import Building, Floor, Property, Unit
from apps.tenants.models import TenantProfile
from apps.users.models import User

DEMO_OWNER_EMAIL = "owner@demo.propertysystem.local"
DEMO_OWNER_PASSWORD = "DemoPassword123!"
DEMO_MANAGER_EMAIL = "manager@demo.propertysystem.local"
DEMO_MANAGER_PASSWORD = "DemoPassword123!"


class Command(BaseCommand):
    help = "Seeds the database with a demo organization, users, and property hierarchy for local development."

    @transaction.atomic
    def handle(self, *args, **options):
        owner, owner_created = User.objects.get_or_create(
            email=DEMO_OWNER_EMAIL,
            defaults={"first_name": "Dana", "last_name": "Okoth", "is_verified": True},
        )
        if owner_created:
            owner.set_password(DEMO_OWNER_PASSWORD)
            owner.save(update_fields=["password"])

        manager, manager_created = User.objects.get_or_create(
            email=DEMO_MANAGER_EMAIL,
            defaults={"first_name": "Kevin", "last_name": "Mwangi", "is_verified": True},
        )
        if manager_created:
            manager.set_password(DEMO_MANAGER_PASSWORD)
            manager.save(update_fields=["password"])

        organization, org_created = Organization.objects.get_or_create(
            slug="green-holdings",
            defaults={
                "name": "Green Holdings",
                "owner": owner,
                "email": "hello@greenholdings.demo",
                "city": "Mombasa",
                "country": "Kenya",
                "currency": "KES",
                "subscription_plan": Organization.SubscriptionPlan.PROFESSIONAL,
                "created_by": owner,
            },
        )

        Membership.objects.get_or_create(
            organization=organization,
            user=owner,
            defaults={"role": Membership.Role.OWNER, "created_by": owner},
        )
        Membership.objects.get_or_create(
            organization=organization,
            user=manager,
            defaults={"role": Membership.Role.PROPERTY_MANAGER, "invited_by": owner, "created_by": owner},
        )

        property_obj, _ = Property.objects.get_or_create(
            organization=organization,
            name="Green Apartments",
            defaults={
                "property_type": Property.PropertyType.RESIDENTIAL,
                "description": "A 2-block residential complex in Bamburi, Mombasa.",
                "address": "Links Road",
                "city": "Bamburi",
                "country": "Kenya",
                "created_by": owner,
            },
        )

        rent_by_type = {
            Unit.UnitType.STUDIO: Decimal("18000"),
            Unit.UnitType.ONE_BEDROOM: Decimal("25000"),
            Unit.UnitType.TWO_BEDROOM: Decimal("38000"),
        }
        bedrooms_by_type = {
            Unit.UnitType.STUDIO: 0,
            Unit.UnitType.ONE_BEDROOM: 1,
            Unit.UnitType.TWO_BEDROOM: 2,
        }

        for block_name in ["Block A", "Block B"]:
            building, _ = Building.objects.get_or_create(
                organization=organization,
                property=property_obj,
                name=block_name,
                defaults={"code": block_name.split()[-1], "created_by": owner},
            )

            for floor_number in range(1, 4):
                floor, _ = Floor.objects.get_or_create(
                    organization=organization,
                    building=building,
                    number=floor_number,
                    defaults={"name": f"Floor {floor_number}", "created_by": owner},
                )

                for unit_index, unit_type in enumerate(
                    [Unit.UnitType.STUDIO, Unit.UnitType.ONE_BEDROOM, Unit.UnitType.TWO_BEDROOM], start=1
                ):
                    unit_number = f"{building.code}{floor_number}{unit_index:02d}"
                    Unit.objects.get_or_create(
                        organization=organization,
                        floor=floor,
                        unit_number=unit_number,
                        defaults={
                            "unit_type": unit_type,
                            "status": Unit.Status.VACANT,
                            "bedrooms": bedrooms_by_type[unit_type],
                            "bathrooms": 1,
                            "rent_amount": rent_by_type[unit_type],
                            "deposit_amount": rent_by_type[unit_type],
                            "created_by": owner,
                        },
                    )

        # --- Tenants & leases --------------------------------------------
        demo_tenants = [
            {
                "first_name": "Amina",
                "last_name": "Hassan",
                "email": "amina.hassan@example.com",
                "phone_number": "+254700111222",
                "occupation": "Nurse",
            },
            {
                "first_name": "Brian",
                "last_name": "Otieno",
                "email": "brian.otieno@example.com",
                "phone_number": "+254700333444",
                "occupation": "Software Engineer",
            },
        ]

        occupied_units = list(Unit.objects.filter(organization=organization).order_by("unit_number")[:2])
        for tenant_data, target_unit in zip(demo_tenants, occupied_units):
            tenant, _ = TenantProfile.objects.get_or_create(
                organization=organization,
                email=tenant_data["email"],
                defaults={**tenant_data, "created_by": owner},
            )
            lease, lease_created = Lease.objects.get_or_create(
                organization=organization,
                unit=target_unit,
                tenant=tenant,
                defaults={
                    "start_date": timezone.now().date().replace(day=1),
                    "rent_amount": target_unit.rent_amount,
                    "deposit_amount": target_unit.deposit_amount,
                    "billing_day": 1,
                    "created_by": owner,
                },
            )
            if lease_created:
                activate_lease(lease, owner)

            if lease.status == Lease.Status.ACTIVE and not lease.payments.exists():
                payment = Payment.objects.create(
                    organization=organization,
                    lease=lease,
                    tenant=tenant,
                    amount=lease.rent_amount,
                    method=Payment.Method.MPESA,
                    payment_date=timezone.now().date(),
                    created_by=owner,
                )
                mark_payment_paid(payment, owner, provider_reference="DEMO-MPESA-REF")

        # --- Maintenance ----------------------------------------------------
        vendor, _ = Vendor.objects.get_or_create(
            organization=organization,
            name="FixIt Plumbing & Electrical",
            defaults={
                "contact_person": "Samuel Kamau",
                "phone_number": "+254700555666",
                "email": "samuel@fixit.demo",
                "specialty": "Plumbing & Electrical",
                "created_by": owner,
            },
        )

        first_occupied_unit = occupied_units[0] if occupied_units else None
        if first_occupied_unit is not None and not MaintenanceRequest.objects.filter(
            organization=organization, unit=first_occupied_unit
        ).exists():
            tenant_for_unit = TenantProfile.objects.filter(
                organization=organization, leases__unit=first_occupied_unit
            ).first()
            request_obj = MaintenanceRequest.objects.create(
                organization=organization,
                unit=first_occupied_unit,
                tenant=tenant_for_unit,
                reported_by=manager,
                title="Leaking kitchen tap",
                description="The kitchen tap has been dripping constantly for two days.",
                category=MaintenanceRequest.Category.PLUMBING,
                priority=MaintenanceRequest.Priority.MEDIUM,
                created_by=manager,
            )
            request_obj = verify(request_obj, owner)
            assign(request_obj, owner, vendor)

        # --- Documents --------------------------------------------------
        first_lease = Lease.objects.filter(organization=organization).order_by("start_date").first()
        if first_lease is not None and not Document.objects.filter(
            organization=organization, lease=first_lease, document_type=Document.DocumentType.LEASE_AGREEMENT
        ).exists():
            document = Document(
                organization=organization,
                lease=first_lease,
                tenant=first_lease.tenant,
                property=first_lease.unit.floor.building.property,
                uploaded_by=owner,
                title=f"Lease agreement — {first_lease.unit.unit_number}",
                document_type=Document.DocumentType.LEASE_AGREEMENT,
                created_by=owner,
            )
            document.file.save(
                f"lease-{first_lease.unit.unit_number}.pdf",
                ContentFile(b"%PDF-1.4\n% Demo placeholder lease agreement.\n"),
                save=True,
            )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"  Organization: {organization.name} ({organization.slug})")
        self.stdout.write(f"  Owner login: {DEMO_OWNER_EMAIL} / {DEMO_OWNER_PASSWORD}")
        self.stdout.write(f"  Manager login: {DEMO_MANAGER_EMAIL} / {DEMO_MANAGER_PASSWORD}")
