from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.organizations.models import Membership, Organization
from apps.properties.models import Building, Floor, Property, Unit
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

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(f"  Organization: {organization.name} ({organization.slug})")
        self.stdout.write(f"  Owner login: {DEMO_OWNER_EMAIL} / {DEMO_OWNER_PASSWORD}")
        self.stdout.write(f"  Manager login: {DEMO_MANAGER_EMAIL} / {DEMO_MANAGER_PASSWORD}")
