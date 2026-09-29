from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
)


class Command(BaseCommand):
    help = (
        "Safely remove expired JWT session records beyond the "
        "configured retention period."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--retention-days",
            type=int,
            default=30,
            help=(
                "Number of days expired sessions must be retained "
                "before they become eligible for cleanup."
            ),
        )

        parser.add_argument(
            "--execute",
            action="store_true",
            help="Actually delete eligible expired session records.",
        )

        parser.add_argument(
            "--confirm",
            type=str,
            default="",
            help="Required confirmation value when --execute is used.",
        )

    def handle(self, *args, **options):
        retention_days = options["retention_days"]
        execute = options["execute"]
        confirmation = options["confirm"]

        if retention_days < 0:
            self.stderr.write(
                self.style.ERROR(
                    "retention-days cannot be negative."
                )
            )
            return

        now = timezone.now()
        retention_cutoff = now - timedelta(days=retention_days)

        eligible_tokens = (
            OutstandingToken.objects
            .filter(expires_at__lte=retention_cutoff)
            .select_related("user")
            .order_by("expires_at")
        )

        eligible_count = eligible_tokens.count()

        self.stdout.write(
            self.style.NOTICE(
                "JWT SESSION CLEANUP"
            )
        )

        self.stdout.write(
            f"Current time: {now.isoformat()}"
        )

        self.stdout.write(
            f"Retention period: {retention_days} days"
        )

        self.stdout.write(
            f"Retention cutoff: {retention_cutoff.isoformat()}"
        )

        self.stdout.write(
            f"Eligible session records: {eligible_count}"
        )

        if eligible_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No expired session records are eligible for cleanup."
                )
            )
            self.stdout.write(
                "No database records were modified."
            )
            return

        self.stdout.write("")
        self.stdout.write("Eligible sessions:")

        for token in eligible_tokens:
            self.stdout.write(
                (
                    f"- user={token.user.username} "
                    f"user_id={token.user.id} "
                    f"jti={token.jti} "
                    f"created={token.created_at.isoformat()} "
                    f"expires={token.expires_at.isoformat()}"
                )
            )

        if not execute:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN ONLY: no database records were deleted."
                )
            )
            self.stdout.write(
                "To execute cleanup, provide both:"
            )
            self.stdout.write(
                "  --execute --confirm DELETE"
            )
            return

        if confirmation != "DELETE":
            self.stderr.write("")
            self.stderr.write(
                self.style.ERROR(
                    "Cleanup was NOT executed."
                )
            )
            self.stderr.write(
                "When using --execute, you must provide:"
            )
            self.stderr.write(
                "--confirm DELETE"
            )
            self.stderr.write(
                "No database records were modified."
            )
            return

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "EXECUTION CONFIRMED."
            )
        )

        self.stdout.write(
            "Deleting eligible expired JWT session records..."
        )

        token_ids = list(
            eligible_tokens.values_list("id", flat=True)
        )

        with transaction.atomic():
            deleted_count, deleted_details = (
                OutstandingToken.objects
                .filter(id__in=token_ids)
                .delete()
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                (
                    f"Cleanup completed. "
                    f"Deleted {deleted_count} database record(s)."
                )
            )
        )

        self.stdout.write(
            "AuditLog records were not targeted by this cleanup."
        )

        if deleted_details:
            self.stdout.write(
                f"Deletion details: {deleted_details}"
            )
