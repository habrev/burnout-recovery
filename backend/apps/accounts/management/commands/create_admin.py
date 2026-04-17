from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create a new admin user or promote an existing user to admin'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email address for the admin account')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()

        if not email or '@' not in email:
            raise CommandError(f'"{email}" is not a valid email address.')

        user, created = User.objects.get_or_create(email=email)

        if not user.is_admin:
            user.is_admin = True
            user.is_staff = True
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {email}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'User promoted to admin: {email}'))

        self.stdout.write(
            'This user can now log in via OTP at /login and access /admin4reset'
        )
