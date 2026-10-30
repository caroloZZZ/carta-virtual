from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from restaurantes.forms import RegistroUsuarioForm, RegistroRestauranteForm


@csrf_protect
def login_view(request):
    """Vista de login"""
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido, {user.username}!")
            next_url = request.GET.get("next", "dashboard:dashboard")
            return redirect(next_url)
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "auth/login.html")


def logout_view(request):
    """Vista de logout"""
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("home")


def home(request):
    """Redirige al dashboard si está autenticado, al login si no."""
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")
    return redirect("login")


def registro_completo(request):
    """Vista de registro completo (usuario + restaurante)"""
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        user_form = RegistroUsuarioForm(request.POST)
        restaurante_form = RegistroRestauranteForm(request.POST, request.FILES)

        if user_form.is_valid() and restaurante_form.is_valid():
            user = user_form.save()
            user.email = user_form.cleaned_data["email"]
            user.save()

            restaurante = restaurante_form.save(commit=False)
            restaurante.usuario = user
            restaurante.save()

            login(request, user)

            messages.success(request, "¡Registro completado exitosamente!")
            messages.info(request, "Completa la configuración de tu menú.")

            return redirect("dashboard:dashboard")
    else:
        user_form = RegistroUsuarioForm()
        restaurante_form = RegistroRestauranteForm()

    return render(
        request,
        "restaurantes/registro.html",
        {
            "user_form": user_form,
            "restaurante_form": restaurante_form,
        },
    )


def error_404(request, exception):
    return render(request, "core/error_404.html", status=404)


def error_500(request):
    return render(request, "core/error_500.html", status=500)
