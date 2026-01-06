"""
샘플 invitation 생성 관리 명령어

사용법:
    python manage.py create_sample_invitations
    python manage.py create_sample_invitations --update
"""

from django.core.management.base import BaseCommand

from apps.templates.models import Template
from apps.templates.services.template_service import TemplateService


class Command(BaseCommand):
    help = "모든 활성 템플릿에 대해 샘플 invitation을 생성합니다."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update",
            action="store_true",
            help="이미 샘플이 있는 템플릿도 업데이트합니다.",
        )

    def handle(self, *args, **options):
        update_existing = options["update"]
        templates = Template.objects.filter(is_active=True)

        self.stdout.write(f"총 {templates.count()}개의 활성 템플릿을 찾았습니다.")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        for template in templates:
            if template.sample_slug and not update_existing:
                self.stdout.write(
                    self.style.WARNING(f"템플릿 '{template.name}' (ID: {template.id})는 이미 샘플이 있습니다. 스킵합니다.")
                )
                skipped_count += 1
                continue

            try:
                sample_invitation = TemplateService.create_sample_invitation(template, update_existing=update_existing)
                if template.sample_slug == sample_invitation.url_slug and update_existing:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"템플릿 '{template.name}' (ID: {template.id})의 샘플을 업데이트했습니다. "
                            f"Slug: {sample_invitation.url_slug}"
                        )
                    )
                    updated_count += 1
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"템플릿 '{template.name}' (ID: {template.id})의 샘플을 생성했습니다. "
                            f"Slug: {sample_invitation.url_slug}"
                        )
                    )
                    created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"템플릿 '{template.name}' (ID: {template.id}) 샘플 생성 중 오류: {str(e)}")
                )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"완료: 생성 {created_count}개, 업데이트 {updated_count}개, 스킵 {skipped_count}개"))
        self.stdout.write("=" * 50)


