from django.core.management.base import BaseCommand

from gatherer.models import *
from tbot.models import *


class Command(BaseCommand):
    help = 'Count of contributors who used Telegram bot for specific issue'

    def add_arguments(self, parser):
        parser.add_argument('ISSUE_NUMBER',
                            type=int,
                            help='Digest issue number')

    def handle(self, *args, **options):
        issue_number = int(options['ISSUE_NUMBER'])
        digest_issue = DigestIssue.objects.get(number=issue_number)
        digest_issue_records = DigestRecord.objects.filter(digest_issue=digest_issue)
        digest_issue_tbot_categorization_attempts = TelegramBotDigestRecordCategorizationAttempt.objects.filter(digest_record__in=digest_issue_records)
        digest_issue_contributors = set([a.telegram_bot_user for a in digest_issue_tbot_categorization_attempts])
        print(len(digest_issue_contributors))
