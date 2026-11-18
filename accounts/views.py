from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Pseudonym
from .forms import ProfileForm

# Get our custom User model
User = get_user_model()

# Allow only logged-in users to manage their pseudonyms
# GET displays the page and POST handles user actions
@login_required
@require_http_methods(["GET", "POST"])
def pseudonym_settings(request):

    # Check if the user already accepted a pseudonym
    accepted = Pseudonym.objects.filter(
        assigned_to=request.user,
        accepted_at__isnull=False,
    ).first()

    # Handle users who already have a permanent pseudonym
    if accepted:

        # Remove any old pseudonym candidate from the session
        request.session.pop("pseudonym_candidate", None)

        # Allow users to change how their name appears in auctions
        if request.method == "POST":
            action = request.POST.get("action")

            # Show the accepted pseudonym instead of the real name
            if action == "use_pseudonym":
                request.user.use_pseudonym = True

            # Show the real name instead of the pseudonym
            elif action == "use_real_name":
                request.user.use_pseudonym = False

            # Reject actions that are not supported
            else:
                messages.error(request, "Nieznana operacja.")
                return redirect("pseudonym_settings")

            # Save the user's preferred public name
            request.user.save(update_fields=["use_pseudonym"])

            messages.success(
                request,
                "Sposób wyświetlania nazwy został zmieniony.",
            )

            # Reload the page to show the updated preference
            return redirect("pseudonym_settings")

        # Display the accepted pseudonym and visibility settings
        return render(
            request,
            "accounts/pseudonym.html",
            {"accepted": accepted},
        )

    # Handle pseudonym drawing and acceptance
    if request.method == "POST":
        action = request.POST.get("action")

        # Draw a random pseudonym from the available pool
        if action == "draw":

            # Get the pseudonym displayed during the previous draw
            current_id = request.session.get("pseudonym_candidate")

            # Find pseudonyms that have not been assigned to anyone
            available = Pseudonym.objects.filter(
                assigned_to__isnull=True,
                accepted_at__isnull=True,
            )

            # Try to draw a different pseudonym than the previous one
            alternative = available.exclude(
                pk=current_id
            ).order_by("?").first()

            # Reuse the previous option if no alternative is available
            candidate = alternative or available.order_by("?").first()

            # Show an error if the entire pseudonym pool is taken
            if candidate is None:
                request.session.pop("pseudonym_candidate", None)
                messages.error(request, "Brak wolnych pseudonimów.")

            else:
                # Save the candidate ID in the user's session
                # Drawing does not permanently reserve the pseudonym
                request.session["pseudonym_candidate"] = candidate.pk

            return redirect("pseudonym_settings")

        # Permanently assign the selected pseudonym
        if action == "accept":

            # Read the previously drawn candidate from the session
            candidate_id = request.session.get("pseudonym_candidate")

            # Do not accept a pseudonym that was never drawn
            if candidate_id is None:
                messages.error(request, "Najpierw wylosuj pseudonim.")
                return redirect("pseudonym_settings")

            # Keep database changes together in one transaction
            with transaction.atomic():

                # Lock the user to prevent two simultaneous acceptances
                locked_user = User.objects.select_for_update().get(
                    pk=request.user.pk
                )

                # Check if another request already assigned a pseudonym
                existing = Pseudonym.objects.filter(
                    assigned_to=locked_user,
                    accepted_at__isnull=False,
                ).first()

                if existing is not None:
                    messages.info(
                        request,
                        "Masz już przypisany pseudonim.",
                    )

                else:
                    # Lock the candidate while checking availability
                    # Another user cannot accept it at the same time
                    candidate = Pseudonym.objects.select_for_update().filter(
                        pk=candidate_id,
                        assigned_to__isnull=True,
                        accepted_at__isnull=True,
                    ).first()

                    # Ask for another draw if the candidate is already taken
                    if candidate is None:
                        messages.error(
                            request,
                            "Pseudonim jest już niedostępny. Wylosuj kolejny.",
                        )

                    else:
                        # Assign the pseudonym permanently to this user
                        candidate.assigned_to = locked_user
                        candidate.accepted_at = timezone.now()
                        candidate.save(
                            update_fields=["assigned_to", "accepted_at"]
                        )

                        # Start displaying the pseudonym after acceptance
                        locked_user.use_pseudonym = True
                        locked_user.save(update_fields=["use_pseudonym"])

                        messages.success(
                            request,
                            "Pseudonim został przypisany na stałe.",
                        )

            # Clear the candidate after the acceptance attempt
            request.session.pop("pseudonym_candidate", None)

            return redirect("pseudonym_settings")

        # Reject unknown POST actions
        messages.error(request, "Nieznana operacja.")
        return redirect("pseudonym_settings")

    # Read the candidate saved during the previous draw
    candidate_id = request.session.get("pseudonym_candidate")

    # Show the candidate only if it is still available
    candidate = Pseudonym.objects.filter(
        pk=candidate_id,
        assigned_to__isnull=True,
        accepted_at__isnull=True,
    ).first()

    # Display the drawing page for users without a pseudonym
    return render(
        request,
        "accounts/pseudonym.html",
        {
            "accepted": None,
            "candidate": candidate,
        },
    )


# Display and update the user's account details
@login_required
@require_http_methods(["GET", "POST"])
def account_profile(request):

    # Load the user's existing profile data
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)

        # Save the new first and last name if both are valid
        if form.is_valid():
            form.save()
            messages.success(request, "Dane konta zostały zapisane.")
            return redirect("account_profile")

    else:
        form = ProfileForm(instance=request.user)

    # Check if the user has already accepted a pseudonym
    pseudonym = Pseudonym.objects.filter(
        assigned_to=request.user,
        accepted_at__isnull=False,
    ).first()

    # Display the account panel
    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "pseudonym": pseudonym,
        },
    )
