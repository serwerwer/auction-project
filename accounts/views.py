
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Pseudonym


User = get_user_model()


@login_required
@require_http_methods(["GET", "POST"])
def pseudonym_settings(request):
    accepted = Pseudonym.objects.filter(
        assigned_to=request.user,
        accepted_at__isnull=False,
    ).first()

    if accepted:
        request.session.pop("pseudonym_candidate", None)

        return render(
            request,
            "accounts/pseudonym.html",
            {"accepted": accepted},
        )

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "draw":
            current_id = request.session.get("pseudonym_candidate")

            # Draw from pseudonyms that have never been accepted
            available = Pseudonym.objects.filter(
                assigned_to__isnull=True,
                accepted_at__isnull=True,
            )

            alternative = available.exclude(
                pk=current_id
            ).order_by("?").first()

            candidate = alternative or available.order_by("?").first()

            if candidate is None:
                request.session.pop("pseudonym_candidate", None)
                messages.error(request, "Brak wolnych pseudonimów.")
            else:
                request.session["pseudonym_candidate"] = candidate.pk

            return redirect("pseudonym_settings")

        if action == "accept":
            candidate_id = request.session.get("pseudonym_candidate")

            if candidate_id is None:
                messages.error(request, "Najpierw wylosuj pseudonim.")
                return redirect("pseudonym_settings")

            with transaction.atomic():
                # Serialize acceptance requests for the same user
                User.objects.select_for_update().get(pk=request.user.pk)

                existing = Pseudonym.objects.filter(
                    assigned_to=request.user,
                    accepted_at__isnull=False,
                ).first()

                if existing is not None:
                    messages.info(
                        request,
                        "Masz już zaakceptowany pseudonim.",
                    )
                else:
                    # Lock the candidate against concurrent acceptance
                    candidate = Pseudonym.objects.select_for_update().filter(
                        pk=candidate_id,
                        assigned_to__isnull=True,
                        accepted_at__isnull=True,
                    ).first()

                    if candidate is None:
                        messages.error(
                            request,
                            "Pseudonim został już zajęty. Wylosuj kolejny.",
                        )
                    else:
                        candidate.assigned_to = request.user
                        candidate.accepted_at = timezone.now()
                        candidate.save(
                            update_fields=["assigned_to", "accepted_at"]
                        )

                        messages.success(
                            request,
                            "Pseudonim został przypisany na stałe.",
                        )

            request.session.pop("pseudonym_candidate", None)
            return redirect("pseudonym_settings")

        messages.error(request, "Nieznana operacja.")
        return redirect("pseudonym_settings")

    candidate_id = request.session.get("pseudonym_candidate")

    candidate = Pseudonym.objects.filter(
        pk=candidate_id,
        assigned_to__isnull=True,
        accepted_at__isnull=True,
    ).first()

    return render(
        request,
        "accounts/pseudonym.html",
        {
            "accepted": None,
            "candidate": candidate,
        },
    )