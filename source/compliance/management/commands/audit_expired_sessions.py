from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)


class Command(BaseCommand):
    help = (
        "Audit expired JWT session records using a retention period. "
        "This command is read-only and never deletes records."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--retention-days",
            type=int,
            default=30,
            help="Number of days expired sessions are retained before becoming eligible for cleanup.",
        )

    def handle(self, *args, **options):
        retention_days = options["retention_days"]

        if retention_days < 0:
            self.stderr.write(
                self.style.ERROR(
                    "retention-days cannot be negative."
                )
            )
            return

        now = timezone.now()
        retention_cutoff = now - timedelta(days=retention_days)

        expired_tokens = (
            OutstandingToken.objects
            .filter(expires_at__lte=now)
            .select_related("user")
            .order_by("expires_at")
        )

        total = OutstandingToken.objects.count()
        expired_count = expired_tokens.count()

        eligible_tokens = expired_tokens.filter(
            expires_at__lte=retention_cutoff
        )

        retained_tokens = expired_tokens.filter(
            expires_at__gt=retention_cutoff
        )

        eligible_count = eligible_tokens.count()
        retained_count = retained_tokens.count()

        self.stdout.write(
            self.style.NOTICE(
                "JWT SESSION CLEANUP AUDIT - DRY RUN"
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
            f"Total outstanding-token records: {total}"
        )

        self.stdout.write(
            f"Expired session records: {expired_count}"
        )

        self.stdout.write(
            f"Expired but still within retention: {retained_count}"
        )

        self.stdout.write(
            f"Eligible for cleanup: {eligible_count}"
        )

        if expired_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No expired session records require review."
                )
            )
            self.stdout.write(
                "No database records were modified."
            )
            return

        self.stdout.write("")
        self.stdout.write("Expired sessions:")

        for token in expired_tokens:
            is_blacklisted = BlacklistedToken.objects.filter(
                token=token
            ).exists()

            session_status = (
                "BLACKLISTED"
                if is_blacklisted
                else "OUTSTANDING"
            )

            cleanup_status = (
                "ELIGIBLE_FOR_CLEANUP"
                if token.expires_at <= retention_cutoff
                else "WITHIN_RETENTION"
            )

            self.stdout.write(
                (
                    f"- user={token.user.username} "
                    f"jti={token.jti} "
                    f"created={token.created_at.isoformat()} "
                    f"expires={token.expires_at.isoformat()} "
                    f"status={session_status} "
                    f"cleanup_status={cleanup_status}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "DRY RUN ONLY: no database records were deleted."
            )
        )
